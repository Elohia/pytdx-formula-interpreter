#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础指标模块定义

定义了模块化指标计算框架的核心抽象类和接口。
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import time


class IndicatorType(Enum):
    """指标类型枚举"""
    TREND = "trend"              # 趋势指标
    MOMENTUM = "momentum"        # 动量指标  
    OSCILLATOR = "oscillator"    # 震荡指标
    VOLATILITY = "volatility"    # 波动率指标
    VOLUME = "volume"            # 成交量指标
    PRICE = "price"              # 价格指标
    COMPOSITE = "composite"      # 复合指标
    CUSTOM = "custom"            # 自定义指标


@dataclass
class IndicatorResult:
    """
    指标计算结果
    
    封装指标计算的结果数据和相关元信息。
    """
    name: str                           # 指标名称
    data: Union[pd.Series, pd.DataFrame, Tuple]  # 计算结果
    parameters: Dict[str, Any]          # 计算参数
    timestamp: float                    # 计算时间戳
    dependencies: List[str]             # 依赖字段
    cache_key: str                      # 缓存键
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """获取元数据信息（从parameters中提取）"""
        return self.parameters.copy()
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    @property
    def is_series(self) -> bool:
        """是否为Series类型结果"""
        return isinstance(self.data, pd.Series)
    
    @property
    def is_dataframe(self) -> bool:
        """是否为DataFrame类型结果"""
        return isinstance(self.data, pd.DataFrame)
    
    @property
    def is_tuple(self) -> bool:
        """是否为元组类型结果（多个序列）"""
        return isinstance(self.data, tuple)
    
    @property
    def values(self) -> Union[pd.Series, pd.DataFrame, Tuple]:
        """获取计算结果数据（data属性的别名）"""
        return self.data
    
    def get_series(self, index: int = 0) -> pd.Series:
        """
        获取Series结果
        
        Args:
            index: 当结果为元组时，指定要获取的序列索引
            
        Returns:
            pd.Series: 序列数据
        """
        if self.is_series:
            return self.data
        elif self.is_tuple:
            return self.data[index]
        elif self.is_dataframe:
            return self.data.iloc[:, index]
        else:
            raise ValueError(f"Cannot convert {type(self.data)} to Series")


class BaseIndicatorModule(ABC):
    """
    基础指标模块抽象类
    
    所有技术指标模块都应继承此类，提供统一的接口和行为。
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        初始化指标模块
        
        Args:
            name: 指标名称
            parameters: 计算参数
        """
        self.name = name
        self.parameters = parameters or {}
        self._cache: Dict[str, IndicatorResult] = {}
        self._cache_enabled = True
        self._max_cache_size = 100
    
    @property
    @abstractmethod
    def indicator_type(self) -> IndicatorType:
        """指标类型"""
        pass
    
    @property
    @abstractmethod
    def required_fields(self) -> List[str]:
        """获取必需的数据字段"""
        pass
    
    @property
    def optional_fields(self) -> List[str]:
        """获取可选的数据字段"""
        return []
    
    @property
    def default_parameters(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {}
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证输入数据
        
        Args:
            data: 输入的K线数据
            
        Returns:
            bool: 数据是否有效
        """
        # 检查必需字段
        for field in self.required_fields:
            if field not in data.columns:
                raise ValueError(f"Required field '{field}' not found in data")
        
        # 检查数据长度
        if len(data) == 0:
            raise ValueError("Input data is empty")
        
        # 检查数据类型
        for field in self.required_fields:
            if not pd.api.types.is_numeric_dtype(data[field]):
                raise ValueError(f"Field '{field}' must be numeric")
        
        return True
    
    def validate_parameters(self) -> bool:
        """
        验证计算参数
        
        Returns:
            bool: 参数是否有效
        """
        # 合并默认参数
        merged_params = {**self.default_parameters, **self.parameters}
        
        # 子类可以重写此方法进行具体的参数验证
        return True
    
    def _generate_cache_key(self, data: pd.DataFrame, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            data: 输入数据
            **kwargs: 额外参数
            
        Returns:
            str: 缓存键
        """
        # 使用数据哈希、参数和模块名生成唯一键
        data_hash = hashlib.md5(str(data.values.tobytes()).encode()).hexdigest()[:8]
        params_str = str(sorted({**self.parameters, **kwargs}.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        
        return f"{self.name}_{data_hash}_{params_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[IndicatorResult]:
        """
        从缓存获取结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Optional[IndicatorResult]: 缓存的结果，如果不存在则返回None
        """
        if not self._cache_enabled:
            return None
        
        return self._cache.get(cache_key)
    
    def _save_to_cache(self, cache_key: str, result: IndicatorResult) -> None:
        """
        保存结果到缓存
        
        Args:
            cache_key: 缓存键
            result: 计算结果
        """
        if not self._cache_enabled:
            return
        
        # 限制缓存大小
        if len(self._cache) >= self._max_cache_size:
            # 删除最旧的缓存项
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest_key]
        
        self._cache[cache_key] = result
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def enable_cache(self, enabled: bool = True) -> None:
        """启用或禁用缓存"""
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
    
    @abstractmethod
    def _calculate_impl(self, data: pd.DataFrame, **kwargs) -> Union[pd.Series, pd.DataFrame, Tuple]:
        """
        具体的计算实现
        
        子类必须实现此方法来定义具体的指标计算逻辑。
        
        Args:
            data: 输入的K线数据
            **kwargs: 额外的计算参数
            
        Returns:
            Union[pd.Series, pd.DataFrame, Tuple]: 计算结果
        """
        pass
    
    def calculate(self, data: pd.DataFrame, use_cache: bool = True, **kwargs) -> IndicatorResult:
        """
        计算指标值
        
        Args:
            data: 输入的K线数据
            use_cache: 是否使用缓存
            **kwargs: 额外的计算参数
            
        Returns:
            IndicatorResult: 指标计算结果
        """
        # 验证数据和参数
        self.validate_data(data)
        self.validate_parameters()
        
        # 合并参数
        merged_params = {**self.default_parameters, **self.parameters, **kwargs}
        
        # 生成缓存键
        cache_key = self._generate_cache_key(data, **merged_params)
        
        # 尝试从缓存获取
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
        
        # 执行计算
        calc_result = self._calculate_impl(data, **merged_params)
        
        # 封装结果
        result = IndicatorResult(
            name=self.name,
            data=calc_result,
            parameters=merged_params,
            timestamp=time.time(),
            dependencies=self.required_fields + self.optional_fields,
            cache_key=cache_key
        )
        
        # 保存到缓存
        if use_cache:
            self._save_to_cache(cache_key, result)
        
        return result
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', params={self.parameters})"
    
    def __repr__(self) -> str:
        return self.__str__()