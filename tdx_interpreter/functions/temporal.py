#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信时序数据函数实现

实现时序数据处理函数，包括：
- 引用函数（REF, REFX）
- 计数函数（BARSLAST, BARSLASTCOUNT, BARSCOUNT）
- 交叉函数（CROSS, LONGCROSS）
- 过滤函数（FILTER, BACKSET）
- 时序统计（SINCE, LAST）
"""

import pandas as pd
import numpy as np
from typing import Union
from .base import TDXFunction, FunctionCategory, Parameter, ParameterType


class REFFunction(TDXFunction):
    """
    引用函数
    
    引用若干周期前的数据。
    """
    
    @property
    def name(self) -> str:
        return "REF"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "引用若干周期前的数据"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("periods", ParameterType.INTEGER, min_value=0, description="引用周期数"),
        ]
    
    def calculate(self, data: pd.Series, periods: int) -> pd.Series:
        """
        引用历史数据
        
        Args:
            data: 数据序列
            periods: 引用周期数
            
        Returns:
            pd.Series: 引用后的数据序列
        """
        return data.shift(periods)


class BARSLASTFunction(TDXFunction):
    """
    上次条件成立函数
    
    计算上次条件成立到现在的周期数。
    """
    
    @property
    def name(self) -> str:
        return "BARSLAST"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "计算上次条件成立到现在的周期数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
        ]
    
    def calculate(self, condition: pd.Series) -> pd.Series:
        """
        计算上次条件成立的周期数
        
        Args:
            condition: 条件序列（布尔值）
            
        Returns:
            pd.Series: 周期数序列
        """
        result = pd.Series(index=condition.index, dtype=float)
        last_true_index = -1
        
        for i, (idx, value) in enumerate(condition.items()):
            if value:
                last_true_index = i
                result.iloc[i] = 0
            else:
                if last_true_index >= 0:
                    result.iloc[i] = i - last_true_index
                else:
                    result.iloc[i] = np.nan
        
        return result


class BARSLASTCOUNTFunction(TDXFunction):
    """
    连续条件成立函数
    
    计算连续满足条件的周期数。
    """
    
    @property
    def name(self) -> str:
        return "BARSLASTCOUNT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "计算连续满足条件的周期数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
        ]
    
    def calculate(self, condition: pd.Series) -> pd.Series:
        """
        计算连续满足条件的周期数
        
        Args:
            condition: 条件序列（布尔值）
            
        Returns:
            pd.Series: 连续周期数序列
        """
        result = pd.Series(index=condition.index, dtype=int)
        count = 0
        
        for i, (idx, value) in enumerate(condition.items()):
            if value:
                count += 1
            else:
                count = 0
            result.iloc[i] = count
        
        return result


class BARSCOUNTFunction(TDXFunction):
    """
    数据周期数函数
    
    计算有效数据的周期数。
    """
    
    @property
    def name(self) -> str:
        return "BARSCOUNT"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "计算有效数据的周期数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
        ]
    
    def calculate(self, data: pd.Series) -> pd.Series:
        """
        计算有效数据的周期数
        
        Args:
            data: 数据序列
            
        Returns:
            pd.Series: 周期数序列
        """
        # 计算非空值的累计计数
        valid_mask = data.notna()
        return valid_mask.cumsum()


class CROSSFunction(TDXFunction):
    """
    交叉函数
    
    判断两个序列是否发生交叉。
    """
    
    @property
    def name(self) -> str:
        return "CROSS"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "判断两个序列是否发生交叉"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.SERIES, description="第一个数据序列"),
            Parameter("data2", ParameterType.SERIES, description="第二个数据序列"),
        ]
    
    def calculate(self, data1: pd.Series, data2: pd.Series) -> pd.Series:
        """
        判断交叉
        
        Args:
            data1: 第一个数据序列
            data2: 第二个数据序列
            
        Returns:
            pd.Series: 交叉判断结果（布尔值）
        """
        # 当前周期data1 > data2，前一周期data1 <= data2
        current_above = data1 > data2
        prev_below_or_equal = (data1.shift(1) <= data2.shift(1))
        
        return current_above & prev_below_or_equal


class LONGCROSSFunction(TDXFunction):
    """
    长期交叉函数
    
    判断两个序列在指定周期内是否发生交叉。
    """
    
    @property
    def name(self) -> str:
        return "LONGCROSS"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "判断两个序列在指定周期内是否发生交叉"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("data1", ParameterType.SERIES, description="第一个数据序列"),
            Parameter("data2", ParameterType.SERIES, description="第二个数据序列"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="判断周期"),
        ]
    
    def calculate(self, data1: pd.Series, data2: pd.Series, period: int) -> pd.Series:
        """
        判断长期交叉
        
        Args:
            data1: 第一个数据序列
            data2: 第二个数据序列
            period: 判断周期
            
        Returns:
            pd.Series: 长期交叉判断结果（布尔值）
        """
        # 计算普通交叉
        cross = self._calculate_cross(data1, data2)
        
        # 在指定周期内是否发生过交叉
        return cross.rolling(window=period, min_periods=1).sum() > 0
    
    def _calculate_cross(self, data1: pd.Series, data2: pd.Series) -> pd.Series:
        """计算普通交叉"""
        current_above = data1 > data2
        prev_below_or_equal = (data1.shift(1) <= data2.shift(1))
        return current_above & prev_below_or_equal


class FILTERFunction(TDXFunction):
    """
    过滤函数
    
    对信号进行过滤，避免频繁信号。
    """
    
    @property
    def name(self) -> str:
        return "FILTER"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "对信号进行过滤，避免频繁信号"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="过滤周期"),
        ]
    
    def calculate(self, condition: pd.Series, period: int) -> pd.Series:
        """
        信号过滤
        
        Args:
            condition: 条件序列（布尔值）
            period: 过滤周期
            
        Returns:
            pd.Series: 过滤后的信号序列
        """
        result = pd.Series(index=condition.index, dtype=bool)
        last_signal_index = -period - 1
        
        for i, (idx, value) in enumerate(condition.items()):
            if value and (i - last_signal_index) >= period:
                result.iloc[i] = True
                last_signal_index = i
            else:
                result.iloc[i] = False
        
        return result


class BACKSETFunction(TDXFunction):
    """
    向前赋值函数
    
    将当前值向前赋值若干周期。
    """
    
    @property
    def name(self) -> str:
        return "BACKSET"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "将当前值向前赋值若干周期"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
            Parameter("period", ParameterType.INTEGER, min_value=1, description="向前赋值周期数"),
        ]
    
    def calculate(self, condition: pd.Series, period: int) -> pd.Series:
        """
        向前赋值
        
        Args:
            condition: 条件序列（布尔值）
            period: 向前赋值周期数
            
        Returns:
            pd.Series: 向前赋值后的序列
        """
        result = pd.Series(index=condition.index, dtype=bool, data=False)
        
        for i, (idx, value) in enumerate(condition.items()):
            if value:
                # 向前赋值
                start_idx = max(0, i - period + 1)
                for j in range(start_idx, i + 1):
                    result.iloc[j] = True
        
        return result


class SINCEFunction(TDXFunction):
    """
    自从函数
    
    计算自从条件成立以来的周期数。
    """
    
    @property
    def name(self) -> str:
        return "SINCE"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "计算自从条件成立以来的周期数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
        ]
    
    def calculate(self, condition: pd.Series) -> pd.Series:
        """
        计算自从条件成立的周期数
        
        Args:
            condition: 条件序列（布尔值）
            
        Returns:
            pd.Series: 周期数序列
        """
        result = pd.Series(index=condition.index, dtype=int)
        count_since_true = 0
        found_true = False
        
        for i, (idx, value) in enumerate(condition.items()):
            if value:
                count_since_true = 0
                found_true = True
            elif found_true:
                count_since_true += 1
            
            result.iloc[i] = count_since_true if found_true else 0
        
        return result


class LASTFunction(TDXFunction):
    """
    持续函数
    
    计算条件连续成立的周期数。
    """
    
    @property
    def name(self) -> str:
        return "LAST"
    
    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.TEMPORAL
    
    @property
    def description(self) -> str:
        return "计算条件连续成立的周期数"
    
    @property
    def parameters(self) -> list[Parameter]:
        return [
            Parameter("condition", ParameterType.SERIES, description="条件序列（布尔值）"),
            Parameter("period1", ParameterType.INTEGER, min_value=1, description="第一个周期参数"),
            Parameter("period2", ParameterType.INTEGER, min_value=1, description="第二个周期参数"),
        ]
    
    def calculate(self, condition: pd.Series, period1: int, period2: int) -> pd.Series:
        """
        计算条件持续成立
        
        Args:
            condition: 条件序列（布尔值）
            period1: 第一个周期参数
            period2: 第二个周期参数
            
        Returns:
            pd.Series: 持续判断结果
        """
        # 计算连续满足条件的周期数
        consecutive_count = self._calculate_consecutive_count(condition)
        
        # 判断是否在指定范围内持续满足条件
        return (consecutive_count >= period1) & (consecutive_count <= period2)
    
    def _calculate_consecutive_count(self, condition: pd.Series) -> pd.Series:
        """计算连续满足条件的周期数"""
        result = pd.Series(index=condition.index, dtype=int)
        count = 0
        
        for i, (idx, value) in enumerate(condition.items()):
            if value:
                count += 1
            else:
                count = 0
            result.iloc[i] = count
        
        return result