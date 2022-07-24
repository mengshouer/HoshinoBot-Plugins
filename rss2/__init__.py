import asyncio
import itertools

import nonebot
from nonebot.log import logger
from yarl import URL

from . import command
from . import my_trigger as tr
from .config import DATA_PATH
from .rss_class import Rss

# 启动时发送启动成功信息
@nonebot.on_websocket_connect
async def start(event) -> None:
    # 启动后检查 data 目录，不存在就创建
    if not DATA_PATH.is_dir():
        DATA_PATH.mkdir()

    rss_list = Rss.read_rss()  # 读取list
    if not rss_list:
        logger.info("第一次启动，你还没有订阅，记得添加哟！")
    logger.info("ELF_RSS 订阅器启动成功！")
    # 创建检查更新任务
    rss_list_group = zip(
        *[
            list(group)
            for key, group in itertools.groupby(
                rss_list, lambda x: URL(x.get_url()).host
            )
        ]
    )
    for _rss_list in rss_list_group:
        await asyncio.gather(*[tr.add_job(rss) for rss in _rss_list if not rss.stop])
