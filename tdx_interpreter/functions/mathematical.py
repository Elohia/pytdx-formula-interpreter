#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信数学运算函数实现

实现常用的数学运算函数，包括：
- 基本运算（ABS, MAX, MIN, SQRT）
- 统计函数（SUM, COUNT, AVERAGE）
- 极值函数（HHV, LLV）
- 数学函数（ROUND, FLOOR, CEIL）
"""

import pandas as pd
import numpy as np
from typing import Union
from .base import TDXFunction, FunctionCategory, Parameter, ParameterType


class ABSFunction(TDXFunction):
    """
    绝对值函数
    
    计算数值或序列的绝对值。
    """
    
    @property
    def name(self) -> str:
        return "ABS"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算绝对值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="数值或序列"),
        ]
    
    def calculate(self, data: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        计算绝对值
        
        Args:
            data: 数值或序列
            
        Returns:
            Union[float, pd.Series]: 绝对值结果
        """
        if isinstance(data, pd.Series):
            return data.abs()
        else:
            return abs(data)


class MAXFunction(TDXFunction):
    """
    最大值函数
    
    计算两个数值或序列的最大值。
    """
    
    @property
    def name(self) -> str:
        return "MAX"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算最大值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.NUMBER, description="第一个数值或序列"),
            Parameter("data2", ParameterType.NUMBER, description="第二个数值或序列"),
        ]
    
    def calculate(self, data1: Union[float, pd.Series], data2: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        计算最大值
        
        Args:
            data1: 第一个数值或序列
            data2: 第二个数值或序列
            
        Returns:
            Union[float, pd.Series]: 最大值结果
        """
        if isinstance(data1, pd.Series) or isinstance(data2, pd.Series):
            return np.maximum(data1, data2)
        else:
            return max(data1, data2)


class MINFunction(TDXFunction):
    """
    最小值函数
    
    计算两个数值或序列的最小值。
    """
    
    @property
    def name(self) -> str:
        return "MIN"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算最小值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.NUMBER, description="第一个数值或序列"),
            Parameter("data2", ParameterType.NUMBER, description="第二个数值或序列"),
        ]
    
    def calculate(self, data1: Union[float, pd.Series], data2: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        计算最小值
        
        Args:
            data1: 第一个数值或序列
            data2: 第二个数值或序列
            
        Returns:
            Union[float, pd.Series]: 最小值结果
        """
        if isinstance(data1, pd.Series) or isinstance(data2, pd.Series):
            return np.minimum(data1, data2)
        else:
            return min(data1, data2)


class SUMFunction(TDXFunction):
    """
    求和函数
    
    计算序列在指定周期内的累计和。
    """
    
    @property
    def name(self) -> str:
        return "SUM"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期的累计和"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="求和周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算累计和
        
        Args:
            data: 数据序列
            period: 求和周期
            
        Returns:
            pd.Series: 累计和序列
        """
        return data.rolling(window=period, min_periods=1).sum()


class COUNTFunction(TDXFunction):
    """
    计数函数
    
    计算序列在指定周期内满足条件的数量。
    """
    
    @property
    def name(self) -> str:
        return "COUNT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内满足条件的数量"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="计数周期"),
        ]
    
    def calculate(self, condition: pd.Series, period: int) -> pd.Series:
        """
        计算满足条件的数量
        
        Args:
            condition: 条件序列（布尔值）
            period: 计数周期
            
        Returns:
            pd.Series: 计数结果序列
        """
        # 将布尔值转换为数值（True=1, False=0）
        numeric_condition = condition.astype(int)
        return numeric_condition.rolling(window=period, min_periods=1).sum()


class HHVFunction(TDXFunction):
    """
    最高值函数
    
    计算序列在指定周期内的最高值。
    """
    
    @property
    def name(self) -> str:
        return "HHV"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的最高值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算最高值
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 最高值序列
        """
        return data.rolling(window=period, min_periods=1).max()


class LLVFunction(TDXFunction):
    """
    最低值函数
    
    计算序列在指定周期内的最低值。
    """
    
    @property
    def name(self) -> str:
        return "LLV"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期内的最低值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="统计周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算最低值
        
        Args:
            data: 数据序列
            period: 统计周期
            
        Returns:
            pd.Series: 最低值序列
        """
        return data.rolling(window=period, min_periods=1).min()


class SQRTFunction(TDXFunction):
    """
    平方根函数
    
    计算数值或序列的平方根。
    """
    
    @property
    def name(self) -> str:
        return "SQRT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算平方根"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="数值或序列"),
        ]
    
    def calculate(self, data: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        计算平方根
        
        Args:
            data: 数值或序列
            
        Returns:
            Union[float, pd.Series]: 平方根结果
        """
        if isinstance(data, pd.Series):
            return np.sqrt(data)
        else:
            return np.sqrt(data)


class POWFunction(TDXFunction):
    """
    幂函数
    
    计算数值或序列的幂。
    """
    
    @property
    def name(self) -> str:
        return "POW"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算幂"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("base", ParameterType.NUMBER, description="底数"),
            Parameter("exponent", ParameterType.NUMBER, description="指数"),
        ]
    
    def calculate(self, base: Union[float, pd.Series], exponent: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        计算幂
        
        Args:
            base: 底数
            exponent: 指数
            
        Returns:
            Union[float, pd.Series]: 幂结果
        """
        return np.power(base, exponent)


class ROUNDFunction(TDXFunction):
    """
    四舍五入函数
    
    将数值或序列四舍五入到指定小数位数。
    """
    
    @property
    def name(self) -> str:
        return "ROUND"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "四舍五入到指定小数位数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="数值或序列"),
            Parameter("decimals", ParameterType.INTEGER, default_value=0, required=False, min_value=0, description="小数位数"),
        ]
    
    def calculate(self, data: Union[float, pd.Series], decimals: int = 0) -> Union[float, pd.Series]:
        """
        四舍五入
        
        Args:
            data: 数值或序列
            decimals: 小数位数
            
        Returns:
            Union[float, pd.Series]: 四舍五入结果
        """
        if isinstance(data, pd.Series):
            return data.round(decimals)
        else:
            return round(data, decimals)


class FLOORFunction(TDXFunction):
    """
    向下取整函数
    
    将数值或序列向下取整。
    """
    
    @property
    def name(self) -> str:
        return "FLOOR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "向下取整"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="数值或序列"),
        ]
    
    def calculate(self, data: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        向下取整
        
        Args:
            data: 数值或序列
            
        Returns:
            Union[float, pd.Series]: 向下取整结果
        """
        if isinstance(data, pd.Series):
            return np.floor(data)
        else:
            return np.floor(data)


class CEILFunction(TDXFunction):
    """
    向上取整函数
    
    将数值或序列向上取整。
    """
    
    @property
    def name(self) -> str:
        return "CEIL"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "向上取整"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="数值或序列"),
        ]
    
    def calculate(self, data: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        向上取整
        
        Args:
            data: 数值或序列
            
        Returns:
            Union[float, pd.Series]: 向上取整结果
        """
        if isinstance(data, pd.Series):
            return np.ceil(data)
        else:
            return np.ceil(data)


class AVERAGEFunction(TDXFunction):
    """
    平均值函数
    
    计算序列在指定周期内的平均值。
    """
    
    @property
    def name(self) -> str:
        return "AVERAGE"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.MATHEMATICAL
    
    @property
    def description(self) -> str:
        return "计算指定周期的平均值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="平均周期"),
        ]
    
    def calculate(self, data: pd.Series, period: int) -> pd.Series:
        """
        计算平均值
        
        Args:
            data: 数据序列
            period: 平均周期
            
        Returns:
            pd.Series: 平均值序列
        """
        return data.rolling(window=period, min_periods=1).mean()