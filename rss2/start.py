import codecs
import nonebot
import os
import re
import asyncio
from pathlib import Path
from nonebot import logger

from .config import config
from .RSS import rss_class
from .RSS import my_trigger as tr

FILE_PATH = str(str(Path.cwd()) + os.sep + "data" + os.sep)


def hash_clear():
    json_paths = list(Path(FILE_PATH).glob("*.json"))

    for j in [str(i) for i in json_paths if i != "rss.json"]:

        with codecs.open(j, "r", "utf-8") as f:
            lines = f.readlines()

        with codecs.open(j, "w", "utf-8") as f:
            for line in lines:
                if not re.search(r'"hash": "[0-9a-zA-Z]{32}",', line):
                    f.write(line)

async def start():
    try:
        rss = rss_class.Rss('', '', '-1', '-1')
        rss_list = rss.read_rss()  # 读取list
        if not rss_list:
            raise Exception('第一次启动，你还没有订阅，记得添加哟！')
        for rss_tmp in rss_list:
            if not rss_tmp.stop:
                await tr.add_job(rss_tmp)  # 创建检查更新任务
        logger.info('ELF_RSS 订阅器启动成功！')
        hash_clear()
    except Exception as e:
        logger.info('第一次启动，你还没有订阅，记得添加哟！')
        logger.debug(e)

@nonebot.scheduler.scheduled_job('date')
async def _():
    await asyncio.gather(
        start(),
    )