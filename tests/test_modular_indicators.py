#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化指标测试

测试模块化指标计算框架的各个组件功能。
"""

import unittest
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

from tdx_interpreter.indicators import (
    BaseIndicatorModule, IndicatorResult, IndicatorType,
    FilterLayer, FilterCondition, FilterOperator, PrebuiltFilters,
    CompositeIndicator, SignalType, Signal,
    IndicatorManager, get_indicator_manager, reset_indicator_manager,
    MovingAverageModule, RSIModule, MACDModule
)


class TestModularIndicators(unittest.TestCase):
    """
    模块化指标测试类
    """
    
    def setUp(self):
        """
        测试前准备
        """
        # 重置全局管理器
        reset_indicator_manager()
        
        # 创建测试数据
        self.test_data = self._create_test_data()
    
    def _create_test_data(self, days: int = 100) -> pd.DataFrame:
        """
        创建测试K线数据
        
        Args:
            days: 数据天数
            
        Returns:
            pd.DataFrame: K线数据
        """
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # 生成模拟价格数据
        np.random.seed(42)
        base_price = 100.0
        price_changes = np.random.normal(0, 0.02, days)
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1.0))  # 确保价格为正
        
        # 生成OHLC数据
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = low + (high - low) * np.random.random()
            volume = np.random.randint(1000000, 10000000)
            
            data.append({
                'date': date,
                'OPEN': open_price,
                'HIGH': high,
                'LOW': low,
                'CLOSE': close,
                'VOLUME': volume
            })
        
        return pd.DataFrame(data)
    
    def test_base_indicator_module(self):
        """
        测试基础指标模块
        """
        # 测试MovingAverageModule
        ma_module = MovingAverageModule(period=5)
        
        self.assertEqual(ma_module.name, "SMA5")
        self.assertEqual(ma_module.indicator_type, IndicatorType.TREND)
        self.assertEqual(ma_module.parameters['period'], 5)
        
        # 测试计算
        result = ma_module.calculate(self.test_data)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, "SMA5")
        self.assertIsInstance(result.data, pd.Series)
        self.assertEqual(len(result.data), len(self.test_data))
        
        # 验证前几个值为NaN（因为周期不足）
        self.assertTrue(pd.isna(result.data.iloc[0]))
        self.assertTrue(pd.isna(result.data.iloc[3]))
        self.assertFalse(pd.isna(result.data.iloc[4]))  # 第5个值应该有效
    
    def test_rsi_module(self):
        """
        测试RSI指标模块
        """
        rsi_module = RSIModule(period=14)
        
        self.assertEqual(rsi_module.name, "RSI")
        self.assertEqual(rsi_module.indicator_type, IndicatorType.OSCILLATOR)
        
        result = rsi_module.calculate(self.test_data)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, "RSI")
        
        # RSI值应该在0-100之间
        valid_values = result.data.dropna()
        self.assertTrue(all(valid_values >= 0))
        self.assertTrue(all(valid_values <= 100))
    
    def test_macd_module(self):
        """
        测试MACD指标模块
        """
        macd_module = MACDModule(fast_period=12, slow_period=26, signal_period=9)
        
        self.assertEqual(macd_module.name, "MACD")
        self.assertEqual(macd_module.indicator_type, IndicatorType.MOMENTUM)
        
        result = macd_module.calculate(self.test_data)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, "MACD")
        
        # MACD应该返回多个序列
        self.assertIn('macd', result.metadata)
        self.assertIn('signal', result.metadata)
        self.assertIn('histogram', result.metadata)
    
    def test_filter_layer(self):
        """
        测试筛选层
        """
        # 创建筛选层
        filter_layer = FilterLayer("test_filter")
        
        # 添加筛选条件
        def price_above_100(data, indicators):
            return data['CLOSE'] > 100
        
        def volume_above_average(data, indicators):
            avg_volume = data['VOLUME'].mean()
            return data['VOLUME'] > avg_volume
        
        filter_layer.add_condition(price_above_100, "price_filter", "价格大于100")
        filter_layer.add_condition(volume_above_average, "volume_filter", "成交量大于平均值")
        
        # 测试筛选
        filtered_data = filter_layer.apply(self.test_data, {})
        
        self.assertIsInstance(filtered_data, pd.DataFrame)
        self.assertLessEqual(len(filtered_data), len(self.test_data))
        
        # 验证筛选结果
        if len(filtered_data) > 0:
            self.assertTrue((filtered_data['CLOSE'] > 100).all())
    
    def test_trend_following_strategy(self):
        """
        测试趋势跟踪策略
        """
        from tdx_interpreter.indicators.composite import TrendFollowingStrategy
        
        # 创建趋势跟踪策略
        strategy = TrendFollowingStrategy(
            ma_short_period=5,
            ma_long_period=10,
            rsi_period=14
        )
        
        # 计算策略结果
        result = strategy.calculate(self.test_data)
        
        # 验证结果
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, "TrendFollowingStrategy")
        self.assertIsInstance(result.data, pd.DataFrame)
        
        # 验证包含的指标
        self.assertIn('base_indicators', result.parameters)
        expected_indicators = ['MA_SHORT', 'MA_LONG', 'RSI']
        self.assertEqual(result.parameters['base_indicators'], expected_indicators)
        
        # 验证信号生成
        signals = strategy.get_signals()
        self.assertIsInstance(signals, list)
        
        # 如果有信号，验证信号属性
        if signals:
            signal = signals[0]
            self.assertIn(signal.signal_type.value, ['buy', 'sell', 'hold', 'neutral'])
            self.assertGreaterEqual(signal.strength, 0.0)
            self.assertLessEqual(signal.strength, 1.0)
            self.assertGreaterEqual(signal.confidence, 0.0)
            self.assertLessEqual(signal.confidence, 1.0)
    
    def test_prebuilt_filters(self):
        """
        测试预构建筛选条件
        """
        # 创建模拟指标结果
        ma5_result = IndicatorResult(
            name="MA5",
            data=pd.Series([100, 101, 102, 103, 104] * 20, index=self.test_data.index),
            parameters={"period": 5},
            timestamp=time.time(),
            dependencies=["CLOSE"],
            cache_key="MA5_test"
        )
        ma20_result = IndicatorResult(
            name="MA20", 
            data=pd.Series([99, 100, 101, 102, 103] * 20, index=self.test_data.index),
            parameters={"period": 20},
            timestamp=time.time(),
            dependencies=["CLOSE"],
            cache_key="MA20_test"
        )
        rsi_result = IndicatorResult(
            name="RSI",
            data=pd.Series([50, 60, 65, 55, 45] * 20, index=self.test_data.index),
            parameters={"period": 14},
            timestamp=time.time(),
            dependencies=["CLOSE"],
            cache_key="RSI_test"
        )
        vol_ma_result = IndicatorResult(
            name="VOL_MA",
            data=pd.Series([1000, 1100, 1200, 1300, 1400] * 20, index=self.test_data.index),
            parameters={"period": 20},
            timestamp=time.time(),
            dependencies=["VOLUME"],
            cache_key="VOL_MA_test"
        )
        
        indicators = {
            "MA5": ma5_result,
            "MA20": ma20_result,
            "RSI": rsi_result,
            "VOL_MA": vol_ma_result
        }
        
        # 测试趋势向上筛选
        trend_filter = PrebuiltFilters.trend_up(ma_short="MA5", ma_long="MA20")
        result = trend_filter(self.test_data, indicators)
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(self.test_data))
        
        # 测试RSI非超买筛选
        rsi_filter = PrebuiltFilters.rsi_not_overbought(rsi_name="RSI", threshold=70)
        result = rsi_filter(self.test_data, indicators)
        self.assertIsInstance(result, pd.Series)
        
        # 测试成交量筛选
        volume_filter = PrebuiltFilters.volume_above_average(volume_ma_name="VOL_MA", multiplier=1.2)
        result = volume_filter(self.test_data, indicators)
        self.assertIsInstance(result, pd.Series)
    
    def test_composite_indicator(self):
        """
        测试复合指标
        """
        # 创建复合指标
        composite = CompositeIndicator("trend_momentum")
        
        # 添加基础指标
        ma_module = MovingAverageModule(period=20)
        rsi_module = RSIModule(period=14)
        
        composite.add_indicator(ma_module, "ma20")
        composite.add_indicator(rsi_module, "rsi14")
        
        # 设置组合逻辑
        def combination_logic(data, results):
            # 处理不同的数据类型
            ma_result = results['ma20'].data
            rsi_result = results['rsi14'].data
            
            # 如果是DataFrame，取第一列；如果是Series，直接使用
            if isinstance(ma_result, pd.DataFrame):
                ma_values = ma_result.iloc[:, 0]
            else:
                ma_values = ma_result
                
            if isinstance(rsi_result, pd.DataFrame):
                rsi_values = rsi_result.iloc[:, 0]
            else:
                rsi_values = rsi_result
            
            # 简单的组合：价格在MA之上且RSI不超买
            signals = pd.Series(False, index=data.index)
            
            valid_mask = ~(pd.isna(ma_values) | pd.isna(rsi_values))
            price_above_ma = data['CLOSE'] > ma_values
            rsi_not_overbought = rsi_values < 70
            
            signals[valid_mask] = (price_above_ma & rsi_not_overbought)[valid_mask]
            
            return signals
        
        composite.set_combination_logic(combination_logic)
        
        # 计算复合指标
        result = composite.calculate(self.test_data)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, "trend_momentum")
        self.assertIsInstance(result.data, pd.Series)
    
    def test_indicator_manager(self):
        """
        测试指标管理器
        """
        manager = get_indicator_manager()
        
        # 测试管理器基本功能
        self.assertIsInstance(manager, IndicatorManager)
        self.assertGreater(len(manager), 0)  # 应该有内置指标
        
        # 测试获取可用指标
        available_indicators = manager.get_available_indicators()
        self.assertGreater(len(available_indicators), 0)
        
        # 测试创建指标实例
        ma_instance = manager.create_indicator("MovingAverageModule", "ma5", period=5)
        self.assertIsInstance(ma_instance, MovingAverageModule)
        
        # 测试计算指标
        result = manager.calculate_indicator("MovingAverageModule", self.test_data, period=10)
        self.assertIsInstance(result, IndicatorResult)
        
        # 测试批量计算
        indicators_config = {
            "ma5": {"name": "MovingAverageModule", "params": {"period": 5}},
            "rsi14": {"name": "RSIModule", "params": {"period": 14}}
        }
        
        batch_results = manager.batch_calculate(indicators_config, self.test_data)
        self.assertEqual(len(batch_results), 2)
        self.assertIn("ma5", batch_results)
        self.assertIn("rsi14", batch_results)
        
        # 测试统计信息
        stats = manager.get_statistics()
        self.assertIn('total_indicators', stats)
        self.assertIn('active_instances', stats)
        self.assertGreater(stats['total_indicators'], 0)
    
    def test_indicator_caching(self):
        """
        测试指标缓存功能
        """
        ma_module = MovingAverageModule(period=5)
        
        # 第一次计算
        result1 = ma_module.calculate(self.test_data)
        
        # 第二次计算（应该使用缓存）
        result2 = ma_module.calculate(self.test_data)
        
        # 验证结果相同
        pd.testing.assert_series_equal(result1.values, result2.values)
        
        # 清除缓存后重新计算
        ma_module.clear_cache()
        result3 = ma_module.calculate(self.test_data)
        
        # 结果应该仍然相同
        pd.testing.assert_series_equal(result1.values, result3.values)
    
    def test_parameter_validation(self):
        """
        测试参数验证
        """
        # 测试无效参数
        with self.assertRaises(ValueError):
            MovingAverageModule(period=0)  # 周期不能为0
        
        with self.assertRaises(ValueError):
            RSIModule(period=-1)  # 周期不能为负数
        
        # 测试参数类型检查
        with self.assertRaises(TypeError):
            MovingAverageModule(period="invalid")  # 周期必须是数字
    
    def test_data_validation(self):
        """
        测试数据验证
        """
        ma_module = MovingAverageModule(period=5)
        
        # 测试空数据
        empty_data = pd.DataFrame()
        with self.assertRaises(ValueError):
            ma_module.calculate(empty_data)
        
        # 测试缺少必要列的数据
        invalid_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        with self.assertRaises(ValueError):
            ma_module.calculate(invalid_data)
        
        # 测试数据长度不足
        short_data = self.test_data.head(2)  # 只有2行数据，但MA需要5个周期
        result = ma_module.calculate(short_data)
        self.assertTrue(result.values.isna().all())  # 所有值都应该是NaN
    
    def test_error_handling(self):
        """
        测试错误处理
        """
        manager = get_indicator_manager()
        
        # 测试不存在的指标
        with self.assertRaises(ValueError):
            manager.create_indicator("NonExistentIndicator")
        
        # 测试无效的指标参数
        with self.assertRaises(RuntimeError):
            manager.create_indicator("MovingAverageModule", period="invalid")
    
    def tearDown(self):
        """
        测试后清理
        """
        # 重置全局管理器
        reset_indicator_manager()


if __name__ == '__main__':
    unittest.main()