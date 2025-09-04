"""
通达信公式解释器

一个用于解析和执行通达信公式的Python库。
支持通达信公式语法，包括技术指标、数学运算、逻辑判断等功能。

Author: pytdx-interpreter contributors
License: CC BY-NC 4.0 License
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "pytdx-interpreter contributors"
__license__ = "CC BY-NC 4.0"
__email__ = "your.email@example.com"

# 核心类导入
from .core.interpreter import TdxInterpreter
from .core.evaluator import TdxEvaluator
from .core.context import ExecutionContext

# 异常类导入
from .errors.exceptions import (
    TdxError,
    TdxSyntaxError,
    TdxRuntimeError,
    TdxTypeError,
    TdxNameError,
    TdxValueError,
    TdxFunctionError,
)

# 便捷函数
def evaluate(formula: str, context: dict = None) -> any:
    """
    便捷函数：评估通达信公式
    
    Args:
        formula: 通达信公式字符串
        context: 执行上下文字典
        
    Returns:
        公式计算结果
    """
    interpreter = TdxInterpreter()
    return interpreter.evaluate(formula, context or {})

def parse(formula: str):
    """
    便捷函数：解析通达信公式为AST
    
    Args:
        formula: 通达信公式字符串
        
    Returns:
        AST节点
    """
    interpreter = TdxInterpreter()
    return interpreter.parse(formula)

def validate(formula: str) -> bool:
    """
    便捷函数：验证通达信公式语法
    
    Args:
        formula: 通达信公式字符串
        
    Returns:
        是否语法正确
    """
    try:
        parse(formula)
        return True
    except TdxError:
        return False

__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__license__",
    "__email__",
    
    # 核心类
    "TdxInterpreter",
    "TdxEvaluator", 
    "ExecutionContext",
    
    # 异常类
    "TdxError",
    "TdxSyntaxError",
    "TdxRuntimeError",
    "TdxTypeError",
    "TdxNameError",
    "TdxValueError",
    "TdxFunctionError",
    
    # 便捷函数
    "evaluate",
    "parse",
    "validate",
]