# 模块化指标系统使用指南

本目录包含了模块化指标系统的使用示例和文档，展示如何使用分层筛选和复合指标进行股票技术分析。

## 系统架构

模块化指标系统采用分层设计，包含以下核心组件：

### 1. 基础指标模块 (Base Indicator Modules)
- **MovingAverageModule**: 移动平均线指标
- **RSIModule**: 相对强弱指数
- **MACDModule**: 指数平滑异同移动平均线
- **BollingerBandsModule**: 布林带指标

### 2. 筛选层 (Filter Layer)
- **FilterLayer**: 条件筛选管理器
- **FilterCondition**: 单个筛选条件
- **PrebuiltFilters**: 预构建筛选器集合

### 3. 复合指标 (Composite Indicators)
- **CompositeIndicator**: 复合指标基类
- **TrendFollowingStrategy**: 趋势跟踪策略
- **MeanReversionStrategy**: 均值回归策略
- **MultiTimeframeStrategy**: 多时间框架策略

### 4. 指标管理器 (Indicator Manager)
- **IndicatorManager**: 指标注册和批量计算管理
- 支持缓存机制和性能优化

## 快速开始

### 1. 基础指标使用

```python
from tdx_interpreter.indicators import MovingAverageModule, RSIModule

# 创建指标实例
ma20 = MovingAverageModule(period=20, ma_type='SMA')
rsi = RSIModule(period=14)

# 计算指标
ma_result = ma20.calculate(data)
rsi_result = rsi.calculate(data)

# 获取结果
ma_values = ma_result.get_series()
rsi_values = rsi_result.get_series()
```

### 2. 筛选层使用

```python
from tdx_interpreter.indicators import FilterLayer, PrebuiltFilters

# 创建筛选层
filter_layer = FilterLayer("股票筛选")

# 添加筛选条件
filter_layer.add_condition(
    lambda data, indicators: data['CLOSE'] > 100,
    "price_filter",
    "价格大于100"
)

# 使用预构建筛选器
trend_filter = PrebuiltFilters.trend_up(period=5)
filter_layer.add_condition(trend_filter, "trend_up", "趋势向上")

# 应用筛选
filtered_data = filter_layer.apply(data, {})
```

### 3. 复合指标使用

```python
from tdx_interpreter.indicators import CompositeIndicator
from tdx_interpreter.indicators.composite import TrendFollowingStrategy

# 使用预定义策略
strategy = TrendFollowingStrategy(
    ma_short_period=5,
    ma_long_period=20,
    rsi_period=14
)

# 计算策略
result = strategy.calculate(data)

# 获取交易信号
signals = strategy.get_signals()
for signal in signals:
    print(f"{signal.timestamp}: {signal.signal_type.value} - 强度: {signal.strength}")
```

### 4. 指标管理器使用

```python
from tdx_interpreter.indicators import get_indicator_manager

# 获取管理器实例
manager = get_indicator_manager()

# 注册指标
manager.register_indicator("MA20", MovingAverageModule(period=20))
manager.register_indicator("RSI14", RSIModule(period=14))

# 批量计算
results = manager.calculate_batch(["MA20", "RSI14"], data)
```

## 示例文件说明

### modular_indicator_example.py

完整的使用示例，包含：

1. **基础指标使用**: 展示如何使用单个技术指标
2. **筛选层使用**: 展示如何创建和应用筛选条件
3. **复合指标使用**: 展示如何组合多个指标
4. **趋势跟踪策略**: 展示预定义策略的使用
5. **指标管理器使用**: 展示批量管理和计算

运行示例：
```bash
python modular_indicator_example.py
```

## 数据格式要求

输入数据应为pandas DataFrame，包含以下列：
- `OPEN`: 开盘价
- `HIGH`: 最高价
- `LOW`: 最低价
- `CLOSE`: 收盘价
- `VOLUME`: 成交量

索引应为日期时间格式。

## 扩展开发

### 创建自定义指标

```python
from tdx_interpreter.indicators.base import BaseIndicatorModule, IndicatorType

class CustomIndicator(BaseIndicatorModule):
    def __init__(self, period: int = 14):
        super().__init__(
            name="Custom",
            description="自定义指标",
            indicator_type=IndicatorType.OSCILLATOR,
            parameters={'period': period}
        )
        self.period = period
    
    def _calculate_impl(self, data: pd.DataFrame) -> pd.Series:
        # 实现自定义计算逻辑
        return data['CLOSE'].rolling(window=self.period).mean()
```

### 创建自定义筛选器

```python
def custom_filter(data, indicators, threshold=0.05):
    """
    自定义筛选器：价格变化幅度筛选
    """
    price_change = data['CLOSE'].pct_change()
    return abs(price_change) > threshold
```

### 创建自定义复合指标

```python
class CustomStrategy(CompositeIndicator):
    def __init__(self):
        super().__init__("自定义策略", "基于多指标的自定义策略")
        
        # 添加基础指标
        self.add_indicator(MovingAverageModule(period=10), "MA10")
        self.add_indicator(RSIModule(period=14), "RSI14")
        
        # 设置组合逻辑
        self.set_combination_logic(self._custom_logic)
    
    def _custom_logic(self, data, indicators):
        # 实现自定义组合逻辑
        pass
```

## 性能优化建议

1. **使用指标管理器**: 利用缓存机制避免重复计算
2. **合理设置参数**: 避免过短或过长的计算周期
3. **批量处理**: 使用批量计算接口提高效率
4. **内存管理**: 及时清理不需要的中间结果

## 常见问题

### Q: 如何处理缺失数据？
A: 系统会自动跳过缺失数据，但建议在输入前进行数据清洗。

### Q: 如何调整指标参数？
A: 在创建指标实例时传入参数，或使用`update_parameters`方法。

### Q: 如何获取指标的详细信息？
A: 使用`get_info()`方法获取指标的名称、类型和参数信息。

### Q: 如何保存和加载指标配置？
A: 可以序列化指标参数，或使用指标管理器的导入导出功能。

## 更多资源

- [API文档](../docs/api.md)
- [开发指南](../docs/development.md)
- [测试用例](../tests/test_modular_indicators.py)