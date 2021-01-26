import os
import random
from hoshino import aiorequests, R, Service

sv = Service('RIMG') #服务名
rootdir = os.path.abspath(".") #根目录(运行run.py的目录)

@sv.on_prefix('.meat') #触发前缀
async def meat(bot, ev):
    file_names = []
    _path = rootdir + '/res/img/' #根目录下的res/img/目录
    for parent, dirnames, filenames in os.walk(_path):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        file_names = filenames
    x = random.randint(0, len(file_names)-1)
    img = _path + file_names[x]
    await bot.send(ev, f"[CQ:image,file=file:///{img}]")
