# 模块化指标计算框架设计

## 概述

本文档描述了通达信公式解释器的模块化指标计算框架设计，采用分层筛选的架构思路，支持将基础指标像积木一样组合成复杂的综合指标。

## 设计理念

### 核心思想
- **模块化设计**：将复杂指标分解为可复用的基础模块
- **分层筛选**：通过多层过滤逐步精炼数据和信号
- **组合式计算**：支持基础指标的灵活组合和嵌套
- **可扩展性**：便于添加新的指标模块和筛选逻辑

### 架构层次
```
┌─────────────────────────────────────┐
│           复合指标层                 │
│    (综合策略、交易信号)              │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           筛选过滤层                 │
│    (条件筛选、信号过滤)              │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           基础指标层                 │
│    (MA, RSI, MACD, BOLL等)         │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           数据输入层                 │
│    (OHLCV K线数据)                  │
└─────────────────────────────────────┘
```

## 核心组件设计

### 1. 基础指标模块 (BaseIndicatorModule)

```python
class BaseIndicatorModule:
    """
    基础指标模块抽象类
    
    所有技术指标都应继承此类，提供统一的接口
    """
    
    def __init__(self, name: str, parameters: dict = None):
        self.name = name
        self.parameters = parameters or {}
        self.cache = {}
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> Union[pd.Series, tuple]:
        """计算指标值"""
        raise NotImplementedError
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证输入数据"""
        raise NotImplementedError
    
    def get_dependencies(self) -> list:
        """获取依赖的数据字段"""
        raise NotImplementedError
```

### 2. 筛选过滤层 (FilterLayer)

```python
class FilterLayer:
    """
    筛选过滤层
    
    支持多种筛选条件的组合和链式调用
    """
    
    def __init__(self):
        self.filters = []
    
    def add_condition(self, condition: callable, name: str = None):
        """添加筛选条件"""
        self.filters.append({
            'condition': condition,
            'name': name or f'filter_{len(self.filters)}'
        })
        return self
    
    def apply(self, data: pd.DataFrame, indicators: dict) -> pd.DataFrame:
        """应用所有筛选条件"""
        result = data.copy()
        
        for filter_info in self.filters:
            condition = filter_info['condition']
            mask = condition(result, indicators)
            result = result[mask]
        
        return result
```

### 3. 复合指标计算器 (CompositeIndicator)

```python
class CompositeIndicator:
    """
    复合指标计算器
    
    支持多个基础指标的组合计算
    """
    
    def __init__(self, name: str):
        self.name = name
        self.base_indicators = []
        self.filter_layers = []
        self.combination_logic = None
    
    def add_indicator(self, indicator: BaseIndicatorModule):
        """添加基础指标"""
        self.base_indicators.append(indicator)
        return self
    
    def add_filter_layer(self, filter_layer: FilterLayer):
        """添加筛选层"""
        self.filter_layers.append(filter_layer)
        return self
    
    def set_combination_logic(self, logic: callable):
        """设置组合逻辑"""
        self.combination_logic = logic
        return self
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """计算复合指标"""
        # 1. 计算所有基础指标
        indicators = {}
        for indicator in self.base_indicators:
            indicators[indicator.name] = indicator.calculate(data)
        
        # 2. 应用筛选层
        filtered_data = data
        for filter_layer in self.filter_layers:
            filtered_data = filter_layer.apply(filtered_data, indicators)
        
        # 3. 应用组合逻辑
        if self.combination_logic:
            return self.combination_logic(filtered_data, indicators)
        
        return filtered_data
```

## 实际应用场景

### 场景1: 多重确认的买入信号

```python
# 基础指标层
ma5 = MovingAverageModule('MA5', {'period': 5})
ma20 = MovingAverageModule('MA20', {'period': 20})
rsi = RSIModule('RSI14', {'period': 14})
volume_ma = MovingAverageModule('VOL_MA5', {'period': 5, 'field': 'VOLUME'})

# 筛选层1: 趋势筛选
trend_filter = FilterLayer()
trend_filter.add_condition(
    lambda data, indicators: indicators['MA5'] > indicators['MA20'],
    'uptrend'
)

# 筛选层2: 超买筛选
overbought_filter = FilterLayer()
overbought_filter.add_condition(
    lambda data, indicators: indicators['RSI14'] < 70,
    'not_overbought'
)

# 筛选层3: 成交量确认
volume_filter = FilterLayer()
volume_filter.add_condition(
    lambda data, indicators: data['VOLUME'] > indicators['VOL_MA5'] * 1.2,
    'volume_confirmation'
)

# 复合指标: 买入信号
buy_signal = CompositeIndicator('BUY_SIGNAL')
buy_signal.add_indicator(ma5)
buy_signal.add_indicator(ma20)
buy_signal.add_indicator(rsi)
buy_signal.add_indicator(volume_ma)
buy_signal.add_filter_layer(trend_filter)
buy_signal.add_filter_layer(overbought_filter)
buy_signal.add_filter_layer(volume_filter)
buy_signal.set_combination_logic(
    lambda data, indicators: pd.Series(
        (indicators['MA5'] > indicators['MA20']) & 
        (indicators['RSI14'] < 70) & 
        (data['VOLUME'] > indicators['VOL_MA5'] * 1.2),
        index=data.index
    )
)
```

### 场景2: 动态止损策略

```python
# 基础指标层
atr = ATRModule('ATR14', {'period': 14})
ema = EMAModule('EMA20', {'period': 20})
highest_high = HighestModule('HH10', {'period': 10, 'field': 'HIGH'})

# 筛选层: 波动率筛选
volatility_filter = FilterLayer()
volatility_filter.add_condition(
    lambda data, indicators: indicators['ATR14'] > indicators['ATR14'].rolling(20).mean(),
    'high_volatility'
)

# 复合指标: 动态止损位
stop_loss = CompositeIndicator('DYNAMIC_STOP_LOSS')
stop_loss.add_indicator(atr)
stop_loss.add_indicator(ema)
stop_loss.add_indicator(highest_high)
stop_loss.add_filter_layer(volatility_filter)
stop_loss.set_combination_logic(
    lambda data, indicators: pd.Series(
        indicators['HH10'] - indicators['ATR14'] * 2,
        index=data.index
    )
)
```

## 优势特点

### 1. 模块化复用
- 基础指标可在多个策略中复用
- 筛选逻辑可独立测试和优化
- 组合逻辑清晰可读

### 2. 分层处理
- 每层专注特定的筛选逻辑
- 便于调试和性能优化
- 支持条件的渐进式应用

### 3. 灵活扩展
- 易于添加新的基础指标
- 支持自定义筛选条件
- 组合逻辑可动态调整

### 4. 性能优化
- 支持计算结果缓存
- 惰性计算避免不必要的运算
- 并行计算支持

## 实现计划

1. **第一阶段**: 实现基础指标模块框架
2. **第二阶段**: 实现筛选过滤层
3. **第三阶段**: 实现复合指标计算器
4. **第四阶段**: 创建实际应用示例
5. **第五阶段**: 性能优化和测试

## 总结

通过模块化设计和分层筛选的架构，用户可以像搭积木一样构建复杂的技术指标和交易策略。这种设计不仅提高了代码的复用性和可维护性，还为量化交易策略的开发提供了强大而灵活的工具。