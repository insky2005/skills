# DDD Architect Skill - 安装指南

## 🔧 环境要求

- Python 3.8+
- pip 包管理器

## 🐍 使用虚拟环境（推荐）

```bash
# 创建虚拟环境（使用 venv 模块，创建一个名为 .venv 的虚拟环境）
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux
source .venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip3 install -r requirements.txt

# 验证
python scripts/validate-aggregate.py --help
```

## 📦 快速安装

### 方式 1: 使用 pip 直接安装（推荐）

```bash
pip3 install -r requirements.txt
```

### 方式 2: 运行 setup 脚本

```bash
python3 setup.py
```

### 方式 3: 手动安装

```bash
pip3 install pyyaml
```

## 🔍 验证安装

```bash
# 测试 yaml 模块
python -c "import yaml; print('✅ PyYAML 版本:', yaml.__version__)"

# 测试校验脚本
echo 'aggregates: []' | python scripts/validate-aggregate.py
```
