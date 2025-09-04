#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选过滤层实现

提供灵活的数据筛选和条件过滤功能，支持链式调用和组合逻辑。
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from .base import IndicatorResult


class FilterOperator(Enum):
    """筛选操作符"""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class FilterCondition:
    """
    筛选条件
    
    封装单个筛选条件的定义和执行逻辑
    """
    name: str                                    # 条件名称
    condition: Callable                          # 条件函数
    description: str = ""                       # 条件描述
    enabled: bool = True                         # 是否启用
    
    def apply(self, data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
        """
        应用筛选条件
        
        Args:
            data: 原始K线数据
            indicators: 指标计算结果字典
            
        Returns:
            pd.Series: 布尔掩码，True表示满足条件
        """
        if not self.enabled:
            return pd.Series(True, index=data.index)
        
        try:
            result = self.condition(data, indicators)
            
            # 确保返回布尔Series
            if isinstance(result, pd.Series):
                return result.astype(bool)
            elif isinstance(result, (bool, np.bool_)):
                return pd.Series(result, index=data.index)
            elif isinstance(result, (list, np.ndarray)):
                return pd.Series(result, index=data.index).astype(bool)
            else:
                raise ValueError(f"Condition '{self.name}' must return boolean data")
                
        except Exception as e:
            raise RuntimeError(f"Error applying condition '{self.name}': {e}")
    
    def __str__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"FilterCondition('{self.name}', {status})"


class FilterLayer:
    """
    筛选过滤层
    
    支持多种筛选条件的组合和链式调用，提供灵活的数据过滤功能。
    """
    
    def __init__(self, name: str = "FilterLayer"):
        """
        初始化筛选层
        
        Args:
            name: 筛选层名称
        """
        self.name = name
        self.conditions: List[FilterCondition] = []
        self.operator = FilterOperator.AND
        self._stats = {
            'total_applied': 0,
            'total_filtered': 0,
            'condition_stats': {}
        }
    
    def add_condition(self, 
                     condition: Callable, 
                     name: str = None, 
                     description: str = "",
                     enabled: bool = True) -> 'FilterLayer':
        """
        添加筛选条件
        
        Args:
            condition: 条件函数，接受(data, indicators)参数，返回布尔值或布尔Series
            name: 条件名称，如果为None则自动生成
            description: 条件描述
            enabled: 是否启用条件
            
        Returns:
            FilterLayer: 返回自身，支持链式调用
        """
        if name is None:
            name = f"condition_{len(self.conditions) + 1}"
        
        filter_condition = FilterCondition(
            name=name,
            condition=condition,
            description=description,
            enabled=enabled
        )
        
        self.conditions.append(filter_condition)
        self._stats['condition_stats'][name] = {
            'applied_count': 0,
            'filtered_count': 0
        }
        
        return self
    
    def remove_condition(self, name: str) -> bool:
        """
        移除筛选条件
        
        Args:
            name: 条件名称
            
        Returns:
            bool: 是否成功移除
        """
        for i, condition in enumerate(self.conditions):
            if condition.name == name:
                del self.conditions[i]
                if name in self._stats['condition_stats']:
                    del self._stats['condition_stats'][name]
                return True
        return False
    
    def enable_condition(self, name: str, enabled: bool = True) -> bool:
        """
        启用或禁用筛选条件
        
        Args:
            name: 条件名称
            enabled: 是否启用
            
        Returns:
            bool: 是否找到并设置成功
        """
        for condition in self.conditions:
            if condition.name == name:
                condition.enabled = enabled
                return True
        return False
    
    def set_operator(self, operator: FilterOperator) -> 'FilterLayer':
        """
        设置条件组合操作符
        
        Args:
            operator: 组合操作符
            
        Returns:
            FilterLayer: 返回自身，支持链式调用
        """
        self.operator = operator
        return self
    
    def apply(self, 
             data: pd.DataFrame, 
             indicators: Dict[str, IndicatorResult],
             return_mask: bool = False) -> Union[pd.DataFrame, pd.Series]:
        """
        应用所有筛选条件
        
        Args:
            data: 原始K线数据
            indicators: 指标计算结果字典
            return_mask: 是否返回布尔掩码而不是筛选后的数据
            
        Returns:
            Union[pd.DataFrame, pd.Series]: 筛选后的数据或布尔掩码
        """
        if not self.conditions:
            return data.copy() if not return_mask else pd.Series(True, index=data.index)
        
        # 应用所有启用的条件
        masks = []
        for condition in self.conditions:
            if condition.enabled:
                mask = condition.apply(data, indicators)
                masks.append(mask)
                
                # 更新统计信息
                self._stats['condition_stats'][condition.name]['applied_count'] += 1
                filtered_count = mask.sum()
                self._stats['condition_stats'][condition.name]['filtered_count'] += filtered_count
        
        if not masks:
            return data.copy() if not return_mask else pd.Series(True, index=data.index)
        
        # 根据操作符组合条件
        if self.operator == FilterOperator.AND:
            combined_mask = masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask & mask
        elif self.operator == FilterOperator.OR:
            combined_mask = masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask | mask
        elif self.operator == FilterOperator.NOT:
            # NOT操作符只对第一个条件取反
            combined_mask = ~masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask & mask
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")
        
        # 更新总体统计信息
        self._stats['total_applied'] += 1
        self._stats['total_filtered'] += combined_mask.sum()
        
        if return_mask:
            return combined_mask
        else:
            return data[combined_mask].copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取筛选统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return self._stats.copy()
    
    def reset_statistics(self) -> None:
        """重置统计信息"""
        self._stats = {
            'total_applied': 0,
            'total_filtered': 0,
            'condition_stats': {name: {'applied_count': 0, 'filtered_count': 0} 
                              for name in self._stats['condition_stats']}
        }
    
    def __len__(self) -> int:
        return len(self.conditions)
    
    def __str__(self) -> str:
        enabled_count = sum(1 for c in self.conditions if c.enabled)
        return f"FilterLayer('{self.name}', {enabled_count}/{len(self.conditions)} conditions, {self.operator.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class PrebuiltFilters:
    """
    预构建的常用筛选条件
    
    提供一些常用的筛选条件，方便快速使用。
    """
    
    @staticmethod
    def trend_up(ma_short: str = "MA5", ma_long: str = "MA20") -> Callable:
        """
        上升趋势筛选：短期均线在长期均线之上
        
        Args:
            ma_short: 短期均线指标名称
            ma_long: 长期均线指标名称
            
        Returns:
            Callable: 筛选条件函数
        """
        def condition(data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
            short_ma = indicators[ma_short].get_series()
            long_ma = indicators[ma_long].get_series()
            return short_ma > long_ma
        
        return condition
    
    @staticmethod
    def rsi_not_overbought(rsi_name: str = "RSI", threshold: float = 70) -> Callable:
        """
        RSI未超买筛选
        
        Args:
            rsi_name: RSI指标名称
            threshold: 超买阈值
            
        Returns:
            Callable: 筛选条件函数
        """
        def condition(data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
            rsi = indicators[rsi_name].get_series()
            return rsi < threshold
        
        return condition
    
    @staticmethod
    def volume_above_average(volume_ma_name: str = "VOL_MA", multiplier: float = 1.2) -> Callable:
        """
        成交量高于平均值筛选
        
        Args:
            volume_ma_name: 成交量均线指标名称
            multiplier: 倍数阈值
            
        Returns:
            Callable: 筛选条件函数
        """
        def condition(data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
            volume = data['VOLUME']
            volume_ma = indicators[volume_ma_name].get_series()
            return volume > volume_ma * multiplier
        
        return condition
    
    @staticmethod
    def price_breakout(period: int = 20, field: str = 'HIGH') -> Callable:
        """
        价格突破筛选：价格突破N日最高/最低价
        
        Args:
            period: 回看周期
            field: 价格字段（HIGH或LOW）
            
        Returns:
            Callable: 筛选条件函数
        """
        def condition(data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
            if field == 'HIGH':
                current_price = data['CLOSE']
                highest = data['HIGH'].rolling(window=period).max().shift(1)
                return current_price > highest
            elif field == 'LOW':
                current_price = data['CLOSE']
                lowest = data['LOW'].rolling(window=period).min().shift(1)
                return current_price < lowest
            else:
                raise ValueError(f"Unsupported field: {field}")
        
        return condition
    
    @staticmethod
    def volatility_filter(atr_name: str = "ATR", atr_ma_period: int = 20, threshold: float = 1.0) -> Callable:
        """
        波动率筛选：ATR高于其移动平均值
        
        Args:
            atr_name: ATR指标名称
            atr_ma_period: ATR移动平均周期
            threshold: 阈值倍数
            
        Returns:
            Callable: 筛选条件函数
        """
        def condition(data: pd.DataFrame, indicators: Dict[str, IndicatorResult]) -> pd.Series:
            atr = indicators[atr_name].get_series()
            atr_ma = atr.rolling(window=atr_ma_period).mean()
            return atr > atr_ma * threshold
        
        return condition