#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标管理器

提供统一的指标注册、管理和计算接口，支持指标的动态加载和组合。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Type, Union, Callable
from dataclasses import dataclass
import inspect
import importlib
from pathlib import Path

from .base import BaseIndicatorModule, IndicatorResult, IndicatorType
from .filter_layer import FilterLayer
from .composite import CompositeIndicator


@dataclass
class IndicatorInfo:
    """
    指标信息
    
    存储指标的元数据信息
    """
    name: str                           # 指标名称
    class_name: str                     # 类名
    indicator_type: IndicatorType       # 指标类型
    description: str                    # 描述
    parameters: Dict[str, Any]          # 参数信息
    module_path: str                    # 模块路径
    is_builtin: bool = True            # 是否内置指标


class IndicatorManager:
    """
    指标管理器
    
    统一管理所有技术指标，提供注册、创建、计算等功能。
    """
    
    def __init__(self):
        """
        初始化指标管理器
        """
        self._indicators: Dict[str, Type[BaseIndicatorModule]] = {}
        self._indicator_info: Dict[str, IndicatorInfo] = {}
        self._instances: Dict[str, BaseIndicatorModule] = {}
        self._composite_indicators: Dict[str, CompositeIndicator] = {}
        self._filter_layers: Dict[str, FilterLayer] = {}
        
        # 自动注册内置指标
        self._register_builtin_indicators()
    
    def _register_builtin_indicators(self) -> None:
        """
        注册内置指标
        """
        try:
            from .builtin import (
                MovingAverageModule, RSIModule, MACDModule, 
                BollingerBandsModule, ATRModule, KDJModule, VolumeModule
            )
            
            builtin_indicators = [
                MovingAverageModule,
                RSIModule,
                MACDModule,
                BollingerBandsModule,
                ATRModule,
                KDJModule,
                VolumeModule
            ]
            
            for indicator_class in builtin_indicators:
                self.register_indicator(indicator_class)
                
        except ImportError as e:
            print(f"Warning: Failed to import builtin indicators: {e}")
    
    def register_indicator(self, 
                          indicator_class: Type[BaseIndicatorModule],
                          name: str = None) -> bool:
        """
        注册指标类
        
        Args:
            indicator_class: 指标类
            name: 指标名称，如果为None则使用类名
            
        Returns:
            bool: 是否注册成功
        """
        if not issubclass(indicator_class, BaseIndicatorModule):
            raise ValueError(f"Class {indicator_class.__name__} must inherit from BaseIndicatorModule")
        
        class_name = indicator_class.__name__
        indicator_name = name or class_name
        
        # 获取参数信息
        init_signature = inspect.signature(indicator_class.__init__)
        parameters = {}
        for param_name, param in init_signature.parameters.items():
            if param_name != 'self':
                parameters[param_name] = {
                    'type': param.annotation if param.annotation != inspect.Parameter.empty else 'Any',
                    'default': param.default if param.default != inspect.Parameter.empty else None,
                    'required': param.default == inspect.Parameter.empty
                }
        
        # 创建指标信息
        indicator_info = IndicatorInfo(
            name=indicator_name,
            class_name=class_name,
            indicator_type=IndicatorType.CUSTOM,  # 默认类型，实例化后会更新
            description=indicator_class.__doc__ or f"{class_name} indicator",
            parameters=parameters,
            module_path=indicator_class.__module__,
            is_builtin=indicator_class.__module__.startswith('tdx_interpreter.indicators')
        )
        
        self._indicators[indicator_name] = indicator_class
        self._indicator_info[indicator_name] = indicator_info
        
        return True
    
    def create_indicator(self, 
                        name: str, 
                        instance_name: str = None,
                        **kwargs) -> BaseIndicatorModule:
        """
        创建指标实例
        
        Args:
            name: 指标名称
            instance_name: 实例名称，如果为None则使用指标名称
            **kwargs: 指标参数
            
        Returns:
            BaseIndicatorModule: 指标实例
        """
        if name not in self._indicators:
            raise ValueError(f"Indicator '{name}' not found. Available indicators: {list(self._indicators.keys())}")
        
        indicator_class = self._indicators[name]
        
        try:
            instance = indicator_class(**kwargs)
            
            # 更新指标类型信息
            if hasattr(instance, 'indicator_type'):
                self._indicator_info[name].indicator_type = instance.indicator_type
            
            # 存储实例
            key = instance_name or f"{name}_{id(instance)}"
            self._instances[key] = instance
            
            return instance
            
        except Exception as e:
            raise RuntimeError(f"Failed to create indicator '{name}': {e}")
    
    def get_indicator(self, instance_name: str) -> Optional[BaseIndicatorModule]:
        """
        获取指标实例
        
        Args:
            instance_name: 实例名称
            
        Returns:
            Optional[BaseIndicatorModule]: 指标实例
        """
        return self._instances.get(instance_name)
    
    def calculate_indicator(self, 
                          name: str, 
                          data: pd.DataFrame,
                          instance_name: str = None,
                          **kwargs) -> IndicatorResult:
        """
        计算指标
        
        Args:
            name: 指标名称
            data: K线数据
            instance_name: 实例名称
            **kwargs: 指标参数
            
        Returns:
            IndicatorResult: 计算结果
        """
        # 如果指定了实例名称，使用现有实例
        if instance_name and instance_name in self._instances:
            indicator = self._instances[instance_name]
        else:
            # 创建新实例
            indicator = self.create_indicator(name, instance_name, **kwargs)
        
        return indicator.calculate(data)
    
    def batch_calculate(self, 
                       indicators: Dict[str, Dict[str, Any]], 
                       data: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """
        批量计算指标
        
        Args:
            indicators: 指标配置字典，格式为 {instance_name: {name: str, params: dict}}
            data: K线数据
            
        Returns:
            Dict[str, IndicatorResult]: 计算结果字典
        """
        results = {}
        
        for instance_name, config in indicators.items():
            try:
                indicator_name = config['name']
                params = config.get('params', {})
                
                result = self.calculate_indicator(
                    name=indicator_name,
                    data=data,
                    instance_name=instance_name,
                    **params
                )
                
                results[instance_name] = result
                
            except Exception as e:
                print(f"Warning: Failed to calculate indicator '{instance_name}': {e}")
                continue
        
        return results
    
    def create_composite_indicator(self, 
                                 name: str,
                                 base_indicators: List[Dict[str, Any]],
                                 combination_logic: Callable = None) -> CompositeIndicator:
        """
        创建复合指标
        
        Args:
            name: 复合指标名称
            base_indicators: 基础指标配置列表
            combination_logic: 组合逻辑函数
            
        Returns:
            CompositeIndicator: 复合指标实例
        """
        composite = CompositeIndicator(name)
        
        # 添加基础指标
        for config in base_indicators:
            indicator_name = config['name']
            params = config.get('params', {})
            alias = config.get('alias')
            
            indicator = self.create_indicator(indicator_name, **params)
            composite.add_indicator(indicator, alias)
        
        # 设置组合逻辑
        if combination_logic:
            composite.set_combination_logic(combination_logic)
        
        self._composite_indicators[name] = composite
        return composite
    
    def create_filter_layer(self, 
                          name: str,
                          conditions: List[Dict[str, Any]]) -> FilterLayer:
        """
        创建筛选层
        
        Args:
            name: 筛选层名称
            conditions: 条件配置列表
            
        Returns:
            FilterLayer: 筛选层实例
        """
        filter_layer = FilterLayer(name)
        
        for config in conditions:
            condition_func = config['condition']
            condition_name = config.get('name')
            description = config.get('description', '')
            enabled = config.get('enabled', True)
            
            filter_layer.add_condition(
                condition=condition_func,
                name=condition_name,
                description=description,
                enabled=enabled
            )
        
        self._filter_layers[name] = filter_layer
        return filter_layer
    
    def get_available_indicators(self, 
                               indicator_type: IndicatorType = None) -> List[IndicatorInfo]:
        """
        获取可用指标列表
        
        Args:
            indicator_type: 筛选指标类型
            
        Returns:
            List[IndicatorInfo]: 指标信息列表
        """
        indicators = list(self._indicator_info.values())
        
        if indicator_type:
            indicators = [info for info in indicators if info.indicator_type == indicator_type]
        
        return indicators
    
    def get_indicator_info(self, name: str) -> Optional[IndicatorInfo]:
        """
        获取指标信息
        
        Args:
            name: 指标名称
            
        Returns:
            Optional[IndicatorInfo]: 指标信息
        """
        return self._indicator_info.get(name)
    
    def load_custom_indicators(self, module_path: str) -> int:
        """
        从模块加载自定义指标
        
        Args:
            module_path: 模块路径
            
        Returns:
            int: 加载的指标数量
        """
        try:
            module = importlib.import_module(module_path)
            loaded_count = 0
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (inspect.isclass(attr) and 
                    issubclass(attr, BaseIndicatorModule) and 
                    attr != BaseIndicatorModule):
                    
                    self.register_indicator(attr)
                    loaded_count += 1
            
            return loaded_count
            
        except Exception as e:
            raise RuntimeError(f"Failed to load custom indicators from '{module_path}': {e}")
    
    def clear_instances(self) -> None:
        """清空所有实例"""
        self._instances.clear()
        self._composite_indicators.clear()
        self._filter_layers.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取管理器统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        builtin_count = sum(1 for info in self._indicator_info.values() if info.is_builtin)
        custom_count = len(self._indicator_info) - builtin_count
        
        type_counts = {}
        for info in self._indicator_info.values():
            type_name = info.indicator_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_indicators': len(self._indicators),
            'builtin_indicators': builtin_count,
            'custom_indicators': custom_count,
            'active_instances': len(self._instances),
            'composite_indicators': len(self._composite_indicators),
            'filter_layers': len(self._filter_layers),
            'indicators_by_type': type_counts
        }
    
    def __len__(self) -> int:
        return len(self._indicators)
    
    def __contains__(self, name: str) -> bool:
        return name in self._indicators
    
    def __str__(self) -> str:
        stats = self.get_statistics()
        return f"IndicatorManager({stats['total_indicators']} indicators, {stats['active_instances']} instances)"
    
    def __repr__(self) -> str:
        return self.__str__()


# 全局指标管理器实例
_global_manager = None


def get_indicator_manager() -> IndicatorManager:
    """
    获取全局指标管理器实例
    
    Returns:
        IndicatorManager: 全局管理器实例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = IndicatorManager()
    return _global_manager


def reset_indicator_manager() -> None:
    """重置全局指标管理器"""
    global _global_manager
    _global_manager = None