#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式AST求值器

负责执行抽象语法树，计算公式结果。
"""

import pandas as pd
import numpy as np
from typing import Any, Union
from .ast_nodes import (
    ASTNode, NumberLiteral, StringLiteral, Identifier,
    BinaryOperation, UnaryOperation, FunctionCall,
    Assignment, ConditionalExpression, ArrayAccess,
    Block, Program, ASTVisitor
)
from .context import TDXContext
from ..functions import registry
from ..errors.exceptions import TDXRuntimeError, TDXNameError, TDXTypeError


class ASTEvaluator(ASTVisitor):
    """
    AST求值器
    
    使用访问者模式遍历AST并计算结果。
    """
    
    def __init__(self, context: TDXContext):
        """
        初始化求值器
        
        Args:
            context: 数据上下文
        """
        self.context = context
        self._last_result = None
    
    def evaluate(self, ast: Program) -> Any:
        """
        求值AST
        
        Args:
            ast: 程序AST
            
        Returns:
            Any: 计算结果
        """
        return ast.accept(self)
    
    def visit_program(self, node: Program) -> Any:
        """
        访问程序节点
        
        Args:
            node: 程序节点
            
        Returns:
            Any: 最后一个语句的结果
        """
        result = None
        for statement in node.body:
            result = statement.accept(self)
            self._last_result = result
        return result
    
    def visit_number_literal(self, node: NumberLiteral) -> Union[int, float]:
        """
        访问数值字面量节点
        
        Args:
            node: 数值字面量节点
            
        Returns:
            Union[int, float]: 数值
        """
        return node.value
    
    def visit_string_literal(self, node: StringLiteral) -> str:
        """
        访问字符串字面量节点
        
        Args:
            node: 字符串字面量节点
            
        Returns:
            str: 字符串值
        """
        return node.value
    
    def visit_identifier(self, node: Identifier) -> Any:
        """
        访问标识符节点
        
        Args:
            node: 标识符节点
            
        Returns:
            Any: 变量值
        """
        try:
            return self.context.get_variable(node.name)
        except TDXNameError:
            # 如果变量不存在，可能是内置变量（如CLOSE, OPEN等）
            # 这些会在上下文中自动处理
            raise
    
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        """
        访问二元运算节点
        
        Args:
            node: 二元运算节点
            
        Returns:
            Any: 运算结果
        """
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        operator = node.operator
        
        try:
            if operator == "+":
                return self._add(left, right)
            elif operator == "-":
                return self._subtract(left, right)
            elif operator == "*":
                return self._multiply(left, right)
            elif operator == "/":
                return self._divide(left, right)
            elif operator == "%":
                return self._modulo(left, right)
            elif operator == "^":
                return self._power(left, right)
            elif operator == "=":
                return self._equal(left, right)
            elif operator in ["<>", "!="]:
                return self._not_equal(left, right)
            elif operator == ">":
                return self._greater(left, right)
            elif operator == "<":
                return self._less(left, right)
            elif operator == ">=":
                return self._greater_equal(left, right)
            elif operator == "<=":
                return self._less_equal(left, right)
            elif operator == "AND":
                return self._and(left, right)
            elif operator == "OR":
                return self._or(left, right)
            else:
                raise TDXRuntimeError(f"Unknown binary operator: {operator}")
        except Exception as e:
            raise TDXRuntimeError(f"Error in binary operation '{operator}': {str(e)}") from e
    
    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        """
        访问一元运算节点
        
        Args:
            node: 一元运算节点
            
        Returns:
            Any: 运算结果
        """
        operand = node.operand.accept(self)
        operator = node.operator
        
        try:
            if operator == "-":
                return self._negate(operand)
            elif operator == "NOT":
                return self._not(operand)
            else:
                raise TDXRuntimeError(f"Unknown unary operator: {operator}")
        except Exception as e:
            raise TDXRuntimeError(f"Error in unary operation '{operator}': {str(e)}") from e
    
    def visit_function_call(self, node: FunctionCall) -> Any:
        """
        访问函数调用节点
        
        Args:
            node: 函数调用节点
            
        Returns:
            Any: 函数结果
        """
        # 计算参数
        args = [arg.accept(self) for arg in node.arguments]
        
        try:
            # 调用函数
            return registry.call(node.name, *args)
        except Exception as e:
            raise TDXRuntimeError(f"Error calling function '{node.name}': {str(e)}") from e
    
    def visit_assignment(self, node: Assignment) -> Any:
        """
        访问赋值节点
        
        Args:
            node: 赋值节点
            
        Returns:
            Any: 赋值的值
        """
        value = node.value.accept(self)
        self.context.set_variable(node.name, value)
        return value
    
    def visit_conditional_expression(self, node: ConditionalExpression) -> Any:
        """
        访问条件表达式节点
        
        Args:
            node: 条件表达式节点
            
        Returns:
            Any: 条件结果
        """
        condition = node.condition.accept(self)
        
        if self._is_true(condition):
            return node.true_value.accept(self)
        else:
            return node.false_value.accept(self)
    
    def visit_array_access(self, node: ArrayAccess) -> Any:
        """
        访问数组访问节点
        
        Args:
            node: 数组访问节点
            
        Returns:
            Any: 数组元素
        """
        array = node.array.accept(self)
        index = node.index.accept(self)
        
        try:
            if isinstance(array, pd.Series):
                if isinstance(index, (int, float)):
                    idx = int(index)
                    if idx < 0:
                        # 负索引：从末尾开始
                        return array.iloc[idx]
                    else:
                        # 正索引：从开始
                        return array.iloc[idx]
                else:
                    raise TDXTypeError("Array index must be a number")
            else:
                raise TDXTypeError("Array access requires a series")
        except Exception as e:
            raise TDXRuntimeError(f"Error in array access: {str(e)}") from e
    
    def visit_block(self, node: Block) -> Any:
        """
        访问代码块节点
        
        Args:
            node: 代码块节点
            
        Returns:
            Any: 最后一个语句的结果
        """
        result = None
        for statement in node.statements:
            result = statement.accept(self)
        return result
    
    # 辅助方法：算术运算
    def _add(self, left: Any, right: Any) -> Any:
        """加法运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) + pd.Series(right)
        return left + right
    
    def _subtract(self, left: Any, right: Any) -> Any:
        """减法运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) - pd.Series(right)
        return left - right
    
    def _multiply(self, left: Any, right: Any) -> Any:
        """乘法运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) * pd.Series(right)
        return left * right
    
    def _divide(self, left: Any, right: Any) -> Any:
        """除法运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) / pd.Series(right)
        return left / right
    
    def _modulo(self, left: Any, right: Any) -> Any:
        """取模运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) % pd.Series(right)
        return left % right
    
    def _power(self, left: Any, right: Any) -> Any:
        """幂运算"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) ** pd.Series(right)
        return left ** right
    
    def _negate(self, operand: Any) -> Any:
        """取负运算"""
        if isinstance(operand, pd.Series):
            return -operand
        return -operand
    
    # 辅助方法：比较运算
    def _equal(self, left: Any, right: Any) -> Any:
        """等于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) == pd.Series(right)
        return left == right
    
    def _not_equal(self, left: Any, right: Any) -> Any:
        """不等于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) != pd.Series(right)
        return left != right
    
    def _greater(self, left: Any, right: Any) -> Any:
        """大于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) > pd.Series(right)
        return left > right
    
    def _less(self, left: Any, right: Any) -> Any:
        """小于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) < pd.Series(right)
        return left < right
    
    def _greater_equal(self, left: Any, right: Any) -> Any:
        """大于等于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) >= pd.Series(right)
        return left >= right
    
    def _less_equal(self, left: Any, right: Any) -> Any:
        """小于等于比较"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) <= pd.Series(right)
        return left <= right
    
    # 辅助方法：逻辑运算
    def _and(self, left: Any, right: Any) -> Any:
        """逻辑与"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) & pd.Series(right)
        return left and right
    
    def _or(self, left: Any, right: Any) -> Any:
        """逻辑或"""
        if isinstance(left, pd.Series) or isinstance(right, pd.Series):
            return pd.Series(left) | pd.Series(right)
        return left or right
    
    def _not(self, operand: Any) -> Any:
        """逻辑非"""
        if isinstance(operand, pd.Series):
            return ~operand
        return not operand
    
    def _is_true(self, value: Any) -> bool:
        """判断值是否为真"""
        if isinstance(value, pd.Series):
            # 对于序列，如果所有值都为真则返回True
            return value.all()
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)