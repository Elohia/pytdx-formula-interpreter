#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信统计分析函数实现

实现统计分析相关函数，包括：
- 标准差和方差（STD, VAR）
- 相关性分析（CORR, COVAR）
- 分布函数（AVEDEV, DEVSQ）
- 回归分析（SLOPE, FORCAST）
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple
from .base import TDXFunction, FunctionCategory, Parameter, ParameterType


class STDFunction(TDXFunction):
    """
    标准差函数
    
    计算指定周期内的标准差。
    """
    
    @property
    def name(self) -> str:
        return "STD"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的标准差"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算标准差
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 标准差序列
        """
        return data.rolling(window=period, min_periods=1).std()


class VARFunction(TDXFunction):
    """
    方差函数
    
    计算指定周期内的方差。
    """
    
    @property
    def name(self) -> str:
        return "VAR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的方差"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算方差
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 方差序列
        """
        return data.rolling(window=period, min_periods=1).var()


class CORRFunction(TDXFunction):
    """
    相关系数函数
    
    计算两个序列在指定周期内的相关系数。
    """
    
    @property
    def name(self) -> str:
        return "CORR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算两个序列的相关系数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.SERIES, description="第一个数据序列"),
            Parameter("data2", ParameterType.SERIES, description="第二个数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=2, description="统计周期"),
        ]
    
    def calculate(self, data1: pd.Series, data2: pd.Series, period: int) -> pd.Series:
        """
        计算相关系数
        
        Args:
            data1: 第一个数据序列
            data2: 第二个数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 相关系数序列
        """
        return data1.rolling(window=period, min_periods=2).corr(data2)


class COVARFunction(TDXFunction):
    """
    协方差函数
    
    计算两个序列在指定周期内的协方差。
    """
    
    @property
    def name(self) -> str:
        return "COVAR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算两个序列的协方差"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.SERIES, description="第一个数据序列"),
            Parameter("data2", ParameterType.SERIES, description="第二个数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=2, description="统计周期"),
        ]
    
    def calculate(self, data1: pd.Series, data2: pd.Series, period: int) -> pd.Series:
        """
        计算协方差
        
        Args:
            data1: 第一个数据序列
            data2: 第二个数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 协方差序列
        """
        return data1.rolling(window=period, min_periods=2).cov(data2)


class AVEDEVFunction(TDXFunction):
    """
    平均绝对偏差函数
    
    计算指定周期内的平均绝对偏差。
    """
    
    @property
    def name(self) -> str:
        return "AVEDEV"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的平均绝对偏差"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算平均绝对偏差
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 平均绝对偏差序列
        """
        def avedev(x):
            if len(x) == 0:
                return np.nan
            mean_val = x.mean()
            return np.abs(x - mean_val).mean()
        
        return data.rolling(window=period, min_periods=1).apply(avedev, raw=False)


class DEVSQFunction(TDXFunction):
    """
    偏差平方和函数
    
    计算指定周期内的偏差平方和。
    """
    
    @property
    def name(self) -> str:
        return "DEVSQ"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的偏差平方和"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算偏差平方和
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 偏差平方和序列
        """
        def devsq(x):
            if len(x) == 0:
                return np.nan
            mean_val = x.mean()
            return ((x - mean_val) ** 2).sum()
        
        return data.rolling(window=period, min_periods=1).apply(devsq, raw=False)


class SLOPEFunction(TDXFunction):
    """
    斜率函数
    
    计算线性回归的斜率。
    """
    
    @property
    def name(self) -> str:
        return "SLOPE"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算线性回归的斜率"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="因变量数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=2, description="回归周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算线性回归斜率
        
        Args:
            data: 因变量数据序列
            period: 回归周期
            
        Returns:
            pd.Series: 斜率序列
        """
        def slope(y):
            if len(y) < 2:
                return np.nan
            x = np.arange(len(y))
            # 使用最小二乘法计算斜率
            n = len(y)
            sum_x = x.sum()
            sum_y = y.sum()
            sum_xy = (x * y).sum()
            sum_x2 = (x * x).sum()
            
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                return np.nan
            
            return (n * sum_xy - sum_x * sum_y) / denominator
        
        return data.rolling(window=period, min_periods=2).apply(slope, raw=False)


class FORCASTFunction(TDXFunction):
    """
    线性回归预测函数
    
    使用线性回归进行预测。
    """
    
    @property
    def name(self) -> str:
        return "FORCAST"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "使用线性回归进行预测"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=2, description="回归周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        线性回归预测
        
        Args:
            data: 数据序列
            period: 回归周期
            
        Returns:
            pd.Series: 预测值序列
        """
        def forecast(y):
            if len(y) < 2:
                return np.nan
            x = np.arange(len(y))
            # 计算线性回归参数
            n = len(y)
            sum_x = x.sum()
            sum_y = y.sum()
            sum_xy = (x * y).sum()
            sum_x2 = (x * x).sum()
            
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                return y.iloc[-1]  # 如果无法计算回归，返回最后一个值
            
            # 计算斜率和截距
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
            
            # 预测下一个值（x = len(y)）
            return slope * len(y) + intercept
        
        return data.rolling(window=period, min_periods=2).apply(forecast, raw=False)


class SKEWFunction(TDXFunction):
    """
    偏度函数
    
    计算指定周期内的偏度。
    """
    
    @property
    def name(self) -> str:
        return "SKEW"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的偏度"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=3, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算偏度
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 偏度序列
        """
        return data.rolling(window=period, min_periods=3).skew()


class KURTFunction(TDXFunction):
    """
    峰度函数
    
    计算指定周期内的峰度。
    """
    
    @property
    def name(self) -> str:
        return "KURT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.STATISTICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的峰度"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=4, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算峰度
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 峰度序列
        """
        return data.rolling(window=period, min_periods=4).kurt()