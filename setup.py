#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信公式解释器 - 安装配置文件

基于tdx_main库扩展的完整通达信公式解释器，支持完整的语法解析、
函数库、计算引擎和错误处理功能。
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tdx-formula-interpreter",
    version="0.1.0",
    author="TDX Formula Team",
    author_email="dev@tdxformula.com",
    description="完整的通达信公式解释器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tdx-formula/interpreter",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Interpreters",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-benchmark>=3.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "tdx-formula=tdx_interpreter.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="tdx tongdaxin formula interpreter finance stock",
    project_urls={
        "Bug Reports": "https://github.com/tdx-formula/interpreter/issues",
        "Source": "https://github.com/tdx-formula/interpreter",
        "Documentation": "https://tdx-formula-interpreter.readthedocs.io/",
    },
)