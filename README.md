# NL2SQL Injection Evaluation Framework

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/myusername/nl2sql-injection-evaluation/actions/workflows/tests.yml/badge.svg)](https://github.com/myusername/nl2sql-injection-evaluation/actions/workflows/tests.yml)

## 📋 Overview

This repository contains the complete evaluation framework for the paper:

**"When AI writes SQL: Uncovering injection vulnerabilities in LLM-generated database queries"**

We systematically evaluate SQL injection vulnerabilities in LLM-generated SQL across:
- **20** Large Language Models
- **4** Database Systems (SQLite, MySQL, PostgreSQL, Microsoft SQL Server)
- **210** Adversarial Prompts across 7 categories
- **4** Mitigation Strategies

### Key Findings
- Advanced prompts achieve **44.1%** attack success on web-based models
- Existing SQL injection detectors lose **5.3%** accuracy on LLM-generated payloads
- AST validation reduces penetration rates from **28.7%** to **3.1%**
- Full-stack mitigation achieves **1.2%** penetration rate with **32%** latency overhead

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- API keys for LLM services (OpenAI, Anthropic, Google, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/myusername/nl2sql-injection-evaluation.git
cd nl2sql-injection-evaluation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
