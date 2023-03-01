import re
import urllib.parse
import json
from time import localtime, strftime

import aiohttp
import nonebot
from hoshino import Service, logger
from nonebot import Message, MessageSegment

sv = Service("analysis_bilibili")
sv2 = Service("search_bilibili_video")


@sv2.on_prefix("搜视频")
async def search_bilibili_video_by_title(bot, ev):
    title = ev.message.extract_plain_text()
    vurl = await search_bili_by_title(title)
    msg = await bili_keyword(ev.group_id, vurl)
    try:
        await bot.send(ev, msg)
    except:
        # 避免简介有风控内容无法发送
        logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
        msg = re.sub(r"简介.*", "", msg)
        await bot.send(ev, msg)


analysis_stat = {}  # group_id : last_vurl
config = nonebot.get_bot().config
blacklist = getattr(config, "analysis_blacklist", [])
analysis_display_image = getattr(config, "analysis_display_image", False)
analysis_display_image_list = getattr(config, "analysis_display_image_list", [])

# on_rex判断不到小程序信息
@sv.on_message()
async def rex_bilibili(bot, ev):
    text = str(ev.message).strip()
    if blacklist and ev.user_id in blacklist:
        return
    if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    patterns = r"(\.bilibili\.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)"
    match = re.compile(patterns, re.I).search(text)
    if match:
        if ev.group_id:
            group_id = ev.group_id
        elif ev.channel_id:
            group_id = ev.channel_id
        else:
            group_id = None
        msg = await bili_keyword(group_id, text)
        if msg:
            try:
                await bot.send(ev, msg)
            except:
                # 避免简介有风控内容无法发送
                logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
                msg = re.sub(r"简介.*", "", msg)
                await bot.send(ev, msg)


async def bili_keyword(group_id, text):
    try:
        # 提取url
        url, page, time_location = extract(text)
        # 如果是小程序就去搜索标题
        if not url:
            if title := re.search(r'"desc":("[^"哔哩]+")', text):
                vurl = await search_bili_by_title(title[1])
                if vurl:
                    url, page, time_location = extract(vurl)

        # 获取视频详细信息
        msg, vurl = "", ""
        if "view?" in url:
            msg, vurl = await video_detail(url, page=page, time_location=time_location)
        elif "bangumi" in url:
            msg, vurl = await bangumi_detail(url, time_location)
        elif "xlive" in url:
            msg, vurl = await live_detail(url)
        elif "article" in url:
            msg, vurl = await article_detail(url, page)
        elif "dynamic" in url:
            msg, vurl = await dynamic_detail(url)

        # 避免多个机器人解析重复推送
        if group_id:
            if group_id in analysis_stat and analysis_stat[group_id] == vurl:
                return ""
            analysis_stat[group_id] = vurl
    except Exception as e:
        msg = "bili_keyword Error: {}".format(type(e))
    return msg


async def b23_extract(text):
    b23 = re.compile(r"b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)", re.I).search(
        text.replace("\\", "")
    )
    url = f"https://{b23[0]}"
    async with aiohttp.request("GET", url) as resp:
        return str(resp.url)


def extract(text: str):
    try:
        url = ""
        # 视频分p
        page = re.compile(r"([?&]|&amp;)p=\d+").search(text)
        # 视频播放定位时间
        time = re.compile(r"([?&]|&amp;)t=\d+").search(text)
        # 主站视频 av 号
        aid = re.compile(r"av\d+", re.I).search(text)
        # 主站视频 bv 号
        bvid = re.compile(r"BV([A-Za-z0-9]{10})+", re.I).search(text)
        # 番剧视频页
        epid = re.compile(r"ep\d+", re.I).search(text)
        # 番剧剧集ssid(season_id)
        ssid = re.compile(r"ss\d+", re.I).search(text)
        # 番剧详细页
        mdid = re.compile(r"md\d+", re.I).search(text)
        # 直播间
        room_id = re.compile(r"live.bilibili.com/(blanc/|h5/)?(\d+)", re.I).search(text)
        # 文章
        cvid = re.compile(
            r"(/read/(cv|mobile|native)(/|\?id=)?|^cv)(\d+)", re.I
        ).search(text)
        # 动态
        dynamic_id_type2 = re.compile(
            r"(t|m).bilibili.com/(\d+)\?(.*?)(&|&amp;)type=2", re.I
        ).search(text)
        # 动态
        dynamic_id = re.compile(r"(t|m).bilibili.com/(\d+)", re.I).search(text)
        if bvid:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}"
        elif aid:
            url = f"https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}"
        elif epid:
            url = (
                f"https://bangumi.bilibili.com/view/web_api/season?ep_id={epid[0][2:]}"
            )
        elif ssid:
            url = f"https://bangumi.bilibili.com/view/web_api/season?season_id={ssid[0][2:]}"
        elif mdid:
            url = f"https://bangumi.bilibili.com/view/web_api/season?media_id={mdid[0][2:]}"
        elif room_id:
            url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id[2]}"
        elif cvid:
            page = cvid[4]
            url = f"https://api.bilibili.com/x/article/viewinfo?id={page}&mobi_app=pc&from=web"
        elif dynamic_id_type2:
            url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?rid={dynamic_id_type2[2]}&type=2"
        elif dynamic_id:
            url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id[2]}"
        return url, page, time
    except Exception:
        return "", None, None


async def search_bili_by_title(title: str):
    mainsite_url = "https://www.bilibili.com"
    search_url = f"https://api.bilibili.com/x/web-interface/wbi/search/all/v2?keyword={urllib.parse.quote(title)}"

    async with aiohttp.ClientSession() as session:
        # set headers
        async with session.get(mainsite_url) as resp:
            assert resp.status == 200

        async with session.get(search_url) as resp:
            result = (await resp.json())["data"]["result"]

    for i in result:
        if i.get("result_type") != "video":
            continue
        # 只返回第一个结果
        return i["data"][0].get("arcurl")


# 处理超过一万的数字
def handle_num(num: int):
    if num > 10000:
        num = f"{num / 10000:.2f}万"
    return num


async def video_detail(url, **kwargs):
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return "解析到视频被删了/稿件不可见或审核中/权限不足", url
        vurl = f"https://www.bilibili.com/video/av{res['aid']}"
        title = f"\n标题：{res['title']}\n"
        cover = (
            MessageSegment.image(res["pic"])
            if analysis_display_image or "video" in analysis_display_image_list
            else MessageSegment.text("")
        )
        if page := kwargs.get("page"):
            page = page[0].replace("&amp;", "&")
            p = int(page[3:])
            if p <= len(res["pages"]):
                vurl += f"?p={p}"
                part = res["pages"][p - 1]["part"]
                if part != res["title"]:
                    title += f"小标题：{part}\n"
        if time_location := kwargs.get("time_location"):
            time_location = time_location[0].replace("&amp;", "&")[3:]
            if page:
                vurl += f"&t={time_location}"
            else:
                vurl += f"?t={time_location}"
        pubdate = strftime("%Y-%m-%d %H:%M:%S", localtime(res["pubdate"]))
        tname = f"类型：{res['tname']} | UP：{res['owner']['name']} | 日期：{pubdate}\n"
        stat = f"播放：{handle_num(res['stat']['view'])} | 弹幕：{handle_num(res['stat']['danmaku'])} | 收藏：{handle_num(res['stat']['favorite'])}\n"
        stat += f"点赞：{handle_num(res['stat']['like'])} | 硬币：{handle_num(res['stat']['coin'])} | 评论：{handle_num(res['stat']['reply'])}\n"
        desc = f"简介：{res['desc']}"
        desc_list = desc.split("\n")
        desc = "".join(i + "\n" for i in desc_list if i)
        desc_list = desc.split("\n")
        if len(desc_list) > 4:
            desc = desc_list[0] + "\n" + desc_list[1] + "\n" + desc_list[2] + "……"
        mstext = MessageSegment.text("".join([vurl, title, tname, stat, desc]))
        msg = Message([cover, mstext])
        return msg, vurl
    except Exception as e:
        msg = "视频解析出错--Error: {}".format(type(e))
        return msg, None


async def bangumi_detail(url, time_location):
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("result")
            if not res:
                return None, None
        cover = (
            MessageSegment.image(res["cover"])
            if analysis_display_image or "bangumi" in analysis_display_image_list
            else MessageSegment.text("")
        )
        title = f"番剧：{res['title']}\n"
        desc = f"{res['newest_ep']['desc']}\n"
        index_title = ""
        style = "".join(f"{i}," for i in res["style"])
        style = f"类型：{style[:-1]}\n"
        evaluate = f"简介：{res['evaluate']}\n"
        if "season_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}"
        elif "media_id" in url:
            vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}"
        else:
            epid = re.compile(r"ep_id=\d+").search(url)[0][len("ep_id=") :]
            for i in res["episodes"]:
                if str(i["ep_id"]) == epid:
                    index_title = f"标题：{i['index_title']}\n"
                    break
            vurl = f"https://www.bilibili.com/bangumi/play/ep{epid}"
        if time_location:
            time_location = time_location[0].replace("&amp;", "&")[3:]
            vurl += f"?t={time_location}"
        mstext = MessageSegment.text(
            "".join([f"{vurl}\n", title, index_title, desc, style, evaluate])
        )
        msg = Message([cover, mstext])
        return msg, vurl
    except Exception as e:
        msg = "番剧解析出错--Error: {}".format(type(e))
        msg += f"\n{url}"
        return msg, None


async def live_detail(url):
    try:
        async with aiohttp.request("GET", url) as resp:
            res = await resp.json()
            if res["code"] != 0:
                return None, None
        res = res["data"]
        uname = res["anchor_info"]["base_info"]["uname"]
        room_id = res["room_info"]["room_id"]
        title = res["room_info"]["title"]
        cover = (
            MessageSegment.image(res["room_info"]["cover"])
            if analysis_display_image or "live" in analysis_display_image_list
            else MessageSegment.text("")
        )
        live_status = res["room_info"]["live_status"]
        lock_status = res["room_info"]["lock_status"]
        parent_area_name = res["room_info"]["parent_area_name"]
        area_name = res["room_info"]["area_name"]
        online = res["room_info"]["online"]
        tags = res["room_info"]["tags"]
        watched_show = res["watched_show"]["text_large"]
        vurl = f"https://live.bilibili.com/{room_id}\n"
        if lock_status:
            lock_time = res["room_info"]["lock_time"]
            lock_time = strftime("%Y-%m-%d %H:%M:%S", localtime(lock_time))
            title = f"[已封禁]直播间封禁至：{lock_time}\n"
        elif live_status == 1:
            title = f"[直播中]标题：{title}\n"
        elif live_status == 2:
            title = f"[轮播中]标题：{title}\n"
        else:
            title = f"[未开播]标题：{title}\n"
        up = f"主播：{uname}  当前分区：{parent_area_name}-{area_name}\n"
        watch = f"观看：{watched_show}  直播时的人气上一次刷新值：{handle_num(online)}\n"
        if tags:
            tags = f"标签：{tags}\n"
        if live_status:
            player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
        else:
            player = ""
        mstext = MessageSegment.text("".join([vurl, title, up, watch, tags, player]))
        msg = Message([cover, mstext])
        return msg, vurl
    except Exception as e:
        msg = "直播间解析出错--Error: {}".format(type(e))
        return msg, None


async def article_detail(url, cvid):
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return None, None
        images = (
            [MessageSegment.image(i) for i in res["origin_image_urls"]]
            if analysis_display_image or "article" in analysis_display_image_list
            else []
        )
        vurl = f"https://www.bilibili.com/read/cv{cvid}"
        title = f"标题：{res['title']}\n"
        up = f"作者：{res['author_name']} (https://space.bilibili.com/{res['mid']})\n"
        view = f"阅读数：{handle_num(res['stats']['view'])} "
        favorite = f"收藏数：{handle_num(res['stats']['favorite'])} "
        coin = f"硬币数：{handle_num(res['stats']['coin'])}"
        share = f"分享数：{handle_num(res['stats']['share'])} "
        like = f"点赞数：{handle_num(res['stats']['like'])} "
        dislike = f"不喜欢数：{handle_num(res['stats']['dislike'])}"
        desc = view + favorite + coin + "\n" + share + like + dislike + "\n"
        mstext = MessageSegment.text("".join([title, up, desc, vurl]))
        msg = Message(images)
        msg.append(mstext)
        return msg, vurl
    except Exception as e:
        msg = "专栏解析出错--Error: {}".format(type(e))
        return msg, None


async def dynamic_detail(url):
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json())["data"].get("card")
            if not res:
                return None, None
        card = json.loads(res["card"])
        dynamic_id = res["desc"]["dynamic_id"]
        vurl = f"https://t.bilibili.com/{dynamic_id}\n"
        if not (item := card.get("item")):
            return "动态不存在文字内容", vurl
        if not (content := item.get("description")):
            content = item.get("content")
        content = content.replace("\r", "\n")
        if len(content) > 250:
            content = content[:250] + "......"
        images = (
            item.get("pictures", [])
            if analysis_display_image or "dynamic" in analysis_display_image_list
            else []
        )
        if images:
            images = [MessageSegment.image(i.get("img_src")) for i in images]
        else:
            pics = item.get("pictures_count")
            if pics:
                content += f"\nPS：动态中包含{pics}张图片"
        if origin := card.get("origin"):
            jorigin = json.loads(origin)
            short_link = jorigin.get("short_link")
            if short_link:
                content += f"\n动态包含转发视频{short_link}"
            else:
                content += f"\n动态包含转发其他动态"
        msg = Message(content)
        msg.extend(images)
        msg.append(MessageSegment.text(f"\n{vurl}"))
        return msg, vurl
    except Exception as e:
        msg = "动态解析出错--Error: {}".format(type(e))
        return msg, None
