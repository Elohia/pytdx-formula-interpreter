#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内置指标模块

实现常用技术指标的模块化封装，提供标准化的计算接口。
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, Any, Optional
from .base import BaseIndicatorModule, IndicatorResult, IndicatorType


class MovingAverageModule(BaseIndicatorModule):
    """
    移动平均线指标模块
    
    支持简单移动平均(SMA)、指数移动平均(EMA)等多种类型。
    """
    
    def __init__(self, period: int = 20, ma_type: str = "SMA", field: str = "CLOSE"):
        """
        初始化移动平均线模块
        
        Args:
            period: 计算周期
            ma_type: 移动平均类型，支持SMA、EMA、WMA
            field: 计算字段
        """
        self.period = period
        self.ma_type = ma_type.upper()
        self.field = field.upper()
        
        # 参数验证
        if self.period <= 0:
            raise ValueError("Period must be positive")
        if self.ma_type not in ['SMA', 'EMA', 'WMA']:
            raise ValueError(f"Unsupported MA type: {ma_type}")
            
        super().__init__(
            name=f"{ma_type}{period}",
            parameters={'period': period, 'ma_type': ma_type, 'field': field}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.TREND
    
    @property
    def required_fields(self) -> list:
        return [self.field]
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'period': 20, 'ma_type': 'SMA', 'field': 'CLOSE'}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        实现移动平均线计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            pd.Series: 移动平均线序列
        """
        if self.field not in data.columns:
            raise ValueError(f"Field '{self.field}' not found in data")
        
        series = data[self.field]
        
        if self.ma_type == 'SMA':
            return series.rolling(window=self.period).mean()
        elif self.ma_type == 'EMA':
            return series.ewm(span=self.period).mean()
        elif self.ma_type == 'WMA':
            # 加权移动平均
            weights = np.arange(1, self.period + 1)
            return series.rolling(window=self.period).apply(
                lambda x: np.average(x, weights=weights), raw=True
            )
        else:
            raise ValueError(f"Unsupported MA type: {self.ma_type}")


class RSIModule(BaseIndicatorModule):
    """
    相对强弱指标(RSI)模块
    
    计算价格变动的相对强弱程度。
    """
    
    def __init__(self, period: int = 14, field: str = "CLOSE"):
        """        初始化RSI模块
        
        Args:
            period: 计算周期
            field: 计算字段
        """
        self.period = period
        self.field = field.upper()
        
        if self.period <= 0:
            raise ValueError("Period must be positive")
            
        super().__init__(
            name="RSI",
            parameters={'period': period, 'field': field}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.OSCILLATOR
    
    @property
    def required_fields(self) -> list:
        return [self.field]
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'period': 14, 'field': 'CLOSE'}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        实现RSI计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            pd.Series: RSI序列
        """
        if self.field not in data.columns:
            raise ValueError(f"Field '{self.field}' not found in data")
        
        series = data[self.field]
        delta = series.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算RSI
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        rsi_series = self._calculate_impl(data, **kwargs)
        
        result_data = pd.DataFrame({
            f'{self.name}': rsi_series
        }, index=data.index)
        
        # 将元数据信息添加到参数中
        merged_params = {
            **self.parameters,
            **kwargs,
            'overbought_level': 70,
            'oversold_level': 30
        }
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters=merged_params,
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )


class MACDModule(BaseIndicatorModule):
    """
    MACD指标模块
    
    计算移动平均收敛发散指标。
    """
    
    def __init__(self, 
                 fast_period: int = 12, 
                 slow_period: int = 26, 
                 signal_period: int = 9,
                 field: str = "CLOSE"):
        """
        初始化MACD模块
        
        Args:
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            field: 计算字段
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.field = field.upper()
        
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
            
        super().__init__(
            name="MACD",
            parameters={
                'fast_period': fast_period,
                'slow_period': slow_period, 
                'signal_period': signal_period,
                'field': field
            }
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.MOMENTUM
    
    @property
    def required_fields(self) -> list:
        return [self.field]
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'field': 'CLOSE'}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> tuple:
        """
        实现MACD计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            tuple: (MACD线, 信号线, 柱状图)
        """
        if self.field not in data.columns:
            raise ValueError(f"Field '{self.field}' not found in data")
        
        series = data[self.field]
        
        # 计算快慢EMA
        ema_fast = series.ewm(span=self.fast_period).mean()
        ema_slow = series.ewm(span=self.slow_period).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=self.signal_period).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return (macd_line, signal_line, histogram)
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算MACD指标
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 包含MACD各组件的结果
        """
        # 验证数据
        self.validate_data(data)
        
        # 计算MACD
        macd_line, signal_line, histogram = self._calculate_impl(data, **kwargs)
        
        # 创建包含所有MACD组件的DataFrame
        result_data = pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }, index=data.index)
        
        # 创建参数字典，包含metadata信息
        parameters = self.parameters.copy()
        parameters.update({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters=parameters,
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=f"{self.name}_{hash(str(self.parameters))}"
        )


class BollingerBandsModule(BaseIndicatorModule):
    """
    布林带指标模块
    
    计算价格的布林带通道。
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, field: str = "CLOSE"):
        """
        初始化布林带模块
        
        Args:
            period: 计算周期
            std_dev: 标准差倍数
            field: 计算字段
        """
        self.period = period
        self.std_dev = std_dev
        self.field = field.upper()
        
        if self.period <= 0:
            raise ValueError("Period must be positive")
        if self.std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
            
        super().__init__(
            name=f"BOLL({period},{std_dev})",
            parameters={'period': period, 'std_dev': std_dev, 'field': field}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VOLATILITY
    
    @property
    def required_fields(self) -> list:
        return [self.field]
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'period': 20, 'std_dev': 2.0, 'field': 'CLOSE'}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> tuple:
        """
        实现布林带计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            tuple: (上轨, 中轨, 下轨)
        """
        if self.field not in data.columns:
            raise ValueError(f"Field '{self.field}' not found in data")
        
        series = data[self.field]
        
        # 计算中轨（移动平均）
        middle = series.rolling(window=self.period).mean()
        
        # 计算标准差
        std = series.rolling(window=self.period).std()
        
        # 计算上下轨
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)
        
        return (upper, middle, lower)
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算布林带
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        self._validate_data(data)
        
        if self.field not in data.columns:
            raise ValueError(f"Field '{self.field}' not found in data")
        
        series = data[self.field]
        
        # 计算中轨（移动平均）
        middle_band = series.rolling(window=self.period).mean()
        
        # 计算标准差
        std = series.rolling(window=self.period).std()
        
        # 计算上下轨
        upper_band = middle_band + (std * self.std_dev)
        lower_band = middle_band - (std * self.std_dev)
        
        # 计算带宽和位置
        bandwidth = (upper_band - lower_band) / middle_band * 100
        bb_position = (series - lower_band) / (upper_band - lower_band) * 100
        
        result_data = pd.DataFrame({
            'Upper': upper_band,
            'Middle': middle_band,
            'Lower': lower_band,
            'Bandwidth': bandwidth,
            'Position': bb_position
        }, index=data.index)
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters={
                'period': self.period,
                'std_dev': self.std_dev,
                'field': self.field
            },
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )


class ATRModule(BaseIndicatorModule):
    """
    平均真实波幅(ATR)指标模块
    
    计算价格的平均真实波动范围。
    """
    
    def __init__(self, period: int = 14):
        """
        初始化ATR模块
        
        Args:
            period: 计算周期
        """
        self.period = period
        
        if self.period <= 0:
            raise ValueError("Period must be positive")
            
        super().__init__(
            name=f"ATR{period}",
            parameters={'period': period}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VOLATILITY
    
    @property
    def required_fields(self) -> list:
        return ['HIGH', 'LOW', 'CLOSE']
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'period': 14}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        实现ATR计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            pd.Series: ATR值
        """
        required_fields = ['HIGH', 'LOW', 'CLOSE']
        for field in required_fields:
            if field not in data.columns:
                raise ValueError(f"Field '{field}' not found in data")
        
        high = data['HIGH']
        low = data['LOW']
        close = data['CLOSE']
        prev_close = close.shift(1)
        
        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR（移动平均）
        atr = true_range.rolling(window=self.period).mean()
        
        return atr
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算ATR
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        self._validate_data(data)
        
        required_fields = ['HIGH', 'LOW', 'CLOSE']
        for field in required_fields:
            if field not in data.columns:
                raise ValueError(f"Field '{field}' not found in data")
        
        high = data['HIGH']
        low = data['LOW']
        close = data['CLOSE']
        prev_close = close.shift(1)
        
        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR（使用EMA平滑）
        atr = true_range.ewm(span=self.period).mean()
        
        result_data = pd.DataFrame({
            f'{self.name}': atr,
            'TrueRange': true_range
        }, index=data.index)
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters={
                'period': self.period
            },
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )


class KDJModule(BaseIndicatorModule):
    """
    KDJ随机指标模块
    
    计算价格的随机振荡指标。
    """
    
    def __init__(self, k_period: int = 9, d_period: int = 3, j_factor: int = 3):
        """
        初始化KDJ模块
        
        Args:
            k_period: K值计算周期
            d_period: D值平滑周期
            j_factor: J值计算因子
        """
        self.k_period = k_period
        self.d_period = d_period
        self.j_factor = j_factor
        
        if self.k_period <= 0 or self.d_period <= 0:
            raise ValueError("Periods must be positive")
            
        super().__init__(
            name=f"KDJ({k_period},{d_period},{j_factor})",
            parameters={'k_period': k_period, 'd_period': d_period, 'j_factor': j_factor}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.MOMENTUM
    
    @property
    def required_fields(self) -> list:
        return ['HIGH', 'LOW', 'CLOSE']
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'k_period': 9, 'd_period': 3, 'j_factor': 3}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> tuple:
        """
        实现KDJ计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            tuple: (K值, D值, J值)
        """
        required_fields = ['HIGH', 'LOW', 'CLOSE']
        for field in required_fields:
            if field not in data.columns:
                raise ValueError(f"Field '{field}' not found in data")
        
        high = data['HIGH']
        low = data['LOW']
        close = data['CLOSE']
        
        # 计算最高价和最低价的滚动窗口
        lowest_low = low.rolling(window=self.k_period).min()
        highest_high = high.rolling(window=self.k_period).max()
        
        # 计算RSV (Raw Stochastic Value)
        rsv = 100 * (close - lowest_low) / (highest_high - lowest_low)
        rsv = rsv.fillna(50)  # 填充NaN值
        
        # 计算K值（RSV的移动平均）
        k_values = rsv.ewm(span=self.d_period).mean()
        
        # 计算D值（K值的移动平均）
        d_values = k_values.ewm(span=self.d_period).mean()
        
        # 计算J值
        j_values = self.j_factor * k_values - (self.j_factor - 1) * d_values
        
        return (k_values, d_values, j_values)
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算KDJ
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        self._validate_data(data)
        
        required_fields = ['HIGH', 'LOW', 'CLOSE']
        for field in required_fields:
            if field not in data.columns:
                raise ValueError(f"Field '{field}' not found in data")
        
        high = data['HIGH']
        low = data['LOW']
        close = data['CLOSE']
        
        # 计算最高价和最低价
        highest_high = high.rolling(window=self.k_period).max()
        lowest_low = low.rolling(window=self.k_period).min()
        
        # 计算RSV（未成熟随机值）
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        
        # 计算K值（使用EMA平滑）
        k_values = rsv.ewm(alpha=1/self.d_period).mean()
        
        # 计算D值（K值的EMA）
        d_values = k_values.ewm(alpha=1/self.d_period).mean()
        
        # 计算J值
        j_values = self.j_factor * k_values - (self.j_factor - 1) * d_values
        
        result_data = pd.DataFrame({
            'K': k_values,
            'D': d_values,
            'J': j_values,
            'RSV': rsv
        }, index=data.index)
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters={
                'k_period': self.k_period,
                'd_period': self.d_period,
                'j_factor': self.j_factor,
                'overbought_level': 80,
                'oversold_level': 20
            },
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )


class VolumeModule(BaseIndicatorModule):
    """
    成交量指标模块
    
    计算成交量相关指标。
    """
    
    def __init__(self, period: int = 20):
        """
        初始化成交量模块
        
        Args:
            period: 计算周期
        """
        self.period = period
        
        if self.period <= 0:
            raise ValueError("Period must be positive")
            
        super().__init__(
            name=f"VOL_MA{period}",
            parameters={'period': period}
        )
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VOLUME
    
    @property
    def required_fields(self) -> list:
        return ['VOLUME']
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {'period': 20}
    
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        实现成交量指标计算逻辑
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            pd.Series: 成交量移动平均值
        """
        if 'VOLUME' not in data.columns:
            raise ValueError("Field 'VOLUME' not found in data")
        
        volume = data['VOLUME']
        
        # 计算成交量移动平均
        vol_ma = volume.rolling(window=self.period).mean()
        
        return vol_ma
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """
        计算成交量指标
        
        Args:
            data: K线数据
            **kwargs: 额外参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        self._validate_data(data)
        
        if 'VOLUME' not in data.columns:
            raise ValueError("Field 'VOLUME' not found in data")
        
        volume = data['VOLUME']
        
        # 计算成交量移动平均
        vol_ma = volume.rolling(window=self.period).mean()
        
        # 计算成交量比率
        vol_ratio = volume / vol_ma
        
        # 计算累积成交量
        cumulative_volume = volume.cumsum()
        
        result_data = pd.DataFrame({
            f'{self.name}': vol_ma,
            'Volume': volume,
            'VolumeRatio': vol_ratio,
            'CumulativeVolume': cumulative_volume
        }, index=data.index)
        
        return IndicatorResult(
            name=self.name,
            data=result_data,
            parameters={
                'period': self.period
            },
            timestamp=time.time(),
            dependencies=self.required_fields,
            cache_key=self._generate_cache_key(data, **kwargs)
        )