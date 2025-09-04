#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信函数注册表

管理所有内置函数的注册、查找和调用。
"""

from typing import Dict, List, Optional, Set, Callable, Any
from collections import defaultdict
from .base import TDXFunction, FunctionCategory
from ..errors.exceptions import TDXNameError


class FunctionRegistry:
    """
    函数注册表
    
    负责管理所有通达信函数的注册、查找和调用。
    """
    
    def __init__(self):
        """
        初始化注册表
        """
        self._functions: Dict[str, TDXFunction] = {}
        self._categories: Dict[FunctionCategory, Set[str]] = defaultdict(set)
        self._aliases: Dict[str, str] = {}  # 函数别名映射
    
    def register(self, function: TDXFunction, aliases: Optional[List[str]] = None):
        """
        注册函数
        
        Args:
            function: 函数实例
            aliases: 函数别名列表
            
        Raises:
            ValueError: 函数名冲突
        """
        name = function.name.upper()
        
        # 检查函数名冲突
        if name in self._functions:
            raise ValueError(f"Function '{name}' is already registered")
        
        # 注册函数
        self._functions[name] = function
        self._categories[function.category].add(name)
        
        # 注册别名
        if aliases:
            for alias in aliases:
                alias = alias.upper()
                if alias in self._functions or alias in self._aliases:
                    raise ValueError(f"Alias '{alias}' conflicts with existing function or alias")
                self._aliases[alias] = name
    
    def register_simple(self, name: str, category: FunctionCategory, description: str,
                       parameters: List, calculate_func: Callable, aliases: Optional[List[str]] = None):
        """
        注册简单函数
        
        Args:
            name: 函数名
            category: 函数分类
            description: 函数描述
            parameters: 参数列表
            calculate_func: 计算函数
            aliases: 函数别名列表
        """
        from .base import create_simple_function
        
        function = create_simple_function(name, category, description, parameters, calculate_func)
        self.register(function, aliases)
    
    def get(self, name: str) -> TDXFunction:
        """
        获取函数
        
        Args:
            name: 函数名或别名
            
        Returns:
            TDXFunction: 函数实例
            
        Raises:
            TDXNameError: 函数未找到
        """
        name = name.upper()
        
        # 检查直接函数名
        if name in self._functions:
            return self._functions[name]
        
        # 检查别名
        if name in self._aliases:
            return self._functions[self._aliases[name]]
        
        # 函数未找到
        available_names = list(self._functions.keys()) + list(self._aliases.keys())
        raise TDXNameError(
            f"Function '{name}' is not defined",
            name=name,
            available_names=available_names
        )
    
    def has(self, name: str) -> bool:
        """
        检查函数是否存在
        
        Args:
            name: 函数名或别名
            
        Returns:
            bool: 函数是否存在
        """
        name = name.upper()
        return name in self._functions or name in self._aliases
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        调用函数
        
        Args:
            name: 函数名或别名
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 函数结果
        """
        function = self.get(name)
        return function(*args, **kwargs)
    
    def list_functions(self, category: Optional[FunctionCategory] = None) -> List[str]:
        """
        列出函数名
        
        Args:
            category: 函数分类过滤
            
        Returns:
            List[str]: 函数名列表
        """
        if category is None:
            return sorted(self._functions.keys())
        else:
            return sorted(self._categories[category])
    
    def list_categories(self) -> List[FunctionCategory]:
        """
        列出所有函数分类
        
        Returns:
            List[FunctionCategory]: 分类列表
        """
        return list(self._categories.keys())
    
    def get_functions_by_category(self, category: FunctionCategory) -> List[TDXFunction]:
        """
        按分类获取函数
        
        Args:
            category: 函数分类
            
        Returns:
            List[TDXFunction]: 函数列表
        """
        function_names = self._categories[category]
        return [self._functions[name] for name in sorted(function_names)]
    
    def search_functions(self, keyword: str) -> List[TDXFunction]:
        """
        搜索函数
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            List[TDXFunction]: 匹配的函数列表
        """
        keyword = keyword.upper()
        matches = []
        
        for name, function in self._functions.items():
            # 检查函数名
            if keyword in name:
                matches.append(function)
                continue
            
            # 检查描述
            if keyword.lower() in function.description.lower():
                matches.append(function)
                continue
        
        return matches
    
    def get_function_help(self, name: str) -> str:
        """
        获取函数帮助信息
        
        Args:
            name: 函数名
            
        Returns:
            str: 帮助信息
        """
        function = self.get(name)
        return function.get_help()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取注册表统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        category_counts = {}
        for category, functions in self._categories.items():
            category_counts[category.name] = len(functions)
        
        return {
            'total_functions': len(self._functions),
            'total_aliases': len(self._aliases),
            'categories': len(self._categories),
            'category_counts': category_counts,
        }
    
    def validate_all(self) -> List[str]:
        """
        验证所有注册的函数
        
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        
        for name, function in self._functions.items():
            try:
                # 验证函数定义
                function._validate_definition()
            except Exception as e:
                errors.append(f"Function '{name}': {str(e)}")
        
        return errors
    
    def clear(self):
        """
        清空注册表
        """
        self._functions.clear()
        self._categories.clear()
        self._aliases.clear()
    
    def unregister(self, name: str):
        """
        注销函数
        
        Args:
            name: 函数名
            
        Raises:
            TDXNameError: 函数未找到
        """
        name = name.upper()
        
        if name not in self._functions:
            raise TDXNameError(f"Function '{name}' is not registered")
        
        function = self._functions[name]
        
        # 移除函数
        del self._functions[name]
        self._categories[function.category].discard(name)
        
        # 移除相关别名
        aliases_to_remove = [alias for alias, func_name in self._aliases.items() if func_name == name]
        for alias in aliases_to_remove:
            del self._aliases[alias]
    
    def export_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        导出函数定义
        
        Returns:
            Dict[str, Dict[str, Any]]: 函数定义字典
        """
        definitions = {}
        
        for name, function in self._functions.items():
            definitions[name] = {
                'name': function.name,
                'category': function.category.name,
                'description': function.description,
                'signature': function.get_signature(),
                'parameters': [
                    {
                        'name': param.name,
                        'type': param.param_type.name,
                        'required': param.required,
                        'default': param.default_value,
                        'description': param.description,
                    }
                    for param in function.parameters
                ],
            }
        
        return definitions
    
    def __len__(self) -> int:
        """返回注册函数的数量"""
        return len(self._functions)
    
    def __contains__(self, name: str) -> bool:
        """检查函数是否存在"""
        return self.has(name)
    
    def __iter__(self):
        """迭代所有函数"""
        return iter(self._functions.values())
    
    def __str__(self) -> str:
        return f"FunctionRegistry({len(self._functions)} functions, {len(self._categories)} categories)"
    
    def __repr__(self) -> str:
        return f"FunctionRegistry(functions={len(self._functions)}, aliases={len(self._aliases)})"