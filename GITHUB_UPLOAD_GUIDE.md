# GitHub 上传指南

本文档记录了将 pytdx-interpreter 项目上传到 GitHub 的完整过程。

## 项目信息

- **项目名称**: pytdx-interpreter (通达信公式解释器)
- **GitHub 仓库**: https://github.com/Elohia/pytdx-formula-interpreter
- **许可证**: CC BY-NC 4.0许可证（非商业）
- **主要语言**: Python
- **项目类型**: 开源库/工具

## 上传内容概览

### 核心文件
- `README.md` - 项目说明文档
- `setup.py` - Python 包配置
- `requirements.txt` - 依赖列表
- `LICENSE` - 许可证文件
- `.gitignore` - Git 忽略规则

### 源代码结构
```
tdx_interpreter/
├── __init__.py          # 包初始化和便捷函数
├── core/                # 核心解释器模块
│   ├── __init__.py
│   ├── ast_nodes.py     # AST 节点定义
│   ├── context.py       # 执行上下文
│   ├── evaluator.py     # 表达式求值器
│   └── interpreter.py   # 主解释器
├── errors/              # 异常处理
│   ├── __init__.py
│   └── exceptions.py    # 自定义异常类
├── functions/           # 函数库
│   ├── __init__.py
│   ├── base.py          # 函数基类
│   ├── builtin_functions.py  # 内置函数注册
│   ├── logical.py       # 逻辑函数
│   ├── mathematical.py  # 数学函数
│   ├── registry.py      # 函数注册器
│   ├── statistical.py   # 统计函数
│   ├── technical.py     # 技术指标函数
│   └── temporal.py      # 时间序列函数
├── indicators/          # 模块化指标系统
│   ├── __init__.py
│   ├── base.py          # 基础指标类
│   ├── builtin.py       # 内置指标
│   ├── composite.py     # 复合指标
│   ├── filter_layer.py  # 筛选层
│   └── manager.py       # 指标管理器
├── lexer/               # 词法分析器
│   ├── __init__.py
│   ├── lexer.py         # 词法分析器实现
│   └── tokens.py        # 令牌定义
└── parser/              # 语法分析器
    ├── __init__.py
    ├── parser.py        # 语法分析器实现
    └── precedence.py    # 运算符优先级
```

### 测试文件
```
tests/
├── __init__.py
├── test_file_loading.py      # 文件加载测试
├── test_modular_indicators.py # 模块化指标测试
└── unit/
    ├── __init__.py
    ├── test_functions.py     # 函数测试
    ├── test_lexer.py         # 词法分析器测试
    └── test_parser.py        # 语法分析器测试
```

### 示例和文档
```
examples/
├── README.md
├── basic_usage.py            # 基础使用示例
├── formula_file_example.py   # 文件加载示例
├── modular_indicator_example.py  # 模块化指标示例
├── modular_indicators_demo.py     # 模块化指标演示
├── sample_formulas/          # 示例公式文件
└── simple_file_demo.py       # 简单文件演示

formula_examples/             # 公式示例文件
docs/
└── MODULAR_INDICATOR_DESIGN.md  # 模块化指标设计文档
```

## 上传过程记录

### 1. 初始提交 (Initial Commit)
- **时间**: 2024年项目开始
- **内容**: 基础项目结构和核心功能
- **提交信息**: "Initial commit: 通达信公式解释器项目 - 核心配置文件和文档"

### 2. 模块化指标系统 (Modular Indicator System)
- **时间**: 最近更新
- **内容**: 新增模块化指标计算框架
- **提交信息**: "feat: 实现模块化指标系统 - 支持基础指标、筛选层、复合指标和指标管理器"
- **变更统计**: 12 files changed, 4262 insertions(+), 3 deletions(-)

### 3. 许可证更新 (License Update)
- **时间**: 最新更新
- **内容**: 将许可证从 MIT 更改为 CC BY-NC 4.0
- **提交信息**: "license: 修改许可证为CC BY-NC 4.0非商业许可证"
- **变更统计**: 5 files changed, 25 insertions(+), 22 deletions(-)

## 项目特色功能

### 1. 完整的通达信公式支持
- 支持通达信公式语法解析
- 内置常用技术指标函数
- 支持数学运算和逻辑判断
- 支持时间序列数据处理

### 2. 模块化指标系统
- **基础指标模块**: 封装常用技术指标
- **筛选层**: 支持条件过滤和数据筛选
- **复合指标**: 支持多个基础指标的组合计算
- **指标管理器**: 统一管理和调度指标计算

### 3. 文件加载功能
- 支持从文件加载通达信公式
- 支持多种文件格式 (.txt, .tdx)
- 提供便捷的文件操作API

### 4. 完整的测试覆盖
- 单元测试覆盖所有核心功能
- 集成测试验证整体功能
- 持续集成确保代码质量

## 使用说明

### 克隆项目
```bash
git clone https://github.com/Elohia/pytdx-formula-interpreter.git
cd pytdx-formula-interpreter
```

### 安装依赖
```bash
pip install -r requirements.txt
pip install -e .
```

### 运行测试
```bash
pytest
```

### 基本使用
```python
from tdx_interpreter import evaluate

# 计算5日移动平均线
result = evaluate("MA(CLOSE, 5)")
print(result)
```

## 许可证说明

项目采用 **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** 许可证：

- ✅ **允许**: 分享、修改、非商业使用
- ❌ **禁止**: 商业用途
- 📝 **要求**: 署名、标明修改

## 贡献指南

1. Fork 项目到你的 GitHub 账户
2. 创建特性分支进行开发
3. 编写测试确保功能正确
4. 提交 Pull Request

## 联系信息

- **GitHub**: https://github.com/Elohia/pytdx-formula-interpreter
- **Issues**: https://github.com/Elohia/pytdx-formula-interpreter/issues
- **Email**: your.email@example.com

---

**注意**: 本项目仅供学习和非商业用途使用。如需商业使用，请联系项目维护者获取授权。