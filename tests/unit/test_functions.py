#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
函数库单元测试

测试通达信函数库的各种功能，包括：
- 函数注册和查找
- 参数验证
- 计算结果正确性
- 错误处理
"""

import pytest
import pandas as pd
import numpy as np
from tdx_interpreter.functions.registry import FunctionRegistry
from tdx_interpreter.functions.base import TDXFunction, FunctionCategory, Parameter, ParameterType
from tdx_interpreter.functions.technical import MAFunction, EMAFunction
from tdx_interpreter.functions.mathematical import ABSFunction, SUMFunction
from tdx_interpreter.functions.logical import IFFunction, ANDFunction
from tdx_interpreter.functions.temporal import REFFunction, CROSSFunction
from tdx_interpreter.errors import TDXArgumentError, TDXTypeError, TDXNameError, TDXValueError


class TestFunctionRegistry:
    """函数注册表测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.registry = FunctionRegistry()
    
    def test_register_function(self):
        """测试函数注册"""
        ma_func = MAFunction()
        self.registry.register(ma_func)
        
        assert self.registry.has("MA")
        assert len(self.registry) == 1
        
        retrieved_func = self.registry.get("MA")
        assert retrieved_func.name == "MA"
    
    def test_register_with_aliases(self):
        """测试带别名的函数注册"""
        ma_func = MAFunction()
        self.registry.register(ma_func, aliases=["AVERAGE", "AVG"])
        
        assert self.registry.has("MA")
        assert self.registry.has("AVERAGE")
        assert self.registry.has("AVG")
        
        # 所有别名应该返回同一个函数
        func1 = self.registry.get("MA")
        func2 = self.registry.get("AVERAGE")
        func3 = self.registry.get("AVG")
        
        assert func1 is func2 is func3
    
    def test_duplicate_registration_error(self):
        """测试重复注册错误"""
        ma_func1 = MAFunction()
        ma_func2 = MAFunction()
        
        self.registry.register(ma_func1)
        
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(ma_func2)
    
    def test_function_not_found_error(self):
        """测试函数未找到错误"""
        with pytest.raises(TDXNameError, match="not defined"):
            self.registry.get("NONEXISTENT")
    
    def test_list_functions(self):
        """测试函数列表"""
        ma_func = MAFunction()
        abs_func = ABSFunction()
        
        self.registry.register(ma_func)
        self.registry.register(abs_func)
        
        functions = self.registry.list_functions()
        assert "MA" in functions
        assert "ABS" in functions
        assert len(functions) == 2
    
    def test_list_functions_by_category(self):
        """测试按分类列出函数"""
        ma_func = MAFunction()
        abs_func = ABSFunction()
        
        self.registry.register(ma_func)
        self.registry.register(abs_func)
        
        technical_functions = self.registry.list_functions(FunctionCategory.TECHNICAL)
        mathematical_functions = self.registry.list_functions(FunctionCategory.MATHEMATICAL)
        
        assert "MA" in technical_functions
        assert "ABS" in mathematical_functions
        assert len(technical_functions) == 1
        assert len(mathematical_functions) == 1
    
    def test_search_functions(self):
        """测试函数搜索"""
        ma_func = MAFunction()
        ema_func = EMAFunction()
        
        self.registry.register(ma_func)
        self.registry.register(ema_func)
        
        # 搜索包含"MA"的函数
        results = self.registry.search_functions("MA")
        assert len(results) == 2  # MA和EMA都包含"MA"
    
    def test_function_call(self):
        """测试函数调用"""
        abs_func = ABSFunction()
        self.registry.register(abs_func)
        
        result = self.registry.call("ABS", -5)
        assert result == 5
    
    def test_get_statistics(self):
        """测试统计信息"""
        ma_func = MAFunction()
        abs_func = ABSFunction()
        
        self.registry.register(ma_func, aliases=["AVG"])
        self.registry.register(abs_func)
        
        stats = self.registry.get_statistics()
        assert stats['total_functions'] == 2
        assert stats['total_aliases'] == 1
        assert stats['categories'] == 2


class TestTechnicalFunctions:
    """技术指标函数测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建测试数据
        self.data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.high = pd.Series([2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        self.low = pd.Series([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5])
        self.close = self.data
    
    def test_ma_function(self):
        """测试MA函数"""
        ma_func = MAFunction()
        
        result = ma_func(self.data, 3)
        
        # 验证结果类型和长度
        assert isinstance(result, pd.Series)
        assert len(result) == len(self.data)
        
        # 验证计算结果
        expected = self.data.rolling(window=3, min_periods=1).mean()
        pd.testing.assert_series_equal(result, expected)
    
    def test_ema_function(self):
        """测试EMA函数"""
        ema_func = EMAFunction()
        
        result = ema_func(self.data, 3)
        
        # 验证结果类型和长度
        assert isinstance(result, pd.Series)
        assert len(result) == len(self.data)
        
        # EMA的第一个值应该等于原始数据的第一个值
        assert result.iloc[0] == self.data.iloc[0]
    
    def test_rsi_function(self):
        """测试RSI函数"""
        from tdx_interpreter.functions.technical import RSIFunction
        
        rsi_func = RSIFunction()
        
        # 创建有涨跌的数据
        price_data = pd.Series([100, 102, 101, 103, 102, 104, 103, 105, 104, 106])
        result = rsi_func(price_data, 5)
        
        # 验证结果类型和范围
        assert isinstance(result, pd.Series)
        assert len(result) == len(price_data)
        
        # RSI值应该在0-100之间
        valid_values = result.dropna()
        assert all(0 <= val <= 100 for val in valid_values)


class TestMathematicalFunctions:
    """数学函数测试类"""
    
    def test_abs_function(self):
        """测试ABS函数"""
        abs_func = ABSFunction()
        
        # 测试单个数值
        assert abs_func(-5) == 5
        assert abs_func(3) == 3
        assert abs_func(0) == 0
        
        # 测试序列
        data = pd.Series([-3, -1, 0, 2, 4])
        result = abs_func(data)
        expected = pd.Series([3, 1, 0, 2, 4])
        pd.testing.assert_series_equal(result, expected)
    
    def test_sum_function(self):
        """测试SUM函数"""
        sum_func = SUMFunction()
        
        data = pd.Series([1, 2, 3, 4, 5])
        result = sum_func(data, 3)
        
        # 验证滚动求和
        expected = data.rolling(window=3, min_periods=1).sum()
        pd.testing.assert_series_equal(result, expected)
    
    def test_max_min_functions(self):
        """测试MAX和MIN函数"""
        from tdx_interpreter.functions.mathematical import MAXFunction, MINFunction
        
        max_func = MAXFunction()
        min_func = MINFunction()
        
        # 测试数值
        assert max_func(3, 5) == 5
        assert min_func(3, 5) == 3
        
        # 测试序列
        data1 = pd.Series([1, 3, 5])
        data2 = pd.Series([2, 2, 4])
        
        max_result = max_func(data1, data2)
        min_result = min_func(data1, data2)
        
        expected_max = pd.Series([2, 3, 5])
        expected_min = pd.Series([1, 2, 4])
        
        pd.testing.assert_series_equal(max_result, expected_max)
        pd.testing.assert_series_equal(min_result, expected_min)


class TestLogicalFunctions:
    """逻辑函数测试类"""
    
    def test_if_function(self):
        """测试IF函数"""
        if_func = IFFunction()
        
        # 测试单个值
        assert if_func(True, 1, 0) == 1
        assert if_func(False, 1, 0) == 0
        
        # 测试序列
        condition = pd.Series([True, False, True, False])
        result = if_func(condition, 1, 0)
        expected = pd.Series([1, 0, 1, 0])
        
        pd.testing.assert_series_equal(pd.Series(result), expected)
    
    def test_and_or_functions(self):
        """测试AND和OR函数"""
        and_func = ANDFunction()
        from tdx_interpreter.functions.logical import ORFunction
        or_func = ORFunction()
        
        # 测试布尔值
        assert and_func(True, True) == True
        assert and_func(True, False) == False
        assert or_func(True, False) == True
        assert or_func(False, False) == False
        
        # 测试序列
        cond1 = pd.Series([True, True, False, False])
        cond2 = pd.Series([True, False, True, False])
        
        and_result = and_func(cond1, cond2)
        or_result = or_func(cond1, cond2)
        
        expected_and = pd.Series([True, False, False, False])
        expected_or = pd.Series([True, True, True, False])
        
        pd.testing.assert_series_equal(and_result, expected_and)
        pd.testing.assert_series_equal(or_result, expected_or)


class TestTemporalFunctions:
    """时序函数测试类"""
    
    def test_ref_function(self):
        """测试REF函数"""
        ref_func = REFFunction()
        
        data = pd.Series([1, 2, 3, 4, 5])
        result = ref_func(data, 1)
        
        # 验证引用结果
        expected = pd.Series([np.nan, 1, 2, 3, 4])
        pd.testing.assert_series_equal(result, expected)
    
    def test_cross_function(self):
        """测试CROSS函数"""
        cross_func = CROSSFunction()
        
        # 创建交叉数据
        data1 = pd.Series([1, 2, 3, 2, 3, 4])
        data2 = pd.Series([2, 2, 2, 2, 2, 2])
        
        result = cross_func(data1, data2)
        
        # 验证交叉点
        assert isinstance(result, pd.Series)
        assert len(result) == len(data1)
        
        # 第3个位置应该是交叉点（data1从2上升到3，超过data2的2）
        # 第5个位置也应该是交叉点（data1从2上升到3，再次超过data2的2）
        assert result.iloc[2] == True  # 3 > 2 且前一个值 2 <= 2
        assert result.iloc[4] == True  # 3 > 2 且前一个值 2 <= 2


class TestParameterValidation:
    """参数验证测试类"""
    
    def test_parameter_type_validation(self):
        """测试参数类型验证"""
        ma_func = MAFunction()
        
        # 正确的参数类型
        data = pd.Series([1, 2, 3, 4, 5])
        result = ma_func(data, 3)
        assert isinstance(result, pd.Series)
        
        # 错误的参数类型
        with pytest.raises(TDXTypeError):
            ma_func("invalid_data", 3)
        
        with pytest.raises(TDXTypeError):
            ma_func(data, "invalid_period")
    
    def test_parameter_range_validation(self):
        """测试参数范围验证"""
        ma_func = MAFunction()
        data = pd.Series([1, 2, 3, 4, 5])
        
        # 有效范围
        result = ma_func(data, 1)
        assert isinstance(result, pd.Series)
        
        # 无效范围
        with pytest.raises(TDXValueError):
            ma_func(data, 0)  # period必须 >= 1
        
        with pytest.raises(TDXValueError):
            ma_func(data, -1)  # period必须 >= 1
    
    def test_argument_count_validation(self):
        """测试参数数量验证"""
        ma_func = MAFunction()
        data = pd.Series([1, 2, 3, 4, 5])
        
        # 正确的参数数量
        result = ma_func(data, 3)
        assert isinstance(result, pd.Series)
        
        # 参数过少
        with pytest.raises(TDXArgumentError, match="requires at least"):
            ma_func(data)  # 缺少period参数
        
        # 参数过多
        with pytest.raises(TDXArgumentError, match="accepts at most"):
            ma_func(data, 3, 5, 7)  # 多余的参数


class TestFunctionHelp:
    """函数帮助信息测试类"""
    
    def test_function_signature(self):
        """测试函数签名"""
        ma_func = MAFunction()
        signature = ma_func.get_signature()
        
        assert "MA(" in signature
        assert "data" in signature
        assert "period" in signature
    
    def test_function_help(self):
        """测试函数帮助信息"""
        ma_func = MAFunction()
        help_text = ma_func.get_help()
        
        assert "Function: MA" in help_text
        assert "Category: TECHNICAL" in help_text
        assert "Description:" in help_text
        assert "Parameters:" in help_text
    
    def test_registry_help(self):
        """测试注册表帮助信息"""
        registry = FunctionRegistry()
        ma_func = MAFunction()
        registry.register(ma_func)
        
        help_text = registry.get_function_help("MA")
        assert "Function: MA" in help_text