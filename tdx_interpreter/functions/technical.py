#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信技术指标函数实现

实现常用的技术分析指标，包括：
- 移动平均线（MA, EMA, SMA）
- 趋势指标（MACD, KDJ, RSI）
- 波动率指标（BOLL, ATR）
- 成交量指标（OBV, VR）
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple
from .base import TDXFunction, FunctionCategory, Parameter, ParameterType


class MAFunction(TDXFunction):
    """
    简单移动平均线函数
    
    计算指定周期的简单移动平均值。
    """
    
    @property
    def name(self) -> str:
        return "MA"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算简单移动平均线"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="移动平均周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算简单移动平均线
        
        Args:
            data: 价格序列
            period: 移动平均周期
            
        Returns:
            pd.Series: 移动平均线序列
        """
        return data.rolling(window=period, min_periods=1).mean()


class EMAFunction(TDXFunction):
    """
    指数移动平均线函数
    
    计算指定周期的指数移动平均值。
    """
    
    @property
    def name(self) -> str:
        return "EMA"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算指数移动平均线"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="移动平均周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算指数移动平均线
        
        Args:
            data: 价格序列
            period: 移动平均周期
            
        Returns:
            pd.Series: 指数移动平均线序列
        """
        return data.ewm(span=period, adjust=False).mean()


class SMAFunction(TDXFunction):
    """
    平滑移动平均线函数
    
    计算平滑移动平均线，类似于指数移动平均线但使用不同的平滑因子。
    """
    
    @property
    def name(self) -> str:
        return "SMA"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算平滑移动平均线"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="移动平均周期"),
            Parameter("weight", ParameterType.NUMBER, default_value=1.0, required=False, description="权重因子"),
        ]
    
    def calculate(self, data: pd.Series, period: int, weight: float = 1.0) -> pd.Series:
        """
        计算平滑移动平均线
        
        Args:
            data: 价格序列
            period: 移动平均周期
            weight: 权重因子
            
        Returns:
            pd.Series: 平滑移动平均线序列
        """
        alpha = weight / period
        return data.ewm(alpha=alpha, adjust=False).mean()


class MACDFunction(TDXFunction):
    """
    MACD指标函数
    
    计算MACD（Moving Average Convergence Divergence）指标。
    """
    
    @property
    def name(self) -> str:
        return "MACD"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算MACD指标"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("fast_period", ParameterType.INTEGER, default_value=12, required=False, min_value=1, description="快速EMA周期"),
            Parameter("slow_period", ParameterType.INTEGER, default_value=26, required=False, min_value=1, description="慢速EMA周期"),
            Parameter("signal_period", ParameterType.INTEGER, default_value=9, required=False, min_value=1, description="信号线周期"),
        ]
    
    def calculate(self, data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算MACD指标
        
        Args:
            data: 价格序列
            fast_period: 快速EMA周期
            slow_period: 慢速EMA周期
            signal_period: 信号线周期
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: (MACD线, 信号线, 柱状图)
        """
        # 计算快速和慢速EMA
        ema_fast = data.ewm(span=fast_period).mean()
        ema_slow = data.ewm(span=slow_period).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram


class RSIFunction(TDXFunction):
    """
    相对强弱指标函数
    
    计算RSI（Relative Strength Index）指标。
    """
    
    @property
    def name(self) -> str:
        return "RSI"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算相对强弱指标"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("period", ParameterType.INTEGER, default_value=14, required=False, min_value=1, description="RSI周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            data: 价格序列
            period: RSI周期
            
        Returns:
            pd.Series: RSI序列
        """
        # 计算价格变化
        delta = data.diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均收益和平均损失
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 计算RS和RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


class BOLLFunction(TDXFunction):
    """
    布林带指标函数
    
    计算布林带（Bollinger Bands）指标。
    """
    
    @property
    def name(self) -> str:
        return "BOLL"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算布林带指标"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="价格序列"),
            Parameter("period", ParameterType.INTEGER, default_value=20, required=False, min_value=1, description="移动平均周期"),
            Parameter("std_dev", ParameterType.NUMBER, default_value=2.0, required=False, min_value=0.1, description="标准差倍数"),
        ]
    
    def calculate(self, data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带指标
        
        Args:
            data: 价格序列
            period: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: (上轨, 中轨, 下轨)
        """
        # 计算中轨（移动平均线）
        middle_band = data.rolling(window=period).mean()
        
        # 计算标准差
        std = data.rolling(window=period).std()
        
        # 计算上轨和下轨
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band


class KDJFunction(TDXFunction):
    """
    KDJ随机指标函数
    
    计算KDJ（Stochastic Oscillator）指标。
    """
    
    @property
    def name(self) -> str:
        return "KDJ"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算KDJ随机指标"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("high", ParameterType.SERIES, description="最高价序列"),
            Parameter("low", ParameterType.SERIES, description="最低价序列"),
            Parameter("close", ParameterType.SERIES, description="收盘价序列"),
            Parameter("k_period", ParameterType.INTEGER, default_value=9, required=False, min_value=1, description="K值周期"),
            Parameter("d_period", ParameterType.INTEGER, default_value=3, required=False, min_value=1, description="D值周期"),
            Parameter("j_period", ParameterType.INTEGER, default_value=3, required=False, min_value=1, description="J值周期"),
        ]
    
    def calculate(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                 k_period: int = 9, d_period: int = 3, j_period: int = 3) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_period: K值周期
            d_period: D值周期
            j_period: J值周期
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: (K值, D值, J值)
        """
        # 计算最高价和最低价的滚动窗口
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        # 计算RSV（Raw Stochastic Value）
        rsv = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # 计算K值（使用SMA平滑）
        k_values = rsv.ewm(span=d_period, adjust=False).mean()
        
        # 计算D值
        d_values = k_values.ewm(span=j_period, adjust=False).mean()
        
        # 计算J值
        j_values = 3 * k_values - 2 * d_values
        
        return k_values, d_values, j_values


class ATRFunction(TDXFunction):
    """
    平均真实波幅函数
    
    计算ATR（Average True Range）指标。
    """
    
    @property
    def name(self) -> str:
        return "ATR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TECHNICAL
    
    @property
    def description(self) -> str:
        return "计算平均真实波幅"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("high", ParameterType.SERIES, description="最高价序列"),
            Parameter("low", ParameterType.SERIES, description="最低价序列"),
            Parameter("close", ParameterType.SERIES, description="收盘价序列"),
            Parameter("period", ParameterType.INTEGER, default_value=14, required=False, min_value=1, description="ATR周期"),
        ]
    
    def calculate(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        计算ATR指标
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: ATR周期
            
        Returns:
            pd.Series: ATR序列
        """
        # 计算前一日收盘价
        prev_close = close.shift(1)
        
        # 计算真实波幅的三个组成部分
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        # 计算真实波幅
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR（使用EMA平滑）
        atr = true_range.ewm(span=period, adjust=False).mean()
        
        return atr