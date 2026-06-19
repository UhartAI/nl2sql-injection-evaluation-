
## 2. setup.py

```python
"""
Setup configuration for NL2SQL Injection Evaluation Framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nl2sql-injection-evaluation",
    version="1.0.0",
    author="Ahmed Bensaoud, Meenaxi Sharma, Scott Raymond",
    author_email="bensaoud@hartford.edu",
    description="Evaluation framework for SQL injection vulnerabilities in LLM-generated SQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myusername/nl2sql-injection-evaluation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "google-generativeai>=0.3.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "sqlalchemy>=2.0.0",
        "pymysql>=1.1.0",
        "psycopg2-binary>=2.9.0",
        "pymssql>=2.2.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.2.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.14.0",
        "tqdm>=4.65.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "dask>=2023.5.0",
        "sqlparse>=0.4.0",
        "mo-sql-parsing>=0.0.1",
        "pytest>=7.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "pre-commit>=3.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nl2sql-eval=experiments.run_evaluation:main",
            "nl2sql-mitigate=experiments.run_mitigation:main",
            "nl2sql-analyze=experiments.analyze_results:main",
        ],
    },
)
