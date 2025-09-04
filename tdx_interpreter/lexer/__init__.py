#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器词法分析模块

负责将通达信公式字符串分解为词法单元(Token)，识别：
- 数值常量（整数、浮点数）
- 标识符（变量名、函数名）
- 运算符（算术、比较、逻辑）
- 分隔符（括号、逗号、分号）
- 关键字（IF、AND、OR等）
"""

from .lexer import TDXLexer
from .tokens import Token, TokenType

__all__ = [
    "TDXLexer",
    "Token",
    "TokenType",
]