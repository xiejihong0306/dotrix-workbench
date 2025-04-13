#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF密码保护模块，用于为PDF添加用户密码保护
"""

import os
import fitz  # PyMuPDF
from pypinyin import lazy_pinyin


def add_password_to_pdf(input_pdf, output_pdf, password):
    """
    为PDF添加用户密码保护
    
    Args:
        input_pdf: 输入PDF文件路径
        output_pdf: 输出PDF文件路径
        password: 用于保护PDF的密码
    
    Returns:
        bool: 是否成功添加密码
    """
    try:
        # 打开PDF文件
        doc = fitz.open(input_pdf)
        
        # 设置PDF权限和密码
        # 使用兼容不同版本的PyMuPDF的方式设置权限
        perm = int(
            fitz.PDF_PERM_ACCESSIBILITY |  # 允许访问性
            fitz.PDF_PERM_PRINT |          # 允许打印
            fitz.PDF_PERM_COPY |           # 允许复制内容
            fitz.PDF_PERM_ANNOTATE |       # 允许注释
            fitz.PDF_PERM_ASSEMBLE |       # 允许组装
            fitz.PDF_PERM_FORM |           # 允许填写表单
            fitz.PDF_PERM_MODIFY           # 允许修改
        )
        
        # 应用加密设置并保存
        # 添加压缩选项以减小文件大小
        doc.save(
            output_pdf,
            encryption=fitz.PDF_ENCRYPT_AES_256,  # 恢复使用AES-256加密
            user_pw=password,
            owner_pw=password,
            permissions=perm,
            garbage=4,  # 完全垃圾收集
            deflate=True,  # 使用deflate压缩
            pretty=False  # 不使用美化格式（减小大小）
        )
        doc.close()
        return True
    except Exception as e:
        print(f"添加密码时出错: {str(e)}")
        return False


def get_pinyin_password(chinese_name):
    """
    将中文姓名转换为拼音作为密码
    
    Args:
        chinese_name: 中文姓名
    
    Returns:
        str: 拼音密码 (无空格)
    """
    if not chinese_name:
        return ""
    
    # 转换为拼音并连接
    pinyin_list = lazy_pinyin(chinese_name)
    return ''.join(pinyin_list)


def secure_pdf_with_password(input_pdf, output_pdf, chinese_name, fallback_password="dotrix"):
    """
    为PDF添加基于学生姓名拼音的密码保护
    
    Args:
        input_pdf: 输入PDF文件路径
        output_pdf: 输出PDF文件路径
        chinese_name: 学生中文姓名
        fallback_password: 如果无法生成拼音密码时的备用密码
    
    Returns:
        tuple: (是否成功, 使用的密码)
    """
    # 生成拼音密码
    password = get_pinyin_password(chinese_name)
    
    # 如果无法获取拼音，使用备用密码
    if not password:
        password = fallback_password
    
    # 添加密码保护
    success = add_password_to_pdf(input_pdf, output_pdf, password)
    return success, password 