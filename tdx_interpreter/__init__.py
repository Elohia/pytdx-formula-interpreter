#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器 (TDX Formula Interpreter)

一个完整的通达信公式解释器，支持：
- 完整的语法解析
- 所有内置函数和运算符
- 公式编译和执行环境
- 变量作用域管理
- 错误检测和提示功能
- 与通达信软件的兼容性

基本使用方法:
    >>> from tdx_interpreter import TDXInterpreter
    >>> interpreter = TDXInterpreter()
    >>> result = interpreter.evaluate("MA(CLOSE, 5)")
    >>> print(result)

作者: TDX Formula Team
版本: 0.1.0
许可: CC BY-NC 4.0 License
"""

__version__ = "0.1.0"
__author__ = "TDX Formula Team"
__email__ = "dev@tdxformula.com"
__license__ = "CC BY-NC 4.0"

# 导入核心类和函数
from .core.interpreter import TDXInterpreter
from .core.context import TDXContext
from .errors.exceptions import (
    TDXError,
    TDXSyntaxError,
    TDXRuntimeError,
    TDXTypeError,
    TDXNameError,
)

# 公共API
__all__ = [
    # 核心类
    "TDXInterpreter",
    "TDXContext",
    
    # 异常类
    "TDXError",
    "TDXSyntaxError", 
    "TDXRuntimeError",
    "TDXTypeError",
    "TDXNameError",
    
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# 便捷函数
def evaluate(formula: str, context=None, **kwargs):
    """
    快速计算通达信公式
    
    Args:
        formula: 通达信公式字符串
        context: 数据上下文，包含K线数据等
        **kwargs: 其他参数
        
    Returns:
        计算结果
        
    Example:
        >>> result = evaluate("MA(CLOSE, 5)", context=my_data)
    """
    interpreter = TDXInterpreter()
    return interpreter.evaluate(formula, context, **kwargs)

def parse(formula: str):
    """
    解析通达信公式，返回AST
    
    Args:
        formula: 通达信公式字符串
        
    Returns:
        抽象语法树(AST)
        
    Example:
        >>> ast = parse("MA(CLOSE, 5)")
        >>> print(ast)
    """
    interpreter = TDXInterpreter()
    return interpreter.parse(formula)

def validate(formula: str):
    """
    验证通达信公式语法
    
    Args:
        formula: 通达信公式字符串
        
    Returns:
        bool: 语法是否正确
        
    Example:
        >>> is_valid = validate("MA(CLOSE, 5)")
        >>> print(is_valid)  # True
    """
    try:
        parse(formula)
        return True
    except TDXSyntaxError:
        return False