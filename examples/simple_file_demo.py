#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式文件加载功能简单演示

展示如何从txt文件加载通达信公式并进行计算
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_interpreter import TDXInterpreter
from tdx_interpreter.errors.exceptions import TDXError

def create_test_data():
    """
    创建测试用的K线数据
    """
    # 生成20天的模拟数据
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    
    # 模拟股价走势
    np.random.seed(42)
    base_price = 100
    prices = [base_price]
    
    for i in range(19):
        change = np.random.normal(0, 1.5)
        new_price = max(prices[-1] + change, 10)  # 确保价格不会太低
        prices.append(new_price)
    
    # 创建完整的OHLCV数据
    data = []
    for i, close in enumerate(prices):
        open_price = close + np.random.normal(0, 0.5)
        high = max(open_price, close) + abs(np.random.normal(0, 0.8))
        low = min(open_price, close) - abs(np.random.normal(0, 0.8))
        volume = np.random.randint(10000, 100000)
        
        data.append({
            'date': dates[i],
            'OPEN': round(open_price, 2),
            'HIGH': round(high, 2),
            'LOW': round(low, 2),
            'CLOSE': round(close, 2),
            'VOLUME': volume
        })
    
    return pd.DataFrame(data)

def create_formula_files():
    """
    创建示例公式文件
    """
    # 创建公式文件目录
    formula_dir = 'formula_examples'
    if not os.path.exists(formula_dir):
        os.makedirs(formula_dir)
    
    # 创建各种公式文件
    formulas = {
        'ma5.txt': 'MA(CLOSE, 5)',
        'ma20.txt': 'MA(CLOSE, 20)',
        'rsi.txt': 'RSI(CLOSE, 14)',
        'macd.txt': 'MACD(CLOSE, 12, 26, 9)',
        'bollinger_upper.txt': 'MA(CLOSE, 20) + 2 * STD(CLOSE, 20)',
        'price_change.txt': '(CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1) * 100',
        'bullish_signal.txt': 'IF(CLOSE > OPEN, 1, 0)',
        'volume_ma.txt': 'MA(VOLUME, 10)',
        'high_low_ratio.txt': '(HIGH - LOW) / CLOSE * 100',
        'complex_strategy.txt': '''# 复合策略信号
# 当MA5上穿MA20且RSI小于70时买入
IF(CROSS(MA(CLOSE, 5), MA(CLOSE, 20)) AND RSI(CLOSE, 14) < 70, 1, 0)'''
    }
    
    for filename, formula in formulas.items():
        filepath = os.path.join(formula_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formula)
        print(f"创建公式文件: {filepath}")
    
    return formula_dir

def main():
    """
    主演示函数
    """
    print("=" * 60)
    print("通达信公式文件加载功能演示")
    print("=" * 60)
    
    # 创建解释器
    interpreter = TDXInterpreter()
    
    # 创建测试数据
    print("\n1. 创建测试数据...")
    data = create_test_data()
    print(f"数据形状: {data.shape}")
    print("前5行数据:")
    print(data[['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']].head())
    
    # 创建公式文件
    print("\n2. 创建公式文件...")
    formula_dir = create_formula_files()
    
    # 演示文件加载和计算
    print("\n3. 演示文件加载和计算...")
    
    test_files = [
        ('ma5.txt', '5日移动平均线'),
        ('rsi.txt', 'RSI相对强弱指标'),
        ('bullish_signal.txt', '阳线信号'),
        ('complex_strategy.txt', '复合策略（带注释）')
    ]
    
    for filename, description in test_files:
        filepath = os.path.join(formula_dir, filename)
        
        print(f"\n{'='*40}")
        print(f"测试: {description}")
        print(f"文件: {filename}")
        print(f"{'='*40}")
        
        try:
            # 方法1: 先加载公式，再计算
            print("\n方法1: 分步执行")
            formula = interpreter.load_from_file(filepath)
            print(f"加载的公式: {repr(formula)}")
            
            result = interpreter.evaluate(formula, data)
            print(f"计算结果类型: {type(result).__name__}")
            
            if hasattr(result, 'shape'):
                print(f"结果形状: {result.shape}")
                if len(result) > 0:
                    print(f"前3个值: {result[:3].tolist()}")
                    print(f"后3个值: {result[-3:].tolist()}")
            else:
                print(f"计算结果: {result}")
            
            # 方法2: 直接从文件计算
            print("\n方法2: 直接从文件计算")
            result2 = interpreter.evaluate_file(filepath, data)
            
            # 比较两种方法的结果
            if hasattr(result, '__len__') and hasattr(result2, '__len__'):
                is_equal = np.allclose(result, result2, equal_nan=True)
            else:
                is_equal = result == result2
            
            print(f"两种方法结果一致: {is_equal}")
            
        except TDXError as e:
            print(f"TDX错误: {e}")
        except Exception as e:
            print(f"其他错误: {type(e).__name__}: {e}")
    
    print(f"\n{'='*60}")
    print("演示完成！")
    print(f"公式文件保存在: {os.path.abspath(formula_dir)}")
    print("\n使用方法:")
    print("1. 创建包含通达信公式的.txt文件")
    print("2. 使用 interpreter.load_from_file(filepath) 加载公式")
    print("3. 使用 interpreter.evaluate(formula, data) 计算结果")
    print("4. 或直接使用 interpreter.evaluate_file(filepath, data) 一步完成")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()