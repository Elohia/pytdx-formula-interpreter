# 通达信公式解释器 (TDX Formula Interpreter)

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)](#)

一个功能完整的通达信公式解释器，支持通达信公式语法的解析、执行和计算。

## ✨ 特性

- 🔍 **完整语法支持**: 支持通达信公式的完整语法规范
- 📊 **技术指标**: 内置常用技术指标函数 (MA, MACD, RSI, BOLL等)
- 🧮 **数学运算**: 支持基础数学运算和高级数学函数
- 🔗 **逻辑判断**: 支持条件判断和逻辑运算
- 📈 **时间序列**: 支持引用历史数据和时间序列操作
- 🎯 **类型安全**: 完整的类型检查和错误处理
- 📝 **易于使用**: 简洁的API设计，支持文件加载
- 🧪 **测试覆盖**: 完整的单元测试覆盖

## 🚀 快速开始

### 安装

```bash
pip install pytdx-interpreter
```

### 基本使用

```python
from tdx_interpreter import evaluate, TdxInterpreter

# 简单计算
result = evaluate("MA(CLOSE, 5)")
print(result)  # 5日移动平均线

# 复杂公式
formula = """
MA5: MA(CLOSE, 5);
MA10: MA(CLOSE, 10);
BUY: CROSS(MA5, MA10);
"""

interpreter = TdxInterpreter()
result = interpreter.evaluate(formula)
print(result)
```

### 文件加载

```python
from tdx_interpreter import TdxInterpreter

interpreter = TdxInterpreter()

# 从文件加载公式
result = interpreter.evaluate_file("my_formula.txt")
print(result)
```

## 📖 高级用法

### 自定义上下文

```python
import numpy as np
from tdx_interpreter import TdxInterpreter

# 提供自定义数据
context = {
    'CLOSE': np.array([10, 11, 12, 11, 13]),
    'VOLUME': np.array([1000, 1100, 1200, 900, 1300])
}

interpreter = TdxInterpreter()
result = interpreter.evaluate("MA(CLOSE, 3)", context)
print(result)
```

### 错误处理

```python
from tdx_interpreter import TdxInterpreter, TdxSyntaxError, TdxRuntimeError

interpreter = TdxInterpreter()

try:
    result = interpreter.evaluate("INVALID_FUNCTION(CLOSE)")
except TdxSyntaxError as e:
    print(f"语法错误: {e}")
except TdxRuntimeError as e:
    print(f"运行时错误: {e}")
```

## 📁 文件加载功能

解释器支持从文件加载通达信公式：

```python
from tdx_interpreter import TdxInterpreter

interpreter = TdxInterpreter()

# 方法1: 直接从文件评估
result = interpreter.evaluate_file("formulas/ma_cross.txt")

# 方法2: 加载文件内容后评估
with open("formulas/complex_strategy.txt", "r", encoding="utf-8") as f:
    formula_content = f.read()
    result = interpreter.evaluate(formula_content)
```

支持的文件格式：
- `.txt` - 纯文本格式
- `.tdx` - 通达信公式文件
- 任何包含通达信公式语法的文本文件

## 🔧 支持的函数

### 技术指标
- `MA(data, period)` - 移动平均线
- `EMA(data, period)` - 指数移动平均线
- `MACD(close, fast, slow, signal)` - MACD指标
- `RSI(data, period)` - 相对强弱指标
- `BOLL(data, period, std_dev)` - 布林带
- `KDJ(high, low, close, period)` - KDJ指标

### 数学函数
- `ABS(x)` - 绝对值
- `MAX(a, b)` - 最大值
- `MIN(a, b)` - 最小值
- `SQRT(x)` - 平方根
- `POW(x, y)` - 幂运算
- `LOG(x)` - 自然对数

### 逻辑函数
- `IF(condition, true_value, false_value)` - 条件判断
- `AND(a, b)` - 逻辑与
- `OR(a, b)` - 逻辑或
- `NOT(x)` - 逻辑非

### 时间序列
- `REF(data, period)` - 引用历史数据
- `HHV(data, period)` - 最高值
- `LLV(data, period)` - 最低值
- `CROSS(a, b)` - 交叉函数

## 🏗️ 架构设计

项目采用模块化设计：

```
tdx_interpreter/
├── core/           # 核心解释器
│   ├── interpreter.py
│   ├── evaluator.py
│   └── context.py
├── lexer/          # 词法分析器
├── parser/         # 语法分析器
├── functions/      # 函数库
└── errors/         # 异常处理
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_functions.py

# 生成覆盖率报告
pytest --cov=tdx_interpreter
```

## 📚 文档

- [使用指南](USAGE_GUIDE.md)
- [实现计划](IMPLEMENTATION_PLAN.md)
- [API文档](docs/)

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🛠️ 开发环境设置

```bash
# 克隆项目
git clone https://github.com/Elohia/pytdx-formula-interpreter.git
cd pytdx-formula-interpreter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 运行测试
pytest
```

## 📄 许可证

本项目采用 [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) 许可证。

**重要说明**: 本项目仅供非商业用途使用。如需商业使用，请联系项目维护者获取商业许可。

## 🙏 致谢

- 感谢通达信软件提供的公式语法参考
- 感谢所有贡献者的努力

## 📞 联系方式

- 项目主页: [https://github.com/Elohia/pytdx-formula-interpreter](https://github.com/Elohia/pytdx-formula-interpreter)
- 问题反馈: [Issues](https://github.com/Elohia/pytdx-formula-interpreter/issues)
- 邮箱: your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！