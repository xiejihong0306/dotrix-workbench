import PyPDF2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import io
import tempfile
import math
import sys
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter


# 获取可执行文件目录（处理PyInstaller打包的情况）
def get_application_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行
        return os.path.dirname(os.path.abspath(__file__))


# 注册宋体
font_registered = False
try:
    # 尝试从预打包的字体目录加载
    app_path = get_application_path()
    bundled_font_path = os.path.join(app_path, 'fonts', 'simsun.ttc')
    
    if os.path.exists(bundled_font_path):
        pdfmetrics.registerFont(TTFont('SimSun', bundled_font_path))
        font_registered = True
        print(f"从打包目录加载宋体: {bundled_font_path}")
except:
    print("警告：无法从打包目录加载宋体")

# 如果上面失败，尝试从系统加载
if not font_registered:
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        font_registered = True
        print("从系统目录加载宋体成功")
    except:
        print("警告：无法从系统目录加载宋体字体文件，将使用默认字体")


def add_text_watermark(input_pdf, watermark_text, output_pdf, font_name='SimSun', font_size=36, 
                     opacity=0.5, angle=45, on_top=True, color=(0, 0, 0)):
    """
    在PDF的每一页添加旋转文字水印
    
    参数:
        input_pdf: 输入PDF文件路径
        watermark_text: 水印文字内容
        output_pdf: 输出PDF文件路径
        font_name: 字体名称
        font_size: 字体大小
        opacity: 水印透明度(0-1)
        angle: 旋转角度（度）
        on_top: 是否将水印放在内容顶层
        color: RGB颜色元组，值范围0-1
    """
    # 读取原始PDF
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    # 创建RGB颜色对象，添加透明度
    watermark_color = Color(color[0], color[1], color[2], alpha=opacity)
    
    # 处理每一页
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # 创建一个临时PDF作为水印
        watermark_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        c = canvas.Canvas(watermark_pdf.name, pagesize=(page_width, page_height))
        
        # 设置字体和颜色
        if font_name in pdfmetrics._fonts:
            c.setFont(font_name, font_size)
        else:
            c.setFont("Helvetica", font_size)  # 默认字体
            
        c.setFillColor(watermark_color)
        
        # 计算文本在页面上的居中位置
        text_width = c.stringWidth(watermark_text, font_name, font_size)
        text_height = font_size  # 近似高度
        
        # 居中位置
        x_centered = (page_width - text_width) / 2
        y_centered = (page_height - text_height) / 2
        
        # 保存状态以便旋转
        c.saveState()
        
        # 将原点移到页面中心
        c.translate(page_width/2, page_height/2)
        # 旋转指定角度（角度转弧度）
        c.rotate(angle)
        # 绘制文字（注意调整位置，因为原点已经移到了中心）
        c.drawString(-text_width/2, -text_height/2, watermark_text)
        
        # 恢复状态
        c.restoreState()
        c.save()
        
        # 关闭临时文件
        watermark_pdf.close()
        
        watermark_reader = PdfReader(watermark_pdf.name)
        watermark_page = watermark_reader.pages[0]
        
        # 根据on_top参数决定水印是在顶层还是底层
        if on_top:
            # 将水印合并到原始页面上（水印在顶层）
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)
        else:
            # 将原始页面合并到水印页面上（水印在底层）
            watermark_page.merge_page(page)
            pdf_writer.add_page(watermark_page)
        
        # 清理临时文件
        os.unlink(watermark_pdf.name)
    
    # 写入输出文件
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)
    
    position = "顶层" if on_top else "底层"
    print(f"文字水印已添加到{position}，输出文件: {output_pdf}")
    print(f"文字: '{watermark_text}', 字体: {font_name}, 大小: {font_size}, 角度: {angle}度, 透明度: {opacity}")


def add_watermark(input_pdf, watermark_image, output_pdf, scale=0.5, opacity=0.5, on_top=True):
    """
    在PDF的每一页添加透明水印
    
    参数:
        input_pdf: 输入PDF文件路径
        watermark_image: 水印图片路径
        output_pdf: 输出PDF文件路径
        scale: 水印缩放比例(0-1)
        opacity: 水印透明度(0-1)
        on_top: 是否将水印放在内容顶层，True为顶层，False为底层
    """
    # 打开水印图片
    img = Image.open(watermark_image)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 调整图片尺寸
    img_width, img_height = img.size
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 读取原始PDF
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    # 处理每一页
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # 创建一个临时PDF作为水印
        watermark_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        c = canvas.Canvas(watermark_pdf.name, pagesize=(page_width, page_height))
        
        # 计算图片在页面上的居中位置
        x_centered = (page_width - new_width) / 2
        y_centered = (page_height - new_height) / 2
        
        # 在透明画布上绘制水印
        c.saveState()
        c.setFillAlpha(opacity)  # 设置透明度
        c.drawImage(watermark_image, x_centered, y_centered, width=new_width, height=new_height)
        c.restoreState()
        c.save()
        
        # 关闭临时文件
        watermark_pdf.close()
        
        watermark_reader = PdfReader(watermark_pdf.name)
        watermark_page = watermark_reader.pages[0]
        
        # 根据on_top参数决定水印是在顶层还是底层
        if on_top:
            # 将水印合并到原始页面上（水印在顶层）
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)
        else:
            # 将原始页面合并到水印页面上（水印在底层）
            watermark_page.merge_page(page)
            pdf_writer.add_page(watermark_page)
        
        # 清理临时文件
        os.unlink(watermark_pdf.name)
    
    # 写入输出文件
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)
    
    position = "顶层" if on_top else "底层"
    print(f"图片水印已添加到{position}，输出文件: {output_pdf}")
    print(f"使用的透明度: {opacity}，缩放比例: {scale}")


def add_combined_watermark(input_pdf, watermark_image, watermark_text, output_pdf, 
                         img_scale=0.5, img_opacity=0.5, 
                         font_name='SimSun', font_size=36, text_opacity=0.5, angle=45,
                         on_top=True):
    """
    在PDF的每一页同时添加图片和文字水印
    
    参数:
        input_pdf: 输入PDF文件路径
        watermark_image: 水印图片路径
        watermark_text: 水印文字内容
        output_pdf: 输出PDF文件路径
        img_scale: 图片缩放比例(0-1)
        img_opacity: 图片透明度(0-1)
        font_name: 字体名称
        font_size: 字体大小
        text_opacity: 文字透明度(0-1)
        angle: 文字旋转角度（度）
        on_top: 是否将水印放在内容顶层
    """
    # 打开水印图片
    img = Image.open(watermark_image)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 调整图片尺寸
    img_width, img_height = img.size
    new_width = int(img_width * img_scale)
    new_height = int(img_height * img_scale)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 准备英文水印图片
    eng_watermark_path = None
    eng_img = None
    eng_new_width = 0
    eng_new_height = 0
    
    # 检查英文水印图片是否存在
    app_path = get_application_path()
    eng_watermark_path = os.path.join(app_path, "pictures", "dotrix_logo_eng.png")
    if os.path.exists(eng_watermark_path):
        # 打开英文水印图片
        eng_img = Image.open(eng_watermark_path)
        if eng_img.mode != 'RGBA':
            eng_img = eng_img.convert('RGBA')
        
        # 调整英文水印图片尺寸 - 使用更小的缩放比例 (70%的主水印大小)
        eng_img_width, eng_img_height = eng_img.size
        eng_scale = img_scale * 0.5  # 比主水印小50%
        eng_new_width = int(eng_img_width * eng_scale)
        eng_new_height = int(eng_img_height * eng_scale)
        eng_img = eng_img.resize((eng_new_width, eng_new_height), Image.LANCZOS)
    
    # 读取原始PDF
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    # 创建RGB颜色对象，添加透明度
    watermark_color = Color(0, 0, 0, alpha=text_opacity)  # 黑色文字
    
    # 处理每一页
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # 创建一个临时PDF作为水印
        watermark_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        c = canvas.Canvas(watermark_pdf.name, pagesize=(page_width, page_height))
        
        # 1. 绘制图片水印
        # 计算图片在页面上的居中位置
        x_centered = (page_width - new_width) / 2
        y_centered = (page_height - new_height) / 2
        
        # 在透明画布上绘制图片水印
        c.saveState()
        c.setFillAlpha(img_opacity)  # 设置透明度
        c.drawImage(watermark_image, x_centered, y_centered, width=new_width, height=new_height)
        c.restoreState()
        
        # 1.5 添加英文水印图片在随机位置（如果存在）
        if eng_watermark_path and os.path.exists(eng_watermark_path):
            # 生成随机位置，确保图片完全在页面内
            rand_x = random.uniform(eng_new_width/2, page_width - eng_new_width)
            rand_y = random.uniform(eng_new_height/2, page_height - eng_new_height)
            
            # 在透明画布上绘制英文图片水印
            c.saveState()
            c.setFillAlpha(img_opacity)  # 使用相同的透明度
            c.drawImage(eng_watermark_path, rand_x, rand_y, width=eng_new_width, height=eng_new_height)
            c.restoreState()
        
        # 2. 绘制文字水印
        # 设置字体和颜色
        if font_name in pdfmetrics._fonts:
            c.setFont(font_name, font_size)
        else:
            c.setFont("Helvetica", font_size)  # 默认字体
            
        c.setFillColor(watermark_color)
        
        # 计算文本在页面上的居中位置
        text_width = c.stringWidth(watermark_text, font_name, font_size)
        text_height = font_size  # 近似高度
        
        # 保存状态以便旋转
        c.saveState()
        
        # 将原点移到页面中心
        c.translate(page_width/2, page_height/2)
        # 旋转指定角度（角度转弧度）
        c.rotate(angle)
        # 绘制文字（注意调整位置，因为原点已经移到了中心）
        c.drawString(-text_width/2, -text_height/2, watermark_text)
        
        # 恢复状态
        c.restoreState()
        c.save()
        
        # 关闭临时文件
        watermark_pdf.close()
        
        watermark_reader = PdfReader(watermark_pdf.name)
        watermark_page = watermark_reader.pages[0]
        
        # 根据on_top参数决定水印是在顶层还是底层
        if on_top:
            # 将水印合并到原始页面上（水印在顶层）
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)
        else:
            # 将原始页面合并到水印页面上（水印在底层）
            watermark_page.merge_page(page)
            pdf_writer.add_page(watermark_page)
        
        # 清理临时文件
        os.unlink(watermark_pdf.name)
    
    # 写入输出文件
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)
    
    position = "顶层" if on_top else "底层"
    print(f"图片和文字水印已同时添加到{position}，输出文件: {output_pdf}")


def add_multiple_watermarks(input_pdf, watermark_image, watermark_text, output_pdf, 
                         img_scale=0.5, img_opacity=0.5, 
                         font_name='SimSun', font_size=36, text_opacity=0.5, angle=45,
                         on_top=True, rows=5, cols=3, add_horizontal=True):
    """
    在PDF的每一页添加多条文字水印和一个图片水印，以网格形式均匀分布
    
    参数:
        input_pdf: 输入PDF文件路径
        watermark_image: 水印图片路径
        watermark_text: 水印文字内容
        output_pdf: 输出PDF文件路径
        img_scale: 图片缩放比例(0-1)
        img_opacity: 图片透明度(0-1)
        font_name: 字体名称
        font_size: 字体大小
        text_opacity: 文字透明度(0-1)
        angle: 文字旋转角度（度）
        on_top: 是否将水印放在内容顶层
        rows: 每页上水印文字的行数
        cols: 每页上水印文字的列数
        add_horizontal: 是否添加随机位置的水平水印
        
    每页PDF包含:
    1. 中心位置的中文图片水印
    2. 随机位置的英文图片水印 (比中文水印尺寸小50%)
    3. 网格排布的倾斜文字水印
    4. 随机位置的水平黑色与白色文字水印
    """
    # 导入随机模块
    import random
    
    # 打开水印图片
    img = Image.open(watermark_image)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 调整图片尺寸
    img_width, img_height = img.size
    new_width = int(img_width * img_scale)
    new_height = int(img_height * img_scale)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 准备英文水印图片
    eng_watermark_path = None
    eng_img = None
    eng_new_width = 0
    eng_new_height = 0
    
    # 检查英文水印图片是否存在
    app_path = get_application_path()
    eng_watermark_path = os.path.join(app_path, "pictures", "dotrix_logo_eng.png")
    if os.path.exists(eng_watermark_path):
        # 打开英文水印图片
        eng_img = Image.open(eng_watermark_path)
        if eng_img.mode != 'RGBA':
            eng_img = eng_img.convert('RGBA')
        
        # 调整英文水印图片尺寸 - 使用更小的缩放比例
        eng_img_width, eng_img_height = eng_img.size
        eng_scale = img_scale * 0.2  # 比主水印小80%
        eng_new_width = int(eng_img_width * eng_scale)
        eng_new_height = int(eng_img_height * eng_scale)
        eng_img = eng_img.resize((eng_new_width, eng_new_height), Image.LANCZOS)
    
    # 读取原始PDF
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    # 创建RGB颜色对象，添加透明度
    watermark_color = Color(0, 0, 0, alpha=text_opacity)
    
    # 处理每一页
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # 创建一个临时PDF作为水印
        watermark_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        c = canvas.Canvas(watermark_pdf.name, pagesize=(page_width, page_height))
        
        # 1. 绘制图片水印
        # 计算图片在页面上的居中位置
        x_centered = (page_width - new_width) / 2
        y_centered = (page_height - new_height) / 2
        
        # 在透明画布上绘制图片水印
        c.saveState()
        c.setFillAlpha(img_opacity)  # 设置透明度
        c.drawImage(watermark_image, x_centered, y_centered, width=new_width, height=new_height)
        c.restoreState()
        
        # 1.5 添加英文水印图片在随机位置（如果存在）
        if eng_watermark_path and os.path.exists(eng_watermark_path):
            # 生成随机位置，确保图片完全在页面内
            rand_x = random.uniform(eng_new_width/2, page_width - eng_new_width)
            rand_y = random.uniform(eng_new_height/2, page_height - eng_new_height)
            
            # 在透明画布上绘制英文图片水印
            c.saveState()
            c.setFillAlpha(img_opacity)  # 使用相同的透明度
            c.drawImage(eng_watermark_path, rand_x, rand_y, width=eng_new_width, height=eng_new_height)
            c.restoreState()
        
        # 2. 绘制多条文字水印以网格形式分布
        # 设置字体和颜色
        if font_name in pdfmetrics._fonts:
            c.setFont(font_name, font_size)
        else:
            c.setFont("Helvetica", font_size)  # 默认字体
            
        c.setFillColor(watermark_color)
        
        # 计算文本宽度和对角线长度（旋转后的实际占用空间）
        text_width = c.stringWidth(watermark_text, font_name, font_size)
        text_height = font_size  # 近似高度
        
        # 计算旋转后文本的对角线长度（水平投影）
        angle_rad = math.radians(angle)
        rotated_width = abs(text_width * math.cos(angle_rad)) + abs(text_height * math.sin(angle_rad))
        
        # 根据页面尺寸和文本长度自动调整列数
        # 确保文本之间有足够空间不重叠
        required_space_per_text = rotated_width * 1.5  # 加50%的安全边距
        max_possible_cols = max(1, int(page_width / required_space_per_text))
        
        # 如果计算出的最大可能列数小于请求的列数，则减少列数
        actual_cols = min(cols, max_possible_cols)
        
        # 计算行列间距，确保水印均匀分布且不重叠
        row_spacing = page_height / (rows + 1)  # +1 是为了在边缘留出空间
        col_spacing = page_width / (actual_cols + 1)   # +1 是为了在边缘留出空间
        
        # 在页面上添加网格状水印
        for i in range(rows):
            y_pos = (i + 1) * row_spacing
            
            # 根据行号交错排列水印，增强覆盖效果，减少重叠
            offset = (i % 2) * (col_spacing / 2)
            
            for j in range(actual_cols):
                x_pos = offset + (j + 1) * col_spacing
                
                # 保存状态以便旋转
                c.saveState()
                
                # 将原点移到网格中的每个点
                c.translate(x_pos, y_pos)
                # 旋转指定角度（角度转弧度）
                c.rotate(angle)
                # 绘制文字
                c.drawString(-text_width/2, -text_height/2, watermark_text)
                
                # 恢复状态
                c.restoreState()
        
        # 3. 添加随机位置的水平水印（跑马灯效果）
        if add_horizontal:
            # 设置小字号，不透明黑色
            horizontal_size = 7  # 小字号
            c.setFont(font_name, horizontal_size)
            c.setFillColor(Color(0, 0, 0, alpha=1.0))  # 不透明黑色
            
            # 生成3个随机位置的水平水印
            horizontal_text_width = c.stringWidth(watermark_text, font_name, horizontal_size)
            
            for _ in range(3):
                # 生成随机位置
                rand_x = random.uniform(horizontal_text_width/2, page_width - horizontal_text_width/2)
                rand_y = random.uniform(horizontal_size*2, page_height - horizontal_size*2)
                
                # 绘制水平文字
                c.saveState()
                c.drawString(rand_x - horizontal_text_width/2, rand_y, watermark_text)
                c.restoreState()
            
            # 添加3个白色水平水印
            c.setFillColor(Color(1, 1, 1, alpha=1.0))  # 不透明白色
            
            for _ in range(3):
                # 生成随机位置（与黑色水印位置不同）
                rand_x = random.uniform(horizontal_text_width/2, page_width - horizontal_text_width/2)
                rand_y = random.uniform(horizontal_size*2, page_height - horizontal_size*2)
                
                # 绘制水平文字
                c.saveState()
                c.drawString(rand_x - horizontal_text_width/2, rand_y, watermark_text)
                c.restoreState()
        
        c.save()
        
        # 关闭临时文件
        watermark_pdf.close()
        
        watermark_reader = PdfReader(watermark_pdf.name)
        watermark_page = watermark_reader.pages[0]
        
        # 根据on_top参数决定水印是在顶层还是底层
        if on_top:
            # 将水印合并到原始页面上（水印在顶层）
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)
        else:
            # 将原始页面合并到水印页面上（水印在底层）
            watermark_page.merge_page(page)
            pdf_writer.add_page(watermark_page)
        
        # 清理临时文件
        os.unlink(watermark_pdf.name)
    
    # 写入输出文件
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)
    
    position = "顶层" if on_top else "底层"
    print(f"网格状文字水印已添加到{position}，输出文件: {output_pdf}")
    print(f"使用了 {rows} 行，每行约 {actual_cols} 个水印")
    if add_horizontal:
        print(f"每页添加了3个黑色和3个白色随机位置的水平水印")
    if eng_watermark_path and os.path.exists(eng_watermark_path):
        print(f"每页添加了随机位置的英文LOGO水印")


# 示例使用 - 只在直接运行脚本时执行，作为导入模块时不执行
if __name__ == "__main__":
    input_pdf = r"C:\Users\paxini-24042401\Desktop\《STL源码剖析》_11176655.pdf"  # 原始 PDF 文件路径
    watermark_path = r"C:\Users\paxini-24042401\Pictures\图片1.png"  # 水印图片路径
    output_pdf = r"C:\Users\paxini-24042401\Desktop\output.pdf"  # 输出带水印的 PDF 文件路径

    # 同时添加图片和文字水印
    add_combined_watermark(
        input_pdf=input_pdf,
        watermark_image=watermark_path,
        watermark_text="PDF加水印测试",
        output_pdf=output_pdf,
        img_scale=0.5,
        img_opacity=0.3,
        font_name="SimSun",
        font_size=36,
        text_opacity=0.5,
        angle=45,
        on_top=True
    )