import nonebot
import asyncio

from nonebot.log import logger

from .RSS import my_trigger as tr
from .RSS.rss_class import Rss
from .config import DATA_PATH


async def start() -> None:
    # 启动后检查 data 目录，不存在就创建
    if not DATA_PATH.is_dir():
        DATA_PATH.mkdir()

    rss_list = Rss.read_rss()  # 读取list
    if not rss_list:
        logger.warning("第一次启动，你还没有订阅，记得添加哟！")
        return
    # 创建检查更新任务
    # if not tr.get_jobs():
    for rss_tmp in rss_list:
        if not rss_tmp.stop:
            tr.add_job(rss_tmp)
    logger.info("ELF_RSS 订阅器启动成功！")


@nonebot.on_startup
async def _():
    await asyncio.gather(
        start(),
    )
