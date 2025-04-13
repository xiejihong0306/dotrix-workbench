#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件，存储应用程序的各种设置
"""

# 应用程序名称和版本
APP_VERSION = "1.0.1"
APP_NAME = f"DOTRIX Workbench V{APP_VERSION} 点线成面软件工程部 "

# 默认文件夹
PICTURES_DIR = "pictures"

# 水印设置
DEFAULT_IMG_SCALE = 0.5         # 默认图片缩放比例
DEFAULT_IMG_OPACITY = 0.3       # 默认图片透明度
DEFAULT_FONT_NAME = "SimSun"    # 默认字体
DEFAULT_FONT_SIZE = 36          # 默认字体大小
DEFAULT_TEXT_OPACITY = 0.2      # 默认文字透明度
DEFAULT_ANGLE = 45              # 默认旋转角度
DEFAULT_WATERMARK_TEXT = "PDF加水印测试"  # 默认水印文字

# UI设置
UI_WIDTH = 540
UI_HEIGHT = 620  # 增加高度以适应选项卡
PDF_LIST_HEIGHT = 180
IMG_DROP_HEIGHT = 40
PROGRESS_BAR_HEIGHT = 15

# 选项卡设置
TAB_NAMES = {
    "pdf": "PDF水印",
    "video": "视频水印",
    "about": "关于点线成面DOTRIX"
}

# 样式设置
UI_STYLES = {
    "pdf_list": """
        QListWidget {
            border: 2px dashed #aaa;
            background-color: #f8f8f8;
        }
        QListWidget::item {
            padding: 3px;
        }
        QListWidget::item:selected {
            background-color: #e0e0e0;
        }
    """,
    "process_btn": """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-size: 14pt;
            font-weight: bold;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """,
    "tabs": """
        QTabWidget::pane { 
            border: 1px solid #C2C7CB;
        }
        QTabWidget::tab-bar {
            left: 5px;
        }
        QTabBar::tab {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                     stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                     stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
            border: 1px solid #C4C4C3;
            border-bottom-color: #C2C7CB;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            padding: 4px;
        }
        QTabBar::tab:selected, QTabBar::tab:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                     stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                     stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
        }
        QTabBar::tab:selected {
            border-color: #9B9B9B;
            border-bottom-color: #C2C7CB;
        }
    """,
    "developing_label": """
        font-size: 24px;
        color: #666;
        font-weight: bold;
    """
}

# 文件筛选器设置
FILE_FILTERS = {
    "pdf": "PDF文件 (*.pdf)",
    "image": "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
}

# 支持的图片格式
SUPPORTED_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp') 