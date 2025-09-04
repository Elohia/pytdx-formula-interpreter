#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信内置函数注册

将所有内置函数注册到全局函数注册表中。
"""

from .registry import FunctionRegistry
from .technical import (
    MAFunction, EMAFunction, SMAFunction, MACDFunction,
    RSIFunction, BOLLFunction, KDJFunction, ATRFunction
)
from .mathematical import (
    ABSFunction, MAXFunction, MINFunction, SUMFunction,
    COUNTFunction, HHVFunction, LLVFunction, SQRTFunction,
    POWFunction, ROUNDFunction, FLOORFunction, CEILFunction,
    AVERAGEFunction
)
from .logical import (
    IFFunction, ANDFunction, ORFunction, NOTFunction,
    BETWEENFunction, EVERYFunction, EXISTFunction,
    IFFFunction, IFNFunction, RANGEFunction
)
from .temporal import (
    REFFunction, BARSLASTFunction, BARSLASTCOUNTFunction,
    BARSCOUNTFunction, CROSSFunction, LONGCROSSFunction,
    FILTERFunction, BACKSETFunction, SINCEFunction, LASTFunction
)
from .statistical import (
    STDFunction, VARFunction, CORRFunction, COVARFunction,
    AVEDEVFunction, DEVSQFunction, SLOPEFunction, FORCASTFunction,
    SKEWFunction, KURTFunction
)


def register_all(registry: FunctionRegistry):
    """
    注册所有内置函数
    
    Args:
        registry: 函数注册表
    """
    # 注册技术指标函数
    _register_technical_functions(registry)
    
    # 注册数学运算函数
    _register_mathematical_functions(registry)
    
    # 注册逻辑判断函数
    _register_logical_functions(registry)
    
    # 注册时序数据函数
    _register_temporal_functions(registry)
    
    # 注册统计分析函数
    _register_statistical_functions(registry)


def _register_technical_functions(registry: FunctionRegistry):
    """
    注册技术指标函数
    
    Args:
        registry: 函数注册表
    """
    # 移动平均线
    registry.register(MAFunction())
    registry.register(EMAFunction())
    registry.register(SMAFunction())
    
    # 技术指标
    registry.register(MACDFunction())
    registry.register(RSIFunction())
    registry.register(BOLLFunction())
    registry.register(KDJFunction())
    registry.register(ATRFunction())


def _register_mathematical_functions(registry: FunctionRegistry):
    """
    注册数学运算函数
    
    Args:
        registry: 函数注册表
    """
    # 基本数学函数
    registry.register(ABSFunction())
    registry.register(MAXFunction())
    registry.register(MINFunction())
    registry.register(SQRTFunction())
    registry.register(POWFunction())
    
    # 统计函数
    registry.register(SUMFunction())
    registry.register(COUNTFunction())
    registry.register(AVERAGEFunction())
    
    # 极值函数
    registry.register(HHVFunction())
    registry.register(LLVFunction())
    
    # 取整函数
    registry.register(ROUNDFunction())
    registry.register(FLOORFunction())
    registry.register(CEILFunction())


def _register_logical_functions(registry: FunctionRegistry):
    """
    注册逻辑判断函数
    
    Args:
        registry: 函数注册表
    """
    # 条件函数
    registry.register(IFFunction())
    registry.register(IFFFunction())
    registry.register(IFNFunction())
    
    # 逻辑运算
    registry.register(ANDFunction())
    registry.register(ORFunction())
    registry.register(NOTFunction())
    
    # 范围判断
    registry.register(BETWEENFunction())
    registry.register(RANGEFunction())
    
    # 条件统计
    registry.register(EVERYFunction())
    registry.register(EXISTFunction())


def _register_temporal_functions(registry: FunctionRegistry):
    """
    注册时序数据函数
    
    Args:
        registry: 函数注册表
    """
    # 引用函数
    registry.register(REFFunction())
    
    # 计数函数
    registry.register(BARSLASTFunction())
    registry.register(BARSLASTCOUNTFunction())
    registry.register(BARSCOUNTFunction())
    
    # 交叉函数
    registry.register(CROSSFunction())
    registry.register(LONGCROSSFunction())
    
    # 过滤函数
    registry.register(FILTERFunction())
    registry.register(BACKSETFunction())
    
    # 时序统计
    registry.register(SINCEFunction())
    registry.register(LASTFunction())


def _register_statistical_functions(registry: FunctionRegistry):
    """
    注册统计分析函数
    
    Args:
        registry: 函数注册表
    """
    # 基本统计
    registry.register(STDFunction())
    registry.register(VARFunction())
    
    # 相关性分析
    registry.register(CORRFunction())
    registry.register(COVARFunction())
    
    # 偏差分析
    registry.register(AVEDEVFunction())
    registry.register(DEVSQFunction())
    
    # 回归分析
    registry.register(SLOPEFunction())
    registry.register(FORCASTFunction())
    
    # 分布特征
    registry.register(SKEWFunction())
    registry.register(KURTFunction())


def get_function_list() -> dict:
    """
    获取所有内置函数列表
    
    Returns:
        dict: 按分类组织的函数列表
    """
    return {
        'technical': [
            'MA', 'EMA', 'SMA', 'MACD', 'RSI', 'BOLL', 'KDJ', 'ATR'
        ],
        'mathematical': [
            'ABS', 'MAX', 'MIN', 'SQRT', 'POW', 'SUM', 'COUNT', 'AVERAGE',
            'HHV', 'LLV', 'ROUND', 'FLOOR', 'CEIL'
        ],
        'logical': [
            'IF', 'IFF', 'IFN', 'AND', 'OR', 'NOT', 'BETWEEN', 'RANGE',
            'EVERY', 'EXIST'
        ],
        'temporal': [
            'REF', 'BARSLAST', 'BARSLASTCOUNT', 'BARSCOUNT', 'CROSS',
            'LONGCROSS', 'FILTER', 'BACKSET', 'SINCE', 'LAST'
        ],
        'statistical': [
            'STD', 'VAR', 'CORR', 'COVAR', 'AVEDEV', 'DEVSQ',
            'SLOPE', 'FORCAST', 'SKEW', 'KURT'
        ]
    }


def get_function_count() -> dict:
    """
    获取各类函数的数量统计
    
    Returns:
        dict: 函数数量统计
    """
    function_list = get_function_list()
    return {
        category: len(functions)
        for category, functions in function_list.items()
    }


def print_function_summary():
    """
    打印函数摘要信息
    """
    function_list = get_function_list()
    function_count = get_function_count()
    
    print("通达信内置函数摘要")
    print("=" * 50)
    
    total_functions = sum(function_count.values())
    print(f"总函数数量: {total_functions}")
    print()
    
    for category, functions in function_list.items():
        count = function_count[category]
        print(f"{category.upper()} ({count}个):")
        print(f"  {', '.join(functions)}")
        print()
    
    print("注意: 这些函数与通达信软件保持兼容，支持相同的参数和计算逻辑。")


if __name__ == "__main__":
    # 演示用法
    print_function_summary()