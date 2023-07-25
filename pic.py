from .chara import check_chara,check_name
from os.path import join
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import os,base64

PIC_PATH = os.path.dirname(__file__)

def contain_chinese(check_str):
    for ch in check_str:
        if '\u4e00' < ch <= '\u9fa5':
            return True
    return False
def contain_jepanese(check_str):
    for ch in check_str:
        if '\u0800' <= ch < '\u4e00':
            return True
    return False
def crop_transparent(image):
    width, height = image.size
    pixels = list(image.getdata())
    left = width
    right = 0
    top = height
    bottom = 0
    for y in range(height):
        for x in range(width):
            pixel = pixels[y * width + x]
            alpha = pixel[3]
            if alpha != 0:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image
async def stickmaker(image:Image,x:int,y:int,text:str,angle:int,size:int,fill:tuple)->Image:
    border = 5
    space = -15
    if contain_jepanese(text):
        font = ImageFont.truetype(join(PIC_PATH,r'fronts\stick.ttf'),size)
    else :
        if contain_chinese(text):
            font = ImageFont.truetype(join(PIC_PATH,r'fronts\stick2.ttf'),size)
        else:
            font = ImageFont.truetype(join(PIC_PATH,r'fronts\stick.ttf'),size)
    none_img = Image.new("RGBA",(500,500), (255,255,255, 0))
    m1 = 250-int(image.size[0]/2)
    n1 = 250-int(image.size[1]/2)
    none_img.paste(image,(m1,n1))
    text_img = Image.new("RGBA",none_img.size, (255,255,255, 0))
    a1 , b1 = none_img.size
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((int(a1/2),int(b1/2)-2*border), text, font = font, anchor = "mm",stroke_width=border, stroke_fill=(255,255,255),spacing=space)      
    text_draw.text((int(a1/2),int(b1/2)-2*border), text, font = font, anchor = "mm",fill = fill,spacing= space+10)
    rotated_text = text_img.rotate(angle, Image.BICUBIC,expand=1)
    a2 , b2 = rotated_text.size
    line = len(text.split("\n"))
    none_img.paste(rotated_text, ((int(x-0.5*a2)-2*(2-line)*border+m1),int(y-0.5*b2-2*(2-line)*border+n1)), rotated_text)
    image = crop_transparent(none_img) 
    return image

async def stick_maker(chara:str,id:str,text:str) -> str:
    chara = check_chara(chara)
    if not chara:return -1
    name = f'{chara} {id}'
    info = check_name(name)
    if not info:return -2
    path = join(join(PIC_PATH,'img'), info["img"])
    image = Image.open(path)
    default = info["defaultText"]
    size = default["s"]
    hex_color = info["color"]
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    img = await stickmaker(image,x = default["x"],y = default["y"],text = text,angle = -6*default["r"],size= size,fill = rgb_color)
    buf = BytesIO()
    img = img.convert('RGBA')
    img.save(buf, format='GIF')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    msg = f'[CQ:image,file={base64_str}]'
    return msg