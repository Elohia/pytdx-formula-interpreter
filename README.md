# 通达信公式解释器 (TDX Formula Interpreter)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](#)

一个完整的通达信公式解释器，支持通达信软件中所有公式语法和内置函数，为量化交易和技术分析提供强大的工具支持。

## ✨ 特性

- 🔍 **完整语法支持**: 支持通达信公式的完整语法结构
- 📊 **内置函数库**: 实现所有通达信内置函数和运算符
- ⚡ **高性能计算**: 优化的计算引擎，支持大规模K线数据处理
- 🎯 **精确兼容**: 与通达信软件公式引擎保持完全兼容
- 🛠️ **开发友好**: 提供详细的错误信息和调试支持
- 📈 **扩展性强**: 支持自定义函数和变量作用域管理

## 🚀 快速开始

### 安装

```bash
pip install tdx-formula-interpreter
```

或从源码安装：

```bash
git clone https://github.com/tdx-formula/interpreter.git
cd interpreter
pip install -e .
```

### 基本使用

```python
from tdx_interpreter import TDXInterpreter, evaluate
import pandas as pd

# 快速计算
result = evaluate("MA(CLOSE, 5)")
print(result)

# 使用解释器实例
interpreter = TDXInterpreter()

# 设置K线数据
data = pd.DataFrame({
    'OPEN': [10.0, 10.5, 11.0, 10.8, 11.2],
    'HIGH': [10.8, 11.2, 11.5, 11.0, 11.8],
    'LOW': [9.8, 10.2, 10.5, 10.5, 10.9],
    'CLOSE': [10.5, 11.0, 10.8, 11.2, 11.5],
    'VOLUME': [1000, 1200, 800, 1500, 900]
})

# 计算技术指标
ma5 = interpreter.evaluate("MA(CLOSE, 5)", context=data)
macd = interpreter.evaluate("MACD(CLOSE, 12, 26, 9)", context=data)
rsi = interpreter.evaluate("RSI(CLOSE, 14)", context=data)

print(f"MA5: {ma5}")
print(f"MACD: {macd}")
print(f"RSI: {rsi}")
```

### 高级用法

```python
# 复杂公式计算
formula = """
MA5 := MA(CLOSE, 5);
MA10 := MA(CLOSE, 10);
GOLDEN_CROSS := CROSS(MA5, MA10);
IF(GOLDEN_CROSS, 1, 0)
"""

result = interpreter.evaluate(formula, context=data)
print(f"Golden Cross Signal: {result}")

# 自定义函数
interpreter.register_function("CUSTOM_MA", lambda x, n: x.rolling(n).mean())
custom_result = interpreter.evaluate("CUSTOM_MA(CLOSE, 20)", context=data)

# 语法验证
from tdx_interpreter import validate
is_valid = validate("MA(CLOSE, 5)")
print(f"Formula is valid: {is_valid}")

# AST解析
from tdx_interpreter import parse
ast = parse("MA(CLOSE, 5)")
print(f"AST: {ast}")
```

### 文件加载功能

支持从txt文件加载通达信公式，方便管理和复用复杂的公式策略：

```python
# 创建公式文件 ma5.txt
# 内容: MA(CLOSE, 5)

# 方法1: 分步加载和计算
formula = interpreter.load_from_file('ma5.txt')
result = interpreter.evaluate(formula, context=data)

# 方法2: 直接从文件计算
result = interpreter.evaluate_file('ma5.txt', context=data)

# 支持带注释的复杂公式文件
# 文件内容示例:
# # 这是一个复合策略
# # 当MA5上穿MA20且RSI小于70时产生买入信号
# IF(CROSS(MA(CLOSE, 5), MA(CLOSE, 20)) AND RSI(CLOSE, 14) < 70, 1, 0)

strategy_result = interpreter.evaluate_file('strategy.txt', context=data)
print(f"Strategy Signal: {strategy_result}")
```

**支持的文件格式：**
- 仅支持 `.txt` 格式文件
- 支持 UTF-8 编码
- 支持 `#`、`//`、`{}` 三种注释风格
- 自动过滤空行和注释行

## 📚 支持的函数

### 技术指标函数

| 函数名 | 说明 | 示例 |
|--------|------|------|
| MA | 简单移动平均 | `MA(CLOSE, 5)` |
| EMA | 指数移动平均 | `EMA(CLOSE, 12)` |
| SMA | 平滑移动平均 | `SMA(CLOSE, 5, 1)` |
| MACD | MACD指标 | `MACD(CLOSE, 12, 26, 9)` |
| KDJ | KDJ指标 | `KDJ(HIGH, LOW, CLOSE, 9)` |
| RSI | 相对强弱指标 | `RSI(CLOSE, 14)` |
| BOLL | 布林带 | `BOLL(CLOSE, 20, 2)` |

### 数学函数

| 函数名 | 说明 | 示例 |
|--------|------|------|
| ABS | 绝对值 | `ABS(CLOSE - OPEN)` |
| MAX | 最大值 | `MAX(HIGH, CLOSE)` |
| MIN | 最小值 | `MIN(LOW, OPEN)` |
| SUM | 求和 | `SUM(VOLUME, 5)` |
| COUNT | 计数 | `COUNT(CLOSE > OPEN, 10)` |
| HHV | 最高值 | `HHV(HIGH, 20)` |
| LLV | 最低值 | `LLV(LOW, 20)` |

### 逻辑函数

| 函数名 | 说明 | 示例 |
|--------|------|------|
| IF | 条件判断 | `IF(CLOSE > OPEN, 1, 0)` |
| AND | 逻辑与 | `AND(CLOSE > MA5, VOLUME > 1000)` |
| OR | 逻辑或 | `OR(CLOSE > HIGH[1], VOLUME > VOLUME[1])` |
| NOT | 逻辑非 | `NOT(CLOSE < OPEN)` |

### 时序函数

| 函数名 | 说明 | 示例 |
|--------|------|------|
| REF | 引用 | `REF(CLOSE, 1)` |
| BARSLAST | 上次条件成立 | `BARSLAST(CLOSE > OPEN)` |
| CROSS | 交叉 | `CROSS(MA5, MA10)` |
| FILTER | 过滤 | `FILTER(CLOSE > OPEN, 5)` |

## 🏗️ 架构设计

```
通达信公式解释器
├── 词法分析器 (Lexer)
│   ├── 标识符识别
│   ├── 操作符识别
│   ├── 数值常量识别
│   └── 关键字识别
├── 语法解析器 (Parser)
│   ├── 表达式解析
│   ├── 函数调用解析
│   ├── 条件语句解析
│   └── AST构建
├── 函数库 (Functions)
│   ├── 技术指标函数
│   ├── 数学运算函数
│   ├── 逻辑判断函数
│   └── 时序数据函数
├── 计算引擎 (Engine)
│   ├── 表达式求值
│   ├── 变量作用域管理
│   ├── 数据上下文管理
│   └── 缓存优化
└── 错误处理 (ErrorHandler)
    ├── 语法错误检测
    ├── 运行时错误处理
    ├── 调试信息输出
    └── 错误恢复机制
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=tdx_interpreter --cov-report=html

# 运行性能测试
pytest tests/performance/ --benchmark-only
```

## 📖 文档

- [完整文档](https://tdx-formula-interpreter.readthedocs.io/)
- [API参考](https://tdx-formula-interpreter.readthedocs.io/api/)
- [函数参考](https://tdx-formula-interpreter.readthedocs.io/functions/)
- [示例代码](examples/)

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/tdx-formula/interpreter.git
cd interpreter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行代码格式化
black tdx_interpreter/
flake8 tdx_interpreter/

# 运行类型检查
mypy tdx_interpreter/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 [tdx_main](https://github.com/BeardedManZhao/tdx_main) 项目提供的基础函数实现
- 感谢 [mathematical-expression](https://github.com/BeardedManZhao/mathematical-expression) 项目的架构设计参考
- 感谢所有贡献者的支持

## 📞 联系我们

- 项目主页: https://github.com/tdx-formula/interpreter
- 问题反馈: https://github.com/tdx-formula/interpreter/issues
- 邮箱: dev@tdxformula.com

---

**注意**: 本项目仅用于学习和研究目的，不构成投资建议。使用本工具进行交易决策的风险由用户自行承担。