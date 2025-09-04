#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器主类

提供完整的公式解析、编译和执行功能。
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
from ..lexer import TDXLexer, Token
from ..errors.exceptions import TDXError, TDXSyntaxError, TDXRuntimeError
from .context import TDXContext


class TDXInterpreter:
    """
    通达信公式解释器主类
    
    提供完整的通达信公式解释功能：
    - 词法分析
    - 语法解析
    - 表达式求值
    - 错误处理
    """
    
    def __init__(self):
        """
        初始化解释器
        """
        self.lexer = TDXLexer()
        self.context = TDXContext()
        self._debug_mode = False
    
    def evaluate(self, formula: str, context: Optional[Union[pd.DataFrame, Dict]] = None, **kwargs) -> Any:
        """
        计算通达信公式
        
        Args:
            formula: 通达信公式字符串
            context: 数据上下文（K线数据等）
            **kwargs: 其他参数
            
        Returns:
            计算结果
            
        Raises:
            TDXError: 解析或计算错误
        """
        try:
            # 设置上下文
            if context is not None:
                self.context.set_data(context)
            
            # 词法分析
            tokens = self.lexer.tokenize(formula)
            
            if self._debug_mode:
                print(f"Tokens: {[str(t) for t in tokens]}")
            
            # 语法分析
            from ..parser import TDXParser
            parser = TDXParser()
            ast = parser.parse(tokens)
            
            if self._debug_mode:
                print(f"AST: {ast}")
            
            # 执行计算
            from .evaluator import ASTEvaluator
            evaluator = ASTEvaluator(self.context)
            result = evaluator.evaluate(ast)
            
            return result
            
        except Exception as e:
            if isinstance(e, TDXError):
                raise
            else:
                raise TDXRuntimeError(f"Unexpected error: {str(e)}") from e
    
    def parse(self, formula: str):
        """
        解析通达信公式，返回AST
        
        Args:
            formula: 通达信公式字符串
            
        Returns:
            抽象语法树
            
        Raises:
            TDXSyntaxError: 语法错误
        """
        try:
            tokens = self.lexer.tokenize(formula)
            from ..parser import TDXParser
            parser = TDXParser()
            ast = parser.parse(tokens)
            return ast
        except Exception as e:
            if isinstance(e, TDXError):
                raise
            else:
                raise TDXSyntaxError(f"Parse error: {str(e)}") from e
    
    def validate(self, formula: str) -> bool:
        """
        验证公式语法
        
        Args:
            formula: 通达信公式字符串
            
        Returns:
            bool: 语法是否正确
        """
        try:
            self.parse(formula)
            return True
        except TDXError:
            return False
    
    def set_debug_mode(self, enabled: bool):
        """
        设置调试模式
        
        Args:
            enabled: 是否启用调试模式
        """
        self._debug_mode = enabled
    
    def register_function(self, name: str, func: callable):
        """
        注册自定义函数
        
        Args:
            name: 函数名
            func: 函数实现
        """
        from ..functions.base import create_simple_function, FunctionCategory, Parameter, ParameterType
        from ..functions import registry
        
        # 创建简单的参数定义（这里简化处理，实际使用中可以更精确）
        parameters = [
            Parameter("data", ParameterType.SERIES, description="数据序列"),
            Parameter("period", ParameterType.INTEGER, description="周期参数")
        ]
        
        # 创建函数对象并注册到全局注册表
        tdx_function = create_simple_function(
            name=name.upper(),
            category=FunctionCategory.UTILITY,
            description=f"自定义函数: {name}",
            parameters=parameters,
            calculate_func=func
        )
        
        registry.register(tdx_function)
    
    def get_context(self) -> TDXContext:
        """
        获取当前上下文
        
        Returns:
            TDXContext: 当前上下文
        """
        return self.context