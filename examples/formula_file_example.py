#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式文件加载示例

演示如何从txt文件加载通达信公式并进行计算
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_interpreter import TDXInterpreter
from tdx_interpreter.errors.exceptions import TDXError

def create_sample_formula_files():
    """
    创建示例公式文件
    """
    # 创建示例目录
    sample_dir = os.path.join(os.path.dirname(__file__), 'sample_formulas')
    os.makedirs(sample_dir, exist_ok=True)
    
    # 示例1：简单移动平均线
    ma_formula = "MA(CLOSE, 5)"
    with open(os.path.join(sample_dir, 'ma5.txt'), 'w', encoding='utf-8') as f:
        f.write(ma_formula)
    
    # 示例2：MACD指标
    macd_formula = "MACD(CLOSE, 12, 26, 9)"
    with open(os.path.join(sample_dir, 'macd.txt'), 'w', encoding='utf-8') as f:
        f.write(macd_formula)
    
    # 示例3：复杂公式 - 布林带上轨
    boll_upper_formula = "MA(CLOSE, 20) + 2 * STD(CLOSE, 20)"
    with open(os.path.join(sample_dir, 'boll_upper.txt'), 'w', encoding='utf-8') as f:
        f.write(boll_upper_formula)
    
    # 示例4：条件判断公式
    condition_formula = "IF(CLOSE > OPEN, 1, 0)"
    with open(os.path.join(sample_dir, 'bullish_candle.txt'), 'w', encoding='utf-8') as f:
        f.write(condition_formula)
    
    # 示例5：多行公式（注释版本）
    complex_formula = """# 这是一个复杂的技术指标公式
# 计算RSI指标
RSI(CLOSE, 14)"""
    with open(os.path.join(sample_dir, 'rsi_with_comments.txt'), 'w', encoding='utf-8') as f:
        f.write(complex_formula)
    
    return sample_dir

def create_sample_data():
    """
    创建示例K线数据
    """
    # 生成30天的模拟K线数据
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    
    # 模拟价格数据
    np.random.seed(42)
    base_price = 100
    price_changes = np.random.normal(0, 2, 30)
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = max(prices[-1] + change, 1)  # 确保价格为正
        prices.append(new_price)
    
    # 创建OHLC数据
    data = []
    for i, price in enumerate(prices):
        high = price + abs(np.random.normal(0, 1))
        low = price - abs(np.random.normal(0, 1))
        open_price = price + np.random.normal(0, 0.5)
        close_price = price
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'date': dates[i],
            'OPEN': round(open_price, 2),
            'HIGH': round(high, 2),
            'LOW': round(low, 2),
            'CLOSE': round(close_price, 2),
            'VOLUME': volume
        })
    
    return pd.DataFrame(data)

def demonstrate_file_loading():
    """
    演示文件加载功能
    """
    print("=" * 60)
    print("通达信公式文件加载功能演示")
    print("=" * 60)
    
    # 创建解释器实例
    interpreter = TDXInterpreter()
    interpreter.set_debug_mode(True)
    
    # 创建示例文件和数据
    sample_dir = create_sample_formula_files()
    sample_data = create_sample_data()
    
    print(f"\n创建的示例数据:")
    print(sample_data.head())
    print(f"数据形状: {sample_data.shape}")
    
    # 测试各种公式文件
    formula_files = [
        ('ma5.txt', 'MA5移动平均线'),
        ('macd.txt', 'MACD指标'),
        ('boll_upper.txt', '布林带上轨'),
        ('bullish_candle.txt', '阳线判断'),
        ('rsi_with_comments.txt', 'RSI指标（带注释）')
    ]
    
    for filename, description in formula_files:
        file_path = os.path.join(sample_dir, filename)
        
        print(f"\n{'='*40}")
        print(f"测试: {description}")
        print(f"文件: {filename}")
        print(f"{'='*40}")
        
        try:
            # 方法1：先加载公式，再计算
            print("\n方法1: 分步执行")
            formula = interpreter.load_from_file(file_path)
            print(f"加载的公式: {formula}")
            
            result = interpreter.evaluate(formula, sample_data)
            print(f"计算结果类型: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"结果形状: {result.shape}")
                print(f"前5个值: {result[:5] if len(result) > 5 else result}")
            else:
                print(f"计算结果: {result}")
            
            # 方法2：直接从文件计算
            print("\n方法2: 直接从文件计算")
            result2 = interpreter.evaluate_file(file_path, sample_data)
            print(f"直接计算结果与分步结果一致: {np.array_equal(result, result2) if hasattr(result, '__len__') else result == result2}")
            
        except TDXError as e:
            print(f"TDX错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")
    
    print(f"\n{'='*60}")
    print("文件加载功能演示完成")
    print(f"示例文件保存在: {sample_dir}")
    print(f"{'='*60}")

def demonstrate_error_handling():
    """
    演示错误处理
    """
    print("\n" + "=" * 60)
    print("错误处理演示")
    print("=" * 60)
    
    interpreter = TDXInterpreter()
    
    # 测试各种错误情况
    error_cases = [
        ('不存在的文件', 'nonexistent.txt'),
        ('错误的文件格式', 'test.csv'),
        ('空文件', None)  # 我们会创建一个空文件
    ]
    
    for case_name, filename in error_cases:
        print(f"\n测试: {case_name}")
        
        if filename == None:  # 创建空文件
            filename = 'empty.txt'
            with open(filename, 'w') as f:
                pass  # 创建空文件
        
        try:
            result = interpreter.load_from_file(filename)
            print(f"意外成功: {result}")
        except TDXError as e:
            print(f"预期的TDX错误: {e}")
        except Exception as e:
            print(f"其他错误: {e}")
        
        # 清理空文件
        if filename == 'empty.txt' and os.path.exists(filename):
            os.remove(filename)

def main():
    """
    主函数
    """
    try:
        demonstrate_file_loading()
        demonstrate_error_handling()
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()