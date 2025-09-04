#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器主类

提供完整的公式解析、编译和执行功能。
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import os
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
    
    def load_from_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        从文件加载通达信公式
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            str: 文件中的公式内容
            
        Raises:
            TDXError: 文件读取错误
        """
        try:
            if not os.path.exists(file_path):
                raise TDXError(f"文件不存在: {file_path}")
            
            if not file_path.lower().endswith('.txt'):
                raise TDXError(f"不支持的文件格式，仅支持.txt文件: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read().strip()
            
            if not content:
                raise TDXError(f"文件内容为空: {file_path}")
            
            if self._debug_mode:
                print(f"从文件加载公式: {file_path}")
                print(f"公式内容: {content}")
            
            return content
            
        except UnicodeDecodeError as e:
            raise TDXError(f"文件编码错误，请检查文件编码格式: {str(e)}")
        except IOError as e:
            raise TDXError(f"文件读取错误: {str(e)}")
        except Exception as e:
            raise TDXError(f"加载文件时发生未知错误: {str(e)}")
    
    def evaluate_file(self, file_path: str, context: Optional[Union[pd.DataFrame, Dict]] = None, 
                     encoding: str = 'utf-8', **kwargs) -> Any:
        """
        从文件加载并计算通达信公式
        
        Args:
            file_path: 包含通达信公式的txt文件路径
            context: 数据上下文（K线数据等）
            encoding: 文件编码，默认为utf-8
            **kwargs: 其他参数
            
        Returns:
            计算结果
            
        Raises:
            TDXError: 文件加载或计算错误
        """
        try:
            # 从文件加载公式
            formula = self.load_from_file(file_path, encoding)
            
            # 计算公式
            return self.evaluate(formula, context, **kwargs)
            
        except Exception as e:
            if isinstance(e, TDXError):
                raise
            else:
                raise TDXRuntimeError(f"执行文件公式时发生错误: {str(e)}") from e
    
    def get_context(self) -> TDXContext:
        """
        获取当前上下文
        
        Returns:
            TDXContext: 当前上下文
        """
        return self.context