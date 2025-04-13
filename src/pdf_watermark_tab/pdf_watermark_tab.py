#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF水印选项卡模块，包含PDF水印相关的所有功能
"""

import os
import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QMessageBox, QFileDialog, QListWidgetItem)
from PyQt5.QtCore import Qt, QDateTime
import fitz  # PyMuPDF
from pathlib import Path

# 修改相对导入为绝对导入
from src.workbench_app.widgets import DropListWidget
from src.pdf_watermark_tab.watermark_core import add_multiple_watermarks, get_application_path
from src.pdf_watermark_tab.pdf_password import secure_pdf_with_password  # 导入密码保护功能
from src.workbench_app.ui_pdf_watermark_tab import PDFWatermarkUI
import config


class PDFWatermarkTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_files = []
        # 获取应用根目录
        app_path = get_application_path()
        # 固定使用dotrix_logo_chn.png作为水印图片
        self.watermark_image = os.path.join(app_path, config.PICTURES_DIR, "dotrix_logo_chn.png")
        self.output_dir = ""
        self.watermark_text = config.DEFAULT_WATERMARK_TEXT  # 默认水印文本
        
        # 安全模式设置 - 写死为始终开启，固定DPI=150
        self.secure_mode = True
        self.dpi = 150
        
        # 初始化UI
        self.ui = PDFWatermarkUI()
        self.ui.setup_ui(self)
        
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
    
    def convert_to_secure_pdf(self, input_pdf, output_pdf):
        """将PDF转换为图像格式以防止编辑"""
        try:
            # 打开输入PDF
            pdf_doc = fitz.open(input_pdf)
            # 创建一个新的输出PDF
            output_doc = fitz.open()
            
            # 逐页转换为图像然后添加到新PDF
            for page_num in range(len(pdf_doc)):
                # 获取页面
                page = pdf_doc[page_num]
                # 计算适当的缩放因子，基于DPI (固定为150)
                zoom = self.dpi / 72  # 默认PDF分辨率是72 DPI
                # 创建页面的图像
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                
                # 创建新页面，尺寸与原始页面相同（但会按DPI缩放）
                new_page = output_doc.new_page(width=pix.width, height=pix.height)
                # 将图像插入新页面
                new_page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), pixmap=pix)
            
            # 保存输出PDF
            output_doc.save(output_pdf)
            output_doc.close()
            pdf_doc.close()
            
            return True
        except Exception as e:
            print(f"转换PDF到安全格式时出错: {str(e)}")
            return False
    
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
            # 处理步骤现在是三倍文件数，因为每个文件都需要添加水印、安全转换和添加密码三个步骤
            max_steps = total_files * 3
            self.progress_bar.setMaximum(max_steps)
            successful = 0
            failed = 0
            
            step_count = 0
            
            # 处理每个PDF文件
            for i, input_pdf in enumerate(self.pdf_files):
                try:
                    # 更新进度
                    self.progress_bar.setValue(step_count)
                    self.status_label.setText(f"处理中: {os.path.basename(input_pdf)} - 添加水印 ({i+1}/{total_files})")
                    QApplication.processEvents()  # 确保UI更新
                    
                    # 创建输出文件路径
                    base_name = os.path.basename(input_pdf)
                    name, ext = os.path.splitext(base_name)
                    
                    # 使用学生名作为文件后缀，而不是"带水印"
                    student_name = self.student_input.text().strip()
                    # 先创建临时文件用于添加水印
                    temp_output = os.path.join(self.output_dir, f"{name}_temp{ext}")
                    secure_output = os.path.join(self.output_dir, f"{name}_secure{ext}")
                    final_output = os.path.join(self.output_dir, f"{name}_{student_name}_可用chrome打开{ext}")
                    
                    # 添加网格状水印
                    add_multiple_watermarks(
                        input_pdf=input_pdf,
                        watermark_image=self.watermark_image,
                        watermark_text=self.watermark_text,
                        output_pdf=temp_output,
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
                    
                    step_count += 1
                    self.progress_bar.setValue(step_count)
                    
                    # 将带水印的PDF转换为图像格式
                    self.status_label.setText(f"处理中: {os.path.basename(input_pdf)} - 安全转换 ({i+1}/{total_files})")
                    QApplication.processEvents()
                    
                    # 执行安全转换
                    if self.convert_to_secure_pdf(temp_output, secure_output):
                        # 删除临时文件
                        try:
                            os.remove(temp_output)
                        except:
                            pass  # 忽略临时文件删除失败
                    else:
                        # 转换失败，使用临时文件作为安全输出
                        if os.path.exists(temp_output):
                            secure_output = temp_output
                    
                    step_count += 1
                    self.progress_bar.setValue(step_count)
                    
                    # 为安全转换后的PDF添加密码保护
                    self.status_label.setText(f"处理中: {os.path.basename(input_pdf)} - 添加密码保护 ({i+1}/{total_files})")
                    QApplication.processEvents()
                    
                    # 使用密码保护方法
                    success, password = secure_pdf_with_password(secure_output, final_output, student_name)
                    
                    # 删除中间文件
                    if os.path.exists(secure_output) and secure_output != temp_output:
                        try:
                            os.remove(secure_output)
                        except:
                            pass
                    
                    step_count += 1
                    self.progress_bar.setValue(step_count)
                    
                    successful += 1
                except Exception as e:
                    print(f"处理文件 {input_pdf} 时出错: {str(e)}")
                    failed += 1
            
            # 更新最终进度
            self.progress_bar.setValue(max_steps)
            
            status_color = "green" if failed == 0 else "orange"
            self.status_label.setText(f"处理完成! 成功: {successful}, 失败: {failed}")
            self.status_label.setStyleSheet(f"color: {status_color};")
            
            QMessageBox.information(
                self, 
                "处理完成", 
                f"批量处理完成!\n已启用防编辑模式，PDF已转换为不可编辑格式\n已添加密码保护，密码为学生姓名拼音\n成功: {successful} 个文件\n失败: {failed} 个文件\n输出目录: {self.output_dir}"
            )
        
        except Exception as e:
            self.status_label.setText(f"错误: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "错误", f"处理时出错: {str(e)}")
        finally:
            # 恢复按钮状态
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("批量处理")
            
    def get_pinyin_password(self, chinese_name):
        """获取中文姓名的拼音密码"""
        from src.pdf_watermark_tab.pdf_password import get_pinyin_password
        return get_pinyin_password(chinese_name)
    
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