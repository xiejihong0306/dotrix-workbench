#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包脚本 - 将水印生成器打包为exe文件
"""

import os
import shutil
import multiprocessing
import subprocess
import sys
import PyInstaller.__main__

# 确保当前工作目录是脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 导入config模块中的版本号
sys.path.append(os.path.join(script_dir, 'src'))
from config import APP_VERSION

# 定义图标路径
icon_path = os.path.join('pictures', 'icon_toolkit.png')

# 检查是否安装了UPX (用于压缩可执行文件)
upx_available = False
try:
    subprocess.run(['upx', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    upx_available = True
    print("检测到UPX压缩工具，将用于减小生成文件大小")
except (subprocess.SubprocessError, FileNotFoundError):
    print("未检测到UPX压缩工具，跳过压缩步骤")
    print("提示: 安装UPX可以大幅减小生成的.exe文件大小")
    print("      可以从 https://github.com/upx/upx/releases 下载安装")

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

# 确保pictures目录中包含必要的水印图片
pictures_dir = os.path.join(script_dir, 'pictures')
required_images = ['dotrix_logo_chn.png', 'dotrix_logo_eng.png', 'icon_toolkit.png']
missing_images = [img for img in required_images if not os.path.exists(os.path.join(pictures_dir, img))]
if missing_images:
    print(f"警告: 在pictures目录中找不到以下必要图片: {', '.join(missing_images)}")
    print("这些文件必须存在才能正常运行!")

# 定义应用名称（使用版本号）
app_name = f"DOTRIX Workbench V{APP_VERSION}"

# 获取CPU核心数
cpu_count = multiprocessing.cpu_count()
print(f"检测到 {cpu_count} 个CPU核心")
print("注意：当前版本的PyInstaller不支持并行构建，将使用单核心打包")

# 设置入口脚本路径
entry_script = os.path.join('src', 'run.py')

# PyInstaller参数
pyinstaller_args = [
    entry_script,                     # 入口脚本(src/run.py)
    f'--name={app_name}',             # 应用名称
    '--onefile',                      # 生成单个exe文件
    '--windowed',                     # 不显示控制台窗口
    f'--icon={icon_path}',            # 设置应用图标
    '--add-data=pictures;pictures',   # 添加资源文件夹
    '--add-data=fonts;fonts',         # 添加字体文件夹
    '--hidden-import=PyPDF2',         # 显式指定PDF库
    '--hidden-import=reportlab',      # 显式指定reportlab库
    '--hidden-import=PIL',            # 显式指定PIL库
    '--hidden-import=fitz',           # 显式指定PyMuPDF库
    '--clean',                        # 清理临时文件
    '--noconfirm',                    # 不要询问确认
    '--paths=src',                    # 添加源代码目录到Python路径
]

# 减少收集的库资源，只保留必要部分
# 替换掉collect-all，使用更精细的导入控制
for module in ['PyPDF2', 'reportlab', 'PIL', 'fitz', 'PyQt5', 'html']:
    pyinstaller_args.append(f'--hidden-import={module}')

# 排除一些不必要的模块来减小文件体积
excludes = [
    'matplotlib', 'scipy', 'numpy.random', 'numpy.f2py',
    'PySide2', 'PyQt6', 'IPython', 'pandas', 'lib2to3',
    'notebook', 'test', 'tests', 'setuptools'
]
for module in excludes:
    pyinstaller_args.append(f'--exclude-module={module}')

# 如果UPX可用，使用UPX压缩
if upx_available:
    pyinstaller_args.append('--upx-dir=.')  # UPX在当前目录或PATH中
    pyinstaller_args.append('--upx')        # 启用UPX压缩

# 执行PyInstaller打包
PyInstaller.__main__.run(pyinstaller_args)

print("打包完成！可执行文件位于 dist 文件夹中。")
print(f"已生成: {app_name}.exe")
print("提示: 打包后的程序将依赖pictures和fonts目录中的资源，但这些资源已嵌入到exe中") 