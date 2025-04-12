#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
水印生成器主应用程序
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QLabel, 
                           QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                           QPushButton, QFileDialog, QProgressBar, QMessageBox, 
                           QScrollArea, QApplication, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from src.pdf_watermark_tab import PDFWatermarkTab
from src.video_watermark_tab import VideoWatermarkTab
from src.about_tab import AboutTab
from src.pdf_watermark_tab.watermark_core import get_application_path, add_combined_watermark
import config
from src.widgets import DropArea, DropListWidget

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_files = []
        self.watermark_image = ""
        self.output_dir = ""
        
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
        
    def create_image_drop_section(self):
        """创建图片拖放区域"""
        img_frame = QFrame()
        img_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(3, 3, 3, 3)
        img_layout.setSpacing(3)
        
        img_title = QLabel("水印图片拖放区")
        img_title.setStyleSheet("font-weight: bold;")
        img_layout.addWidget(img_title)
        
        self.img_drop_area = DropArea(accept_func=self.drag_image)
        self.img_drop_area.setText("拖放水印图片到这里")
        self.img_drop_area.setFixedHeight(config.IMG_DROP_HEIGHT)
        img_layout.addWidget(self.img_drop_area)
        
        return img_frame
        
    def create_watermark_selection_layout(self):
        """创建水印图片选择布局"""
        watermark_layout = QHBoxLayout()
        watermark_layout.setSpacing(5)
        watermark_layout.addWidget(QLabel("水印图片:"))
        
        self.watermark_label = QLabel("未选择")
        self.watermark_label.setStyleSheet("background: #f0f0f0; padding: 1px;")
        watermark_layout.addWidget(self.watermark_label, 1)
        
        self.watermark_btn = QPushButton("浏览...")
        self.watermark_btn.setFixedWidth(60)
        self.watermark_btn.clicked.connect(self.select_watermark_image)
        watermark_layout.addWidget(self.watermark_btn)
        
        return watermark_layout
        
    def create_output_dir_layout(self):
        """创建输出目录选择布局"""
        output_layout = QHBoxLayout()
        output_layout.setSpacing(5)
        output_layout.addWidget(QLabel("输出目录:"))
        
        self.output_label = QLabel("未选择")
        self.output_label.setStyleSheet("background: #f0f0f0; padding: 1px;")
        output_layout.addWidget(self.output_label, 1)
        
        self.output_btn = QPushButton("浏览...")
        self.output_btn.setFixedWidth(60)
        self.output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_btn)
        
        return output_layout
        
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
    
    def drag_image(self, files):
        """处理图片文件拖放"""
        if files:
            filepath = files[0]
            if filepath.lower().endswith(config.SUPPORTED_IMAGE_EXTENSIONS):
                self.watermark_image = filepath
                self.watermark_label.setText(os.path.basename(filepath))
                self.img_drop_area.setText(f"已选择: {os.path.basename(filepath)}")
            else:
                QMessageBox.warning(self, "格式错误", "请拖放图片文件")
    
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
    
    def select_watermark_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "选择水印图片",
            "",
            config.FILE_FILTERS["image"]
        )
        if filepath:
            self.watermark_image = filepath
            self.watermark_label.setText(os.path.basename(filepath))
            self.img_drop_area.setText(f"已选择: {os.path.basename(filepath)}")
    
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
            QMessageBox.critical(self, "错误", "请选择水印图片")
            return
        if not self.output_dir:
            QMessageBox.critical(self, "错误", "请选择输出目录")
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
                    
                    # 添加水印
                    add_combined_watermark(
                        input_pdf=input_pdf,
                        watermark_image=self.watermark_image,
                        watermark_text=config.DEFAULT_WATERMARK_TEXT,
                        output_pdf=output_pdf,
                        img_scale=config.DEFAULT_IMG_SCALE,
                        img_opacity=config.DEFAULT_IMG_OPACITY,
                        font_name=config.DEFAULT_FONT_NAME,
                        font_size=config.DEFAULT_FONT_SIZE,
                        text_opacity=config.DEFAULT_TEXT_OPACITY,
                        angle=config.DEFAULT_ANGLE,
                        on_top=True
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