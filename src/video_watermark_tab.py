#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频水印选项卡模块，目前显示"开发中"提示
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

import config

class VideoWatermarkTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        """初始化视频水印选项卡的UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建"开发中"的提示标签
        developing_label = QLabel("开发中，敬请期待")
        developing_label.setStyleSheet(config.UI_STYLES["developing_label"])
        developing_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(developing_label)
        
        # 添加占位空间，使标签垂直居中
        layout.addStretch(1) 