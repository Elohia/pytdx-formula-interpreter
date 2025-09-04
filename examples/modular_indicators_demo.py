#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化指标示例

展示通达信公式解释器中模块化指标计算框架的使用方法，
包括分层筛选、组合指标和复杂策略的实现。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tdx_interpreter.indicators import (
    get_indicator_manager, reset_indicator_manager,
    FilterLayer, PrebuiltFilters,
    CompositeIndicator, SignalType, Signal,
    MovingAverageModule, RSIModule, MACDModule, BollingerBandsModule,
    IndicatorResult, IndicatorType
)


def create_sample_data(days: int = 252) -> pd.DataFrame:
    """
    创建模拟股票数据
    
    Args:
        days: 数据天数（默认一年交易日）
        
    Returns:
        pd.DataFrame: 包含OHLCV的股票数据
    """
    print(f"创建 {days} 天的模拟股票数据...")
    
    # 生成日期序列
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    # 设置随机种子以获得可重复的结果
    np.random.seed(42)
    
    # 生成价格走势（带趋势的随机游走）
    base_price = 50.0
    trend = 0.0002  # 轻微上涨趋势
    volatility = 0.02
    
    price_changes = np.random.normal(trend, volatility, days)
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1.0))  # 确保价格为正
    
    # 生成OHLCV数据
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # 生成日内波动
        daily_range = close * np.random.uniform(0.01, 0.05)
        high = close + np.random.uniform(0, daily_range)
        low = close - np.random.uniform(0, daily_range)
        open_price = low + (high - low) * np.random.random()
        
        # 确保OHLC关系正确
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # 生成成交量（与价格变化相关）
        volume_base = 1000000
        volume_factor = 1 + abs(price_changes[i]) * 10  # 价格波动大时成交量增加
        volume = int(volume_base * volume_factor * np.random.uniform(0.5, 2.0))
        
        data.append({
            'date': date,
            'OPEN': round(open_price, 2),
            'HIGH': round(high, 2),
            'LOW': round(low, 2),
            'CLOSE': round(close, 2),
            'VOLUME': volume
        })
    
    df = pd.DataFrame(data)
    print(f"数据创建完成，价格范围: {df['CLOSE'].min():.2f} - {df['CLOSE'].max():.2f}")
    return df


def demo_basic_indicators():
    """
    演示基础指标的使用
    """
    print("\n=== 基础指标演示 ===")
    
    # 获取指标管理器
    manager = get_indicator_manager()
    
    # 创建测试数据
    data = create_sample_data(100)
    
    print(f"\n可用指标数量: {len(manager)}")
    
    # 演示移动平均线
    print("\n1. 移动平均线指标")
    ma5_result = manager.calculate_indicator("MovingAverageModule", data, period=5)
    ma20_result = manager.calculate_indicator("MovingAverageModule", data, period=20)
    
    print(f"MA5 最新值: {ma5_result.values.iloc[-1]:.2f}")
    print(f"MA20 最新值: {ma20_result.values.iloc[-1]:.2f}")
    
    # 演示RSI指标
    print("\n2. RSI指标")
    rsi_result = manager.calculate_indicator("RSIModule", data, period=14)
    print(f"RSI 最新值: {rsi_result.values.iloc[-1]:.2f}")
    
    # 演示MACD指标
    print("\n3. MACD指标")
    macd_result = manager.calculate_indicator("MACDModule", data, fast_period=12, slow_period=26, signal_period=9)
    print(f"MACD 最新值: {macd_result.values.iloc[-1]:.4f}")
    print(f"MACD 元数据: {list(macd_result.metadata.keys())}")
    
    # 批量计算指标
    print("\n4. 批量计算指标")
    indicators_config = {
        "ma5": {"name": "MovingAverageModule", "params": {"period": 5}},
        "ma10": {"name": "MovingAverageModule", "params": {"period": 10}},
        "ma20": {"name": "MovingAverageModule", "params": {"period": 20}},
        "rsi14": {"name": "RSIModule", "params": {"period": 14}},
        "macd": {"name": "MACDModule", "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}}
    }
    
    batch_results = manager.batch_calculate(indicators_config, data)
    print(f"批量计算完成，共计算 {len(batch_results)} 个指标")
    
    for name, result in batch_results.items():
        latest_value = result.values.iloc[-1]
        if pd.notna(latest_value):
            print(f"  {name}: {latest_value:.4f}")
        else:
            print(f"  {name}: N/A")


def demo_filter_layer():
    """
    演示筛选层的使用
    """
    print("\n=== 筛选层演示 ===")
    
    data = create_sample_data(100)
    
    # 创建筛选层
    filter_layer = FilterLayer("stock_filter")
    
    # 添加自定义筛选条件
    def price_above_ma20(data):
        """价格在20日均线之上"""
        ma20 = data['CLOSE'].rolling(window=20).mean()
        return data['CLOSE'] > ma20
    
    def volume_surge(data):
        """成交量放大"""
        avg_volume = data['VOLUME'].rolling(window=10).mean()
        return data['VOLUME'] > avg_volume * 1.5
    
    def price_range_filter(data):
        """价格在合理范围内"""
        return (data['CLOSE'] > 30) & (data['CLOSE'] < 100)
    
    # 添加筛选条件
    filter_layer.add_condition(price_above_ma20, "price_above_ma20", "价格在20日均线之上")
    filter_layer.add_condition(volume_surge, "volume_surge", "成交量放大1.5倍")
    filter_layer.add_condition(price_range_filter, "price_range", "价格在30-100区间")
    
    print(f"原始数据行数: {len(data)}")
    
    # 应用筛选
    filtered_data = filter_layer.apply(data)
    print(f"筛选后数据行数: {len(filtered_data)}")
    print(f"筛选比例: {len(filtered_data)/len(data)*100:.1f}%")
    
    if len(filtered_data) > 0:
        print(f"筛选后价格范围: {filtered_data['CLOSE'].min():.2f} - {filtered_data['CLOSE'].max():.2f}")
        print(f"筛选后平均成交量: {filtered_data['VOLUME'].mean():,.0f}")
    
    # 演示预构建筛选条件
    print("\n使用预构建筛选条件:")
    
    # 趋势向上筛选
    trend_filter = FilterLayer("trend_filter")
    trend_condition = PrebuiltFilters.trend_up(period=10)
    trend_filter.add_condition(trend_condition, "trend_up", "10日趋势向上")
    
    trend_filtered = trend_filter.apply(data)
    print(f"趋势向上筛选: {len(data)} -> {len(trend_filtered)} 行")
    
    # RSI非超买筛选
    rsi_filter = FilterLayer("rsi_filter")
    rsi_condition = PrebuiltFilters.rsi_not_overbought(period=14, threshold=70)
    rsi_filter.add_condition(rsi_condition, "rsi_normal", "RSI未超买")
    
    rsi_filtered = rsi_filter.apply(data)
    print(f"RSI非超买筛选: {len(data)} -> {len(rsi_filtered)} 行")
    
    # 组合多个筛选条件
    combined_filter = FilterLayer("combined_filter")
    combined_filter.add_condition(trend_condition, "trend_up", "趋势向上")
    combined_filter.add_condition(rsi_condition, "rsi_normal", "RSI正常")
    combined_filter.add_condition(PrebuiltFilters.volume_above_average(period=20), "volume_active", "成交量活跃")
    
    combined_filtered = combined_filter.apply(data)
    print(f"组合筛选: {len(data)} -> {len(combined_filtered)} 行")


def demo_composite_indicator():
    """
    演示复合指标的使用
    """
    print("\n=== 复合指标演示 ===")
    
    data = create_sample_data(100)
    
    # 创建趋势跟踪复合指标
    print("\n1. 趋势跟踪策略")
    trend_following = CompositeIndicator("trend_following")
    
    # 添加基础指标
    ma_short = MovingAverageModule(period=5)
    ma_long = MovingAverageModule(period=20)
    rsi = RSIModule(period=14)
    
    trend_following.add_indicator(ma_short, "ma5")
    trend_following.add_indicator(ma_long, "ma20")
    trend_following.add_indicator(rsi, "rsi14")
    
    # 定义组合逻辑
    def trend_following_logic(results):
        """趋势跟踪逻辑：短期均线上穿长期均线且RSI不超买"""
        ma5_values = results['ma5'].values
        ma20_values = results['ma20'].values
        rsi_values = results['rsi14'].values
        
        # 计算信号
        signals = pd.Series(0, index=ma5_values.index)  # 0=无信号, 1=买入, -1=卖出
        
        # 有效数据掩码
        valid_mask = ~(pd.isna(ma5_values) | pd.isna(ma20_values) | pd.isna(rsi_values))
        
        # 买入信号：短均线上穿长均线且RSI < 70
        buy_condition = (ma5_values > ma20_values) & (rsi_values < 70)
        signals[valid_mask & buy_condition] = 1
        
        # 卖出信号：短均线下穿长均线或RSI > 80
        sell_condition = (ma5_values < ma20_values) | (rsi_values > 80)
        signals[valid_mask & sell_condition] = -1
        
        return IndicatorResult(
            name="trend_following_signal",
            values=signals,
            indicator_type=IndicatorType.CUSTOM,
            metadata={
                'buy_signals': (signals == 1).sum(),
                'sell_signals': (signals == -1).sum(),
                'total_signals': (signals != 0).sum()
            }
        )
    
    trend_following.set_combination_logic(trend_following_logic)
    
    # 计算复合指标
    trend_result = trend_following.calculate(data)
    print(f"趋势跟踪信号统计:")
    print(f"  买入信号: {trend_result.metadata['buy_signals']} 次")
    print(f"  卖出信号: {trend_result.metadata['sell_signals']} 次")
    print(f"  总信号数: {trend_result.metadata['total_signals']} 次")
    
    # 创建均值回归复合指标
    print("\n2. 均值回归策略")
    mean_reversion = CompositeIndicator("mean_reversion")
    
    # 添加布林带和RSI
    boll = BollingerBandsModule(period=20, std_dev=2)
    rsi_mr = RSIModule(period=14)
    
    mean_reversion.add_indicator(boll, "boll")
    mean_reversion.add_indicator(rsi_mr, "rsi")
    
    def mean_reversion_logic(results):
        """均值回归逻辑：价格触及布林带边界且RSI确认"""
        boll_result = results['boll']
        rsi_values = results['rsi'].values
        
        # 从布林带结果中提取上下轨
        upper_band = boll_result.metadata['upper_band']
        lower_band = boll_result.metadata['lower_band']
        
        signals = pd.Series(0, index=rsi_values.index)
        
        # 有效数据掩码
        valid_mask = ~(pd.isna(upper_band) | pd.isna(lower_band) | pd.isna(rsi_values))
        
        # 买入信号：价格接近下轨且RSI超卖
        price = data['CLOSE']
        buy_condition = (price <= lower_band * 1.02) & (rsi_values < 30)
        signals[valid_mask & buy_condition] = 1
        
        # 卖出信号：价格接近上轨且RSI超买
        sell_condition = (price >= upper_band * 0.98) & (rsi_values > 70)
        signals[valid_mask & sell_condition] = -1
        
        return IndicatorResult(
            name="mean_reversion_signal",
            values=signals,
            indicator_type=IndicatorType.CUSTOM,
            metadata={
                'buy_signals': (signals == 1).sum(),
                'sell_signals': (signals == -1).sum(),
                'total_signals': (signals != 0).sum()
            }
        )
    
    mean_reversion.set_combination_logic(mean_reversion_logic)
    
    # 计算均值回归信号
    mr_result = mean_reversion.calculate(data)
    print(f"均值回归信号统计:")
    print(f"  买入信号: {mr_result.metadata['buy_signals']} 次")
    print(f"  卖出信号: {mr_result.metadata['sell_signals']} 次")
    print(f"  总信号数: {mr_result.metadata['total_signals']} 次")


def demo_layered_filtering():
    """
    演示分层筛选的完整流程
    """
    print("\n=== 分层筛选演示 ===")
    
    data = create_sample_data(200)
    manager = get_indicator_manager()
    
    print(f"原始数据: {len(data)} 行")
    
    # 第一层：基础筛选
    print("\n第一层筛选 - 基础条件:")
    layer1 = FilterLayer("basic_filter")
    
    # 价格和成交量基础条件
    layer1.add_condition(
        lambda df: (df['CLOSE'] > 20) & (df['CLOSE'] < 200),
        "price_range", "价格在合理范围"
    )
    layer1.add_condition(
        lambda df: df['VOLUME'] > df['VOLUME'].rolling(20).mean(),
        "volume_active", "成交量活跃"
    )
    
    filtered_l1 = layer1.apply(data)
    print(f"  筛选结果: {len(data)} -> {len(filtered_l1)} 行 ({len(filtered_l1)/len(data)*100:.1f}%)")
    
    # 第二层：技术指标筛选
    print("\n第二层筛选 - 技术指标:")
    layer2 = FilterLayer("technical_filter")
    
    # 趋势和动量指标
    layer2.add_condition(
        PrebuiltFilters.trend_up(period=10),
        "trend_up", "短期趋势向上"
    )
    layer2.add_condition(
        PrebuiltFilters.rsi_not_overbought(period=14, threshold=75),
        "rsi_normal", "RSI未超买"
    )
    
    filtered_l2 = layer2.apply(filtered_l1)
    print(f"  筛选结果: {len(filtered_l1)} -> {len(filtered_l2)} 行 ({len(filtered_l2)/len(filtered_l1)*100:.1f}%)")
    
    # 第三层：复合指标筛选
    print("\n第三层筛选 - 复合指标:")
    
    if len(filtered_l2) > 30:  # 确保有足够数据进行复合指标计算
        # 创建多重确认买入信号
        multi_confirm = CompositeIndicator("multi_confirm")
        
        # 添加多个指标
        multi_confirm.add_indicator(MovingAverageModule(period=5), "ma5")
        multi_confirm.add_indicator(MovingAverageModule(period=20), "ma20")
        multi_confirm.add_indicator(RSIModule(period=14), "rsi")
        multi_confirm.add_indicator(MACDModule(), "macd")
        
        def multi_confirm_logic(results):
            """多重确认逻辑"""
            ma5 = results['ma5'].values
            ma20 = results['ma20'].values
            rsi = results['rsi'].values
            macd = results['macd'].values
            
            # 多重确认条件
            conditions = [
                ma5 > ma20,  # 短期均线在长期均线之上
                (rsi > 40) & (rsi < 70),  # RSI在合理区间
                macd > 0,  # MACD为正
            ]
            
            # 所有条件都满足
            all_conditions = conditions[0]
            for condition in conditions[1:]:
                all_conditions = all_conditions & condition
            
            signals = pd.Series(False, index=ma5.index)
            valid_mask = ~(pd.isna(ma5) | pd.isna(ma20) | pd.isna(rsi) | pd.isna(macd))
            signals[valid_mask] = all_conditions[valid_mask]
            
            return IndicatorResult(
                name="multi_confirm_signal",
                values=signals,
                indicator_type=IndicatorType.CUSTOM
            )
        
        multi_confirm.set_combination_logic(multi_confirm_logic)
        
        # 计算复合指标
        confirm_result = multi_confirm.calculate(filtered_l2)
        
        # 根据复合指标结果进行最终筛选
        final_signals = confirm_result.values
        filtered_l3 = filtered_l2[final_signals].copy()
        
        print(f"  筛选结果: {len(filtered_l2)} -> {len(filtered_l3)} 行 ({len(filtered_l3)/len(filtered_l2)*100:.1f}%)")
        
        # 最终结果统计
        print("\n=== 分层筛选总结 ===")
        print(f"原始数据: {len(data)} 行")
        print(f"第一层筛选后: {len(filtered_l1)} 行 (保留 {len(filtered_l1)/len(data)*100:.1f}%)")
        print(f"第二层筛选后: {len(filtered_l2)} 行 (保留 {len(filtered_l2)/len(data)*100:.1f}%)")
        print(f"第三层筛选后: {len(filtered_l3)} 行 (保留 {len(filtered_l3)/len(data)*100:.1f}%)")
        
        if len(filtered_l3) > 0:
            print(f"\n最终筛选结果特征:")
            print(f"  价格范围: {filtered_l3['CLOSE'].min():.2f} - {filtered_l3['CLOSE'].max():.2f}")
            print(f"  平均价格: {filtered_l3['CLOSE'].mean():.2f}")
            print(f"  平均成交量: {filtered_l3['VOLUME'].mean():,.0f}")
            
            # 显示最后几个筛选结果
            print(f"\n最后5个筛选结果:")
            for idx, row in filtered_l3.tail().iterrows():
                print(f"  {row['date'].strftime('%Y-%m-%d')}: 收盘价 {row['CLOSE']:.2f}, 成交量 {row['VOLUME']:,}")
    else:
        print(f"  数据不足，跳过第三层筛选 (需要至少30行数据，当前{len(filtered_l2)}行)")


def demo_manager_features():
    """
    演示管理器的高级功能
    """
    print("\n=== 管理器高级功能演示 ===")
    
    manager = get_indicator_manager()
    
    # 显示管理器统计信息
    stats = manager.get_statistics()
    print(f"\n管理器统计信息:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    # 显示可用指标列表
    print(f"\n可用指标列表:")
    available_indicators = manager.get_available_indicators()
    for info in available_indicators:
        print(f"  {info.name} ({info.class_name})")
        print(f"    类型: {info.indicator_type.value}")
        print(f"    描述: {info.description[:50]}..." if len(info.description) > 50 else f"    描述: {info.description}")
        print(f"    参数: {list(info.parameters.keys())}")
        print()
    
    # 演示复合指标创建
    print("通过管理器创建复合指标:")
    
    base_indicators = [
        {"name": "MovingAverageModule", "params": {"period": 10}, "alias": "ma10"},
        {"name": "RSIModule", "params": {"period": 14}, "alias": "rsi14"}
    ]
    
    def simple_combination(results):
        """简单组合逻辑"""
        ma_values = results['ma10'].values
        rsi_values = results['rsi14'].values
        
        # 简单的买入信号：价格在MA之上且RSI不超买
        data = create_sample_data(50)  # 创建小量数据用于演示
        signals = (data['CLOSE'] > ma_values) & (rsi_values < 70)
        
        return IndicatorResult(
            name="simple_signal",
            values=signals,
            indicator_type=IndicatorType.CUSTOM
        )
    
    composite = manager.create_composite_indicator(
        "demo_composite",
        base_indicators,
        simple_combination
    )
    
    print(f"复合指标创建成功: {composite.name}")
    print(f"包含基础指标: {list(composite.indicators.keys())}")


def main():
    """
    主函数 - 运行所有演示
    """
    print("通达信公式解释器 - 模块化指标演示")
    print("=" * 50)
    
    try:
        # 重置管理器确保干净的环境
        reset_indicator_manager()
        
        # 运行各个演示
        demo_basic_indicators()
        demo_filter_layer()
        demo_composite_indicator()
        demo_layered_filtering()
        demo_manager_features()
        
        print("\n=== 演示完成 ===")
        print("\n模块化指标框架提供了以下核心功能:")
        print("1. 基础指标模块化封装 - 统一接口，易于扩展")
        print("2. 灵活的筛选层设计 - 支持多条件组合筛选")
        print("3. 复合指标计算 - 多指标组合生成交易信号")
        print("4. 分层筛选流程 - 逐步精细化数据筛选")
        print("5. 统一的管理接口 - 便于指标注册和使用")
        print("\n通过这些功能，可以构建复杂的量化交易策略和选股系统。")
        
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        reset_indicator_manager()


if __name__ == "__main__":
    main()