#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器词法单元定义

定义了所有可能的Token类型和Token类。
"""

from enum import Enum, auto
from typing import Any, Optional
from dataclasses import dataclass


class TokenType(Enum):
    """
    词法单元类型枚举
    
    定义了通达信公式中所有可能的词法单元类型。
    """
    
    # 字面量
    NUMBER = auto()          # 数值常量: 123, 3.14, 0.5
    STRING = auto()          # 字符串常量: "hello"
    
    # 标识符
    IDENTIFIER = auto()      # 标识符: CLOSE, MA, MyVar
    
    # 算术运算符
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # ^
    
    # 比较运算符
    EQUAL = auto()          # =
    NOT_EQUAL = auto()      # <> 或 !=
    GREATER = auto()        # >
    LESS = auto()           # <
    GREATER_EQUAL = auto()  # >=
    LESS_EQUAL = auto()     # <=
    
    # 逻辑运算符
    AND = auto()            # AND
    OR = auto()             # OR
    NOT = auto()            # NOT
    
    # 赋值运算符
    ASSIGN = auto()         # :=
    
    # 分隔符
    LEFT_PAREN = auto()     # (
    RIGHT_PAREN = auto()    # )
    LEFT_BRACKET = auto()   # [
    RIGHT_BRACKET = auto()  # ]
    COMMA = auto()          # ,
    SEMICOLON = auto()      # ;
    
    # 关键字
    IF = auto()             # IF
    THEN = auto()           # THEN (可选)
    ELSE = auto()           # ELSE (可选)
    
    # 特殊符号
    NEWLINE = auto()        # 换行符
    EOF = auto()            # 文件结束
    
    # 错误类型
    UNKNOWN = auto()        # 未知字符


@dataclass
class Token:
    """
    词法单元类
    
    表示词法分析过程中识别出的一个词法单元。
    """
    
    type: TokenType         # Token类型
    value: Any              # Token值
    position: int           # 在源码中的位置
    line: int = 1           # 行号
    column: int = 1         # 列号
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Token({self.type.name}, {repr(self.value)}, {self.position})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"Token(type={self.type.name}, value={repr(self.value)}, "
                f"position={self.position}, line={self.line}, column={self.column})")
    
    def is_type(self, *token_types: TokenType) -> bool:
        """
        检查Token是否为指定类型之一
        
        Args:
            *token_types: 要检查的Token类型
            
        Returns:
            bool: 是否匹配任一类型
        """
        return self.type in token_types
    
    def is_operator(self) -> bool:
        """
        检查是否为运算符Token
        
        Returns:
            bool: 是否为运算符
        """
        operator_types = {
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.POWER, TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL,
            TokenType.AND, TokenType.OR, TokenType.NOT
        }
        return self.type in operator_types
    
    def is_literal(self) -> bool:
        """
        检查是否为字面量Token
        
        Returns:
            bool: 是否为字面量
        """
        return self.type in {TokenType.NUMBER, TokenType.STRING}
    
    def is_delimiter(self) -> bool:
        """
        检查是否为分隔符Token
        
        Returns:
            bool: 是否为分隔符
        """
        delimiter_types = {
            TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
            TokenType.COMMA, TokenType.SEMICOLON
        }
        return self.type in delimiter_types
    
    def get_precedence(self) -> int:
        """
        获取运算符优先级
        
        Returns:
            int: 优先级数值，数值越大优先级越高
        """
        precedence_map = {
            # 逻辑运算符 (最低优先级)
            TokenType.OR: 1,
            TokenType.AND: 2,
            TokenType.NOT: 3,
            
            # 比较运算符
            TokenType.EQUAL: 4,
            TokenType.NOT_EQUAL: 4,
            TokenType.GREATER: 4,
            TokenType.LESS: 4,
            TokenType.GREATER_EQUAL: 4,
            TokenType.LESS_EQUAL: 4,
            
            # 算术运算符
            TokenType.PLUS: 5,
            TokenType.MINUS: 5,
            TokenType.MULTIPLY: 6,
            TokenType.DIVIDE: 6,
            TokenType.MODULO: 6,
            
            # 幂运算 (最高优先级)
            TokenType.POWER: 7,
        }
        return precedence_map.get(self.type, 0)
    
    def is_right_associative(self) -> bool:
        """
        检查运算符是否为右结合
        
        Returns:
            bool: 是否为右结合运算符
        """
        # 幂运算和NOT运算符是右结合的
        return self.type in {TokenType.POWER, TokenType.NOT}


# 关键字映射
KEYWORDS = {
    'IF': TokenType.IF,
    'THEN': TokenType.THEN,
    'ELSE': TokenType.ELSE,
    'AND': TokenType.AND,
    'OR': TokenType.OR,
    'NOT': TokenType.NOT,
}

# 运算符映射
OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '^': TokenType.POWER,
    '=': TokenType.EQUAL,
    '<>': TokenType.NOT_EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '>': TokenType.GREATER,
    '<': TokenType.LESS,
    '>=': TokenType.GREATER_EQUAL,
    '<=': TokenType.LESS_EQUAL,
    ':=': TokenType.ASSIGN,
}

# 分隔符映射
DELIMITERS = {
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    '[': TokenType.LEFT_BRACKET,
    ']': TokenType.RIGHT_BRACKET,
    ',': TokenType.COMMA,
    ';': TokenType.SEMICOLON,
}