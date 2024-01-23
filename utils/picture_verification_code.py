from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

def check_code(width = 140, height = 30, interfere=20, char_len = 5):
    # width = 120     # 宽
    # height = 30     # 高
    # char_len = 5    # 验证码字符个数
    code = []

    # 创建一张空白的验证码图片
    img = Image.new(mode='RGB',size=(width,height), color=(221,227,233))
    # 创建一个绘图对象
    draw = ImageDraw.Draw(img, mode="RGB")

    # 生成随机字符
    def rndChar():
        return chr(random.randint(65,90))

    # 生成随机颜色
    def rndColor():
        return (
            random.randint(0,255),
            random.randint(10,255),
            random.randint(64, 255),
        )

    # 写文字
    font = ImageFont.truetype('utils/ttf.ttf',28)
    for i in range(char_len):
        char = rndChar()
        code.append(char)
        h = random.random()
        draw.text((i * width / char_len +5 , h), char, font=font, fill=rndColor())

    # 写干扰点
    for i in range(interfere):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())

    # 写干扰圆圈
    for i in range(interfere):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x+4, y+ 4), 0, 90, fill = rndColor())

    # 画干扰线
    for i in range(int(interfere / 10)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=rndColor())

    # 对验证码图片进行滤镜处理，增强边缘
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # 返回生成的验证码图片对象和验证码字符串
    return img, "".join(code)


if __name__ == '__main__':
    img_object, code = check_code()
    print(code)
    # 写入本地
    with open("code.png","wb")as f:
        img_object.save(f, format="png")

    # 写入内存
    # from io import BytesIO
    # stream = BytesIO()
    # img_object.save(stream, "png")
    # stream.getvalue()
