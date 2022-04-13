import httpx
import re
import traceback
from hoshino import Service

sv = Service("nuannuan")

def get_video_id(mid):
    # 获取用户信息最新视频的前五个，避免第一个视频不是攻略ps=5处修改
    url = f"https://api.bilibili.com/x/space/arc/search?mid={mid}&order=pubdate&pn=1&ps=5"
    with httpx.Client(proxies={}) as client:
        r = client.get(url, timeout=3).json()
    video_list = r["data"]["list"]["vlist"]
    for i in video_list:
        # match title
        if re.match(r"【FF14\/时尚品鉴】第\d+期 满分攻略", i["title"]):
            return i["bvid"]

def extract_nn(bvid):
    try:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        with httpx.Client(proxies={}) as client:
            r = client.get(url, timeout=3).json()
        if r["code"] == 0:
            url = f"https://www.bilibili.com/video/{bvid}"
            title = r["data"]["title"]
            desc = r["data"]["desc"]
            text = desc.replace("个人攻略网站", "游玩C攻略站")
            image = r["data"]["pic"]
            res_data = {
                "url": url,
                "title": title,
                "content": text,
                "image": image,
            }
            return res_data
    except:
        traceback.print_exc()
    return None

@sv.on_prefix(("/暖暖", "\暖暖"))
async def nuannuan(bot, ev):
    # 获取视频av号(aid)
    bvid = get_video_id(15503317)
    # 获取数据
    res_data = extract_nn(bvid)
    if not res_data:
        msg = "无法查询到有效数据，请稍后再试"
    else:
        msg = res_data["title"] + "\n" + res_data["content"]
    await bot.send(ev, msg)
    
@sv.on_prefix(("/nuannuan", "/nn"))
async def nuannuan_guild(bot, ev):
    if ev['message_type'] == 'guild':
        # 获取视频av号(aid)
        bvid = get_video_id(15503317)
        # 获取数据
        res_data = extract_nn(bvid)
        if not res_data:
            msg = "无法查询到有效数据，请稍后再试"
        else:
            msg = res_data["title"] + "\n" + res_data["content"]
        await bot.send(ev, msg)


