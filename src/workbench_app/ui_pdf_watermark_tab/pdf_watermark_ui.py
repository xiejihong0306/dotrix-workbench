#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF水印选项卡UI模块，包含PDF水印相关的UI设计
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                           QFrame, QFileDialog, QProgressBar, QMessageBox, 
                           QListWidgetItem, QLineEdit,
                           QGridLayout, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime
import os
import config
from src.workbench_app.widgets import DropListWidget

class PDFWatermarkUI:
    def setup_ui(self, parent):
        """初始化PDF水印选项卡的UI"""
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # PDF文件列表区域
        list_frame = self.create_pdf_list_section(parent)
        layout.addWidget(list_frame)
        
        # 输出目录选择 - 使用addLayout而不是addWidget
        output_dir_layout = self.create_output_dir_layout(parent)
        layout.addLayout(output_dir_layout)
        
        # 水印参数输入区域
        params_layout = self.create_watermark_params_layout(parent)
        layout.addLayout(params_layout)
        
        # 进度条
        progress_layout = self.create_progress_layout(parent)
        layout.addLayout(progress_layout)
        
        # 生成水印按钮
        parent.generate_btn = QPushButton("批量处理")
        parent.generate_btn.setStyleSheet(config.UI_STYLES["process_btn"])
        parent.generate_btn.clicked.connect(parent.batch_process)
        layout.addWidget(parent.generate_btn)
        
        # 状态标签
        parent.status_label = QLabel("准备就绪")
        parent.status_label.setStyleSheet("color: blue;")
        parent.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(parent.status_label)
        
    def create_pdf_list_section(self, parent):
        """创建PDF文件列表区域"""
        list_frame = QFrame()
        list_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(3, 3, 3, 3)
        list_layout.setSpacing(3)
        
        # 使用支持拖放的列表控件
        parent.pdf_list = DropListWidget(accept_func=parent.drag_pdf)
        parent.pdf_list.setFixedHeight(config.PDF_LIST_HEIGHT)
        parent.pdf_list.setStyleSheet(config.UI_STYLES["pdf_list"])
        
        # 添加占位提示
        if parent.pdf_list.count() == 0:
            placeholder = QListWidgetItem('将PDF文件拖放到此处或点击"添加PDF"按钮')
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(Qt.gray)
            parent.pdf_list.addItem(placeholder)
            parent.has_placeholder = True
        else:
            parent.has_placeholder = False
        list_layout.addWidget(parent.pdf_list)
        
        # PDF文件操作按钮
        pdf_btn_layout = QHBoxLayout()
        pdf_btn_layout.setSpacing(3)
        
        parent.add_pdf_btn = QPushButton("添加PDF")
        parent.add_pdf_btn.clicked.connect(parent.select_pdf_files)
        pdf_btn_layout.addWidget(parent.add_pdf_btn)
        
        parent.remove_pdf_btn = QPushButton("移除选中")
        parent.remove_pdf_btn.clicked.connect(parent.remove_selected_pdf)
        pdf_btn_layout.addWidget(parent.remove_pdf_btn)
        
        parent.clear_pdf_btn = QPushButton("清空列表")
        parent.clear_pdf_btn.clicked.connect(parent.clear_pdf_list)
        pdf_btn_layout.addWidget(parent.clear_pdf_btn)
        
        parent.file_count_label = QLabel("已选择: 0 个文件")
        pdf_btn_layout.addWidget(parent.file_count_label)
        
        list_layout.addLayout(pdf_btn_layout)
        return list_frame
        
    def create_output_dir_layout(self, parent):
        """创建输出目录选择布局"""
        # 创建包装布局
        wrapper_layout = QVBoxLayout()
        
        # 输出目录标签 - 移到frame外面
        dir_label = QLabel("输出目录:")
        dir_label.setStyleSheet("font-weight: bold; color: #333333;")
        wrapper_layout.addWidget(dir_label)
        
        # 创建带虚线边框的Frame，与PDF拖放区类似
        output_frame = QFrame()
        output_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        output_frame.setStyleSheet("QFrame {background-color: #f8f8f8; border: 2px dashed #aaa; border-radius: 3px; padding: 5px;}")
        
        output_layout = QHBoxLayout(output_frame)
        output_layout.setSpacing(8)
        output_layout.setContentsMargins(8, 6, 8, 6)
        
        # 输出目录显示标签
        parent.output_label = QLabel("未选择")
        parent.output_label.setStyleSheet("background: #f0f0f0; padding: 3px; border: 1px solid #ddd; border-radius: 2px;")
        parent.output_label.setMinimumWidth(250)
        output_layout.addWidget(parent.output_label, 1)
        
        # 浏览按钮
        parent.output_btn = QPushButton("浏览...")
        parent.output_btn.setFixedWidth(80)
        parent.output_btn.setStyleSheet(config.UI_STYLES["process_btn"])
        parent.output_btn.clicked.connect(parent.select_output_dir)
        output_layout.addWidget(parent.output_btn)
        
        # 添加frame到包装布局
        wrapper_layout.addWidget(output_frame)
        
        return wrapper_layout
        
    def create_watermark_params_layout(self, parent):
        """创建水印参数输入区域"""
        # 创建整体布局
        wrapper_layout = QVBoxLayout()
        
        # 使用网格布局，不使用Frame包装
        params_layout = QGridLayout()
        params_layout.setContentsMargins(10, 10, 10, 10)
        params_layout.setSpacing(10)
        
        # 添加标题
        title_label = QLabel("水印文本参数")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        params_layout.addWidget(title_label, 0, 0, 1, 2)
        
        # 设置标签样式
        label_style = "font-size: 12px; color: #000000; background: none; font-weight: bold;"
        
        # 添加日期时间选择器
        date_label = QLabel("日期时间:")
        date_label.setStyleSheet(label_style)
        params_layout.addWidget(date_label, 1, 0)
        parent.date_input = QDateTimeEdit()
        parent.date_input.setDateTime(QDateTime.currentDateTime())
        parent.date_input.setCalendarPopup(True)
        parent.date_input.dateTimeChanged.connect(parent.update_watermark_text)
        params_layout.addWidget(parent.date_input, 1, 1)
        
        # 添加学生名输入框
        student_label = QLabel("学生名:")
        student_label.setStyleSheet(label_style)
        params_layout.addWidget(student_label, 2, 0)
        parent.student_input = QLineEdit()
        parent.student_input.setPlaceholderText("请输入学生姓名")
        parent.student_input.textChanged.connect(parent.update_watermark_text)
        params_layout.addWidget(parent.student_input, 2, 1)
        
        # 确保标签列有合适的宽度
        params_layout.setColumnMinimumWidth(0, 80)
        
        wrapper_layout.addLayout(params_layout)
        
        return wrapper_layout
        
    def create_progress_layout(self, parent):
        """创建进度条布局"""
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(5)
        progress_layout.addWidget(QLabel("处理进度:"))
        
        parent.progress_bar = QProgressBar()
        parent.progress_bar.setTextVisible(True)
        parent.progress_bar.setFixedHeight(config.PROGRESS_BAR_HEIGHT)
        progress_layout.addWidget(parent.progress_bar)
        
        return progress_layout 