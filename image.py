from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import qrcode


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


def split_text(text, width, font):
    lines = []
    line = ''
    for word in text:
        if word == '\n':
            lines.append(line + '\n')
            line = ""
            continue
        if font.getlength(line + word) <= width:
            line += word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def conversation2png(title, conv_user, conv_robot, seed=42):
    # 图片大小
    img_width = 1000
    img_height = 1200 + 150 * len(conv_user)

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
        line_arr = []
        for txt in text.split('\n'):
            line_arr.append(textwrap.fill(txt, width=31))
        lines = '\n'.join(line_arr)
        # lines = text_wrap(text, width=62)
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


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    """
    绘制圆角矩形
    """
    # 计算圆角矩形的四个角的坐标
    x1, y1, x2, y2 = xy
    draw.rectangle([(x1+radius,y1),(x2-radius,y2)], fill=fill, outline=outline, width=width)
    draw.rectangle([(x1,y1+radius),(x2,y2-radius)], fill=fill, outline=outline, width=width)
    draw.pieslice([(x1,y1),(x1+radius*2,y1+radius*2)], 180, 270, fill=fill, outline=outline, width=width)
    draw.pieslice([(x2-radius*2,y1),(x2,y1+radius*2)], 270, 360, fill=fill, outline=outline, width=width)
    draw.pieslice([(x1,y2-radius*2),(x1+radius*2,y2)], 90, 180, fill=fill, outline=outline, width=width)
    draw.pieslice([(x2-radius*2,y2-radius*2),(x2,y2)], 0, 90, fill=fill, outline=outline, width=width)


def generate_tag_image(text):
    # 字体文件路径
    font_path = 'font/MaoKenZhuYuanTi-2.ttf'
    # font_path = 'font/NotoColorEmoji-Regular.ttf'

    # 设置字体
    font = ImageFont.truetype(font_path, size=16)

    # 计算文本所需宽度和高度
    text_width, text_height = font.getbbox(text)[-2:]

    # 创建画布
    img_width = text_width + 20
    img_height = text_height + 20
    img = Image.new("RGBA", (img_width, img_height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制圆角矩形
    radius = text_height / 1.5
    rectangle_xy = (0, 0, text_width + 20, text_height + 20)
    rectangle_fill = (255, 255, 255, 255)
    draw_rounded_rectangle(draw, rectangle_xy, radius, fill=rectangle_fill)

    # 绘制文本
    text_x = 10
    text_y = 10
    text_color = (0, 0, 0, 255)
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    return img
    

def generate_article_image(title, summary, url, tag_list, words, author):
    title = title.strip()
    summary = summary.strip()

    # 设置图片宽度
    img_width = 1000

    # 字体文件路径
    font_path = 'font/MaoKenZhuYuanTi-2.ttf'

    # 设置字体
    title_font = ImageFont.truetype(font_path, size=30)
    summary_font = ImageFont.truetype(font_path, size=24)
    hint_font = ImageFont.truetype(font_path, size=16)

    # 计算摘要所需高度
    summary_line_padding = 10
    # summary_lines = textwrap.wrap(summary, width=32)
    summary_lines = split_text(summary, 860, summary_font)
    summary_height = len(summary_lines) * (summary_font.getbbox(' ')[-1] + summary_line_padding) + 68 - 7 * 3
    summary_height = len(summary_lines) * (summary_font.getbbox(' ')[-1] + summary_line_padding + 4) + 31
    print('Summary height', summary_height)

    # 创建画布
    title_lines = split_text(title, 820, title_font)  # 自动标题换行
    title = "\n".join(title_lines)
    title_text_height = len(title_lines) * (title_font.getbbox(title)[-1] + 0)
    print("["+title+"]", title_font.getbbox(title), summary_font.getlength(title), '==', title_text_height)
    img_height = 50 + title_text_height + 50 + summary_height + 50 + 150
    img = Image.new("RGB", (img_width, img_height), color=(255, 192, 0))
    draw = ImageDraw.Draw(img)

    # 绘制标题
    title_x = 50
    title_y = 50
    draw.text((title_x, title_y), title, font=title_font, fill=(0, 0, 0))

    # 绘制摘要
    summary_x = 50
    summary_y = title_y + 50 + title_text_height
    summary_bg_width = 900
    summary_bg_height = summary_height
    summary_bg_x = summary_x
    summary_bg_y = summary_y
    ofs = 8
    draw_rounded_rectangle(draw, (summary_bg_x+ofs, summary_bg_y+ofs, summary_bg_x + summary_bg_width + ofs, summary_bg_y + summary_bg_height + ofs), radius=40, fill=(132, 60, 12), outline=(0, 192, 0), width=0)
    draw_rounded_rectangle(draw, (summary_bg_x, summary_bg_y, summary_bg_x + summary_bg_width, summary_bg_y + summary_bg_height), radius=40, fill=(255, 255, 255), outline=(0, 192, 0), width=0)

    # 在摘要上方绘制提示文字
    read_words_per_minute = 380
    draw.text((summary_x + 20, summary_y - 30), f"全文约 {words} 字 （{max(round(words / read_words_per_minute), 1)} 分钟阅读）", font=hint_font, fill=(0, 32, 192))

    summary_x += 20
    summary_y += 20
    summary_lines = split_text(summary, 860, summary_font)
    for line in summary_lines:
        draw.text((summary_x, summary_y), line, font=summary_font, fill=(0, 0, 0))
        summary_y += summary_font.getbbox(line)[-1] + summary_line_padding

    # summary_x = 50
    # summary_y = title_y + 50 + title_font.getbbox(title)[-1]
    # summary_lines = textwrap.wrap(summary, width=32)
    # for line in summary_lines:
    #     draw.text((summary_x, summary_y), line, font=summary_font, fill=(0, 0, 0))
    #     summary_y += summary_font.getbbox(line)[-1] + summary_line_padding
        print("["+line+"]", summary_font.getbbox(line), summary_font.getlength(line), '==', summary_y)


    # 绘制标签
    tag_x = summary_x
    tag_y = summary_y + 40
    for tag_str in tag_list:
        img_tag = generate_tag_image("· " + tag_str)
        img.paste(img_tag, (tag_x, tag_y), img_tag)
        tag_x += img_tag.size[0] + 20
        print('img size', img_tag.size)

    # 绘制二维码
    qr_size = 150
    qr_margin = 20
    qr_x = img_width - qr_size - qr_margin
    qr_y = img_height - qr_size - qr_margin
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((qr_size, qr_size)) # 缩放二维码
    img.paste(qr_img, (qr_x, qr_y))

    # 绘制来源信息及版权声明
    source_x = summary_x
    source_y = tag_y + 60

    draw.text((source_x, source_y), f"[*] 本内容使用 ChatGPT 辅助生成\n\n原始来源：{author}    >> 扫描右侧二维码查看原文", font=hint_font, fill=(0, 32, 192))
    print((source_x, source_y), "["+author+"]")


    # 裁剪图片
    img = img.crop((0, 0, img_width, title_y + 50 + title_text_height + 50 + summary_height + qr_size))
    print(img.size)

    return img

if __name__ == '__main__':
    title = "人手一个ChatGPT！微软DeepSpeed Chat震撼发布.吴恩达ChatGPT Prompt Engineering for De"
    summary = "本文介绍了微软开源的DeepSpeed Chat系统框架，它可以帮助开发者实现类ChatGPT模型的端到端RLHF训练，并大幅降低训练成本。文章详细介绍了DeepSpeed Chat的三大核心功能和不同规模模型和硬件配置下的训练时间和成本。同时，本文还介绍了DeepSpeed-HE在Azure云上训练RLHF模型的优异性能，包括快速训练、卓越的扩展性和完整的训练流程。特别是，混合引擎的设计使得RLHF训练的经验生成阶段的推理执行过程中，DeepSpeed混合引擎使用轻量级的内存管理系统，来处理KV缓存和中间结果，同时使用高度优化的推理CUDA核和张量并行计算，与现有方案相比，实现了吞吐量（每秒token数）的大幅提升。推荐阅读此文，了解如何使用DeepSpeed Chat实现高质量类ChatGPT模型的训练，以及DeepSpeed-HE的优势和混合引擎的设计，对于从事RLHF模型训练的数据科学家和研究者具有重要参考价值。"
    url = "https://example.com"
    tag_list = ["人工智能", "NLP"]
    words = 400
    author = "hahah"
    summary = "本文介绍了吴恩达和OpenAI工程师Isa Fulford推出的课程ChatGPT Prompt Engineering for Developers，该课程讲解了基于预训练模型的Prompt工程和指导原则。对于开发者来说，这是一个非常有价值的课程，建议关注该领域的读者可以深入了解。推荐阅读原版视频学习，以获取更多实用知识和技能。"
    # summary = "a\nb\ncccdddd"

    img = generate_article_image(title, summary, url, tag_list, words, author)
    # img.show()
    img.save('summary.png')

    #TODO: 调整每行的字符数以匹配宽度 Done
    #TODO: 加入类别 + emoji 的标签 tag
    #TODO: 给标题加上 emoji 的诠释
    # https://playgpt3.streamlit.app/?share=y0snzxcr

    # from pilmoji import Pilmoji
    # from PIL import Image, ImageFont

    # im = Image.new('RGB', (1024, 768))

    # drawer = Pilmoji(im).draw

    # FONT_PATH = 'font/NotoColorEmoji.ttf'
    # FONT_PATH = 'font/MaoKenZhuYuanTi-2.ttf'
    # FONT_PATH = r'D:\\Workspace\\streamlit-gpt3\\font\\NotoColorEmoji-Regular.ttf'
    # font_size = 30
    # font = ImageFont.truetype(FONT_PATH, size=font_size)

    # text = "Hello, world! 👋 Here are some emojis: 🎨 🌊 😎"
    # drawer((10, 10), text, font=font)

    # im.save('emoji.png')

    # from PIL import Image, ImageDraw, ImageFont

    # back_ground_color = (50, 50, 50)

    # # unicode_text = "some test\U0001f602"
    # unicode_text = "😎" # "\U0001f602"
    # im = Image.new("RGB", (500, 500), back_ground_color)
    # draw = ImageDraw.Draw(im)

    # # noto emoji, bit-map based, src: https://github.com/googlefonts/noto-emoji/blob/main/fonts/NotoColorEmoji.ttf
    # # apple emoji, bit-map based, src: https://github.com/samuelngs/apple-emoji-linux/releases
    # # segoe ui emoji, vector-based, works with different font size, font from here: https://fontsdata.com/132714/segoeuiemoji.htm (for test only)

    # font_info = { #'symbola': [r"E:\symbola-font\Symbola-AjYx.ttf", 30],
    #             'notoemoji': [r"D:\\Workspace\\streamlit-gpt3\\font\\NotoColorEmoji-Regular.ttf", 30],
    #             #'appleemoji': [r"E:\AppleColorEmoji.ttf", 137],
    #             #'segoeuiemoji': [r"E:\segoeuiemoji\seguiemj.ttf", 50]
    #             }

    # pos = [(100, 10), (50, 40), (50, 160), (100, 320)]

    # for i, item in enumerate(font_info.items()):
    #     path, size = item[1]
    #     font = ImageFont.FreeTypeFont(path, size)
    #     draw.text(pos[i], unicode_text, font=font, embedded_color=True)

    # im.save('emoji.png')