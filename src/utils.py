#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块，包含各种工具函数
"""

import os
import fitz  # PyMuPDF

def is_valid_pdf(file_path):
    """
    检查文件是否是有效的PDF文件
    
    Args:
        file_path: PDF文件路径
        
    Returns:
        bool: 如果是有效的PDF文件则返回True，否则返回False
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return False
        
    # 检查文件扩展名
    if not file_path.lower().endswith('.pdf'):
        return False
        
    # 尝试用PyMuPDF打开文件
    try:
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
        
        # 有页面的PDF才是有效的
        return page_count > 0
    except Exception as e:
        print(f"验证PDF文件时出错: {str(e)}")
        return False 