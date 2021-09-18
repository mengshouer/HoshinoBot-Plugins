import json
import nonebot
import asyncio
from nonebot import logger

from pathlib import Path
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from .RSS import my_trigger as rt
from .RSS import rss_class
from .RSS.routes.Parsing.cache_manage import cache_filter
from .RSS.routes.Parsing.check_update import dict_hash
from .config import config, DATA_PATH, JSON_PATH


# 将 xxx.json (缓存) 改造为 tinydb 数据库
def change_cache_json():
    for cache_path in DATA_PATH.glob("*.json"):

        if cache_path.name == "rss.json":
            continue

        cache_json = json.loads(cache_path.read_bytes())
        entries = cache_json.get("entries")

        if entries:
            Path.unlink(cache_path)
            db = TinyDB(
                cache_path,
                storage=CachingMiddleware(JSONStorage),
                encoding="utf-8",
                sort_keys=True,
                indent=4,
                ensure_ascii=False,
            )

            result = []
            for i in entries:
                i["hash"] = dict_hash(i)
                result.append(cache_filter(i))

            db.insert_multiple(result)
            db.close()

        else:
            db = TinyDB(
                cache_path,
                storage=CachingMiddleware(JSONStorage),
                encoding="utf-8",
                sort_keys=True,
                indent=4,
                ensure_ascii=False,
            )

            result = []
            for i in db.all():
                result.append(cache_filter(i))

            db.truncate()
            db.insert_multiple(result)
            db.close()


# 将 rss.json 改造为 tinydb 数据库
def change_rss_json():
    if not Path.exists(JSON_PATH):
        return

    rss_list_json = json.loads(JSON_PATH.read_bytes())
    if isinstance(rss_list_json, list):
        _default = None
    else:
        _default = rss_list_json.get("_default")

    if not _default:
        Path.unlink(JSON_PATH)
        db = TinyDB(
            JSON_PATH,
            storage=CachingMiddleware(JSONStorage),
            encoding="utf-8",
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
        )

        for rss_json in rss_list_json:
            db.insert(rss_json)

        db.close()


async def start():
    change_rss_json()
    change_cache_json()

    try:
        rss = rss_class.Rss()
        rss_list = rss.read_rss()  # 读取list
        if not rss_list:
            raise Exception("第一次启动，你还没有订阅，记得添加哟！")
        for rss_tmp in rss_list:
            if not rss_tmp.stop:
                await rt.add_job(rss_tmp)  # 创建检查更新任务
        logger.info("ELF_RSS 订阅器启动成功！")
    except Exception as e:
        logger.info("第一次启动，你还没有订阅，记得添加哟！")
        logger.debug(e)
        raise

@nonebot.scheduler.scheduled_job('date')
async def _():
    await asyncio.gather(
        start(),
    )