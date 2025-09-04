#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词法分析器单元测试

测试TDXLexer的各种功能，包括：
- 数值识别
- 标识符识别
- 运算符识别
- 分隔符识别
- 关键字识别
- 错误处理
"""

import pytest
from tdx_interpreter.lexer import TDXLexer, Token, TokenType
from tdx_interpreter.errors import TDXSyntaxError


class TestTDXLexer:
    """TDXLexer测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.lexer = TDXLexer()
    
    def test_empty_input(self):
        """测试空输入"""
        tokens = self.lexer.tokenize("")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        tokens = self.lexer.tokenize("   \t  ")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_number_recognition(self):
        """测试数值识别"""
        # 整数
        tokens = self.lexer.tokenize("123")
        assert len(tokens) == 2  # NUMBER + EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 123
        
        # 浮点数
        tokens = self.lexer.tokenize("3.14")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14
        
        # 小数点开头
        tokens = self.lexer.tokenize("0.5")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 0.5
    
    def test_identifier_recognition(self):
        """测试标识符识别"""
        # 简单标识符
        tokens = self.lexer.tokenize("CLOSE")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "CLOSE"
        
        # 包含数字和下划线的标识符
        tokens = self.lexer.tokenize("MA_5")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "MA_5"
        
        # 小写转大写
        tokens = self.lexer.tokenize("close")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "CLOSE"
    
    def test_keyword_recognition(self):
        """测试关键字识别"""
        keywords = [
            ("IF", TokenType.IF),
            ("AND", TokenType.AND),
            ("OR", TokenType.OR),
            ("NOT", TokenType.NOT),
        ]
        
        for keyword, expected_type in keywords:
            tokens = self.lexer.tokenize(keyword)
            assert len(tokens) == 2
            assert tokens[0].type == expected_type
            assert tokens[0].value == keyword
    
    def test_operator_recognition(self):
        """测试运算符识别"""
        operators = [
            ("+", TokenType.PLUS),
            ("-", TokenType.MINUS),
            ("*", TokenType.MULTIPLY),
            ("/", TokenType.DIVIDE),
            ("%", TokenType.MODULO),
            ("^", TokenType.POWER),
            ("=", TokenType.EQUAL),
            ("<>", TokenType.NOT_EQUAL),
            ("!=", TokenType.NOT_EQUAL),
            (">", TokenType.GREATER),
            ("<", TokenType.LESS),
            (">=", TokenType.GREATER_EQUAL),
            ("<=", TokenType.LESS_EQUAL),
            (":=", TokenType.ASSIGN),
        ]
        
        for op, expected_type in operators:
            tokens = self.lexer.tokenize(op)
            assert len(tokens) == 2
            assert tokens[0].type == expected_type
            assert tokens[0].value == op
    
    def test_delimiter_recognition(self):
        """测试分隔符识别"""
        delimiters = [
            ("(", TokenType.LEFT_PAREN),
            (")", TokenType.RIGHT_PAREN),
            ("[", TokenType.LEFT_BRACKET),
            ("]", TokenType.RIGHT_BRACKET),
            (",", TokenType.COMMA),
            (";", TokenType.SEMICOLON),
        ]
        
        for delim, expected_type in delimiters:
            tokens = self.lexer.tokenize(delim)
            assert len(tokens) == 2
            assert tokens[0].type == expected_type
            assert tokens[0].value == delim
    
    def test_string_recognition(self):
        """测试字符串识别"""
        # 简单字符串
        tokens = self.lexer.tokenize('"hello"')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
        
        # 包含转义字符的字符串
        tokens = self.lexer.tokenize('"hello\\world"')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello\\world"
    
    def test_comment_handling(self):
        """测试注释处理"""
        # 单行注释
        tokens = self.lexer.tokenize("123 // this is a comment")
        assert len(tokens) == 2  # NUMBER + EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 123
        
        # 块注释
        tokens = self.lexer.tokenize("123 { this is a block comment } 456")
        assert len(tokens) == 3  # NUMBER + NUMBER + EOF
        assert tokens[0].value == 123
        assert tokens[1].value == 456
    
    def test_newline_handling(self):
        """测试换行符处理"""
        tokens = self.lexer.tokenize("123\n456")
        assert len(tokens) == 4  # NUMBER + NEWLINE + NUMBER + EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.NUMBER
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        formula = "MA(CLOSE, 5) > MA(CLOSE, 10) AND VOLUME > 1000"
        tokens = self.lexer.tokenize(formula)
        
        expected_types = [
            TokenType.IDENTIFIER,    # MA
            TokenType.LEFT_PAREN,    # (
            TokenType.IDENTIFIER,    # CLOSE
            TokenType.COMMA,         # ,
            TokenType.NUMBER,        # 5
            TokenType.RIGHT_PAREN,   # )
            TokenType.GREATER,       # >
            TokenType.IDENTIFIER,    # MA
            TokenType.LEFT_PAREN,    # (
            TokenType.IDENTIFIER,    # CLOSE
            TokenType.COMMA,         # ,
            TokenType.NUMBER,        # 10
            TokenType.RIGHT_PAREN,   # )
            TokenType.AND,           # AND
            TokenType.IDENTIFIER,    # VOLUME
            TokenType.GREATER,       # >
            TokenType.NUMBER,        # 1000
            TokenType.EOF,           # EOF
        ]
        
        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i}: expected {expected_type}, got {tokens[i].type}"
    
    def test_assignment_expression(self):
        """测试赋值表达式"""
        formula = "MA5 := MA(CLOSE, 5);"
        tokens = self.lexer.tokenize(formula)
        
        expected_types = [
            TokenType.IDENTIFIER,    # MA5
            TokenType.ASSIGN,        # :=
            TokenType.IDENTIFIER,    # MA
            TokenType.LEFT_PAREN,    # (
            TokenType.IDENTIFIER,    # CLOSE
            TokenType.COMMA,         # ,
            TokenType.NUMBER,        # 5
            TokenType.RIGHT_PAREN,   # )
            TokenType.SEMICOLON,     # ;
            TokenType.EOF,           # EOF
        ]
        
        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_conditional_expression(self):
        """测试条件表达式"""
        formula = "IF(CLOSE > OPEN, 1, 0)"
        tokens = self.lexer.tokenize(formula)
        
        expected_types = [
            TokenType.IF,            # IF
            TokenType.LEFT_PAREN,    # (
            TokenType.IDENTIFIER,    # CLOSE
            TokenType.GREATER,       # >
            TokenType.IDENTIFIER,    # OPEN
            TokenType.COMMA,         # ,
            TokenType.NUMBER,        # 1
            TokenType.COMMA,         # ,
            TokenType.NUMBER,        # 0
            TokenType.RIGHT_PAREN,   # )
            TokenType.EOF,           # EOF
        ]
        
        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_position_tracking(self):
        """测试位置跟踪"""
        tokens = self.lexer.tokenize("123 + 456")
        
        # 检查位置信息
        assert tokens[0].position == 0  # 123
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        
        assert tokens[1].position == 4  # +
        assert tokens[1].line == 1
        assert tokens[1].column == 5
        
        assert tokens[2].position == 6  # 456
        assert tokens[2].line == 1
        assert tokens[2].column == 7
    
    def test_multiline_position_tracking(self):
        """测试多行位置跟踪"""
        tokens = self.lexer.tokenize("123\n456")
        
        assert tokens[0].line == 1  # 123
        assert tokens[1].line == 1  # \n
        assert tokens[2].line == 2  # 456
        assert tokens[2].column == 1
    
    def test_unknown_character_error(self):
        """测试未知字符错误"""
        with pytest.raises(TDXSyntaxError) as exc_info:
            self.lexer.tokenize("123 @ 456")
        
        error = exc_info.value
        assert "Unknown character '@'" in str(error)
        assert error.position == 4
        assert error.line == 1
        assert error.column == 5
    
    def test_token_methods(self):
        """测试Token类的方法"""
        tokens = self.lexer.tokenize("+")
        token = tokens[0]
        
        # 测试类型检查方法
        assert token.is_type(TokenType.PLUS)
        assert not token.is_type(TokenType.MINUS)
        assert token.is_operator()
        assert not token.is_literal()
        assert not token.is_delimiter()
        
        # 测试优先级
        assert token.get_precedence() == 5
        assert not token.is_right_associative()
    
    def test_precedence_and_associativity(self):
        """测试运算符优先级和结合性"""
        tokens = self.lexer.tokenize("+ - * / ^ NOT")
        
        # 检查优先级
        assert tokens[0].get_precedence() == 5  # +
        assert tokens[1].get_precedence() == 5  # -
        assert tokens[2].get_precedence() == 6  # *
        assert tokens[3].get_precedence() == 6  # /
        assert tokens[4].get_precedence() == 7  # ^
        assert tokens[5].get_precedence() == 3  # NOT
        
        # 检查结合性
        assert not tokens[0].is_right_associative()  # +
        assert tokens[4].is_right_associative()      # ^
        assert tokens[5].is_right_associative()      # NOT
    
    def test_lexer_iterator(self):
        """测试词法分析器迭代器"""
        tokens = self.lexer.tokenize("1 + 2")
        
        # 测试迭代
        token_types = [token.type for token in self.lexer]
        expected_types = [TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER, TokenType.EOF]
        assert token_types == expected_types
    
    def test_peek_method(self):
        """测试peek方法"""
        self.lexer.tokenize("1 + 2")
        
        # 测试peek
        assert self.lexer.peek(0).type == TokenType.NUMBER
        assert self.lexer.peek(1).type == TokenType.PLUS
        assert self.lexer.peek(2).type == TokenType.NUMBER
        assert self.lexer.peek(3).type == TokenType.EOF
        assert self.lexer.peek(4) is None
    
    def test_debug_print(self, capsys):
        """测试调试打印功能"""
        self.lexer.tokenize("1 + 2")
        self.lexer.debug_print()
        
        captured = capsys.readouterr()
        assert "Lexer Debug Info:" in captured.out
        assert "Tokens (4):" in captured.out


class TestTokenizeFunctions:
    """测试便捷函数"""
    
    def test_tokenize_function(self):
        """测试tokenize便捷函数"""
        from tdx_interpreter.lexer.lexer import tokenize
        
        tokens = tokenize("MA(CLOSE, 5)")
        assert len(tokens) == 7  # MA + ( + CLOSE + , + 5 + ) + EOF
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "MA"