#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信逻辑判断函数实现

实现逻辑判断和条件处理函数，包括：
- 条件函数（IF, IFF, IFN）
- 逻辑运算（AND, OR, NOT）
- 比较函数（BETWEEN, RANGE）
- 状态函数（EVERY, EXIST）
"""

import pandas as pd
import numpy as np
from typing import Union, Any
from .base import TDXFunction, FunctionCategory, Parameter, ParameterType


class IFFunction(TDXFunction):
    """
    条件判断函数
    
    根据条件返回不同的值。
    """
    
    @property
    def name(self) -> str:
        return "IF"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "根据条件返回不同的值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.ANY, description="条件表达式"),
            Parameter("true_value", ParameterType.ANY, description="条件为真时的返回值"),
            Parameter("false_value", ParameterType.ANY, description="条件为假时的返回值"),
        ]
    
    def calculate(self, condition: Union[bool, pd.Series], true_value: Any, false_value: Any) -> Any:
        """
        条件判断
        
        Args:
            condition: 条件表达式
            true_value: 条件为真时的返回值
            false_value: 条件为假时的返回值
            
        Returns:
            Any: 根据条件返回的值
        """
        if isinstance(condition, pd.Series):
            return np.where(condition, true_value, false_value)
        else:
            return true_value if condition else false_value


class ANDFunction(TDXFunction):
    """
    逻辑与函数
    
    计算两个条件的逻辑与。
    """
    
    @property
    def name(self) -> str:
        return "AND"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "计算逻辑与"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition1", ParameterType.ANY, description="第一个条件"),
            Parameter("condition2", ParameterType.ANY, description="第二个条件"),
        ]
    
    def calculate(self, condition1: Union[bool, pd.Series], condition2: Union[bool, pd.Series]) -> Union[bool, pd.Series]:
        """
        逻辑与运算
        
        Args:
            condition1: 第一个条件
            condition2: 第二个条件
            
        Returns:
            Union[bool, pd.Series]: 逻辑与结果
        """
        if isinstance(condition1, pd.Series) or isinstance(condition2, pd.Series):
            return pd.Series(condition1) & pd.Series(condition2)
        else:
            return condition1 and condition2


class ORFunction(TDXFunction):
    """
    逻辑或函数
    
    计算两个条件的逻辑或。
    """
    
    @property
    def name(self) -> str:
        return "OR"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "计算逻辑或"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition1", ParameterType.ANY, description="第一个条件"),
            Parameter("condition2", ParameterType.ANY, description="第二个条件"),
        ]
    
    def calculate(self, condition1: Union[bool, pd.Series], condition2: Union[bool, pd.Series]) -> Union[bool, pd.Series]:
        """
        逻辑或运算
        
        Args:
            condition1: 第一个条件
            condition2: 第二个条件
            
        Returns:
            Union[bool, pd.Series]: 逻辑或结果
        """
        if isinstance(condition1, pd.Series) or isinstance(condition2, pd.Series):
            return pd.Series(condition1) | pd.Series(condition2)
        else:
            return condition1 or condition2


class NOTFunction(TDXFunction):
    """
    逻辑非函数
    
    计算条件的逻辑非。
    """
    
    @property
    def name(self) -> str:
        return "NOT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "计算逻辑非"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.ANY, description="条件表达式"),
        ]
    
    def calculate(self, condition: Union[bool, pd.Series]) -> Union[bool, pd.Series]:
        """
        逻辑非运算
        
        Args:
            condition: 条件表达式
            
        Returns:
            Union[bool, pd.Series]: 逻辑非结果
        """
        if isinstance(condition, pd.Series):
            return ~condition
        else:
            return not condition


class BETWEENFunction(TDXFunction):
    """
    区间判断函数
    
    判断数值是否在指定区间内。
    """
    
    @property
    def name(self) -> str:
        return "BETWEEN"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "判断数值是否在指定区间内"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="待判断的数值或序列"),
            Parameter("min_value", ParameterType.NUMBER, description="区间最小值"),
            Parameter("max_value", ParameterType.NUMBER, description="区间最大值"),
        ]
    
    def calculate(self, data: Union[float, pd.Series], min_value: Union[float, pd.Series], 
                 max_value: Union[float, pd.Series]) -> Union[bool, pd.Series]:
        """
        区间判断
        
        Args:
            data: 待判断的数值或序列
            min_value: 区间最小值
            max_value: 区间最大值
            
        Returns:
            Union[bool, pd.Series]: 判断结果
        """
        if isinstance(data, pd.Series):
            return (data >= min_value) & (data <= max_value)
        else:
            return min_value <= data <= max_value


class EVERYFunction(TDXFunction):
    """
    全部满足函数
    
    判断指定周期内是否全部满足条件。
    """
    
    @property
    def name(self) -> str:
        return "EVERY"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "判断指定周期内是否全部满足条件"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="判断周期"),
        ]
    
    def calculate(self, condition: pd.Series, period: int) -> pd.Series:
        """
        全部满足判断
        
        Args:
            condition: 条件序列
            period: 判断周期
            
        Returns:
            pd.Series: 判断结果序列
        """
        # 将布尔值转换为数值进行滚动求和
        condition_numeric = condition.astype(int)
        rolling_sum = condition_numeric.rolling(window=period, min_periods=1).sum()
        rolling_count = condition_numeric.rolling(window=period, min_periods=1).count()
        
        # 全部满足条件时，求和等于计数
        return rolling_sum == rolling_count


class EXISTFunction(TDXFunction):
    """
    存在满足函数
    
    判断指定周期内是否存在满足条件的情况。
    """
    
    @property
    def name(self) -> str:
        return "EXIST"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "判断指定周期内是否存在满足条件的情况"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="判断周期"),
        ]
    
    def calculate(self, condition: pd.Series, period: int) -> pd.Series:
        """
        存在满足判断
        
        Args:
            condition: 条件序列
            period: 判断周期
            
        Returns:
            pd.Series: 判断结果序列
        """
        # 将布尔值转换为数值进行滚动求和
        condition_numeric = condition.astype(int)
        rolling_sum = condition_numeric.rolling(window=period, min_periods=1).sum()
        
        # 存在满足条件时，求和大于0
        return rolling_sum > 0


class IFFFunction(TDXFunction):
    """
    浮点条件函数
    
    根据条件返回浮点数值。
    """
    
    @property
    def name(self) -> str:
        return "IFF"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "根据条件返回浮点数值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.ANY, description="条件表达式"),
            Parameter("true_value", ParameterType.NUMBER, description="条件为真时的返回值"),
            Parameter("false_value", ParameterType.NUMBER, description="条件为假时的返回值"),
        ]
    
    def calculate(self, condition: Union[bool, pd.Series], true_value: Union[float, pd.Series], 
                 false_value: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        浮点条件判断
        
        Args:
            condition: 条件表达式
            true_value: 条件为真时的返回值
            false_value: 条件为假时的返回值
            
        Returns:
            Union[float, pd.Series]: 根据条件返回的浮点数值
        """
        if isinstance(condition, pd.Series):
            return np.where(condition, true_value, false_value)
        else:
            return float(true_value) if condition else float(false_value)


class IFNFunction(TDXFunction):
    """
    空值条件函数
    
    当条件为真时返回NaN，否则返回指定值。
    """
    
    @property
    def name(self) -> str:
        return "IFN"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "当条件为真时返回NaN，否则返回指定值"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.ANY, description="条件表达式"),
            Parameter("value", ParameterType.NUMBER, description="条件为假时的返回值"),
        ]
    
    def calculate(self, condition: Union[bool, pd.Series], value: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        空值条件判断
        
        Args:
            condition: 条件表达式
            value: 条件为假时的返回值
            
        Returns:
            Union[float, pd.Series]: 根据条件返回的值或NaN
        """
        if isinstance(condition, pd.Series):
            return np.where(condition, np.nan, value)
        else:
            return np.nan if condition else value


class RANGEFunction(TDXFunction):
    """
    范围限制函数
    
    将数值限制在指定范围内。
    """
    
    @property
    def name(self) -> str:
        return "RANGE"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.LOGICAL
    
    @property
    def description(self) -> str:
        return "将数值限制在指定范围内"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.NUMBER, description="待限制的数值或序列"),
            Parameter("min_value", ParameterType.NUMBER, description="最小值"),
            Parameter("max_value", ParameterType.NUMBER, description="最大值"),
        ]
    
    def calculate(self, data: Union[float, pd.Series], min_value: Union[float, pd.Series], 
                 max_value: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        范围限制
        
        Args:
            data: 待限制的数值或序列
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            Union[float, pd.Series]: 限制后的值
        """
        if isinstance(data, pd.Series):
            return data.clip(lower=min_value, upper=max_value)
        else:
            return max(min_value, min(data, max_value))