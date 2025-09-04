#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器函数库模块

实现完整的通达信内置函数，包括：
- 技术指标函数（MA, EMA, MACD, KDJ, RSI等）
- 数学运算函数（ABS, MAX, MIN, SUM, COUNT等）
- 逻辑判断函数（IF, AND, OR, NOT等）
- 时序数据函数（REF, BARSLAST, CROSS等）
- 统计分析函数（STD, VAR, CORR等）
"""

from .registry import FunctionRegistry
from .base import TDXFunction, FunctionCategory

# 创建全局函数注册表
registry = FunctionRegistry()

# 注册所有内置函数
from . import builtin_functions
builtin_functions.register_all(registry)

__all__ = [
    "FunctionRegistry",
    "TDXFunction",
    "FunctionCategory",
    "registry",
]