#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件加载功能
"""

import os
import tempfile
import unittest
import pandas as pd
import numpy as np

from tdx_interpreter.core.interpreter import TDXInterpreter
from tdx_interpreter.errors.exceptions import TDXError


class TestFileLoading(unittest.TestCase):
    """测试文件加载功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.interpreter = TDXInterpreter()
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'OPEN': [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.0, 11.8, 12.0, 11.5],
            'HIGH': [10.8, 11.2, 11.5, 11.0, 11.8, 12.0, 11.5, 12.2, 12.5, 12.0],
            'LOW': [9.8, 10.2, 10.5, 10.5, 10.9, 11.2, 10.8, 11.5, 11.8, 11.2],
            'CLOSE': [10.5, 11.0, 10.8, 11.2, 11.5, 11.8, 11.2, 12.0, 12.2, 11.8],
            'VOLUME': [1000, 1200, 800, 1500, 900, 1100, 1300, 1000, 1400, 1200]
        })
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_file(self, content: str, filename: str = 'test.txt', encoding: str = 'utf-8') -> str:
        """创建临时文件"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return file_path
    
    def test_load_simple_formula(self):
        """测试加载简单公式"""
        # 创建简单公式文件
        formula_content = "MA(CLOSE, 5)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试加载
        loaded_formula = self.interpreter.load_from_file(file_path)
        self.assertEqual(loaded_formula, formula_content)
    
    def test_load_complex_formula(self):
        """测试加载复杂公式"""
        # 创建复杂公式文件
        formula_content = """MA5 := MA(CLOSE, 5);
MA20 := MA(CLOSE, 20);
IF(MA5 > MA20, 1, 0)"""
        file_path = self.create_temp_file(formula_content)
        
        # 测试加载
        loaded_formula = self.interpreter.load_from_file(file_path)
        self.assertEqual(loaded_formula, formula_content)
    
    def test_load_formula_with_comments(self):
        """测试加载带注释的公式"""
        # 创建带注释的公式文件
        formula_content = """# 这是注释
RSI(CLOSE, 14)"""
        file_path = self.create_temp_file(formula_content)
        
        # 测试加载
        loaded_formula = self.interpreter.load_from_file(file_path)
        self.assertEqual(loaded_formula, formula_content)
    
    def test_evaluate_file_simple(self):
        """测试直接从文件计算简单公式"""
        # 创建MA公式文件
        formula_content = "MA(CLOSE, 5)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试计算
        result = self.interpreter.evaluate_file(file_path, self.test_data)
        
        # 验证结果
        self.assertIsInstance(result, (pd.Series, np.ndarray, list))
        
        # 与直接计算结果比较
        direct_result = self.interpreter.evaluate(formula_content, self.test_data)
        np.testing.assert_array_equal(result, direct_result)
    
    def test_evaluate_file_complex(self):
        """测试直接从文件计算复杂公式"""
        # 创建条件判断公式文件
        formula_content = "IF(CLOSE > OPEN, 1, 0)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试计算
        result = self.interpreter.evaluate_file(file_path, self.test_data)
        
        # 验证结果（可能是数组或单个值）
        self.assertIsInstance(result, (pd.Series, np.ndarray, list, int, float))
        
        # 与直接计算结果比较
        direct_result = self.interpreter.evaluate(formula_content, self.test_data)
        if hasattr(result, '__len__') and hasattr(direct_result, '__len__'):
            np.testing.assert_array_equal(result, direct_result)
        else:
            self.assertEqual(result, direct_result)
    
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        non_existent_file = os.path.join(self.temp_dir, 'nonexistent.txt')
        
        with self.assertRaises(TDXError) as cm:
            self.interpreter.load_from_file(non_existent_file)
        
        self.assertIn("文件不存在", str(cm.exception))
    
    def test_invalid_file_format(self):
        """测试无效文件格式"""
        # 创建非txt文件
        csv_file = self.create_temp_file("MA(CLOSE, 5)", "test.csv")
        
        with self.assertRaises(TDXError) as cm:
            self.interpreter.load_from_file(csv_file)
        
        self.assertIn("不支持的文件格式", str(cm.exception))
    
    def test_empty_file(self):
        """测试空文件"""
        # 创建空文件
        empty_file = self.create_temp_file("")
        
        with self.assertRaises(TDXError) as cm:
            self.interpreter.load_from_file(empty_file)
        
        self.assertIn("文件内容为空", str(cm.exception))
    
    def test_whitespace_only_file(self):
        """测试只有空白字符的文件"""
        # 创建只有空白字符的文件
        whitespace_file = self.create_temp_file("   \n\t  \n  ")
        
        with self.assertRaises(TDXError) as cm:
            self.interpreter.load_from_file(whitespace_file)
        
        self.assertIn("文件内容为空", str(cm.exception))
    
    def test_different_encodings(self):
        """测试不同编码格式"""
        # 测试UTF-8编码（默认）
        formula_content = "MA(CLOSE, 5)"
        utf8_file = self.create_temp_file(formula_content, "utf8.txt", "utf-8")
        
        loaded_formula = self.interpreter.load_from_file(utf8_file)
        self.assertEqual(loaded_formula, formula_content)
        
        # 测试GBK编码
        try:
            gbk_file = self.create_temp_file(formula_content, "gbk.txt", "gbk")
            loaded_formula = self.interpreter.load_from_file(gbk_file, encoding="gbk")
            self.assertEqual(loaded_formula, formula_content)
        except UnicodeEncodeError:
            # 如果系统不支持GBK编码，跳过此测试
            self.skipTest("系统不支持GBK编码")
    
    def test_encoding_error(self):
        """测试编码错误"""
        # 创建GBK编码的文件，但用UTF-8读取
        try:
            formula_content = "移动平均线MA(CLOSE, 5)"  # 包含中文
            gbk_file = self.create_temp_file(formula_content, "gbk.txt", "gbk")
            
            with self.assertRaises(TDXError) as cm:
                self.interpreter.load_from_file(gbk_file, encoding="utf-8")
            
            self.assertIn("文件编码错误", str(cm.exception))
        except UnicodeEncodeError:
            # 如果系统不支持GBK编码，跳过此测试
            self.skipTest("系统不支持GBK编码")
    
    def test_debug_mode(self):
        """测试调试模式"""
        # 启用调试模式
        self.interpreter.set_debug_mode(True)
        
        formula_content = "MA(CLOSE, 5)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试加载（应该有调试输出，但我们只验证功能正常）
        loaded_formula = self.interpreter.load_from_file(file_path)
        self.assertEqual(loaded_formula, formula_content)
        
        # 关闭调试模式
        self.interpreter.set_debug_mode(False)
    
    def test_evaluate_file_with_kwargs(self):
        """测试带额外参数的文件计算"""
        formula_content = "MA(CLOSE, 5)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试带额外参数的计算
        result = self.interpreter.evaluate_file(file_path, self.test_data, some_param="test")
        
        # 验证结果
        self.assertIsInstance(result, (pd.Series, np.ndarray, list))
    
    def test_file_path_normalization(self):
        """测试文件路径规范化"""
        formula_content = "MA(CLOSE, 5)"
        file_path = self.create_temp_file(formula_content)
        
        # 测试不同的路径表示方式
        normalized_path = os.path.normpath(file_path)
        loaded_formula = self.interpreter.load_from_file(normalized_path)
        self.assertEqual(loaded_formula, formula_content)


if __name__ == '__main__':
    unittest.main()