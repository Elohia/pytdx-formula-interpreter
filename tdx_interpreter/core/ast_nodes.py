#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器抽象语法树节点定义

定义了所有AST节点类型，用于表示解析后的公式结构。
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union
from dataclasses import dataclass


class ASTNode(ABC):
    """
    抽象语法树节点基类
    
    所有AST节点的基类，定义了通用接口。
    """
    
    @abstractmethod
    def accept(self, visitor):
        """
        访问者模式接口
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问结果
        """
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """
        字符串表示
        """
        pass


@dataclass
class NumberLiteral(ASTNode):
    """
    数值字面量节点
    
    表示数值常量，如：123, 3.14
    """
    
    value: Union[int, float]
    
    def accept(self, visitor):
        return visitor.visit_number_literal(self)
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class StringLiteral(ASTNode):
    """
    字符串字面量节点
    
    表示字符串常量，如："hello"
    """
    
    value: str
    
    def accept(self, visitor):
        return visitor.visit_string_literal(self)
    
    def __str__(self) -> str:
        return f'"{self.value}"'


@dataclass
class Identifier(ASTNode):
    """
    标识符节点
    
    表示变量名或函数名，如：CLOSE, MA
    """
    
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)
    
    def __str__(self) -> str:
        return self.name


@dataclass
class BinaryOperation(ASTNode):
    """
    二元运算节点
    
    表示二元运算，如：a + b, x > y
    """
    
    left: ASTNode
    operator: str
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_binary_operation(self)
    
    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOperation(ASTNode):
    """
    一元运算节点
    
    表示一元运算，如：-x, NOT condition
    """
    
    operator: str
    operand: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_unary_operation(self)
    
    def __str__(self) -> str:
        return f"({self.operator} {self.operand})"


@dataclass
class FunctionCall(ASTNode):
    """
    函数调用节点
    
    表示函数调用，如：MA(CLOSE, 5), IF(condition, true_value, false_value)
    """
    
    name: str
    arguments: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"


@dataclass
class Assignment(ASTNode):
    """
    赋值节点
    
    表示变量赋值，如：MA5 := MA(CLOSE, 5)
    """
    
    name: str
    value: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)
    
    def __str__(self) -> str:
        return f"{self.name} := {self.value}"


@dataclass
class ConditionalExpression(ASTNode):
    """
    条件表达式节点
    
    表示条件表达式，如：IF(condition, true_value, false_value)
    """
    
    condition: ASTNode
    true_value: ASTNode
    false_value: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_conditional_expression(self)
    
    def __str__(self) -> str:
        return f"IF({self.condition}, {self.true_value}, {self.false_value})"


@dataclass
class ArrayAccess(ASTNode):
    """
    数组访问节点
    
    表示数组或时序数据访问，如：CLOSE[1], HIGH[-5]
    """
    
    array: ASTNode
    index: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_array_access(self)
    
    def __str__(self) -> str:
        return f"{self.array}[{self.index}]"


@dataclass
class Block(ASTNode):
    """
    代码块节点
    
    表示一系列语句的集合
    """
    
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_block(self)
    
    def __str__(self) -> str:
        statements_str = "; ".join(str(stmt) for stmt in self.statements)
        return f"{{{statements_str}}}"


@dataclass
class Program(ASTNode):
    """
    程序节点
    
    表示整个公式程序的根节点
    """
    
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_program(self)
    
    def __str__(self) -> str:
        body_str = "\n".join(str(stmt) for stmt in self.body)
        return body_str


class ASTVisitor(ABC):
    """
    AST访问者基类
    
    定义了访问各种AST节点的接口，用于实现不同的AST处理逻辑。
    """
    
    @abstractmethod
    def visit_number_literal(self, node: NumberLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_string_literal(self, node: StringLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass
    
    @abstractmethod
    def visit_assignment(self, node: Assignment) -> Any:
        pass
    
    @abstractmethod
    def visit_conditional_expression(self, node: ConditionalExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_array_access(self, node: ArrayAccess) -> Any:
        pass
    
    @abstractmethod
    def visit_block(self, node: Block) -> Any:
        pass
    
    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass


class ASTPrinter(ASTVisitor):
    """
    AST打印器
    
    用于将AST转换为可读的字符串表示。
    """
    
    def __init__(self, indent: int = 0):
        self.indent = indent
    
    def _indent_str(self) -> str:
        return "  " * self.indent
    
    def visit_number_literal(self, node: NumberLiteral) -> str:
        return f"{self._indent_str()}NumberLiteral({node.value})"
    
    def visit_string_literal(self, node: StringLiteral) -> str:
        return f"{self._indent_str()}StringLiteral(\"{node.value}\")"
    
    def visit_identifier(self, node: Identifier) -> str:
        return f"{self._indent_str()}Identifier({node.name})"
    
    def visit_binary_operation(self, node: BinaryOperation) -> str:
        self.indent += 1
        left_str = node.left.accept(self)
        right_str = node.right.accept(self)
        self.indent -= 1
        return f"{self._indent_str()}BinaryOperation({node.operator})\n{left_str}\n{right_str}"
    
    def visit_unary_operation(self, node: UnaryOperation) -> str:
        self.indent += 1
        operand_str = node.operand.accept(self)
        self.indent -= 1
        return f"{self._indent_str()}UnaryOperation({node.operator})\n{operand_str}"
    
    def visit_function_call(self, node: FunctionCall) -> str:
        self.indent += 1
        args_str = "\n".join(arg.accept(self) for arg in node.arguments)
        self.indent -= 1
        return f"{self._indent_str()}FunctionCall({node.name})\n{args_str}"
    
    def visit_assignment(self, node: Assignment) -> str:
        self.indent += 1
        value_str = node.value.accept(self)
        self.indent -= 1
        return f"{self._indent_str()}Assignment({node.name})\n{value_str}"
    
    def visit_conditional_expression(self, node: ConditionalExpression) -> str:
        self.indent += 1
        condition_str = node.condition.accept(self)
        true_str = node.true_value.accept(self)
        false_str = node.false_value.accept(self)
        self.indent -= 1
        return f"{self._indent_str()}ConditionalExpression\n{condition_str}\n{true_str}\n{false_str}"
    
    def visit_array_access(self, node: ArrayAccess) -> str:
        self.indent += 1
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)
        self.indent -= 1
        return f"{self._indent_str()}ArrayAccess\n{array_str}\n{index_str}"
    
    def visit_block(self, node: Block) -> str:
        self.indent += 1
        statements_str = "\n".join(stmt.accept(self) for stmt in node.statements)
        self.indent -= 1
        return f"{self._indent_str()}Block\n{statements_str}"
    
    def visit_program(self, node: Program) -> str:
        self.indent += 1
        body_str = "\n".join(stmt.accept(self) for stmt in node.body)
        self.indent -= 1
        return f"{self._indent_str()}Program\n{body_str}"