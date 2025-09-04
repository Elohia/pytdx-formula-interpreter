#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器词法分析器实现

将通达信公式字符串分解为词法单元序列。
"""

import re
from typing import List, Optional, Iterator, Union
from .tokens import Token, TokenType, KEYWORDS, OPERATORS, DELIMITERS
from ..errors.exceptions import TDXSyntaxError


class TDXLexer:
    """
    通达信公式词法分析器
    
    负责将输入的公式字符串转换为Token序列，支持：
    - 数值常量识别（整数、浮点数）
    - 标识符识别（变量名、函数名）
    - 运算符识别（算术、比较、逻辑）
    - 分隔符识别（括号、逗号等）
    - 关键字识别（IF、AND、OR等）
    - 注释处理
    - 错误检测和报告
    """
    
    def __init__(self):
        """
        初始化词法分析器
        """
        self.text = ""
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # 编译正则表达式模式
        self._compile_patterns()
    
    def _compile_patterns(self):
        """
        编译正则表达式模式
        """
        # 数值模式：支持整数和浮点数
        self.number_pattern = re.compile(r'\d+(?:\.\d+)?')
        
        # 标识符模式：字母开头，可包含字母、数字、下划线
        self.identifier_pattern = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
        
        # 字符串模式：双引号包围
        self.string_pattern = re.compile(r'"([^"\\]|\\.)*"')
        
        # 空白字符模式
        self.whitespace_pattern = re.compile(r'[ \t]+')
        
        # 注释模式：// 或 { } 或 # 风格
        self.comment_pattern = re.compile(r'//.*?$|\{.*?\}|#.*?$', re.MULTILINE | re.DOTALL)
    
    def tokenize(self, text: str) -> List[Token]:
        """
        对输入文本进行词法分析
        
        Args:
            text: 要分析的通达信公式字符串
            
        Returns:
            List[Token]: 词法单元列表
            
        Raises:
            TDXSyntaxError: 词法分析错误
        """
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        while self.position < len(self.text):
            # 跳过空白字符
            if self._skip_whitespace():
                continue
                
            # 跳过注释
            if self._skip_comment():
                continue
                
            # 处理换行符
            if self._handle_newline():
                continue
                
            # 识别数值
            if self._tokenize_number():
                continue
                
            # 识别字符串
            if self._tokenize_string():
                continue
                
            # 识别运算符
            if self._tokenize_operator():
                continue
                
            # 识别分隔符
            if self._tokenize_delimiter():
                continue
                
            # 识别标识符和关键字
            if self._tokenize_identifier():
                continue
                
            # 未识别的字符
            self._handle_unknown_character()
        
        # 添加EOF标记
        self._add_token(TokenType.EOF, None)
        
        return self.tokens
    
    def _skip_whitespace(self) -> bool:
        """
        跳过空白字符
        
        Returns:
            bool: 是否跳过了空白字符
        """
        match = self.whitespace_pattern.match(self.text, self.position)
        if match:
            self.column += len(match.group())
            self.position = match.end()
            return True
        return False
    
    def _skip_comment(self) -> bool:
        """
        跳过注释
        
        Returns:
            bool: 是否跳过了注释
        """
        match = self.comment_pattern.match(self.text, self.position)
        if match:
            comment_text = match.group()
            # 更新行号和列号
            newlines = comment_text.count('\n')
            if newlines > 0:
                self.line += newlines
                self.column = len(comment_text.split('\n')[-1]) + 1
            else:
                self.column += len(comment_text)
            self.position = match.end()
            return True
        return False
    
    def _handle_newline(self) -> bool:
        """
        处理换行符
        
        Returns:
            bool: 是否处理了换行符
        """
        if self._current_char() == '\n':
            self._add_token(TokenType.NEWLINE, '\n')
            self.line += 1
            self.column = 1
            self.position += 1
            return True
        return False
    
    def _tokenize_number(self) -> bool:
        """
        识别数值常量
        
        Returns:
            bool: 是否识别了数值
        """
        match = self.number_pattern.match(self.text, self.position)
        if match:
            value_str = match.group()
            # 转换为适当的数值类型
            if '.' in value_str:
                value = float(value_str)
            else:
                value = int(value_str)
            
            self._add_token(TokenType.NUMBER, value)
            self.column += len(value_str)
            self.position = match.end()
            return True
        return False
    
    def _tokenize_string(self) -> bool:
        """
        识别字符串常量
        
        Returns:
            bool: 是否识别了字符串
        """
        match = self.string_pattern.match(self.text, self.position)
        if match:
            value_str = match.group()
            # 去掉引号并处理转义字符
            value = value_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            
            self._add_token(TokenType.STRING, value)
            self.column += len(value_str)
            self.position = match.end()
            return True
        return False
    
    def _tokenize_operator(self) -> bool:
        """
        识别运算符
        
        Returns:
            bool: 是否识别了运算符
        """
        # 按长度降序检查运算符，优先匹配长运算符
        for op in sorted(OPERATORS.keys(), key=len, reverse=True):
            if self.text[self.position:].startswith(op):
                self._add_token(OPERATORS[op], op)
                self.column += len(op)
                self.position += len(op)
                return True
        return False
    
    def _tokenize_delimiter(self) -> bool:
        """
        识别分隔符
        
        Returns:
            bool: 是否识别了分隔符
        """
        char = self._current_char()
        if char in DELIMITERS:
            self._add_token(DELIMITERS[char], char)
            self.column += 1
            self.position += 1
            return True
        return False
    
    def _tokenize_identifier(self) -> bool:
        """
        识别标识符和关键字
        
        Returns:
            bool: 是否识别了标识符
        """
        match = self.identifier_pattern.match(self.text, self.position)
        if match:
            value = match.group().upper()  # 转换为大写
            
            # 检查是否为关键字
            if value in KEYWORDS:
                token_type = KEYWORDS[value]
            else:
                token_type = TokenType.IDENTIFIER
            
            self._add_token(token_type, value)
            self.column += len(value)
            self.position = match.end()
            return True
        return False
    
    def _handle_unknown_character(self):
        """
        处理未知字符
        
        Raises:
            TDXSyntaxError: 未知字符错误
        """
        char = self._current_char()
        raise TDXSyntaxError(
            f"Unknown character '{char}'",
            formula=self.text,
            position=self.position,
            line=self.line,
            column=self.column
        )
    
    def _current_char(self) -> str:
        """
        获取当前字符
        
        Returns:
            str: 当前字符，如果到达末尾返回空字符串
        """
        if self.position >= len(self.text):
            return ''
        return self.text[self.position]
    
    def _add_token(self, token_type: TokenType, value: Union[str, int, float, None]):
        """
        添加Token到列表
        
        Args:
            token_type: Token类型
            value: Token值
        """
        token = Token(
            type=token_type,
            value=value,
            position=self.position,
            line=self.line,
            column=self.column
        )
        self.tokens.append(token)
    
    def get_tokens(self) -> List[Token]:
        """
        获取已分析的Token列表
        
        Returns:
            List[Token]: Token列表
        """
        return self.tokens
    
    def __iter__(self) -> Iterator[Token]:
        """
        支持迭代器协议
        
        Returns:
            Iterator[Token]: Token迭代器
        """
        return iter(self.tokens)
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """
        查看指定位置的Token，不移动位置
        
        Args:
            offset: 相对当前位置的偏移量
            
        Returns:
            Optional[Token]: Token或None
        """
        index = offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None
    
    def debug_print(self):
        """
        打印调试信息
        """
        print(f"Lexer Debug Info:")
        print(f"Text: {repr(self.text)}")
        print(f"Position: {self.position}")
        print(f"Line: {self.line}, Column: {self.column}")
        print(f"Tokens ({len(self.tokens)}):")
        for i, token in enumerate(self.tokens):
            print(f"  {i:2d}: {token}")


def tokenize(text: str) -> List[Token]:
    """
    便捷函数：对文本进行词法分析
    
    Args:
        text: 要分析的文本
        
    Returns:
        List[Token]: Token列表
    """
    lexer = TDXLexer()
    return lexer.tokenize(text)