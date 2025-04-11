#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF水印选项卡模块，包含PDF水印相关的所有功能
"""

import os
import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                           QFrame, QFileDialog, QProgressBar, QMessageBox, 
                           QApplication, QListWidgetItem, QInputDialog, QLineEdit,
                           QGridLayout, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QPixmap

from widgets import DropListWidget
from main import add_multiple_watermarks, get_application_path
import config

class PDFWatermarkTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_files = []
        # 获取应用根目录
        app_path = get_application_path()
        # 固定使用dotrix_logo_chn.png作为水印图片
        self.watermark_image = os.path.join(app_path, "pictures", "dotrix_logo_chn.png")
        self.output_dir = ""
        self.watermark_text = config.DEFAULT_WATERMARK_TEXT  # 默认水印文本
        
        self.setup_ui()
        
    def setup_ui(self):
        """初始化PDF水印选项卡的UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # PDF文件列表区域
        list_frame = self.create_pdf_list_section()
        layout.addWidget(list_frame)
        
        # 输出目录选择 - 使用addLayout而不是addWidget
        output_dir_layout = self.create_output_dir_layout()
        layout.addLayout(output_dir_layout)
        
        # 水印参数输入区域
        params_layout = self.create_watermark_params_layout()
        layout.addLayout(params_layout)
        
        # 进度条
        progress_layout = self.create_progress_layout()
        layout.addLayout(progress_layout)
        
        # 生成水印按钮
        self.generate_btn = QPushButton("批量处理")
        self.generate_btn.setStyleSheet(config.UI_STYLES["process_btn"])
        self.generate_btn.clicked.connect(self.batch_process)
        layout.addWidget(self.generate_btn)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: blue;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
    def create_pdf_list_section(self):
        """创建PDF文件列表区域"""
        list_frame = QFrame()
        list_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(3, 3, 3, 3)
        list_layout.setSpacing(3)
        
        # 使用支持拖放的列表控件
        self.pdf_list = DropListWidget(accept_func=self.drag_pdf)
        self.pdf_list.setFixedHeight(config.PDF_LIST_HEIGHT)
        self.pdf_list.setStyleSheet(config.UI_STYLES["pdf_list"])
        
        # 添加占位提示
        if self.pdf_list.count() == 0:
            placeholder = QListWidgetItem('将PDF文件拖放到此处或点击"添加PDF"按钮')
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(Qt.gray)
            self.pdf_list.addItem(placeholder)
            self.has_placeholder = True
        else:
            self.has_placeholder = False
        list_layout.addWidget(self.pdf_list)
        
        # PDF文件操作按钮
        pdf_btn_layout = QHBoxLayout()
        pdf_btn_layout.setSpacing(3)
        
        self.add_pdf_btn = QPushButton("添加PDF")
        self.add_pdf_btn.clicked.connect(self.select_pdf_files)
        pdf_btn_layout.addWidget(self.add_pdf_btn)
        
        self.remove_pdf_btn = QPushButton("移除选中")
        self.remove_pdf_btn.clicked.connect(self.remove_selected_pdf)
        pdf_btn_layout.addWidget(self.remove_pdf_btn)
        
        self.clear_pdf_btn = QPushButton("清空列表")
        self.clear_pdf_btn.clicked.connect(self.clear_pdf_list)
        pdf_btn_layout.addWidget(self.clear_pdf_btn)
        
        self.file_count_label = QLabel("已选择: 0 个文件")
        pdf_btn_layout.addWidget(self.file_count_label)
        
        list_layout.addLayout(pdf_btn_layout)
        return list_frame
        
    def create_output_dir_layout(self):
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
        self.output_label = QLabel("未选择")
        self.output_label.setStyleSheet("background: #f0f0f0; padding: 3px; border: 1px solid #ddd; border-radius: 2px;")
        self.output_label.setMinimumWidth(250)
        output_layout.addWidget(self.output_label, 1)
        
        # 浏览按钮
        self.output_btn = QPushButton("浏览...")
        self.output_btn.setFixedWidth(80)
        self.output_btn.setStyleSheet(config.UI_STYLES["process_btn"])
        self.output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_btn)
        
        # 添加frame到包装布局
        wrapper_layout.addWidget(output_frame)
        
        return wrapper_layout
        
    def create_watermark_params_layout(self):
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
        self.date_input = QDateTimeEdit()
        self.date_input.setDateTime(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        self.date_input.dateTimeChanged.connect(self.update_watermark_text)
        params_layout.addWidget(self.date_input, 1, 1)
        
        # 添加学生名输入框
        student_label = QLabel("学生名:")
        student_label.setStyleSheet(label_style)
        params_layout.addWidget(student_label, 2, 0)
        self.student_input = QLineEdit()
        self.student_input.setPlaceholderText("请输入学生姓名")
        self.student_input.textChanged.connect(self.update_watermark_text)
        params_layout.addWidget(self.student_input, 2, 1)
        
        # 确保标签列有合适的宽度
        params_layout.setColumnMinimumWidth(0, 80)
        
        wrapper_layout.addLayout(params_layout)
        
        return wrapper_layout
        
    def create_progress_layout(self):
        """创建进度条布局"""
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(5)
        progress_layout.addWidget(QLabel("处理进度:"))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(config.PROGRESS_BAR_HEIGHT)
        progress_layout.addWidget(self.progress_bar)
        
        return progress_layout
        
    def drag_pdf(self, files):
        """处理PDF文件拖放，支持多个文件"""
        # 如果有占位符，先清除
        if hasattr(self, 'has_placeholder') and self.has_placeholder:
            self.pdf_list.clear()
            self.has_placeholder = False
            
        new_files_added = 0
        
        for filepath in files:
            if filepath.lower().endswith('.pdf'):
                # 检查是否已在列表中，避免重复添加
                if filepath not in self.pdf_files:
                    self.pdf_files.append(filepath)
                    self.pdf_list.addItem(os.path.basename(filepath))
                    new_files_added += 1
        
        if new_files_added > 0:
            self.update_file_count()
            self.status_label.setText(f"已添加 {new_files_added} 个新PDF文件")
            self.status_label.setStyleSheet("color: green;")
            
            # 如果还没选择输出目录，自动设置为第一个PDF所在的目录
            if not self.output_dir and self.pdf_files:
                self.output_dir = os.path.dirname(self.pdf_files[0])
                self.output_label.setText(self.output_dir)
        else:
            self.status_label.setText("未发现新的PDF文件或文件已存在")
            self.status_label.setStyleSheet("color: orange;")
    
    def select_pdf_files(self):
        """选择多个PDF文件"""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择PDF文件",
            "",
            config.FILE_FILTERS["pdf"]
        )
        if filepaths:
            # 如果有占位符，先清除
            if hasattr(self, 'has_placeholder') and self.has_placeholder:
                self.pdf_list.clear()
                self.has_placeholder = False
                
            new_files_added = 0
            for filepath in filepaths:
                if filepath not in self.pdf_files:
                    self.pdf_files.append(filepath)
                    self.pdf_list.addItem(os.path.basename(filepath))
                    new_files_added += 1
            
            if new_files_added > 0:
                self.update_file_count()
                self.status_label.setText(f"已添加 {new_files_added} 个新PDF文件")
                self.status_label.setStyleSheet("color: green;")
                
                # 如果还没选择输出目录，自动设置为第一个PDF所在的目录
                if not self.output_dir:
                    self.output_dir = os.path.dirname(self.pdf_files[0])
                    self.output_label.setText(self.output_dir)
    
    def remove_selected_pdf(self):
        """移除选中的PDF文件"""
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先选择要删除的文件")
            return
        
        for item in selected_items:
            index = self.pdf_list.row(item)
            del self.pdf_files[index]
            self.pdf_list.takeItem(index)
        
        self.update_file_count()
    
    def clear_pdf_list(self):
        """清空PDF文件列表"""
        if not self.pdf_files:
            return
            
        reply = QMessageBox.question(
            self, '确认', '确定要清空所有文件吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.pdf_files.clear()
            self.pdf_list.clear()
            self.update_file_count()
            
            # 添加回占位符
            placeholder = QListWidgetItem('将PDF文件拖放到此处或点击"添加PDF"按钮')
            placeholder.setFlags(Qt.NoItemFlags)  # 设置为不可选择
            placeholder.setForeground(Qt.gray)    # 设置文字为灰色
            self.pdf_list.addItem(placeholder)
            self.has_placeholder = True
            
            self.status_label.setText("已清空文件列表")
            self.status_label.setStyleSheet("color: blue;")
    
    def update_file_count(self):
        """更新文件计数"""
        count = len(self.pdf_files)
        self.file_count_label.setText(f"已选择: {count} 个文件")
    
    def select_output_dir(self):
        """选择输出目录"""
        dirpath = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录"
        )
        if dirpath:
            self.output_dir = dirpath
            self.output_label.setText(self.output_dir)
    
    def batch_process(self):
        """批量处理PDF文件"""
        # 检查是否已选择所有必要文件
        if not self.pdf_files:
            QMessageBox.critical(self, "错误", "请添加至少一个PDF文件")
            return
        if not self.watermark_image:
            QMessageBox.critical(self, "错误", "水印图片不存在")
            return
        if not self.output_dir:
            QMessageBox.critical(self, "错误", "请选择输出目录")
            return
        
        # 检查学生名是否已填写
        student_name = self.student_input.text().strip()
        if not student_name:
            QMessageBox.critical(self, "错误", "请输入该PDF课件将要交付给的学生实名")
            return
        
        try:
            # 禁用按钮显示处理中
            self.generate_btn.setEnabled(False)
            self.generate_btn.setText("处理中...")
            self.status_label.setText("正在处理，请稍候...")
            self.status_label.setStyleSheet("color: orange;")
            
            # 更新UI
            QApplication.processEvents()
            
            total_files = len(self.pdf_files)
            self.progress_bar.setMaximum(total_files)
            successful = 0
            failed = 0
            
            # 处理每个PDF文件
            for i, input_pdf in enumerate(self.pdf_files):
                try:
                    # 更新进度
                    self.progress_bar.setValue(i)
                    self.status_label.setText(f"处理中: {os.path.basename(input_pdf)} ({i+1}/{total_files})")
                    QApplication.processEvents()  # 确保UI更新
                    
                    # 创建输出文件路径
                    base_name = os.path.basename(input_pdf)
                    name, ext = os.path.splitext(base_name)
                    output_pdf = os.path.join(self.output_dir, f"{name}_带水印{ext}")
                    
                    # 添加网格状水印
                    add_multiple_watermarks(
                        input_pdf=input_pdf,
                        watermark_image=self.watermark_image,
                        watermark_text=self.watermark_text,
                        output_pdf=output_pdf,
                        img_scale=config.DEFAULT_IMG_SCALE,
                        img_opacity=config.DEFAULT_IMG_OPACITY,
                        font_name=config.DEFAULT_FONT_NAME,
                        font_size=24,  # 将字体调小为24（默认一般是36）
                        text_opacity=config.DEFAULT_TEXT_OPACITY,
                        angle=config.DEFAULT_ANGLE,
                        on_top=True,
                        rows=5,   # 5行
                        cols=3    # 3列
                    )
                    successful += 1
                except Exception as e:
                    print(f"处理文件 {input_pdf} 时出错: {str(e)}")
                    failed += 1
            
            # 更新最终进度
            self.progress_bar.setValue(total_files)
            
            status_color = "green" if failed == 0 else "orange"
            self.status_label.setText(f"处理完成! 成功: {successful}, 失败: {failed}")
            self.status_label.setStyleSheet(f"color: {status_color};")
            
            QMessageBox.information(
                self, 
                "处理完成", 
                f"批量处理完成!\n成功: {successful} 个文件\n失败: {failed} 个文件\n输出目录: {self.output_dir}"
            )
        
        except Exception as e:
            self.status_label.setText(f"错误: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "错误", f"处理时出错: {str(e)}")
        finally:
            # 恢复按钮状态
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("批量处理")
    
    def update_watermark_text(self):
        """根据输入参数更新水印文本"""
        # 使用日期和时间格式
        datetime = self.date_input.dateTime().toString("yyyy-MM-dd HH:mm")
        student = self.student_input.text().strip()
        
        # 按照新的格式构建水印文本 - 不包含科目名和第几节
        if student:
            self.watermark_text = f"小红书号100135317 点线成面DOTRIX {student}同学 {datetime}"
            # 更新状态
            self.status_label.setText(f"水印文本已更新: {self.watermark_text}")
            self.status_label.setStyleSheet("color: green;")
        else:
            # 提醒用户填写完整信息
            self.status_label.setText("请输入该PDF课件将要交付给的学生实名")
            self.status_label.setStyleSheet("color: orange;") 