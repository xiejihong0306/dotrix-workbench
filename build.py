#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包脚本 - 将水印生成器打包为exe文件
"""

import os
import shutil
import PyInstaller.__main__

# 确保当前工作目录是脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 定义图标路径
icon_path = os.path.join('pictures', 'icon.png')

# 创建临时字体目录
fonts_dir = os.path.join(script_dir, 'fonts')
os.makedirs(fonts_dir, exist_ok=True)

# 从Windows系统目录复制宋体字体到fonts目录
try:
    windows_font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'simsun.ttc')
    if os.path.exists(windows_font_path):
        shutil.copy2(windows_font_path, os.path.join(fonts_dir, 'simsun.ttc'))
        print(f"成功复制宋体字体文件到 {fonts_dir}")
    else:
        print("警告：找不到宋体字体文件")
except Exception as e:
    print(f"复制字体文件时发生错误: {e}")

# PyInstaller参数
PyInstaller.__main__.run([
    'run.py',                         # 入口脚本
    '--name=WatermarkApp',            # 应用名称
    '--onefile',                      # 生成单个exe文件
    '--windowed',                     # 不显示控制台窗口
    f'--icon={icon_path}',            # 设置应用图标
    '--add-data=pictures;pictures',   # 添加资源文件夹
    '--add-data=fonts;fonts',         # 添加字体文件夹
    '--hidden-import=PyPDF2',         # 显式指定PDF库
    '--hidden-import=reportlab',      # 显式指定reportlab库
    '--hidden-import=PIL',            # 显式指定PIL库
    '--collect-all=PyPDF2',           # 收集所有PyPDF2相关资源
    '--collect-all=reportlab',        # 收集所有reportlab相关资源  
    '--collect-all=PIL',              # 收集所有PIL相关资源
    '--clean',                        # 清理临时文件
    '--noconfirm',                    # 不要询问确认
])

print("打包完成！可执行文件位于 dist 文件夹中。") 