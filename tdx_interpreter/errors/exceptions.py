#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器异常类定义

提供详细的错误信息、位置定位和调试支持。
"""

from typing import Optional, Any, Dict, List


class TDXError(Exception):
    """
    通达信解释器基础异常类
    
    所有TDX相关异常的基类，提供统一的错误处理接口。
    """
    
    def __init__(self, message: str, position: Optional[int] = None, 
                 line: Optional[int] = None, column: Optional[int] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            position: 错误在源码中的位置
            line: 错误所在行号
            column: 错误所在列号
            context: 错误上下文信息
        """
        super().__init__(message)
        self.message = message
        self.position = position
        self.line = line
        self.column = column
        self.context = context or {}
        
    def __str__(self) -> str:
        """格式化错误信息"""
        parts = [self.message]
        
        if self.line is not None and self.column is not None:
            parts.append(f"at line {self.line}, column {self.column}")
        elif self.position is not None:
            parts.append(f"at position {self.position}")
            
        return " ".join(parts)
        
    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "position": self.position,
            "line": self.line,
            "column": self.column,
            "context": self.context,
        }


class TDXSyntaxError(TDXError):
    """
    语法错误异常
    
    当公式语法不符合通达信规范时抛出。
    """
    
    def __init__(self, message: str, formula: Optional[str] = None,
                 position: Optional[int] = None, line: Optional[int] = None,
                 column: Optional[int] = None, expected: Optional[List[str]] = None,
                 actual: Optional[str] = None):
        """
        初始化语法错误
        
        Args:
            message: 错误消息
            formula: 出错的公式字符串
            position: 错误位置
            line: 行号
            column: 列号
            expected: 期望的语法元素列表
            actual: 实际遇到的语法元素
        """
        context = {
            "formula": formula,
            "expected": expected,
            "actual": actual,
        }
        super().__init__(message, position, line, column, context)
        
    def get_suggestion(self) -> Optional[str]:
        """获取修复建议"""
        expected = self.context.get("expected")
        actual = self.context.get("actual")
        
        if expected and actual:
            if len(expected) == 1:
                return f"Expected '{expected[0]}', but got '{actual}'"
            else:
                return f"Expected one of {expected}, but got '{actual}'"
        return None


class TDXRuntimeError(TDXError):
    """
    运行时错误异常
    
    当公式执行过程中发生错误时抛出。
    """
    
    def __init__(self, message: str, function_name: Optional[str] = None,
                 arguments: Optional[List[Any]] = None, 
                 stack_trace: Optional[List[str]] = None, **kwargs):
        """
        初始化运行时错误
        
        Args:
            message: 错误消息
            function_name: 出错的函数名
            arguments: 函数参数
            stack_trace: 调用栈跟踪
        """
        context = {
            "function_name": function_name,
            "arguments": arguments,
            "stack_trace": stack_trace or [],
        }
        super().__init__(message, **kwargs)
        self.context.update(context)


class TDXTypeError(TDXRuntimeError):
    """
    类型错误异常
    
    当函数参数类型不匹配时抛出。
    """
    
    def __init__(self, message: str, expected_type: Optional[str] = None,
                 actual_type: Optional[str] = None, argument_name: Optional[str] = None,
                 **kwargs):
        """
        初始化类型错误
        
        Args:
            message: 错误消息
            expected_type: 期望的类型
            actual_type: 实际的类型
            argument_name: 参数名
        """
        context = {
            "expected_type": expected_type,
            "actual_type": actual_type,
            "argument_name": argument_name,
        }
        super().__init__(message, **kwargs)
        self.context.update(context)


class TDXNameError(TDXRuntimeError):
    """
    名称错误异常
    
    当引用未定义的变量或函数时抛出。
    """
    
    def __init__(self, message: str, name: Optional[str] = None,
                 available_names: Optional[List[str]] = None, **kwargs):
        """
        初始化名称错误
        
        Args:
            message: 错误消息
            name: 未找到的名称
            available_names: 可用的名称列表
        """
        context = {
            "name": name,
            "available_names": available_names,
        }
        super().__init__(message, **kwargs)
        self.context.update(context)
        
    def get_suggestion(self) -> Optional[str]:
        """获取名称建议"""
        name = self.context.get("name")
        available = self.context.get("available_names", [])
        
        if name and available:
            # 简单的字符串相似度匹配
            suggestions = [n for n in available if name.lower() in n.lower() or n.lower() in name.lower()]
            if suggestions:
                return f"Did you mean: {', '.join(suggestions[:3])}?"
        return None


class TDXValueError(TDXRuntimeError):
    """
    值错误异常
    
    当函数参数值不在有效范围内时抛出。
    """
    
    def __init__(self, message: str, value: Optional[Any] = None,
                 valid_range: Optional[str] = None, **kwargs):
        """
        初始化值错误
        
        Args:
            message: 错误消息
            value: 无效的值
            valid_range: 有效值范围描述
        """
        context = {
            "value": value,
            "valid_range": valid_range,
        }
        super().__init__(message, **kwargs)
        self.context.update(context)


class TDXArgumentError(TDXRuntimeError):
    """
    参数错误异常
    
    当函数参数数量不正确时抛出。
    """
    
    def __init__(self, message: str, expected_count: Optional[int] = None,
                 actual_count: Optional[int] = None, function_name: Optional[str] = None,
                 **kwargs):
        """
        初始化参数错误
        
        Args:
            message: 错误消息
            expected_count: 期望的参数数量
            actual_count: 实际的参数数量
            function_name: 函数名
        """
        context = {
            "expected_count": expected_count,
            "actual_count": actual_count,
        }
        super().__init__(message, function_name=function_name, **kwargs)
        self.context.update(context)