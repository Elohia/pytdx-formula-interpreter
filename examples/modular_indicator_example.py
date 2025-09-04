#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化指标系统使用示例

展示如何使用分层筛选和复合指标进行股票技术分析。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入模块化指标系统组件
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_interpreter.indicators.builtin import MovingAverageModule, RSIModule, MACDModule
from tdx_interpreter.indicators.filter_layer import FilterLayer, FilterCondition, FilterOperator, PrebuiltFilters
from tdx_interpreter.indicators.composite import CompositeIndicator, SignalType, Signal, TrendFollowingStrategy
from tdx_interpreter.indicators.manager import IndicatorManager, get_indicator_manager


def create_sample_data(days: int = 100) -> pd.DataFrame:
    """
    创建示例股票数据
    
    Args:
        days: 数据天数
        
    Returns:
        pd.DataFrame: 股票K线数据
    """
    # 生成日期索引
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    
    # 生成模拟价格数据（带趋势和波动）
    np.random.seed(42)
    base_price = 100.0
    trend = np.linspace(0, 20, days)  # 上升趋势
    noise = np.random.normal(0, 2, days)  # 随机波动
    
    prices = base_price + trend + noise
    
    # 生成OHLC数据
    data = pd.DataFrame({
        'OPEN': prices * (1 + np.random.uniform(-0.02, 0.02, days)),
        'HIGH': prices * (1 + np.random.uniform(0.01, 0.05, days)),
        'LOW': prices * (1 + np.random.uniform(-0.05, -0.01, days)),
        'CLOSE': prices,
        'VOLUME': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    
    return data


def example_basic_indicators():
    """
    示例1: 基础指标使用
    """
    print("=== 示例1: 基础指标使用 ===")
    
    # 创建示例数据
    data = create_sample_data(50)
    print(f"数据范围: {data.index[0]} 到 {data.index[-1]}")
    print(f"价格范围: {data['CLOSE'].min():.2f} - {data['CLOSE'].max():.2f}")
    
    # 1. 移动平均线
    ma5 = MovingAverageModule(period=5, ma_type='SMA')
    ma20 = MovingAverageModule(period=20, ma_type='SMA')
    
    ma5_result = ma5.calculate(data)
    ma20_result = ma20.calculate(data)
    
    print(f"\n5日均线 ({ma5_result.name}):")
    print(f"最新值: {ma5_result.get_series().iloc[-1]:.2f}")
    print(f"20日均线 ({ma20_result.name}):")
    print(f"最新值: {ma20_result.get_series().iloc[-1]:.2f}")
    
    # 2. RSI指标
    rsi = RSIModule(period=14)
    rsi_result = rsi.calculate(data)
    
    print(f"\nRSI指标:")
    print(f"最新值: {rsi_result.get_series().iloc[-1]:.2f}")
    
    # 3. MACD指标
    macd = MACDModule()
    macd_result = macd.calculate(data)
    
    print(f"\nMACD指标:")
    print(f"MACD线: {macd_result.data['macd'].iloc[-1]:.4f}")
    print(f"信号线: {macd_result.data['signal'].iloc[-1]:.4f}")
    print(f"柱状图: {macd_result.data['histogram'].iloc[-1]:.4f}")


def example_filter_layer():
    """
    示例2: 筛选层使用
    """
    print("\n=== 示例2: 筛选层使用 ===")
    
    # 创建示例数据
    data = create_sample_data(100)
    
    # 创建筛选层
    filter_layer = FilterLayer("股票筛选")
    
    # 添加筛选条件
    # 1. 价格筛选：收盘价大于110
    def price_filter(data, indicators):
        return data['CLOSE'] > 110
    
    # 2. 成交量筛选：成交量大于平均值
    def volume_filter(data, indicators):
        avg_volume = data['VOLUME'].mean()
        return data['VOLUME'] > avg_volume
    
    # 3. 价格波动筛选：日内波动幅度小于5%
    def volatility_filter(data, indicators):
        daily_range = (data['HIGH'] - data['LOW']) / data['CLOSE']
        return daily_range < 0.05
    
    filter_layer.add_condition(price_filter, "price_gt_110", "价格大于110")
    filter_layer.add_condition(volume_filter, "volume_above_avg", "成交量大于平均")
    filter_layer.add_condition(volatility_filter, "low_volatility", "低波动率")
    
    # 应用筛选
    filtered_data = filter_layer.apply(data, {})
    
    print(f"原始数据: {len(data)} 条")
    print(f"筛选后数据: {len(filtered_data)} 条")
    print(f"筛选比例: {len(filtered_data)/len(data)*100:.1f}%")
    
    if len(filtered_data) > 0:
        print(f"\n筛选后价格范围: {filtered_data['CLOSE'].min():.2f} - {filtered_data['CLOSE'].max():.2f}")
        print(f"筛选后平均成交量: {filtered_data['VOLUME'].mean():.0f}")


def example_composite_indicator():
    """
    示例3: 复合指标使用
    """
    print("\n=== 示例3: 复合指标使用 ===")
    
    # 创建示例数据
    data = create_sample_data(100)
    
    # 创建自定义复合指标
    composite = CompositeIndicator("多指标组合", "基于MA和RSI的组合指标")
    
    # 添加基础指标
    composite.add_indicator(MovingAverageModule(period=5), "MA5")
    composite.add_indicator(MovingAverageModule(period=20), "MA20")
    composite.add_indicator(RSIModule(period=14), "RSI")
    
    # 定义组合逻辑
    def combination_logic(data, indicators):
        """
        组合逻辑：生成买卖信号
        """
        ma5 = indicators['MA5'].get_series()
        ma20 = indicators['MA20'].get_series()
        rsi = indicators['RSI'].get_series()
        
        # 创建信号DataFrame
        signals = pd.DataFrame(index=data.index)
        
        # 买入信号：MA5上穿MA20且RSI不超买
        buy_signal = (ma5 > ma20) & (ma5.shift(1) <= ma20.shift(1)) & (rsi < 70)
        
        # 卖出信号：MA5下穿MA20且RSI不超卖
        sell_signal = (ma5 < ma20) & (ma5.shift(1) >= ma20.shift(1)) & (rsi > 30)
        
        # 组合信号强度
        signals['signal_strength'] = 0.0
        signals.loc[buy_signal, 'signal_strength'] = 1.0
        signals.loc[sell_signal, 'signal_strength'] = -1.0
        
        return signals
    
    composite.set_combination_logic(combination_logic)
    
    # 计算复合指标
    result = composite.calculate(data)
    
    print(f"复合指标名称: {result.name}")
    print(f"包含的基础指标: {result.parameters['base_indicators']}")
    print(f"生成的信号数量: {result.parameters['signals_generated']}")
    
    # 获取信号
    signals = composite.get_signals()
    if signals:
        print(f"\n最近的信号:")
        for signal in signals[-3:]:  # 显示最近3个信号
            print(f"  {signal.timestamp.strftime('%Y-%m-%d')}: {signal.signal_type.value.upper()} "
                  f"强度={signal.strength:.2f} 置信度={signal.confidence:.2f} 价格={signal.price:.2f}")


def example_trend_following_strategy():
    """
    示例4: 趋势跟踪策略
    """
    print("\n=== 示例4: 趋势跟踪策略 ===")
    
    # 创建示例数据
    data = create_sample_data(100)
    
    # 创建趋势跟踪策略
    strategy = TrendFollowingStrategy(
        ma_short_period=5,
        ma_long_period=20,
        rsi_period=14
    )
    
    # 计算策略
    result = strategy.calculate(data)
    
    print(f"策略名称: {result.name}")
    print(f"使用的指标: {result.parameters['base_indicators']}")
    print(f"生成信号数量: {result.parameters['signals_generated']}")
    
    # 获取信号统计
    signal_summary = strategy.get_signal_summary()
    print(f"\n信号统计:")
    print(f"  总信号数: {signal_summary['total']}")
    if signal_summary['total'] > 0:
        by_type = signal_summary.get('by_type', {})
        print(f"  买入信号: {by_type.get('buy', 0)} 个")
        print(f"  卖出信号: {by_type.get('sell', 0)} 个")
        print(f"  平均信号强度: {signal_summary['avg_strength']:.3f}")
        print(f"  平均置信度: {signal_summary['avg_confidence']:.3f}")
    else:
        print("  暂无交易信号生成")
    
    # 获取高质量信号（强度>0.5）
    high_quality_signals = strategy.get_signals(min_strength=0.5)
    print(f"\n高质量信号 (强度>0.5): {len(high_quality_signals)} 个")
    
    if high_quality_signals:
        print("最近的高质量信号:")
        for signal in high_quality_signals[-2:]:  # 显示最近2个
            print(f"  {signal.timestamp.strftime('%Y-%m-%d')}: {signal.signal_type.value.upper()} "
                  f"强度={signal.strength:.2f} 价格={signal.price:.2f}")
            if signal.metadata:
                print(f"    MA短期={signal.metadata.get('ma_short', 0):.2f} "
                      f"MA长期={signal.metadata.get('ma_long', 0):.2f} "
                      f"RSI={signal.metadata.get('rsi', 0):.1f}")


def example_indicator_manager():
    """
    示例5: 指标管理器使用
    """
    print("\n=== 示例5: 指标管理器使用 ===")
    
    # 获取指标管理器
    manager = get_indicator_manager()
    
    # 创建示例数据
    data = create_sample_data(50)
    
    # 注册指标类（注意：传入类而不是实例）
    manager.register_indicator(MovingAverageModule, "CustomMA")
    manager.register_indicator(RSIModule, "CustomRSI")
    
    # 获取可用指标列表
    available = manager.get_available_indicators()
    print(f"可用指标数量: {len(available)}")
    
    # 创建指标实例并计算
    ma5 = MovingAverageModule(period=5)
    ma20 = MovingAverageModule(period=20)
    rsi = RSIModule(period=14)
    
    results = {
        "MA5": ma5.calculate(data),
        "MA20": ma20.calculate(data),
        "RSI14": rsi.calculate(data)
    }
    
    print(f"\n批量计算结果:")
    for name, result in results.items():
        if hasattr(result, 'get_series'):
            latest_value = result.get_series().iloc[-1]
            print(f"  {name}: {latest_value:.2f}")
        else:
            print(f"  {name}: 多列数据")
    
    # 显示管理器统计信息
    stats = manager.get_statistics()
    print(f"\n管理器统计:")
    print(f"  总指标数: {stats['total_indicators']}")
    print(f"  内置指标数: {stats['builtin_indicators']}")
    print(f"  自定义指标数: {stats['custom_indicators']}")
    print(f"  活跃实例数: {stats['active_instances']}")
    print(f"  复合指标数: {stats['composite_indicators']}")
    print(f"  筛选层数: {stats['filter_layers']}")


def main():
    """
    主函数：运行所有示例
    """
    print("模块化指标系统使用示例")
    print("=" * 50)
    
    try:
        # 运行各个示例
        example_basic_indicators()
        example_filter_layer()
        example_composite_indicator()
        example_trend_following_strategy()
        example_indicator_manager()
        
        print("\n=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"\n运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()