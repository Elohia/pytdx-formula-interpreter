#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器运算符优先级管理

定义和管理运算符的优先级和结合性，用于正确解析表达式。
"""

from enum import IntEnum
from typing import Dict, Set
from ..lexer.tokens import TokenType


class Precedence(IntEnum):
    """
    运算符优先级枚举
    
    数值越大，优先级越高。
    """
    
    NONE = 0          # 无优先级
    ASSIGNMENT = 1    # := 
    OR = 2           # OR
    AND = 3          # AND
    EQUALITY = 4     # = <> !=
    COMPARISON = 5   # > < >= <=
    TERM = 6         # + -
    FACTOR = 7       # * / %
    UNARY = 8        # - NOT
    POWER = 9        # ^
    CALL = 10        # 函数调用
    PRIMARY = 11     # 字面量、标识符、括号


class OperatorPrecedence:
    """
    运算符优先级管理器
    
    提供运算符优先级查询和比较功能。
    """
    
    # 运算符优先级映射
    PRECEDENCE_MAP: Dict[TokenType, Precedence] = {
        # 赋值运算符
        TokenType.ASSIGN: Precedence.ASSIGNMENT,
        
        # 逻辑运算符
        TokenType.OR: Precedence.OR,
        TokenType.AND: Precedence.AND,
        TokenType.NOT: Precedence.UNARY,
        
        # 比较运算符
        TokenType.EQUAL: Precedence.EQUALITY,
        TokenType.NOT_EQUAL: Precedence.EQUALITY,
        TokenType.GREATER: Precedence.COMPARISON,
        TokenType.LESS: Precedence.COMPARISON,
        TokenType.GREATER_EQUAL: Precedence.COMPARISON,
        TokenType.LESS_EQUAL: Precedence.COMPARISON,
        
        # 算术运算符
        TokenType.PLUS: Precedence.TERM,
        TokenType.MINUS: Precedence.TERM,
        TokenType.MULTIPLY: Precedence.FACTOR,
        TokenType.DIVIDE: Precedence.FACTOR,
        TokenType.MODULO: Precedence.FACTOR,
        TokenType.POWER: Precedence.POWER,
    }
    
    # 右结合运算符
    RIGHT_ASSOCIATIVE: Set[TokenType] = {
        TokenType.ASSIGN,
        TokenType.POWER,
        TokenType.NOT,
    }
    
    # 二元运算符
    BINARY_OPERATORS: Set[TokenType] = {
        TokenType.ASSIGN,
        TokenType.OR,
        TokenType.AND,
        TokenType.EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.GREATER,
        TokenType.LESS,
        TokenType.GREATER_EQUAL,
        TokenType.LESS_EQUAL,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.MULTIPLY,
        TokenType.DIVIDE,
        TokenType.MODULO,
        TokenType.POWER,
    }
    
    # 一元运算符
    UNARY_OPERATORS: Set[TokenType] = {
        TokenType.MINUS,
        TokenType.NOT,
    }
    
    @classmethod
    def get_precedence(cls, token_type: TokenType) -> Precedence:
        """
        获取运算符优先级
        
        Args:
            token_type: Token类型
            
        Returns:
            Precedence: 优先级
        """
        return cls.PRECEDENCE_MAP.get(token_type, Precedence.NONE)
    
    @classmethod
    def is_right_associative(cls, token_type: TokenType) -> bool:
        """
        检查运算符是否为右结合
        
        Args:
            token_type: Token类型
            
        Returns:
            bool: 是否为右结合
        """
        return token_type in cls.RIGHT_ASSOCIATIVE
    
    @classmethod
    def is_binary_operator(cls, token_type: TokenType) -> bool:
        """
        检查是否为二元运算符
        
        Args:
            token_type: Token类型
            
        Returns:
            bool: 是否为二元运算符
        """
        return token_type in cls.BINARY_OPERATORS
    
    @classmethod
    def is_unary_operator(cls, token_type: TokenType) -> bool:
        """
        检查是否为一元运算符
        
        Args:
            token_type: Token类型
            
        Returns:
            bool: 是否为一元运算符
        """
        return token_type in cls.UNARY_OPERATORS
    
    @classmethod
    def compare_precedence(cls, left: TokenType, right: TokenType) -> int:
        """
        比较两个运算符的优先级
        
        Args:
            left: 左运算符
            right: 右运算符
            
        Returns:
            int: -1 (left < right), 0 (left == right), 1 (left > right)
        """
        left_prec = cls.get_precedence(left)
        right_prec = cls.get_precedence(right)
        
        if left_prec < right_prec:
            return -1
        elif left_prec > right_prec:
            return 1
        else:
            return 0
    
    @classmethod
    def should_reduce(cls, stack_op: TokenType, input_op: TokenType) -> bool:
        """
        判断是否应该进行归约操作
        
        用于运算符优先级解析算法。
        
        Args:
            stack_op: 栈顶运算符
            input_op: 输入运算符
            
        Returns:
            bool: 是否应该归约
        """
        stack_prec = cls.get_precedence(stack_op)
        input_prec = cls.get_precedence(input_op)
        
        # 如果栈顶运算符优先级更高，应该归约
        if stack_prec > input_prec:
            return True
        
        # 如果优先级相同，检查结合性
        if stack_prec == input_prec:
            # 左结合：归约
            # 右结合：不归约
            return not cls.is_right_associative(input_op)
        
        # 栈顶运算符优先级更低，不归约
        return False
    
    @classmethod
    def get_operator_info(cls, token_type: TokenType) -> Dict[str, any]:
        """
        获取运算符的完整信息
        
        Args:
            token_type: Token类型
            
        Returns:
            Dict: 运算符信息
        """
        return {
            'precedence': cls.get_precedence(token_type),
            'right_associative': cls.is_right_associative(token_type),
            'binary': cls.is_binary_operator(token_type),
            'unary': cls.is_unary_operator(token_type),
        }
    
    @classmethod
    def debug_precedence_table(cls) -> str:
        """
        生成优先级表的调试信息
        
        Returns:
            str: 优先级表字符串
        """
        lines = ["Operator Precedence Table:"]
        lines.append("=" * 50)
        lines.append(f"{'Operator':<15} {'Precedence':<12} {'Associativity':<15} {'Type':<10}")
        lines.append("-" * 50)
        
        # 按优先级排序
        sorted_ops = sorted(cls.PRECEDENCE_MAP.items(), 
                          key=lambda x: x[1], reverse=True)
        
        for token_type, precedence in sorted_ops:
            associativity = "Right" if cls.is_right_associative(token_type) else "Left"
            op_type = []
            if cls.is_binary_operator(token_type):
                op_type.append("Binary")
            if cls.is_unary_operator(token_type):
                op_type.append("Unary")
            type_str = ", ".join(op_type) if op_type else "N/A"
            
            lines.append(f"{token_type.name:<15} {precedence.name:<12} {associativity:<15} {type_str:<10}")
        
        return "\n".join(lines)