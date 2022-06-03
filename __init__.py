import asyncio
import re
import arrow

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from hoshino import Service, priv
from hoshino.config import NICKNAME
from hoshino.util import DailyNumberLimiter
from tinydb import JSONStorage, Query, TinyDB
from tinydb.middlewares import CachingMiddleware

from .utils import check_screenshot
from .send_msg import send_result_message
from .ascii2d import ascii2d_search
from .cache import clear_expired_cache, exist_in_cache
from .config import config
from .ehentai import ehentai_search
from .result import Result
from .saucenao import saucenao_search


sv = Service("picsearch")

lmtd = DailyNumberLimiter(config.daily_limit)

if type(NICKNAME) == str:
    NICKNAME = [NICKNAME]


async def image_search(
    url: str,
    mode: str,
    purge: bool,
    db: TinyDB,
    proxy: Optional[str] = config.proxy,
    hide_img: bool = config.hide_img,
) -> Union[List[str], Any]:
    image_md5 = re.search("[A-F0-9]{32}", url)[0]  # type: ignore
    _result = exist_in_cache(db, image_md5, mode)
    cached = bool(_result)
    if purge or not _result:
        result_dict: Dict[str, Any] = {}
        if mode == "a2d":
            result_dict["ascii2d"] = await ascii2d_search(url, proxy, hide_img)
        elif mode == "ex":
            result_dict["ex"] = await ehentai_search(url, proxy, hide_img)
        else:
            result_dict["saucenao"] = await saucenao_search(url, mode, proxy, hide_img)
        result_dict["mode"] = mode
        result_dict["image_md5"] = image_md5
        result_dict["update_at"] = arrow.now().for_json()
        _result = Result(result_dict)
        db.upsert(
            _result.__dict__, (Query().image_md5 == image_md5) & (Query().mode == mode)
        )
    if mode == "a2d":
        final_res = _result.ascii2d
    elif mode == "ex":
        final_res = _result.ex
    else:
        final_res = _result.saucenao
    if cached and not purge:
        return [f"[缓存] {i}" for i in final_res]
    return final_res


def get_args(plain_text) -> Tuple[str, bool]:
    mode = "all"
    args = ["pixiv", "danbooru", "doujin", "anime", "a2d", "ex"]
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
            await bot.finish(
                ev, f"您今天已经搜过{config.daily_limit}次图了，休息一下明天再来吧～", at_sender=True
            )
    if sbtype and config.ignore_stamp:
        if sbtype != "0":
            await bot.finish(ev, f"[CQ:reply,id={mid}]该图为表情，已忽略~如确需搜索请尝试单发搜索或回复搜索~")

        if config.check_screenshot:
            result = await check_screenshot(bot, file, url)
            if result:
                if result == 1:
                    await bot.finish(
                        ev,
                        f"[CQ:reply,id={mid}]该图似乎是手机截屏，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~",
                    )
                if result == 2:
                    await bot.finish(
                        ev,
                        f"[CQ:reply,id={mid}]该图似乎是长图拼接，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~",
                    )

    if "c2cpicdw.qpic.cn/offpic_new/" in url:
        md5 = file[:-6].upper()
        url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
    await bot.send(ev, "正在搜索，请稍候～")
    db = TinyDB(
        f"{config.run_path}/cache.json",
        storage=CachingMiddleware(JSONStorage),  # type: ignore
        encoding="utf-8",
        sort_keys=True,
        indent=4,
        ensure_ascii=False,
    )
    search_results = await asyncio.gather(*[image_search(url, mode, purge, db)])
    for i in search_results:
        await send_result_message(bot, ev, i)
    clear_expired_cache(db)
    db.close()


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
                await bot.finish(ev, f"您已经在搜图模式下啦！\n如想退出搜图模式请发送“谢谢{NICKNAME[0]}”~")
            else:
                await bot.finish(ev, f"本群[CQ:at,qq={pls.on[gid]}]正在搜图，请耐心等待~")
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
