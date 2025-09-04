#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法解析器单元测试

测试TDXParser的各种功能，包括：
- 表达式解析
- 函数调用解析
- 条件语句解析
- 赋值语句解析
- 运算符优先级
- 错误处理
"""

import pytest
from tdx_interpreter.lexer import TDXLexer
from tdx_interpreter.parser import TDXParser
from tdx_interpreter.core.ast_nodes import (
    NumberLiteral, StringLiteral, Identifier,
    BinaryOperation, UnaryOperation, FunctionCall,
    Assignment, ConditionalExpression, ArrayAccess,
    Program
)
from tdx_interpreter.errors import TDXSyntaxError


class TestTDXParser:
    """TDXParser测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.lexer = TDXLexer()
        self.parser = TDXParser()
    
    def _parse_expression(self, formula: str):
        """辅助方法：解析单个表达式"""
        tokens = self.lexer.tokenize(formula)
        ast = self.parser.parse(tokens)
        assert len(ast.body) == 1
        return ast.body[0]
    
    def test_number_literal(self):
        """测试数值字面量解析"""
        # 整数
        node = self._parse_expression("123")
        assert isinstance(node, NumberLiteral)
        assert node.value == 123
        
        # 浮点数
        node = self._parse_expression("3.14")
        assert isinstance(node, NumberLiteral)
        assert node.value == 3.14
    
    def test_string_literal(self):
        """测试字符串字面量解析"""
        node = self._parse_expression('"hello"')
        assert isinstance(node, StringLiteral)
        assert node.value == "hello"
    
    def test_identifier(self):
        """测试标识符解析"""
        node = self._parse_expression("CLOSE")
        assert isinstance(node, Identifier)
        assert node.name == "CLOSE"
    
    def test_binary_operations(self):
        """测试二元运算解析"""
        # 算术运算
        node = self._parse_expression("1 + 2")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "+"
        assert isinstance(node.left, NumberLiteral)
        assert node.left.value == 1
        assert isinstance(node.right, NumberLiteral)
        assert node.right.value == 2
        
        # 比较运算
        node = self._parse_expression("CLOSE > OPEN")
        assert isinstance(node, BinaryOperation)
        assert node.operator == ">"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "CLOSE"
        assert isinstance(node.right, Identifier)
        assert node.right.name == "OPEN"
        
        # 逻辑运算
        node = self._parse_expression("A AND B")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "AND"
    
    def test_unary_operations(self):
        """测试一元运算解析"""
        # 负号
        node = self._parse_expression("-123")
        assert isinstance(node, UnaryOperation)
        assert node.operator == "-"
        assert isinstance(node.operand, NumberLiteral)
        assert node.operand.value == 123
        
        # NOT运算
        node = self._parse_expression("NOT condition")
        assert isinstance(node, UnaryOperation)
        assert node.operator == "NOT"
        assert isinstance(node.operand, Identifier)
        assert node.operand.name == "CONDITION"
    
    def test_function_call(self):
        """测试函数调用解析"""
        # 无参数函数
        node = self._parse_expression("NOW()")
        assert isinstance(node, FunctionCall)
        assert node.name == "NOW"
        assert len(node.arguments) == 0
        
        # 单参数函数
        node = self._parse_expression("ABS(x)")
        assert isinstance(node, FunctionCall)
        assert node.name == "ABS"
        assert len(node.arguments) == 1
        assert isinstance(node.arguments[0], Identifier)
        assert node.arguments[0].name == "X"
        
        # 多参数函数
        node = self._parse_expression("MA(CLOSE, 5)")
        assert isinstance(node, FunctionCall)
        assert node.name == "MA"
        assert len(node.arguments) == 2
        assert isinstance(node.arguments[0], Identifier)
        assert node.arguments[0].name == "CLOSE"
        assert isinstance(node.arguments[1], NumberLiteral)
        assert node.arguments[1].value == 5
    
    def test_nested_function_calls(self):
        """测试嵌套函数调用"""
        node = self._parse_expression("MA(ABS(CLOSE), 5)")
        assert isinstance(node, FunctionCall)
        assert node.name == "MA"
        assert len(node.arguments) == 2
        
        # 第一个参数是函数调用
        first_arg = node.arguments[0]
        assert isinstance(first_arg, FunctionCall)
        assert first_arg.name == "ABS"
        assert len(first_arg.arguments) == 1
        assert isinstance(first_arg.arguments[0], Identifier)
        assert first_arg.arguments[0].name == "CLOSE"
    
    def test_conditional_expression(self):
        """测试条件表达式解析"""
        node = self._parse_expression("IF(CLOSE > OPEN, 1, 0)")
        assert isinstance(node, ConditionalExpression)
        
        # 条件部分
        assert isinstance(node.condition, BinaryOperation)
        assert node.condition.operator == ">"
        
        # 真值部分
        assert isinstance(node.true_value, NumberLiteral)
        assert node.true_value.value == 1
        
        # 假值部分
        assert isinstance(node.false_value, NumberLiteral)
        assert node.false_value.value == 0
    
    def test_array_access(self):
        """测试数组访问解析"""
        node = self._parse_expression("CLOSE[1]")
        assert isinstance(node, ArrayAccess)
        assert isinstance(node.array, Identifier)
        assert node.array.name == "CLOSE"
        assert isinstance(node.index, NumberLiteral)
        assert node.index.value == 1
        
        # 负索引
        node = self._parse_expression("HIGH[-1]")
        assert isinstance(node, ArrayAccess)
        assert isinstance(node.index, UnaryOperation)
        assert node.index.operator == "-"
    
    def test_assignment(self):
        """测试赋值语句解析"""
        tokens = self.lexer.tokenize("MA5 := MA(CLOSE, 5)")
        ast = self.parser.parse(tokens)
        assert len(ast.body) == 1
        
        node = ast.body[0]
        assert isinstance(node, Assignment)
        assert node.name == "MA5"
        assert isinstance(node.value, FunctionCall)
        assert node.value.name == "MA"
    
    def test_operator_precedence(self):
        """测试运算符优先级"""
        # 乘法优先于加法
        node = self._parse_expression("1 + 2 * 3")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "+"
        assert isinstance(node.left, NumberLiteral)
        assert node.left.value == 1
        assert isinstance(node.right, BinaryOperation)
        assert node.right.operator == "*"
        
        # 括号改变优先级
        node = self._parse_expression("(1 + 2) * 3")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "*"
        assert isinstance(node.left, BinaryOperation)
        assert node.left.operator == "+"
        assert isinstance(node.right, NumberLiteral)
        assert node.right.value == 3
    
    def test_right_associativity(self):
        """测试右结合运算符"""
        # 幂运算是右结合的
        node = self._parse_expression("2 ^ 3 ^ 4")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "^"
        assert isinstance(node.left, NumberLiteral)
        assert node.left.value == 2
        assert isinstance(node.right, BinaryOperation)
        assert node.right.operator == "^"
        assert node.right.left.value == 3
        assert node.right.right.value == 4
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        formula = "MA(CLOSE, 5) > MA(CLOSE, 10) AND VOLUME > 1000"
        node = self._parse_expression(formula)
        
        assert isinstance(node, BinaryOperation)
        assert node.operator == "AND"
        
        # 左侧是比较运算
        left = node.left
        assert isinstance(left, BinaryOperation)
        assert left.operator == ">"
        assert isinstance(left.left, FunctionCall)
        assert left.left.name == "MA"
        
        # 右侧也是比较运算
        right = node.right
        assert isinstance(right, BinaryOperation)
        assert right.operator == ">"
        assert isinstance(right.left, Identifier)
        assert right.left.name == "VOLUME"
    
    def test_multiple_statements(self):
        """测试多语句解析"""
        formula = """
        MA5 := MA(CLOSE, 5);
        MA10 := MA(CLOSE, 10);
        MA5 > MA10
        """
        
        tokens = self.lexer.tokenize(formula)
        ast = self.parser.parse(tokens)
        
        assert len(ast.body) == 3
        
        # 第一个赋值语句
        assert isinstance(ast.body[0], Assignment)
        assert ast.body[0].name == "MA5"
        
        # 第二个赋值语句
        assert isinstance(ast.body[1], Assignment)
        assert ast.body[1].name == "MA10"
        
        # 第三个表达式语句
        assert isinstance(ast.body[2], BinaryOperation)
        assert ast.body[2].operator == ">"
    
    def test_parentheses(self):
        """测试括号处理"""
        node = self._parse_expression("(1 + 2) * (3 + 4)")
        assert isinstance(node, BinaryOperation)
        assert node.operator == "*"
        
        # 左括号内容
        assert isinstance(node.left, BinaryOperation)
        assert node.left.operator == "+"
        
        # 右括号内容
        assert isinstance(node.right, BinaryOperation)
        assert node.right.operator == "+"
    
    def test_syntax_errors(self):
        """测试语法错误处理"""
        # 缺少右括号
        with pytest.raises(TDXSyntaxError) as exc_info:
            self._parse_expression("MA(CLOSE, 5")
        assert "Expected ')' after function arguments" in str(exc_info.value)
        
        # 缺少函数参数
        with pytest.raises(TDXSyntaxError) as exc_info:
            self._parse_expression("MA(,5)")
        # 应该在解析第一个参数时出错
        
        # 意外的Token
        with pytest.raises(TDXSyntaxError) as exc_info:
            self._parse_expression(")")
        assert "Unexpected token" in str(exc_info.value)
    
    def test_empty_program(self):
        """测试空程序"""
        tokens = self.lexer.tokenize("")
        ast = self.parser.parse(tokens)
        assert isinstance(ast, Program)
        assert len(ast.body) == 0
    
    def test_whitespace_and_newlines(self):
        """测试空白字符和换行符处理"""
        formula = """
        
        1 + 2
        
        3 * 4
        
        """
        
        tokens = self.lexer.tokenize(formula)
        ast = self.parser.parse(tokens)
        
        assert len(ast.body) == 2
        assert isinstance(ast.body[0], BinaryOperation)
        assert ast.body[0].operator == "+"
        assert isinstance(ast.body[1], BinaryOperation)
        assert ast.body[1].operator == "*"
    
    def test_debug_mode(self, capsys):
        """测试调试模式"""
        self.parser.set_debug_mode(True)
        self._parse_expression("1 + 2")
        
        # 检查是否有调试输出
        captured = capsys.readouterr()
        # 调试输出可能包含解析过程信息
    
    def test_ast_string_representation(self):
        """测试AST节点的字符串表示"""
        node = self._parse_expression("MA(CLOSE, 5)")
        str_repr = str(node)
        assert "MA" in str_repr
        assert "CLOSE" in str_repr
        assert "5" in str_repr
    
    def test_error_position_tracking(self):
        """测试错误位置跟踪"""
        with pytest.raises(TDXSyntaxError) as exc_info:
            self._parse_expression("1 + + 2")
        
        error = exc_info.value
        assert error.position is not None
        assert error.line is not None
        assert error.column is not None


class TestParserFunctions:
    """测试便捷函数"""
    
    def test_parse_function(self):
        """测试parse便捷函数"""
        from tdx_interpreter.parser.parser import parse
        from tdx_interpreter.lexer.lexer import tokenize
        
        tokens = tokenize("MA(CLOSE, 5)")
        ast = parse(tokens)
        
        assert isinstance(ast, Program)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], FunctionCall)
        assert ast.body[0].name == "MA"