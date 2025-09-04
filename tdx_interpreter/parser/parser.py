#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器语法解析器实现

使用递归下降解析算法将Token序列转换为抽象语法树(AST)。
"""

from typing import List, Optional, Union
from ..lexer.tokens import Token, TokenType
from ..core.ast_nodes import (
    ASTNode, NumberLiteral, StringLiteral, Identifier,
    BinaryOperation, UnaryOperation, FunctionCall,
    Assignment, ConditionalExpression, ArrayAccess,
    Block, Program
)
from ..errors.exceptions import TDXSyntaxError
from .precedence import OperatorPrecedence, Precedence


class TDXParser:
    """
    通达信公式语法解析器
    
    使用递归下降解析算法，支持：
    - 表达式解析（运算符优先级）
    - 函数调用解析
    - 条件语句解析
    - 赋值语句解析
    - 数组访问解析
    - 语法错误检测和恢复
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        self.tokens: List[Token] = []
        self.current = 0
        self._debug_mode = False
    
    def parse(self, tokens: List[Token]) -> Program:
        """
        解析Token序列，生成AST
        
        Args:
            tokens: Token序列
            
        Returns:
            Program: 程序AST节点
            
        Raises:
            TDXSyntaxError: 语法错误
        """
        self.tokens = tokens
        self.current = 0
        
        try:
            statements = []
            
            while not self._is_at_end():
                # 跳过换行符
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue
                
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            
            return Program(statements)
            
        except Exception as e:
            if isinstance(e, TDXSyntaxError):
                raise
            else:
                current_token = self._peek()
                raise TDXSyntaxError(
                    f"Unexpected error during parsing: {str(e)}",
                    position=current_token.position if current_token else 0,
                    line=current_token.line if current_token else 1,
                    column=current_token.column if current_token else 1
                ) from e
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """
        解析语句
        
        Returns:
            Optional[ASTNode]: 语句节点
        """
        # 检查赋值语句
        if self._check_assignment():
            stmt = self._parse_assignment()
            # 可选的分号
            if self._check(TokenType.SEMICOLON):
                self._advance()
            return stmt
        
        # 解析表达式语句
        expr = self._parse_expression()
        
        # 可选的分号
        if self._check(TokenType.SEMICOLON):
            self._advance()
        
        return expr
    
    def _check_assignment(self) -> bool:
        """
        检查是否为赋值语句
        
        Returns:
            bool: 是否为赋值语句
        """
        if not self._check(TokenType.IDENTIFIER):
            return False
        
        # 向前看一个Token
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1].type == TokenType.ASSIGN
        
        return False
    
    def _parse_assignment(self) -> Assignment:
        """
        解析赋值语句
        
        Returns:
            Assignment: 赋值节点
        """
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        self._consume(TokenType.ASSIGN, "Expected ':=' after variable name")
        value = self._parse_expression()
        
        return Assignment(name_token.value, value)
    
    def _parse_expression(self) -> ASTNode:
        """
        解析表达式
        
        Returns:
            ASTNode: 表达式节点
        """
        return self._parse_precedence(Precedence.ASSIGNMENT)
    
    def _parse_precedence(self, precedence: Precedence) -> ASTNode:
        """
        使用运算符优先级解析表达式
        
        Args:
            precedence: 最小优先级
            
        Returns:
            ASTNode: 表达式节点
        """
        # 解析前缀表达式
        left = self._parse_prefix()
        
        # 解析中缀表达式
        while (not self._is_at_end() and 
               OperatorPrecedence.get_precedence(self._peek().type) >= precedence):
            
            operator_token = self._advance()
            left = self._parse_infix(left, operator_token)
        
        return left
    
    def _parse_prefix(self) -> ASTNode:
        """
        解析前缀表达式
        
        Returns:
            ASTNode: 前缀表达式节点
        """
        token = self._advance()
        
        if token.type == TokenType.NUMBER:
            return NumberLiteral(token.value)
        
        elif token.type == TokenType.STRING:
            return StringLiteral(token.value)
        
        elif token.type == TokenType.IDENTIFIER:
            return self._parse_identifier_or_call(token)
        
        elif token.type == TokenType.LEFT_PAREN:
            expr = self._parse_expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        elif token.type in {TokenType.MINUS, TokenType.NOT}:
            operand = self._parse_precedence(Precedence.UNARY)
            return UnaryOperation(token.value, operand)
        
        elif token.type == TokenType.IF:
            return self._parse_conditional()
        
        else:
            raise TDXSyntaxError(
                f"Unexpected token '{token.value}'",
                position=token.position,
                line=token.line,
                column=token.column,
                expected=["number", "string", "identifier", "(", "-", "NOT", "IF"],
                actual=str(token.value)
            )
    
    def _parse_identifier_or_call(self, name_token: Token) -> ASTNode:
        """
        解析标识符或函数调用
        
        Args:
            name_token: 标识符Token
            
        Returns:
            ASTNode: 标识符或函数调用节点
        """
        # 检查是否为函数调用
        if self._check(TokenType.LEFT_PAREN):
            return self._parse_function_call(name_token.value)
        
        # 检查是否为数组访问
        if self._check(TokenType.LEFT_BRACKET):
            identifier = Identifier(name_token.value)
            return self._parse_array_access(identifier)
        
        # 普通标识符
        return Identifier(name_token.value)
    
    def _parse_function_call(self, name: str) -> FunctionCall:
        """
        解析函数调用
        
        Args:
            name: 函数名
            
        Returns:
            FunctionCall: 函数调用节点
        """
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        arguments = []
        
        if not self._check(TokenType.RIGHT_PAREN):
            # 解析参数列表
            arguments.append(self._parse_expression())
            
            while self._check(TokenType.COMMA):
                self._advance()  # 消费逗号
                arguments.append(self._parse_expression())
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments")
        
        return FunctionCall(name, arguments)
    
    def _parse_array_access(self, array: ASTNode) -> ArrayAccess:
        """
        解析数组访问
        
        Args:
            array: 数组表达式
            
        Returns:
            ArrayAccess: 数组访问节点
        """
        self._consume(TokenType.LEFT_BRACKET, "Expected '['")
        index = self._parse_expression()
        self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array index")
        
        return ArrayAccess(array, index)
    
    def _parse_conditional(self) -> ConditionalExpression:
        """
        解析条件表达式
        
        Returns:
            ConditionalExpression: 条件表达式节点
        """
        # IF已经被消费了
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'IF'")
        
        condition = self._parse_expression()
        self._consume(TokenType.COMMA, "Expected ',' after condition")
        
        true_value = self._parse_expression()
        self._consume(TokenType.COMMA, "Expected ',' after true value")
        
        false_value = self._parse_expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after false value")
        
        return ConditionalExpression(condition, true_value, false_value)
    
    def _parse_infix(self, left: ASTNode, operator_token: Token) -> ASTNode:
        """
        解析中缀表达式
        
        Args:
            left: 左操作数
            operator_token: 运算符Token
            
        Returns:
            ASTNode: 中缀表达式节点
        """
        operator = operator_token.value
        
        # 获取运算符优先级
        precedence = OperatorPrecedence.get_precedence(operator_token.type)
        
        # 如果是右结合运算符，降低优先级
        if OperatorPrecedence.is_right_associative(operator_token.type):
            precedence = Precedence(precedence - 1)
        
        right = self._parse_precedence(precedence)
        
        return BinaryOperation(left, operator, right)
    
    def _peek(self) -> Token:
        """
        查看当前Token
        
        Returns:
            Token: 当前Token
        """
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """
        获取前一个Token
        
        Returns:
            Token: 前一个Token
        """
        return self.tokens[self.current - 1]
    
    def _advance(self) -> Token:
        """
        前进到下一个Token
        
        Returns:
            Token: 当前Token（前进前的）
        """
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """
        检查是否到达Token序列末尾
        
        Returns:
            bool: 是否到达末尾
        """
        return (self.current >= len(self.tokens) or 
                (self.current < len(self.tokens) and self.tokens[self.current].type == TokenType.EOF))
    
    def _check(self, token_type: TokenType) -> bool:
        """
        检查当前Token是否为指定类型
        
        Args:
            token_type: 要检查的Token类型
            
        Returns:
            bool: 是否匹配
        """
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *token_types: TokenType) -> bool:
        """
        检查当前Token是否匹配任一指定类型
        
        Args:
            *token_types: Token类型列表
            
        Returns:
            bool: 是否匹配任一类型
        """
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        消费指定类型的Token
        
        Args:
            token_type: 期望的Token类型
            message: 错误消息
            
        Returns:
            Token: 消费的Token
            
        Raises:
            TDXSyntaxError: Token类型不匹配
        """
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise TDXSyntaxError(
            message,
            position=current_token.position,
            line=current_token.line,
            column=current_token.column,
            expected=[token_type.name],
            actual=current_token.type.name
        )
    
    def _synchronize(self):
        """
        错误恢复：同步到下一个语句开始
        """
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in {
                TokenType.IF,
                TokenType.IDENTIFIER,  # 可能是赋值语句
            }:
                return
            
            self._advance()
    
    def set_debug_mode(self, enabled: bool):
        """
        设置调试模式
        
        Args:
            enabled: 是否启用调试模式
        """
        self._debug_mode = enabled
    
    def _debug_print(self, message: str):
        """
        调试输出
        
        Args:
            message: 调试消息
        """
        if self._debug_mode:
            current_token = self._peek()
            print(f"[Parser Debug] {message} (current: {current_token})")


def parse(tokens: List[Token]) -> Program:
    """
    便捷函数：解析Token序列
    
    Args:
        tokens: Token序列
        
    Returns:
        Program: 程序AST
    """
    parser = TDXParser()
    return parser.parse(tokens)