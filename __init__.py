import asyncio
import re
from typing import List, Tuple

import aiohttp
from aiohttp import ClientSession
from diskcache import Cache
from PicImageSearch import Network
from tenacity import AsyncRetrying, stop_after_attempt, stop_after_delay
from datetime import datetime, timedelta

from hoshino import Service, priv, logger
from hoshino.config import NICKNAME
from hoshino.util import DailyNumberLimiter

from .ascii2d import ascii2d_search
from .cache import exist_in_cache, upsert_cache
from .config import config
from .ehentai import ehentai_search
from .iqdb import iqdb_search
from .saucenao import saucenao_search
from .utils import check_screenshot
from .send_msg import send_result_message


sv = Service("picsearch")

lmtd = DailyNumberLimiter(config.daily_limit)

if type(NICKNAME) == str:
    NICKNAME = [NICKNAME]


async def image_search(
    url: str,
    mode: str,
    purge: bool,
    _cache: Cache,
    client: ClientSession,
    hide_img: bool = config.hide_img,
) -> List[str]:
    url = await get_universal_img_url(url)
    image_md5 = re.search(r"[A-F\d]{32}", url)[0]  # type: ignore
    if not purge and (result := exist_in_cache(_cache, image_md5, mode)):
        return [f"[缓存] {i}" for i in result]
    result = []
    try:
        async for attempt in AsyncRetrying(
            stop=(stop_after_attempt(3) | stop_after_delay(30)), reraise=True
        ):
            with attempt:
                if mode == "a2d":
                    result = await ascii2d_search(url, client, hide_img)
                elif mode == "iqdb":
                    result = await iqdb_search(url, client, hide_img)
                elif mode == "ex":
                    result = await ehentai_search(url, client, hide_img)
                else:
                    result = await saucenao_search(url, mode, client, hide_img)
                upsert_cache(_cache, image_md5, mode, result)
    except Exception as e:
        logger.exception(f"❌️ 该图 [{url}] 搜图失败")
        result = [f"❌️ 该图搜图失败\nE: {repr(e)}"]
    return result


async def get_universal_img_url(url: str) -> str:
    final_url = url.replace(
        "/c2cpicdw.qpic.cn/offpic_new/", "/gchat.qpic.cn/gchatpic_new/"
    )
    final_url = re.sub(r"/\d+/+\d+-\d+-", "/0/0-0-", final_url)
    final_url = re.sub(r"\?.*$", "", final_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(final_url) as resp:
            if resp.status == 200:
                return final_url
    return url


def get_args(plain_text) -> Tuple[str, bool]:
    mode = "all"
    args = ["pixiv", "danbooru", "doujin", "anime", "a2d", "ex", "iqdb"]
    if plain_text:
        for i in args:
            if f"--{i}" in plain_text:
                mode = i
                break
    purge = "--purge" in plain_text
    return mode, purge


def handle_message(ev):
    ret, mode, purge, file, url, sbtype = 0, "all", False, "", "", ""
    for m in ev.message:
        if m.type == "image":
            file = m.data["file"]
            url = m.data["url"]
            if "subType" in m.data:
                sbtype = m.data["subType"]
            else:
                sbtype = None
            ret = 1
            continue
        else:
            mode, purge = get_args(str(m))
    return ret, mode, purge, file, url, sbtype


async def process_images(
    bot, ev, uid, gid, mid, sbtype, file, url, mode="all", purge=False
):
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(
                ev, f"您今天已经搜过{config.daily_limit}次图了，休息一下明天再来吧～", at_sender=True
            )
            if pls.get_on_off_status(gid):
                pls.turn_off(gid)
                return

    if pls.get_on_off_status(gid):
        pls.count_plus(gid)
        if pls.count[gid] > pls.limit[gid]:
            pls.turn_off(gid)
            await bot.send(
                ev, f"您今天已经搜过{config.daily_limit}次图了，休息一下明天再来吧～", at_sender=True
            )
            return

    if sbtype and config.ignore_stamp:
        if sbtype != "0":
            await bot.send(ev, f"[CQ:reply,id={mid}]该图为表情，已忽略~如确需搜索请尝试单发搜索或回复搜索~")
            return

    if config.check_screenshot:
        result = await check_screenshot(bot, file, url)
        if result:
            if result == 1:
                await bot.send(
                    ev,
                    f"[CQ:reply,id={mid}]该图似乎是手机截屏，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~",
                )
            if result == 2:
                await bot.send(
                    ev,
                    f"[CQ:reply,id={mid}]该图似乎是长图拼接，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~",
                )
            return

    await bot.send(ev, "正在搜索，请稍候～")
    network = (
        Network(proxies=config.proxy, cookies=config.exhentai_cookies, timeout=60)
        if mode == "ex"
        else Network(proxies=config.proxy)
    )
    async with network as client:
        with Cache("picsearch_cache") as _cache:
            await send_result_message(
                bot, ev, await image_search(url, mode, purge, _cache, client)
            )
            _cache.expire()


class PicListener:
    def __init__(self):
        self.on = {}
        self.count = {}
        self.limit = {}
        self.timeout = {}

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) else False

    def turn_on(self, gid, uid):
        self.on[gid] = uid
        self.timeout[gid] = datetime.now() + timedelta(seconds=config.search_timeout)
        self.count[gid] = 0
        self.limit[gid] = config.daily_limit - lmtd.get_num(uid)

    def turn_off(self, gid):
        self.on.pop(gid)
        self.count.pop(gid)
        self.timeout.pop(gid)
        self.limit.pop(gid)

    def count_plus(self, gid):
        self.count[gid] += 1


pls = PicListener()


async def handle_image_search(bot, ev, gid):
    uid = ev.user_id
    ret, mode, purge, file, url, sbtype = handle_message(ev)
    if not ret:
        if pls.get_on_off_status(gid):
            if uid == pls.on[gid]:
                pls.timeout[gid] = datetime.now() + timedelta(seconds=30)
                await bot.send(ev, f"您已经在搜图模式下啦！\n如想退出搜图模式请发送“谢谢{NICKNAME[0]}”~")
            else:
                await bot.send(ev, f"本群[CQ:at,qq={pls.on[gid]}]正在搜图，请耐心等待~")
            return
        pls.turn_on(gid, uid)
        await bot.send(ev, f"了解～请发送图片吧！支持批量噢！\n如想退出搜索模式请发送“谢谢{NICKNAME[0]}”")
        await asyncio.sleep(30)
        ct = 0
        while pls.get_on_off_status(gid):
            if datetime.now() < pls.timeout[gid]:
                if ct != pls.count[gid]:
                    ct = pls.count[gid]
                    pls.timeout[gid] = datetime.now() + timedelta(seconds=60)
            else:
                temp = pls.on[gid]
                if not pls.count[gid]:
                    await bot.send(
                        ev,
                        f"[CQ:at,qq={temp}] 由于超时，已为您自动退出搜图模式~\n您本次搜索期间未发送任何图片，请检查是否被吞图~",
                    )
                else:
                    await bot.send(
                        ev,
                        f"[CQ:at,qq={temp}] 由于超时，已为您自动退出搜图模式，以后要记得说“谢谢{NICKNAME[0]}”来退出搜图模式噢~\n您本次搜索共搜索了{pls.count[gid]}张图片～",
                    )
                pls.turn_off(gid)
                break
            await asyncio.sleep(30)
        return
    mid = ev.message_id
    await process_images(bot, ev, uid, gid, mid, sbtype, file, url, mode, purge)


async def thanks(bot, ev, gid):
    name = str(ev.message).strip()[2:]
    if name not in NICKNAME:
        return
    if pls.get_on_off_status(gid):
        if pls.on[gid] != ev.user_id:
            await bot.send(ev, "不能替别人结束搜图哦～")
            return
        if not pls.count[gid]:
            await bot.send(ev, f"不用谢～\n您本次搜索期间未发送任何图片，请检查是否被吞图～")
        else:
            await bot.send(ev, f"不用谢～\n您本次搜索共搜索了{pls.count[gid]}张图片～")
        pls.turn_off(gid)
        return
    await bot.send(ev, "にゃ～")


@sv.on_message(["group", "private"])
async def picmessage(bot, ev):
    atcheck, hasimage = False, False
    for m in ev.message:
        if m.type == "image":
            hasimage = True
        elif m.type == "at" and int(m.data["qq"]) == ev.self_id:
            atcheck = True
    gid = ev.group_id if ev.message_type == "group" else ev.user_id
    if str(ev.message).startswith(("识图", "搜图", "查图", "找图")):
        await handle_image_search(bot, ev, gid)
        return
    elif str(ev.message).startswith("谢谢"):
        await thanks(bot, ev, gid)
        return
    if not hasimage:
        return
    if (ev.message_type == "private" and config.search_immediately) or atcheck:
        pass
    # 群号和Q号相同的概率我认为是可以接受的
    elif pls.get_on_off_status(gid):
        batchcheck = False
        if int(pls.on[gid]) == ev.user_id:
            batchcheck = True
        if not batchcheck:
            return
    else:
        return
    await handle_image_search(bot, ev, gid)
