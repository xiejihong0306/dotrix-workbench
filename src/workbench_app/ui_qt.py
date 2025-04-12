#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
此文件用于支持向后兼容
新代码应直接导入 watermark_app 模块中的 WatermarkApp 类
"""

import sys
import warnings

# 导入主应用类以保持向后兼容
from src.workbench_app import WatermarkApp

# 发出弃用警告
warnings.warn(
    "直接导入ui_qt模块已弃用，请改为从watermark_app模块导入WatermarkApp",
    DeprecationWarning,
    stacklevel=2
)

# 如果此文件被直接执行，启动应用程序
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    warnings.warn(
        "直接运行ui_qt.py已弃用，请使用run.py",
        DeprecationWarning,
        stacklevel=2
    )
    
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_()) 