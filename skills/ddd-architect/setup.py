#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDD Architect Skill - 环境设置脚本
自动检查并安装所需依赖
"""

import sys
import subprocess

REQUIRED_PACKAGES = [
    "pyyaml>=6.0",
]

def check_package(package_name: str) -> bool:
    """检查包是否已安装"""
    try:
        __import__(package_name.split('>=')[0].split('==')[0])
        return True
    except ImportError:
        return False

def install_packages():
    """安装缺失的包"""
    missing = []
    for package in REQUIRED_PACKAGES:
        pkg_name = package.split('>=')[0].split('==')[0]
        if not check_package(pkg_name):
            missing.append(package)
    
    if missing:
        print("📦 检测到缺失的依赖包:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        
        confirm = input("是否自动安装？(y/n): ").strip().lower()
        if confirm == 'y':
            print("🔧 正在安装...")
            subprocess.check_call(["pip3", "install"] + missing)
            print("✅ 安装完成!")
            return True
        else:
            print("⚠️  请手动安装: pip3 install " + " ".join(missing))
            return False
    else:
        print("✅ 所有依赖已就绪")
        return True

if __name__ == "__main__":
    success = install_packages()
    sys.exit(0 if success else 1)