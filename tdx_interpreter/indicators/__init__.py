#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化指标计算框架

提供分层筛选和组合式计算的技术指标框架，支持：
- 基础指标模块化封装
- 筛选条件组合
- 复合指标计算
- 统一的管理接口
"""

# 基础模块
from .base import BaseIndicatorModule, IndicatorResult, IndicatorType
from .filter_layer import FilterLayer, FilterCondition, FilterOperator, PrebuiltFilters
from .composite import CompositeIndicator, SignalType, Signal
from .manager import IndicatorManager, IndicatorInfo, get_indicator_manager, reset_indicator_manager

# 内置指标模块
from .builtin import (
    MovingAverageModule,
    RSIModule, 
    MACDModule,
    BollingerBandsModule,
    ATRModule,
    KDJModule,
    VolumeModule
)

__all__ = [
    # 基础组件
    'BaseIndicatorModule',
    'IndicatorResult', 
    'IndicatorType',
    'FilterLayer',
    'FilterCondition',
    'FilterOperator',
    'PrebuiltFilters',
    'CompositeIndicator',
    'SignalType',
    'Signal',
    
    # 管理器
    'IndicatorManager',
    'IndicatorInfo',
    'get_indicator_manager',
    'reset_indicator_manager',
    
    # 内置指标
    'MovingAverageModule',
    'RSIModule',
    'MACDModule', 
    'BollingerBandsModule',
    'ATRModule',
    'KDJModule',
    'VolumeModule'
]