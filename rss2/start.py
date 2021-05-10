import nonebot
from nonebot import logger
import asyncio
from .config import config
from .RSS import rss_class
from .RSS import my_trigger as tr


async def start():
    bot = nonebot.get_bot()

    try:
        rss = rss_class.Rss('', '', '-1', '-1')
        rss_list = rss.read_rss()  # 读取list
        if not rss_list:
            raise Exception('第一次启动，你还没有订阅，记得添加哟！')
        for rss_tmp in rss_list:
            await tr.add_job(rss_tmp)  # 创建检查更新任务
        logger.info('ELF_RSS 订阅器启动成功！')
    except Exception as e:
        logger.info('第一次启动，你还没有订阅，记得添加哟！')
        logger.debug(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(start())