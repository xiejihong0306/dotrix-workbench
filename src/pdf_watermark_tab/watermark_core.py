from PIL import Image
from reportlab.pdfgen import canvas
import os
import tempfile
import math
import sys
import random
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import config


# 获取可执行文件目录（处理PyInstaller打包的情况）
def get_application_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        try:
            # PyInstaller在临时目录中创建了一个_MEI文件夹
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(sys.executable)
        return base_path
    else:
        # 如果是脚本运行
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 检查当前目录是否为pdf_watermark_tab目录
        parent_dir = os.path.dirname(current_dir)
        if os.path.basename(current_dir) == 'pdf_watermark_tab' and os.path.basename(parent_dir) == 'src':
            # 返回src的父目录（因为pictures和fonts在src的上一级）
            return os.path.dirname(parent_dir)
        elif os.path.basename(current_dir) == 'src':
            # 返回父目录（因为pictures和fonts在src的上一级）
            return os.path.dirname(current_dir)
        else:
            return current_dir


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


def _add_center_image_watermark(c, watermark_image, page_width, page_height, img_scale, img_opacity):
    """
    在PDF页面中心添加图片水印
    
    参数:
        c: PDF canvas对象
        watermark_image: 水印图片路径
        page_width: 页面宽度
        page_height: 页面高度
        img_scale: 图片缩放比例(0-1)
        img_opacity: 图片透明度(0-1)
    
    返回:
        元组 (new_width, new_height): 调整后的图片尺寸
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
    
    # 计算图片在页面上的居中位置
    x_centered = (page_width - new_width) / 2
    y_centered = (page_height - new_height) / 2
    
    # 在透明画布上绘制图片水印
    c.saveState()
    c.setFillAlpha(img_opacity)  # 设置透明度
    c.drawImage(watermark_image, x_centered, y_centered, width=new_width, height=new_height)
    c.restoreState()
    
    return new_width, new_height


def _add_english_logo_watermark(c, page_width, page_height, img_scale, img_opacity):
    """
    在PDF页面随机位置添加英文LOGO水印
    
    参数:
        c: PDF canvas对象
        page_width: 页面宽度
        page_height: 页面高度
        img_scale: 图片缩放比例(0-1)
        img_opacity: 图片透明度(0-1)
    
    返回:
        bool: 是否成功添加英文水印
    """
    # 准备英文水印图片
    app_path = get_application_path()
    eng_watermark_path = os.path.join(app_path, config.PICTURES_DIR, "dotrix_logo_eng.png")
    
    if not os.path.exists(eng_watermark_path):
        return False
    
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
    
    # 生成随机位置，确保图片完全在页面内
    rand_x = random.uniform(eng_new_width/2, page_width - eng_new_width)
    rand_y = random.uniform(eng_new_height/2, page_height - eng_new_height)
    
    # 在透明画布上绘制英文图片水印
    c.saveState()
    c.setFillAlpha(img_opacity)  # 使用相同的透明度
    c.drawImage(eng_watermark_path, rand_x, rand_y, width=eng_new_width, height=eng_new_height)
    c.restoreState()
    
    return True


def _add_grid_text_watermarks(c, watermark_text, page_width, page_height, font_name, font_size, text_opacity, angle, rows, cols):
    """
    在PDF页面添加网格形式的文字水印
    
    参数:
        c: PDF canvas对象
        watermark_text: 水印文字内容
        page_width: 页面宽度
        page_height: 页面高度
        font_name: 字体名称
        font_size: 字体大小
        text_opacity: 文字透明度(0-1)
        angle: 文字旋转角度（度）
        rows: 每页上水印文字的行数
        cols: 每页上水印文字的列数
    """
    # 设置字体和颜色
    watermark_color = Color(0, 0, 0, alpha=text_opacity)
    
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
    
    return actual_cols


def _add_horizontal_text_watermarks(c, watermark_text, page_width, page_height, font_name):
    """
    在PDF页面随机位置添加水平文字水印
    
    参数:
        c: PDF canvas对象
        watermark_text: 水印文字内容
        page_width: 页面宽度
        page_height: 页面高度
        font_name: 字体名称
    """
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
        
        # 1. 绘制中心图片水印
        _add_center_image_watermark(c, watermark_image, page_width, page_height, img_scale, img_opacity)
        
        # 2. 添加英文水印图片在随机位置（如果存在）
        _add_english_logo_watermark(c, page_width, page_height, img_scale, img_opacity)
        
        # 3. 绘制多条文字水印以网格形式分布
        actual_cols = _add_grid_text_watermarks(c, watermark_text, page_width, page_height, 
                                           font_name, font_size, text_opacity, angle, rows, cols)
        
        # 4. 添加随机位置的水平水印（跑马灯效果）
        if add_horizontal:
            _add_horizontal_text_watermarks(c, watermark_text, page_width, page_height, font_name)
        
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
    has_eng_watermark = os.path.exists(os.path.join(get_application_path(), config.PICTURES_DIR, "dotrix_logo_eng.png"))
    if has_eng_watermark:
        print(f"每页添加了随机位置的英文LOGO水印")


