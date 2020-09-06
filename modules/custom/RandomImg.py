import os
import random
try:
    import ujson as json
except:
    import json
from hoshino import aiorequests, R, Service
from nonebot import MessageSegment as ms

sv_help = '''
随机回复指定目录的随机一张图片(一般拿来深夜放毒.jpg)
'''.strip()

sv = Service('img')

rootdir = "C:/Users/Administrator/Desktop/HoshinoBot/res/img/"  #根目录

@sv.on_prefix('.meat')   #触发前缀
async def meat(bot, ev):
    file_names = []
    _path = rootdir + 'night/'  #根目录下的某个目录
    for parent, dirnames, filenames in os.walk(_path):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        file_names = filenames
    x = random.randint(0, len(file_names)-1)
    img = _path + file_names[x]
    img = f"\n{ms.image(img)}"
    await bot.send(ev, img)

