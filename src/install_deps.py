#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安装依赖脚本 - 安装程序所需的所有Python包
"""

import sys
import subprocess
import os

def install_package(package):
    """安装单个Python包并处理错误"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} 安装成功!")
        return True
    except Exception as e:
        print(f"{package} 安装失败: {e}")
        return False

def install_from_requirements():
    """从requirements.txt安装依赖"""
    if os.path.exists("requirements.txt"):
        try:
            print("从requirements.txt安装依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("依赖安装成功!")
            return True
        except Exception as e:
            print(f"从requirements.txt安装失败: {e}")
            return False
    else:
        print("找不到requirements.txt文件")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    return install_package("pyinstaller")

def main():
    """安装所有必要的依赖"""
    print("="*50)
    print("安装DOTRIX水印工具所需的依赖")
    print("="*50)
    
    # 尝试从requirements.txt安装
    if install_from_requirements():
        print("所有依赖已从requirements.txt安装")
    else:
        # 分别安装核心依赖
        packages = [
            "PyPDF2>=2.0.0",
            "Pillow>=8.0.0",
            "reportlab>=3.6.0",
            "PyQt5>=5.15.0",
            "pymupdf>=1.19.0",
        ]
        
        successful = 0
        for package in packages:
            if install_package(package):
                successful += 1
        
        print(f"成功安装了 {successful}/{len(packages)} 个依赖包")
    
    # 安装打包工具
    print("\n是否要安装PyInstaller用于打包程序? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        if install_pyinstaller():
            print("\n所有依赖安装完成。现在可以使用以下命令打包程序:")
            print("python build.py")
        else:
            print("\n其他依赖已安装，但PyInstaller安装失败。")
            print("如需打包程序，请手动安装: pip install pyinstaller")
    else:
        print("\n已跳过PyInstaller安装")
    
    print("\n安装完成。您现在可以运行程序: python run.py")
    input("按Enter键退出...")

if __name__ == "__main__":
    main() 