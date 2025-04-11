#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
水印生成器启动脚本
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from watermark_app import WatermarkApp

def exception_hook(exctype, value, tb):
    """全局异常处理器"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"发生错误:\n{error_msg}")
     
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 保存错误日志
    with open(os.path.join(log_dir, 'error_log.txt'), 'a', encoding='utf-8') as f:
        f.write(f"错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"错误信息:\n{error_msg}\n\n")
    
    # 显示错误对话框
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("程序发生错误")
    msg.setInformativeText("详细错误信息已保存到logs/error_log.txt文件中")
    msg.setWindowTitle("错误")
    msg.setDetailedText(error_msg)
    msg.exec_()

if __name__ == "__main__":
    # 设置全局异常钩子
    from datetime import datetime
    sys.excepthook = exception_hook
    
    try:
        app = QApplication(sys.argv)
        window = WatermarkApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        exception_hook(type(e), e, e.__traceback__)