#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作台应用程序 - 仅包含UI相关代码
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QLabel, 
                           QVBoxLayout, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from src.pdf_watermark_tab import PDFWatermarkTab
from video_watermark_tab.video_watermark_tab import VideoWatermarkTab
from about_tab.about_tab import AboutTab
# 所有PDF相关功能都从watermark_core.py导入
from src.pdf_watermark_tab.watermark_core import get_application_path
import config

class WorkbenchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化应用程序UI"""
        self.setWindowTitle(config.APP_NAME)
        self.setFixedSize(config.UI_WIDTH, config.UI_HEIGHT)
        
        # 设置窗口图标
        self.setup_window_icon()
        
        # 创建主窗口小部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # 创建标题栏布局
        title_layout = self.create_title_layout()
        main_layout.addLayout(title_layout)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(config.UI_STYLES["tabs"])
        
        # 添加PDF水印选项卡
        pdf_tab = PDFWatermarkTab()
        self.tab_widget.addTab(pdf_tab, config.TAB_NAMES["pdf"])
        
        # 添加视频水印选项卡
        video_tab = VideoWatermarkTab()
        self.tab_widget.addTab(video_tab, config.TAB_NAMES["video"])
        
        # 添加关于选项卡
        about_tab = AboutTab()
        self.tab_widget.addTab(about_tab, config.TAB_NAMES["about"])
        
        # 将选项卡控件添加到主布局
        main_layout.addWidget(self.tab_widget)
        
        # 添加小间距
        main_layout.addSpacing(1)
    
    def setup_window_icon(self):
        """设置窗口图标"""
        # 使用get_application_path获取应用根目录
        app_path = get_application_path()
        
        # 使用pictures目录下的图标
        icon_path = os.path.join(app_path, config.PICTURES_DIR, "icon_toolkit.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            print(f"成功加载图标: {icon_path}")
        else:
            # 尝试查找目录中的第一个图片文件作为图标
            pictures_dir = os.path.join(app_path, config.PICTURES_DIR)
            if os.path.exists(pictures_dir):
                for file in os.listdir(pictures_dir):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.ico')):
                        icon_path = os.path.join(pictures_dir, file)
                        self.setWindowIcon(QIcon(icon_path))
                        print(f"使用替代图标: {icon_path}")
                        break
            else:
                print(f"警告: 无法找到图标目录 {pictures_dir}")
    
    def create_title_layout(self):
        """创建标题栏布局"""
        title_layout = QHBoxLayout()
        
        # 获取应用根目录
        app_path = get_application_path()
        
        # 左侧第一个Logo - 中文
        chn_logo_path = os.path.join(app_path, config.PICTURES_DIR, "dotrix_logo_chn.png")
        if os.path.exists(chn_logo_path):
            img_label1 = QLabel()
            pixmap1 = QPixmap(chn_logo_path)
            # 保持纵横比缩放到合适大小
            pixmap1 = pixmap1.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label1.setPixmap(pixmap1)
            title_layout.addWidget(img_label1)
            print(f"加载中文Logo: {chn_logo_path}")
        
        # 左侧第二个Logo - 英文
        # UI需要显示该logo
        eng_logo_path = os.path.join(app_path, config.PICTURES_DIR, "dotrix_logo_eng.png")
        if os.path.exists(eng_logo_path):
            img_label2 = QLabel()
            pixmap2 = QPixmap(eng_logo_path)
            # 保持纵横比缩放到合适大小
            pixmap2 = pixmap2.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label2.setPixmap(pixmap2)
            title_layout.addWidget(img_label2)
            print(f"加载英文Logo: {eng_logo_path}")
            
        # 占位符 - 放在右侧
        title_spacer = QWidget()
        title_layout.addWidget(title_spacer, 1)  # 占据右侧最大空间
        
        return title_layout 