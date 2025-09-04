# 通达信公式解释器使用指南

## 📦 安装方法

### 方法1：本地开发安装

```bash
# 克隆或下载项目到本地
cd pytdx

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装（推荐）
pip install -e .
```

### 方法2：直接使用

如果不想安装，可以直接将项目目录添加到Python路径：

```python
import sys
import os
sys.path.insert(0, '/path/to/pytdx')  # 替换为实际路径

from tdx_interpreter import evaluate, TDXInterpreter
```

## 🚀 快速开始

### 基本使用

```python
from tdx_interpreter import evaluate
import pandas as pd

# 创建K线数据
data = pd.DataFrame({
    'OPEN': [10.0, 10.5, 11.0, 10.8, 11.2],
    'HIGH': [10.8, 11.2, 11.5, 11.0, 11.8],
    'LOW': [9.8, 10.2, 10.5, 10.5, 10.9],
    'CLOSE': [10.5, 11.0, 10.8, 11.2, 11.5],
    'VOLUME': [1000, 1200, 800, 1500, 900]
})

# 计算5日移动平均线
ma5 = evaluate("MA(CLOSE, 5)", context=data)
print(ma5)

# 计算RSI指标
rsi = evaluate("RSI(CLOSE, 14)", context=data)
print(rsi)

# 判断金叉信号
cross_signal = evaluate("CROSS(MA(CLOSE, 5), MA(CLOSE, 10))", context=data)
print(cross_signal)
```

### 高级用法

```python
from tdx_interpreter import TDXInterpreter

# 创建解释器实例
interpreter = TDXInterpreter()

# 注册自定义函数
def price_strength(close_prices, period):
    """价格强度指标"""
    return (close_prices / close_prices.rolling(period).mean() - 1) * 100

interpreter.register_function("STRENGTH", price_strength)

# 使用自定义函数
result = interpreter.evaluate("STRENGTH(CLOSE, 20)", context=data)
print(result)

# 复杂公式
complex_formula = """
MA5 := MA(CLOSE, 5);
MA20 := MA(CLOSE, 20);
IF(MA5 > MA20 AND VOLUME > MA(VOLUME, 10), 1, 0)
"""

signal = interpreter.evaluate(complex_formula, context=data)
print(signal)
```

### 从文件加载公式

```python
from tdx_interpreter import TDXInterpreter

# 创建解释器实例
interpreter = TDXInterpreter()

# 方法1：先加载公式，再计算
formula = interpreter.load_from_file('my_formula.txt')
result = interpreter.evaluate(formula, context=data)

# 方法2：直接从文件计算
result = interpreter.evaluate_file('my_formula.txt', context=data)

# 支持不同编码格式
result = interpreter.evaluate_file('gbk_formula.txt', context=data, encoding='gbk')
```

#### 公式文件格式

公式文件应该是纯文本文件（.txt格式），内容示例：

**ma5.txt**:
```
MA(CLOSE, 5)
```

**complex_strategy.txt**:
```
# 这是注释
MA5 := MA(CLOSE, 5);
MA20 := MA(CLOSE, 20);
IF(MA5 > MA20, 1, 0)
```

**macd_signal.txt**:
```
MACD(CLOSE, 12, 26, 9)
```

#### 错误处理

```python
from tdx_interpreter.errors.exceptions import TDXError

try:
    result = interpreter.evaluate_file('formula.txt', context=data)
except TDXError as e:
    print(f"公式执行错误: {e}")
```

## 📊 支持的函数

### 技术指标函数 (8个)
- **MA**: 简单移动平均线
- **EMA**: 指数移动平均线
- **SMA**: 平滑移动平均线
- **MACD**: MACD指标
- **RSI**: 相对强弱指标
- **BOLL**: 布林带指标
- **KDJ**: KDJ随机指标
- **ATR**: 平均真实波幅

### 数学运算函数 (13个)
- **ABS**: 绝对值
- **MAX/MIN**: 最大值/最小值
- **SUM**: 求和
- **COUNT**: 计数
- **HHV/LLV**: 最高值/最低值
- **SQRT**: 平方根
- **POW**: 幂运算
- **ROUND/FLOOR/CEIL**: 取整函数
- **AVERAGE**: 平均值

### 逻辑判断函数 (10个)
- **IF**: 条件判断
- **AND/OR/NOT**: 逻辑运算
- **BETWEEN**: 区间判断
- **EVERY/EXIST**: 条件统计
- **IFF/IFN**: 特殊条件函数
- **RANGE**: 范围限制

### 时序数据函数 (10个)
- **REF**: 引用历史数据
- **BARSLAST**: 上次条件成立周期数
- **CROSS**: 交叉判断
- **FILTER**: 信号过滤
- **BACKSET**: 向前赋值
- 等等...

### 统计分析函数 (10个)
- **STD/VAR**: 标准差/方差
- **CORR**: 相关系数
- **SLOPE**: 线性回归斜率
- **FORCAST**: 线性回归预测
- 等等...

## 🔧 实用示例

### 1. 技术分析策略

```python
# 双均线策略
strategy = """
MA5 := MA(CLOSE, 5);
MA20 := MA(CLOSE, 20);
GOLDEN_CROSS := CROSS(MA5, MA20);
DEATH_CROSS := CROSS(MA20, MA5);
IF(GOLDEN_CROSS, 1, IF(DEATH_CROSS, -1, 0))
"""

signals = interpreter.evaluate(strategy, context=data)
print("交易信号:", signals)
```

### 2. 风险控制

```python
# 波动率过滤
volatility_filter = """
ATR_14 := ATR(HIGH, LOW, CLOSE, 14);
AVG_ATR := MA(ATR_14, 20);
HIGH_VOL := ATR_14 > AVG_ATR * 1.5;
IF(HIGH_VOL, 0, 1)
"""

filter_result = interpreter.evaluate(volatility_filter, context=data)
print("波动率过滤:", filter_result)
```

### 3. 多指标综合

```python
# 综合信号
composite_signal = """
RSI_14 := RSI(CLOSE, 14);
MA_SIGNAL := IF(MA(CLOSE, 5) > MA(CLOSE, 20), 1, 0);
RSI_SIGNAL := IF(RSI_14 > 30 AND RSI_14 < 70, 1, 0);
VOL_SIGNAL := IF(VOLUME > MA(VOLUME, 10), 1, 0);
MA_SIGNAL AND RSI_SIGNAL AND VOL_SIGNAL
"""

composite = interpreter.evaluate(composite_signal, context=data)
print("综合信号:", composite)
```

## 🛠️ 调试和错误处理

### 启用调试模式

```python
interpreter = TDXInterpreter()
interpreter.set_debug_mode(True)

# 这将输出详细的解析和计算过程
result = interpreter.evaluate("MA(CLOSE, 5)", context=data)
```

### 错误处理

```python
from tdx_interpreter.errors import TDXError, TDXSyntaxError, TDXRuntimeError

try:
    result = evaluate("INVALID_FORMULA()", context=data)
except TDXSyntaxError as e:
    print(f"语法错误: {e}")
except TDXRuntimeError as e:
    print(f"运行时错误: {e}")
except TDXError as e:
    print(f"通用错误: {e}")
```

### 公式验证

```python
from tdx_interpreter import validate, parse

# 验证语法
if validate("MA(CLOSE, 5)"):
    print("公式语法正确")

# 查看AST结构
ast = parse("MA(CLOSE, 5)")
print(f"AST类型: {type(ast.body[0]).__name__}")
```

## 📈 性能优化建议

1. **批量计算**: 一次计算多个指标比分别计算更高效
2. **数据预处理**: 确保输入数据格式正确，避免类型转换开销
3. **缓存结果**: 对于重复使用的计算结果进行缓存
4. **合理的数据量**: 避免在过大的数据集上进行复杂计算

## 🔍 函数查询

```python
from tdx_interpreter.functions import registry

# 查看所有函数
all_functions = registry.list_functions()
print(f"总共 {len(all_functions)} 个函数")

# 搜索函数
ma_functions = registry.search_functions("MA")
print(f"包含MA的函数: {[f.name for f in ma_functions]}")

# 获取函数帮助
help_text = registry.get_function_help("MA")
print(help_text)

# 查看统计信息
stats = registry.get_statistics()
print(f"函数统计: {stats}")
```

## ❓ 常见问题

### Q: 如何处理缺失数据？
A: 库会自动处理NaN值，大多数函数都能正确处理缺失数据。

### Q: 支持哪些数据格式？
A: 主要支持pandas DataFrame，列名应为标准的OHLCV格式。

### Q: 如何添加自定义指标？
A: 使用`interpreter.register_function()`方法注册自定义函数。

### Q: 性能如何？
A: 在20条K线数据上，平均每个公式计算时间约0.5毫秒。

### Q: 与通达信的兼容性如何？
A: 高度兼容，支持通达信的主要语法和函数，计算结果保持一致。

## 📞 技术支持

- 查看更多示例: `python examples/basic_usage.py`
- 运行完整测试: `python test_library_usage.py`
- 查看源码: 项目GitHub仓库
- 问题反馈: 提交Issue或Pull Request

---

**注意**: 本库仅用于学习和研究目的，不构成投资建议。使用本工具进行交易决策的风险由用户自行承担。