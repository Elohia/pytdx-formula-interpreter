from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pytdx-interpreter",
    version="0.1.0",
    author="pytdx-interpreter contributors",
    author_email="your.email@example.com",
    description="通达信公式解释器 - 支持通达信公式语法的Python解释器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elohia/pytdx-formula-interpreter",
    project_urls={
        "Bug Tracker": "https://github.com/Elohia/pytdx-formula-interpreter/issues",
        "Documentation": "https://github.com/Elohia/pytdx-formula-interpreter#readme",
        "Source Code": "https://github.com/Elohia/pytdx-formula-interpreter",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pytdx-interpreter=tdx_interpreter.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="tdx, tongdaxin, formula, interpreter, technical-analysis, stock, finance",
)