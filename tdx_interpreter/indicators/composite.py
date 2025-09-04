#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复合指标实现

支持多个基础指标的组合计算，实现复杂的交易策略和信号生成。
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from .base import BaseIndicatorModule, IndicatorResult, IndicatorType
from .filter_layer import FilterLayer, FilterCondition


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NEUTRAL = "neutral"


@dataclass
class Signal:
    """
    交易信号
    
    封装单个交易信号的信息
    """
    timestamp: pd.Timestamp          # 信号时间
    signal_type: SignalType          # 信号类型
    strength: float                  # 信号强度 (0-1)
    price: float                     # 信号价格
    confidence: float = 0.0          # 信号置信度 (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)  # 附加信息
    
    def __str__(self) -> str:
        return f"Signal({self.signal_type.value}, {self.strength:.2f}, {self.price:.2f})"


class CompositeIndicator(BaseIndicatorModule):
    """
    复合指标基类
    
    支持多个基础指标的组合计算，实现复杂的交易策略。
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化复合指标
        
        Args:
            name: 指标名称
            description: 指标描述
        """
        super().__init__(name, {'description': description})
        self.description = description
        self.base_indicators: Dict[str, BaseIndicatorModule] = {}
        self.filter_layers: List[FilterLayer] = []
        self.signals: List[Signal] = []
        self._combination_logic: Optional[Callable] = None
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.COMPOSITE
    
    @property
    def required_fields(self) -> List[str]:
        """复合指标的必需字段由其包含的基础指标决定"""
        all_fields = set()
        for indicator in self.base_indicators.values():
            all_fields.update(indicator.required_fields)
        return list(all_fields)
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        实现复合指标计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            pd.DataFrame: 复合指标结果
        """
        # 计算所有基础指标
        indicators = {}
        for alias, indicator in self.base_indicators.items():
            indicators[alias] = indicator.calculate(data, **kwargs)
        
        # 应用组合逻辑
        if self._combination_logic:
            return self._combination_logic(data, indicators)
        else:
            return self._default_combination(data, indicators)
    
    def add_indicator(self, indicator: BaseIndicatorModule, alias: str = None) -> 'CompositeIndicator':
        """
        添加基础指标
        
        Args:
            indicator: 基础指标实例
            alias: 指标别名，如果为None则使用指标名称
            
        Returns:
            CompositeIndicator: 返回自身，支持链式调用
        """
        key = alias or indicator.name
        self.base_indicators[key] = indicator
        return self
    
    def add_filter_layer(self, filter_layer: FilterLayer) -> 'CompositeIndicator':
        """
        添加筛选层
        
        Args:
            filter_layer: 筛选层实例
            
        Returns:
            CompositeIndicator: 返回自身，支持链式调用
        """
        self.filter_layers.append(filter_layer)
        return self
    
    def set_combination_logic(self, logic: Callable) -> 'CompositeIndicator':
        """
        设置组合逻辑
        
        Args:
            logic: 组合逻辑函数，接受(data, indicators)参数
            
        Returns:
            CompositeIndicator: 返回自身，支持链式调用
        """
        self._combination_logic = logic
        return self
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算复合指标
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        # 验证数据
        self.validate_data(data)
        
        # 计算所有基础指标
        indicator_results = {}
        for alias, indicator in self.base_indicators.items():
            try:
                result = indicator.calculate(data, **kwargs)
                indicator_results[alias] = result
            except Exception as e:
                raise RuntimeError(f"Error calculating indicator '{alias}': {e}")
        
        # 应用筛选层
        filtered_data = data.copy()
        for filter_layer in self.filter_layers:
            try:
                filtered_data = filter_layer.apply(filtered_data, indicator_results)
            except Exception as e:
                raise RuntimeError(f"Error applying filter layer '{filter_layer.name}': {e}")
        
        # 执行组合逻辑
        if self._combination_logic:
            try:
                combined_result = self._combination_logic(filtered_data, indicator_results)
            except Exception as e:
                raise RuntimeError(f"Error in combination logic: {e}")
        else:
            # 默认组合逻辑：简单平均
            combined_result = self._default_combination(filtered_data, indicator_results)
        
        # 生成交易信号
        signals = self._generate_signals(filtered_data, indicator_results, combined_result)
        self.signals.extend(signals)
        
        # 创建结果
        result = IndicatorResult(
            name=self.name,
            data=combined_result,
            parameters={
                'base_indicators': list(self.base_indicators.keys()),
                'filter_layers': len(self.filter_layers),
                'signals_generated': len(signals),
                'filtered_rows': len(filtered_data)
            },
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )
        
        return result
    
    def _default_combination(self, 
                           data: pd.DataFrame, 
                           indicators: Dict[str, IndicatorResult]) -> pd.DataFrame:
        """
        默认组合逻辑：简单平均
        
        Args:
            data: 筛选后的数据
            indicators: 指标结果字典
            
        Returns:
            pd.DataFrame: 组合结果
        """
        if not indicators:
            return pd.DataFrame(index=data.index)
        
        # 获取所有指标的主要序列
        series_list = []
        for result in indicators.values():
            main_series = result.get_series()
            if main_series is not None:
                series_list.append(main_series)
        
        if not series_list:
            return pd.DataFrame(index=data.index)
        
        # 计算平均值
        combined_series = pd.concat(series_list, axis=1).mean(axis=1)
        
        return pd.DataFrame({
            'composite_value': combined_series,
            'component_count': len(series_list)
        }, index=data.index)
    
    def _generate_signals(self, 
                         data: pd.DataFrame, 
                         indicators: Dict[str, IndicatorResult],
                         combined_result: pd.DataFrame) -> List[Signal]:
        """
        生成交易信号（子类可重写）
        
        Args:
            data: 筛选后的数据
            indicators: 指标结果字典
            combined_result: 组合计算结果
            
        Returns:
            List[Signal]: 生成的信号列表
        """
        return []  # 默认不生成信号
    
    def get_signals(self, 
                   signal_type: SignalType = None, 
                   min_strength: float = 0.0) -> List[Signal]:
        """
        获取交易信号
        
        Args:
            signal_type: 筛选信号类型
            min_strength: 最小信号强度
            
        Returns:
            List[Signal]: 符合条件的信号列表
        """
        filtered_signals = self.signals
        
        if signal_type:
            filtered_signals = [s for s in filtered_signals if s.signal_type == signal_type]
        
        if min_strength > 0:
            filtered_signals = [s for s in filtered_signals if s.strength >= min_strength]
        
        return filtered_signals
    
    def clear_signals(self) -> None:
        """清空信号历史"""
        self.signals.clear()
    
    def get_signal_summary(self) -> Dict[str, Any]:
        """
        获取信号统计摘要
        
        Returns:
            Dict[str, Any]: 信号统计信息
        """
        if not self.signals:
            return {'total': 0}
        
        summary = {
            'total': len(self.signals),
            'by_type': {},
            'avg_strength': np.mean([s.strength for s in self.signals]),
            'avg_confidence': np.mean([s.confidence for s in self.signals]),
            'date_range': {
                'start': min(s.timestamp for s in self.signals),
                'end': max(s.timestamp for s in self.signals)
            }
        }
        
        # 按类型统计
        for signal_type in SignalType:
            count = sum(1 for s in self.signals if s.signal_type == signal_type)
            if count > 0:
                summary['by_type'][signal_type.value] = count
        
        return summary


class TrendFollowingStrategy(CompositeIndicator):
    """
    趋势跟踪策略
    
    基于移动平均线和趋势指标的复合策略。
    """
    
    def __init__(self, 
                 ma_short_period: int = 5,
                 ma_long_period: int = 20,
                 rsi_period: int = 14):
        """
        初始化趋势跟踪策略
        
        Args:
            ma_short_period: 短期均线周期
            ma_long_period: 长期均线周期
            rsi_period: RSI周期
        """
        super().__init__(
            name="TrendFollowingStrategy",
            description="基于移动平均线和RSI的趋势跟踪策略"
        )
        
        # 导入并添加具体的指标模块
        from .builtin import MovingAverageModule, RSIModule
        self.add_indicator(MovingAverageModule(period=ma_short_period), "MA_SHORT")
        self.add_indicator(MovingAverageModule(period=ma_long_period), "MA_LONG")
        self.add_indicator(RSIModule(period=rsi_period), "RSI")
        
        self.ma_short_period = ma_short_period
        self.ma_long_period = ma_long_period
        self.rsi_period = rsi_period
    
    def _generate_signals(self, 
                         data: pd.DataFrame, 
                         indicators: Dict[str, IndicatorResult],
                         combined_result: pd.DataFrame) -> List[Signal]:
        """
        生成趋势跟踪信号
        
        Args:
            data: 筛选后的数据
            indicators: 指标结果字典
            combined_result: 组合计算结果
            
        Returns:
            List[Signal]: 生成的信号列表
        """
        signals = []
        
        if 'MA_SHORT' not in indicators or 'MA_LONG' not in indicators:
            return signals
        
        ma_short = indicators['MA_SHORT'].get_series()
        ma_long = indicators['MA_LONG'].get_series()
        rsi = indicators.get('RSI', {}).get_series() if 'RSI' in indicators else None
        
        # 生成买入信号：短期均线上穿长期均线，且RSI不超买
        buy_condition = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
        if rsi is not None:
            buy_condition = buy_condition & (rsi < 70)
        
        # 生成卖出信号：短期均线下穿长期均线，且RSI不超卖
        sell_condition = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
        if rsi is not None:
            sell_condition = sell_condition & (rsi > 30)
        
        # 创建信号
        for idx in data.index:
            if buy_condition.get(idx, False):
                strength = min(1.0, abs(ma_short[idx] - ma_long[idx]) / ma_long[idx])
                confidence = 0.8 if rsi is None else min(0.9, (70 - rsi[idx]) / 70)
                
                signals.append(Signal(
                    timestamp=idx,
                    signal_type=SignalType.BUY,
                    strength=strength,
                    price=data.loc[idx, 'CLOSE'],
                    confidence=confidence,
                    metadata={
                        'ma_short': ma_short[idx],
                        'ma_long': ma_long[idx],
                        'rsi': rsi[idx] if rsi is not None else None
                    }
                ))
            
            elif sell_condition.get(idx, False):
                strength = min(1.0, abs(ma_long[idx] - ma_short[idx]) / ma_long[idx])
                confidence = 0.8 if rsi is None else min(0.9, (rsi[idx] - 30) / 70)
                
                signals.append(Signal(
                    timestamp=idx,
                    signal_type=SignalType.SELL,
                    strength=strength,
                    price=data.loc[idx, 'CLOSE'],
                    confidence=confidence,
                    metadata={
                        'ma_short': ma_short[idx],
                        'ma_long': ma_long[idx],
                        'rsi': rsi[idx] if rsi is not None else None
                    }
                ))
        
        return signals


class MeanReversionStrategy(CompositeIndicator):
    """
    均值回归策略
    
    基于布林带和RSI的均值回归策略。
    """
    
    def __init__(self, 
                 bb_period: int = 20,
                 bb_std: float = 2.0,
                 rsi_period: int = 14):
        """
        初始化均值回归策略
        
        Args:
            bb_period: 布林带周期
            bb_std: 布林带标准差倍数
            rsi_period: RSI周期
        """
        super().__init__(
            name="MeanReversionStrategy",
            description="基于布林带和RSI的均值回归策略"
        )
        
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
    
    def _generate_signals(self, 
                         data: pd.DataFrame, 
                         indicators: Dict[str, IndicatorResult],
                         combined_result: pd.DataFrame) -> List[Signal]:
        """
        生成均值回归信号
        
        Args:
            data: 筛选后的数据
            indicators: 指标结果字典
            combined_result: 组合计算结果
            
        Returns:
            List[Signal]: 生成的信号列表
        """
        signals = []
        
        # 这里需要具体的布林带和RSI指标实现
        # 暂时返回空列表
        return signals


class MultiTimeframeStrategy(CompositeIndicator):
    """
    多时间框架策略
    
    结合多个时间框架的指标进行综合分析。
    """
    
    def __init__(self, timeframes: List[str] = None):
        """
        初始化多时间框架策略
        
        Args:
            timeframes: 时间框架列表，如['1D', '1W', '1M']
        """
        super().__init__(
            name="MultiTimeframeStrategy",
            description="多时间框架综合分析策略"
        )
        
        self.timeframes = timeframes or ['1D', '1W']
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算多时间框架指标
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        # 多时间框架分析的具体实现
        # 这里需要重采样数据到不同时间框架
        # 暂时调用父类方法
        return super().calculate(data, **kwargs)