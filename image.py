from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

def text_wrap(text, width):
    """将文本按指定宽度换行，中英文字符长度不同"""
    wrapped_text = ""
    line_len = 0
    for char in text:
        if line_len + (2 if ord(char) > 127 else 1) > width:
            wrapped_text += '\n'
            line_len = 0
        wrapped_text += char
        line_len += 2 if ord(char) > 127 else 1
    return wrapped_text

def conversation2png(title, conv_user, conv_robot, seed=42):
    # 图片大小
    img_width = 1000
    img_height = 2000

    # 背景颜色
    bg_color = (255, 255, 255)
    bg_color = (32, 32, 32)

    # 字体文件路径
    font_path = 'font/MaoKenZhuYuanTi-2.ttf'

    # 字体大小
    font_size = 24

    # 字体颜色
    font_color = (0, 0, 0)

    # 创建一张空白图片
    image = Image.new('RGB', (img_width, img_height), bg_color)

    # 获取头像图片并调整大小

    user_url = f"https://api.dicebear.com/5.x/lorelei/png?seed={seed}"
    robot_url = f"https://api.dicebear.com/5.x/bottts/png?seed={seed}"
    avatar_default = Image.new(mode="RGBA", size=(50, 50), color="gray")
    try:
        avatar_user = Image.open(BytesIO(requests.get(user_url).content)).resize((50, 50))
        avatar_robot = Image.open(BytesIO(requests.get(robot_url).content)).resize((50, 50))
    except:
        avatar_user = avatar_default
        avatar_robot = avatar_default

    # image.paste(avatar_a, (50, 50))
    # image.paste(avatar_b, (img_width - 150, 50))

    # 创建Draw对象
    draw = ImageDraw.Draw(image)

    # 定义字体
    font = ImageFont.truetype(font_path, font_size)

    # 定义对话内容
    dialogue = []
    for us, rs in zip(conv_user, conv_robot):
        dialogue.append({'speaker': 'user', 'text': us})
        dialogue.append({'speaker': 'robot', 'text': rs})
    # dialogue = [
    #     {'speaker': 'A', 'text': '你好啊\nHello'},
    #     {'speaker': 'B', 'text': '你好，最近怎么样？'},
    #     {'speaker': 'A', 'text': '还不错，最近忙着写代码呢'},
    #     {'speaker': 'B', 'text': '哦，有什么好玩的项目吗？'},
    #     {'speaker': 'A', 'text': '有啊，最近在做一个图片渲染的项目 This is a wonderful project nice'},
    #     {'speaker': 'B', 'text': '听起来很有趣啊，能不能给我看看效果？听起来很有趣啊，能不能给我看看效果？有啊，最近在做一个图片渲染的项目'}
    # ]

    # 定义对话框位置和大小
    dialogue_box_width = 780
    dialogue_box_height = font_size + 10
    dialogue_box_x = 110
    dialogue_box_y = 100
    dialogue_box_padding = 10

    # 渲染标题文字
    draw.text((dialogue_box_x // 2, dialogue_box_y - font_size), title, font=font, fill=(233, 233, 233))

    # 渲染对话文字
    box_y = dialogue_box_x
    total_height = dialogue_box_y
    for i, message in enumerate(dialogue):
        speaker = message['speaker']
        text = message['text']

        # 计算对话框位置
        box_x = dialogue_box_x

        box_y += (dialogue_box_padding + font_size)

        # 自动换行
        lines = textwrap.fill(text, width=31)
        # lines = text_wrap(text, width=62)
        print(lines)
        print('====')
        lines = lines.split('\n')

        # 计算对话框高度
        box_height = len(lines) * (font_size + dialogue_box_padding)

        # 更新总高度
        total_height += box_height + dialogue_box_padding

        # 绘制对话框
        fill_color = (240, 240, 240) if speaker == 'robot' else (237, 211, 161)
        draw.rectangle([(box_x, box_y), (box_x + dialogue_box_width, box_y + box_height + dialogue_box_padding)], fill=fill_color, outline=(0, 0, 0))

        # 绘制头像
        if speaker == 'user':
            image.paste(avatar_user, (box_x - 64, box_y))
        else:
            image.paste(avatar_robot, (img_width - 96, box_y))

        # 绘制文字
        for line in lines:
            draw.text((box_x + 10, box_y + 10), line, font=font, fill=font_color)
            box_y += dialogue_box_height 

    # 调整图片高度
    total_height = box_y
    if total_height + 100 < img_height:
        image = image.crop((0, 0, img_width, total_height + 100))

    # 保存图片
    image.save('dialogue.png')
    return image