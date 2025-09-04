#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器基本使用示例

演示如何使用通达信公式解释器进行公式解析和计算。
"""

import pandas as pd
import numpy as np
from tdx_interpreter import TDXInterpreter, evaluate, parse, validate
from tdx_interpreter.functions import registry


def create_sample_data():
    """
    创建示例K线数据
    
    Returns:
        pd.DataFrame: 包含OHLCV数据的DataFrame
    """
    np.random.seed(42)  # 确保结果可重现
    
    # 生成模拟的股价数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # 生成价格数据（随机游走）
    returns = np.random.normal(0.001, 0.02, 100)  # 日收益率
    prices = 100 * np.exp(np.cumsum(returns))  # 价格序列
    
    # 生成OHLC数据
    high_factor = np.random.uniform(1.01, 1.05, 100)
    low_factor = np.random.uniform(0.95, 0.99, 100)
    
    data = pd.DataFrame({
        'DATE': dates,
        'OPEN': prices * np.random.uniform(0.98, 1.02, 100),
        'HIGH': prices * high_factor,
        'LOW': prices * low_factor,
        'CLOSE': prices,
        'VOLUME': np.random.randint(1000000, 10000000, 100),
        'AMOUNT': prices * np.random.randint(1000000, 10000000, 100)
    })
    
    return data


def demo_basic_functions():
    """
    演示基本函数使用
    """
    print("=== 基本函数使用演示 ===")
    
    # 创建示例数据
    data = create_sample_data()
    print(f"数据样本 ({len(data)} 条记录):")
    print(data.head())
    print()
    
    # 使用便捷函数进行计算
    print("1. 使用便捷函数计算技术指标:")
    
    try:
        # 计算5日移动平均线
        ma5_result = evaluate("MA(CLOSE, 5)", context=data)
        print(f"MA5 最后5个值: {ma5_result.tail().values}")
        
        # 计算相对强弱指标
        rsi_result = evaluate("RSI(CLOSE, 14)", context=data)
        print(f"RSI14 最后5个值: {rsi_result.tail().values}")
        
        # 计算布林带
        boll_result = evaluate("BOLL(CLOSE, 20, 2)", context=data)
        print(f"BOLL 最后一个值: {boll_result[0].iloc[-1]:.2f}, {boll_result[1].iloc[-1]:.2f}, {boll_result[2].iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"计算出错: {e}")
    
    print()


def demo_complex_formulas():
    """
    演示复杂公式解析
    """
    print("=== 复杂公式解析演示 ===")
    
    # 复杂公式示例
    formulas = [
        "MA(CLOSE, 5) > MA(CLOSE, 10)",
        "IF(CLOSE > OPEN, 1, 0)",
        "CROSS(MA(CLOSE, 5), MA(CLOSE, 20))",
        "RSI(CLOSE, 14) > 70",
        "BOLL(CLOSE, 20, 2)"
    ]
    
    for formula in formulas:
        print(f"公式: {formula}")
        
        # 验证语法
        is_valid = validate(formula)
        print(f"  语法验证: {'✓ 有效' if is_valid else '✗ 无效'}")
        
        if is_valid:
            try:
                # 解析AST
                ast = parse(formula)
                print(f"  AST类型: {type(ast.body[0]).__name__}")
                
            except Exception as e:
                print(f"  解析错误: {e}")
        
        print()


def demo_interpreter_usage():
    """
    演示解释器实例使用
    """
    print("=== 解释器实例使用演示 ===")
    
    # 创建解释器实例
    interpreter = TDXInterpreter()
    interpreter.set_debug_mode(True)
    
    # 创建数据
    data = create_sample_data()
    
    # 注册自定义函数
    def custom_indicator(close_prices, period):
        """自定义指标：价格相对于均线的偏离度"""
        ma = close_prices.rolling(period).mean()
        return ((close_prices - ma) / ma * 100)
    
    interpreter.register_function("CUSTOM_DEV", custom_indicator)
    
    print("1. 使用自定义函数:")
    try:
        result = interpreter.evaluate("CUSTOM_DEV(CLOSE, 20)", context=data)
        print(f"自定义偏离度指标最后5个值: {result.tail().values}")
    except Exception as e:
        print(f"计算出错: {e}")
    
    print()
    
    print("2. 多语句公式:")
    complex_formula = """
    MA5 := MA(CLOSE, 5);
    MA20 := MA(CLOSE, 20);
    SIGNAL := IF(MA5 > MA20, 1, 0)
    """
    
    try:
        result = interpreter.evaluate(complex_formula, context=data)
        print(f"多语句公式结果类型: {type(result)}")
        print(f"结果: {result}")
    except Exception as e:
        print(f"计算出错: {e}")
    
    print()


def demo_function_registry():
    """
    演示函数注册表使用
    """
    print("=== 函数注册表演示 ===")
    
    # 获取统计信息
    stats = registry.get_statistics()
    print(f"注册表统计信息:")
    print(f"  总函数数: {stats['total_functions']}")
    print(f"  总别名数: {stats['total_aliases']}")
    print(f"  分类数: {stats['categories']}")
    print(f"  各分类函数数: {stats['category_counts']}")
    print()
    
    # 列出技术指标函数
    from tdx_interpreter.functions.base import FunctionCategory
    technical_functions = registry.list_functions(FunctionCategory.TECHNICAL)
    print(f"技术指标函数 ({len(technical_functions)} 个):")
    print(f"  {', '.join(technical_functions)}")
    print()
    
    # 搜索函数
    ma_functions = registry.search_functions("MA")
    print(f"包含'MA'的函数 ({len(ma_functions)} 个):")
    for func in ma_functions:
        print(f"  {func.name}: {func.description}")
    print()
    
    # 获取函数帮助
    print("MA函数帮助信息:")
    help_text = registry.get_function_help("MA")
    print(help_text)
    print()


def demo_error_handling():
    """
    演示错误处理
    """
    print("=== 错误处理演示 ===")
    
    error_cases = [
        ("语法错误", "MA(CLOSE, )"),  # 缺少参数
        ("函数不存在", "UNKNOWN_FUNC(CLOSE, 5)"),  # 未知函数
        ("参数类型错误", "MA(\"invalid\", 5)"),  # 错误的参数类型
        ("参数数量错误", "MA(CLOSE)"),  # 参数不足
    ]
    
    for error_type, formula in error_cases:
        print(f"{error_type}: {formula}")
        
        try:
            result = evaluate(formula)
            print(f"  意外成功: {result}")
        except Exception as e:
            print(f"  ✓ 正确捕获错误: {type(e).__name__}: {e}")
        
        print()


def main():
    """
    主函数
    """
    print("通达信公式解释器使用示例")
    print("=" * 50)
    print()
    
    try:
        # 基本功能演示
        demo_basic_functions()
        
        # 复杂公式演示
        demo_complex_formulas()
        
        # 解释器使用演示
        demo_interpreter_usage()
        
        # 函数注册表演示
        demo_function_registry()
        
        # 错误处理演示
        demo_error_handling()
        
        print("=" * 50)
        print("演示完成！")
        print()
        print("提示:")
        print("- 本解释器支持完整的通达信公式语法")
        print("- 包含50+个内置函数，涵盖技术分析的各个方面")
        print("- 支持自定义函数扩展")
        print("- 提供详细的错误信息和调试支持")
        print("- 与通达信软件保持高度兼容")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()