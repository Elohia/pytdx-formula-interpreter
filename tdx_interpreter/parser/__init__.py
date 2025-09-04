#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器语法解析模块

负责将Token序列转换为抽象语法树(AST)，支持：
- 表达式解析（算术、比较、逻辑）
- 函数调用解析
- 条件语句解析
- 赋值语句解析
- 运算符优先级处理
- 语法错误检测和恢复
"""

from .parser import TDXParser
from .precedence import OperatorPrecedence

__all__ = [
    "TDXParser",
    "OperatorPrecedence",
]