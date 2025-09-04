#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信函数基类和接口定义

定义了函数的基本结构、参数验证、类型检查等通用功能。
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, List, Optional, Union, Dict, Callable
from dataclasses import dataclass
import pandas as pd
import numpy as np
from ..errors.exceptions import TDXArgumentError, TDXTypeError, TDXValueError


class FunctionCategory(Enum):
    """
    函数分类枚举
    """
    TECHNICAL = auto()      # 技术指标函数
    MATHEMATICAL = auto()   # 数学运算函数
    LOGICAL = auto()        # 逻辑判断函数
    TEMPORAL = auto()       # 时序数据函数
    STATISTICAL = auto()    # 统计分析函数
    UTILITY = auto()        # 工具函数


class ParameterType(Enum):
    """
    参数类型枚举
    """
    NUMBER = auto()         # 数值类型
    SERIES = auto()         # 序列类型（pandas Series或numpy array）
    INTEGER = auto()        # 整数类型
    BOOLEAN = auto()        # 布尔类型
    STRING = auto()         # 字符串类型
    ANY = auto()            # 任意类型


@dataclass
class Parameter:
    """
    函数参数定义
    """
    name: str                           # 参数名
    param_type: ParameterType          # 参数类型
    required: bool = True              # 是否必需
    default_value: Any = None          # 默认值
    min_value: Optional[float] = None  # 最小值（数值类型）
    max_value: Optional[float] = None  # 最大值（数值类型）
    description: str = ""              # 参数描述
    
    def validate(self, value: Any) -> Any:
        """
        验证参数值
        
        Args:
            value: 参数值
            
        Returns:
            Any: 验证后的参数值
            
        Raises:
            TDXTypeError: 类型错误
            TDXValueError: 值错误
        """
        if value is None:
            if self.required:
                raise TDXArgumentError(f"Parameter '{self.name}' is required")
            return self.default_value
        
        # 类型检查
        validated_value = self._validate_type(value)
        
        # 值范围检查
        if self.param_type in {ParameterType.NUMBER, ParameterType.INTEGER}:
            validated_value = self._validate_range(validated_value)
        
        return validated_value
    
    def _validate_type(self, value: Any) -> Any:
        """
        验证参数类型
        
        Args:
            value: 参数值
            
        Returns:
            Any: 转换后的参数值
        """
        if self.param_type == ParameterType.NUMBER:
            if isinstance(value, (int, float, np.number)):
                return float(value)
            elif isinstance(value, (pd.Series, np.ndarray)):
                return value
            else:
                raise TDXTypeError(
                    f"Parameter '{self.name}' must be a number or series",
                    expected_type="number or series",
                    actual_type=type(value).__name__
                )
        
        elif self.param_type == ParameterType.SERIES:
            if isinstance(value, (pd.Series, np.ndarray, list)):
                return pd.Series(value) if not isinstance(value, pd.Series) else value
            else:
                raise TDXTypeError(
                    f"Parameter '{self.name}' must be a series",
                    expected_type="series",
                    actual_type=type(value).__name__
                )
        
        elif self.param_type == ParameterType.INTEGER:
            if isinstance(value, (int, np.integer)):
                return int(value)
            elif isinstance(value, (float, np.floating)) and value.is_integer():
                return int(value)
            else:
                raise TDXTypeError(
                    f"Parameter '{self.name}' must be an integer",
                    expected_type="integer",
                    actual_type=type(value).__name__
                )
        
        elif self.param_type == ParameterType.BOOLEAN:
            if isinstance(value, (bool, np.bool_)):
                return bool(value)
            else:
                raise TDXTypeError(
                    f"Parameter '{self.name}' must be a boolean",
                    expected_type="boolean",
                    actual_type=type(value).__name__
                )
        
        elif self.param_type == ParameterType.STRING:
            if isinstance(value, str):
                return value
            else:
                raise TDXTypeError(
                    f"Parameter '{self.name}' must be a string",
                    expected_type="string",
                    actual_type=type(value).__name__
                )
        
        else:  # ParameterType.ANY
            return value
    
    def _validate_range(self, value: Union[int, float]) -> Union[int, float]:
        """
        验证数值范围
        
        Args:
            value: 数值
            
        Returns:
            Union[int, float]: 验证后的数值
        """
        if self.min_value is not None and value < self.min_value:
            raise TDXValueError(
                f"Parameter '{self.name}' must be >= {self.min_value}",
                value=value,
                valid_range=f">= {self.min_value}"
            )
        
        if self.max_value is not None and value > self.max_value:
            raise TDXValueError(
                f"Parameter '{self.name}' must be <= {self.max_value}",
                value=value,
                valid_range=f"<= {self.max_value}"
            )
        
        return value


class TDXFunction(ABC):
    """
    通达信函数基类
    
    所有通达信函数的基类，定义了函数的基本接口和通用功能。
    """
    
    def __init__(self):
        """
        初始化函数
        """
        self._validate_definition()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        函数名称
        
        Returns:
            str: 函数名称
        """
        pass
    
    @property
    @abstractmethod
    def category(self) -> FunctionCategory:
        """
        函数分类
        
        Returns:
            FunctionCategory: 函数分类
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        函数描述
        
        Returns:
            str: 函数描述
        """
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[Parameter]:
        """
        函数参数定义
        
        Returns:
            List[Parameter]: 参数列表
        """
        pass
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> Any:
        """
        计算函数结果
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 计算结果
        """
        pass
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        调用函数
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 计算结果
        """
        # 验证参数
        validated_args = self._validate_arguments(*args, **kwargs)
        
        # 执行计算
        try:
            return self.calculate(*validated_args)
        except Exception as e:
            if isinstance(e, (TDXArgumentError, TDXTypeError, TDXValueError)):
                raise
            else:
                raise TDXArgumentError(
                    f"Error in function '{self.name}': {str(e)}",
                    function_name=self.name,
                    arguments=list(args)
                ) from e
    
    def _validate_arguments(self, *args, **kwargs) -> List[Any]:
        """
        验证函数参数
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            List[Any]: 验证后的参数列表
        """
        parameters = self.parameters
        validated_args = []
        
        # 检查参数数量
        required_count = sum(1 for p in parameters if p.required)
        total_count = len(parameters)
        
        if len(args) < required_count:
            raise TDXArgumentError(
                f"Function '{self.name}' requires at least {required_count} arguments, got {len(args)}",
                function_name=self.name,
                expected_count=required_count,
                actual_count=len(args)
            )
        
        if len(args) > total_count:
            raise TDXArgumentError(
                f"Function '{self.name}' accepts at most {total_count} arguments, got {len(args)}",
                function_name=self.name,
                expected_count=total_count,
                actual_count=len(args)
            )
        
        # 验证每个参数
        for i, param in enumerate(parameters):
            if i < len(args):
                # 位置参数
                validated_args.append(param.validate(args[i]))
            elif param.name in kwargs:
                # 关键字参数
                validated_args.append(param.validate(kwargs[param.name]))
            else:
                # 使用默认值
                validated_args.append(param.validate(None))
        
        return validated_args
    
    def _validate_definition(self):
        """
        验证函数定义的正确性
        
        Raises:
            ValueError: 函数定义错误
        """
        if not self.name:
            raise ValueError("Function name cannot be empty")
        
        if not self.name.isupper():
            raise ValueError("Function name must be uppercase")
        
        if not self.parameters:
            return  # 无参数函数是允许的
        
        # 检查参数定义
        param_names = set()
        required_after_optional = False
        
        for param in self.parameters:
            if param.name in param_names:
                raise ValueError(f"Duplicate parameter name: {param.name}")
            param_names.add(param.name)
            
            if not param.required and not required_after_optional:
                required_after_optional = True
            elif param.required and required_after_optional:
                raise ValueError("Required parameters cannot come after optional parameters")
    
    def get_signature(self) -> str:
        """
        获取函数签名
        
        Returns:
            str: 函数签名字符串
        """
        if not self.parameters:
            return f"{self.name}()"
        
        param_strs = []
        for param in self.parameters:
            param_str = param.name
            if not param.required:
                param_str = f"[{param_str}]"
            param_strs.append(param_str)
        
        return f"{self.name}({', '.join(param_strs)})"
    
    def get_help(self) -> str:
        """
        获取函数帮助信息
        
        Returns:
            str: 帮助信息
        """
        lines = [
            f"Function: {self.name}",
            f"Category: {self.category.name}",
            f"Signature: {self.get_signature()}",
            f"Description: {self.description}",
        ]
        
        if self.parameters:
            lines.append("Parameters:")
            for param in self.parameters:
                required_str = "required" if param.required else "optional"
                default_str = f" (default: {param.default_value})" if not param.required else ""
                lines.append(f"  - {param.name} ({param.param_type.name.lower()}, {required_str}){default_str}: {param.description}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return f"{self.name}({len(self.parameters)} params)"
    
    def __repr__(self) -> str:
        return f"TDXFunction(name='{self.name}', category={self.category.name})"


def create_simple_function(name: str, category: FunctionCategory, description: str,
                         parameters: List[Parameter], calculate_func: Callable) -> TDXFunction:
    """
    创建简单函数的工厂方法
    
    Args:
        name: 函数名
        category: 函数分类
        description: 函数描述
        parameters: 参数列表
        calculate_func: 计算函数
        
    Returns:
        TDXFunction: 函数实例
    """
    
    class SimpleTDXFunction(TDXFunction):
        @property
        def name(self) -> str:
            return name
        
        @property
        def category(self) -> FunctionCategory:
            return category
        
        @property
        def description(self) -> str:
            return description
        
        @property
        def parameters(self) -> List[Parameter]:
            return parameters
        
        def calculate(self, *args, **kwargs) -> Any:
            return calculate_func(*args, **kwargs)
    
    return SimpleTDXFunction()