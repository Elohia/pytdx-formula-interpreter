#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器上下文管理

管理变量作用域、数据上下文和函数注册。
"""

from typing import Any, Dict, List, Optional, Union, Callable
import pandas as pd
from ..errors.exceptions import TDXNameError, TDXTypeError


class TDXContext:
    """
    通达信解释器上下文管理器
    
    负责管理：
    - 变量作用域
    - K线数据上下文
    - 自定义函数注册
    - 内置函数库
    """
    
    def __init__(self):
        """
        初始化上下文
        """
        # 变量作用域栈
        self._scopes: List[Dict[str, Any]] = [{}]  # 全局作用域
        
        # K线数据
        self._data: Optional[pd.DataFrame] = None
        
        # 注册的函数
        self._functions: Dict[str, Callable] = {}
        
        # 内置变量（OPEN, HIGH, LOW, CLOSE, VOLUME等）
        self._builtin_vars = {
            'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'AMOUNT'
        }
        
        # 初始化内置函数
        self._init_builtin_functions()
    
    def _init_builtin_functions(self):
        """
        初始化内置函数
        
        TODO: 这里将在函数库模块完成后进行完整实现
        """
        # 占位符实现
        self._functions.update({
            'MA': lambda data, period: data.rolling(period).mean(),
            'SUM': lambda data, period: data.rolling(period).sum(),
            'MAX': lambda data, period: data.rolling(period).max(),
            'MIN': lambda data, period: data.rolling(period).min(),
        })
    
    def set_data(self, data: Union[pd.DataFrame, Dict]):
        """
        设置K线数据上下文
        
        Args:
            data: K线数据，DataFrame或字典格式
            
        Raises:
            TDXTypeError: 数据类型错误
        """
        if isinstance(data, pd.DataFrame):
            self._data = data
        elif isinstance(data, dict):
            self._data = pd.DataFrame(data)
        else:
            raise TDXTypeError(
                f"Data must be DataFrame or dict, got {type(data).__name__}",
                expected_type="DataFrame or dict",
                actual_type=type(data).__name__
            )
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        获取K线数据
        
        Returns:
            Optional[pd.DataFrame]: K线数据
        """
        return self._data
    
    def push_scope(self):
        """
        推入新的作用域
        """
        self._scopes.append({})
    
    def pop_scope(self):
        """
        弹出当前作用域
        
        Raises:
            TDXRuntimeError: 尝试弹出全局作用域
        """
        if len(self._scopes) <= 1:
            from ..errors.exceptions import TDXRuntimeError
            raise TDXRuntimeError("Cannot pop global scope")
        self._scopes.pop()
    
    def set_variable(self, name: str, value: Any):
        """
        设置变量值
        
        Args:
            name: 变量名
            value: 变量值
        """
        # 在当前作用域设置变量
        self._scopes[-1][name] = value
    
    def get_variable(self, name: str) -> Any:
        """
        获取变量值
        
        Args:
            name: 变量名
            
        Returns:
            变量值
            
        Raises:
            TDXNameError: 变量未定义
        """
        # 检查是否为内置变量
        if name in self._builtin_vars and self._data is not None:
            if name in self._data.columns:
                return self._data[name]
        
        # 从作用域栈中查找变量（从内到外）
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        
        # 变量未找到
        available_names = self._get_available_names()
        raise TDXNameError(
            f"Variable '{name}' is not defined",
            name=name,
            available_names=available_names
        )
    
    def has_variable(self, name: str) -> bool:
        """
        检查变量是否存在
        
        Args:
            name: 变量名
            
        Returns:
            bool: 变量是否存在
        """
        try:
            self.get_variable(name)
            return True
        except TDXNameError:
            return False
    
    def register_function(self, name: str, func: Callable):
        """
        注册自定义函数
        
        Args:
            name: 函数名
            func: 函数实现
        """
        self._functions[name.upper()] = func
    
    def get_function(self, name: str) -> Callable:
        """
        获取函数
        
        Args:
            name: 函数名
            
        Returns:
            Callable: 函数实现
            
        Raises:
            TDXNameError: 函数未定义
        """
        name = name.upper()
        if name in self._functions:
            return self._functions[name]
        
        available_names = list(self._functions.keys())
        raise TDXNameError(
            f"Function '{name}' is not defined",
            name=name,
            available_names=available_names
        )
    
    def has_function(self, name: str) -> bool:
        """
        检查函数是否存在
        
        Args:
            name: 函数名
            
        Returns:
            bool: 函数是否存在
        """
        return name.upper() in self._functions
    
    def _get_available_names(self) -> List[str]:
        """
        获取所有可用的名称（变量和函数）
        
        Returns:
            List[str]: 可用名称列表
        """
        names = set()
        
        # 添加变量名
        for scope in self._scopes:
            names.update(scope.keys())
        
        # 添加内置变量名
        names.update(self._builtin_vars)
        
        # 添加数据列名
        if self._data is not None:
            names.update(self._data.columns)
        
        # 添加函数名
        names.update(self._functions.keys())
        
        return sorted(list(names))
    
    def clear(self):
        """
        清空上下文
        """
        self._scopes = [{}]
        self._data = None
        # 保留内置函数，清空自定义函数
        custom_functions = {k: v for k, v in self._functions.items() 
                          if k not in {'MA', 'SUM', 'MAX', 'MIN'}}
        self._init_builtin_functions()
        self._functions.update(custom_functions)
    
    def get_scope_info(self) -> Dict[str, Any]:
        """
        获取作用域信息（调试用）
        
        Returns:
            Dict[str, Any]: 作用域信息
        """
        return {
            'scope_count': len(self._scopes),
            'current_scope': self._scopes[-1].copy(),
            'all_variables': self._get_available_names(),
            'functions': list(self._functions.keys()),
            'has_data': self._data is not None,
            'data_columns': list(self._data.columns) if self._data is not None else [],
        }