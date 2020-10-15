import re, json, requests, aiohttp, asyncio
import lxml.html
import urllib.parse
from hoshino import Service, util

sv = Service('antiMINIAPP')

bili_url = ['www.bilibili.com/video', 'b23.tv/', '当前版本不支持该消息类型',
            '请使用最新版本手机QQ查看', '哔哩哔哩']

analysis_stat = {}   # group_id: (msg, is_analysis)

@sv.on_keyword(bili_url)
async def bili_keyword(bot, ev):
    group_id = ev.group_id
    try:
        text = str(ev.message).strip()
        if "当前版本不支持该消息类型" in text and "哔哩哔哩" not in text:
            return
        elif '请使用最新版本手机QQ查看' in text and "哔哩哔哩" not in text:
            return
        url = await extract(text)
        if not url:
            pattern = re.compile(r'"desc":".*?"')
            desc = re.findall(pattern,text)
            i = 0
            while i < len(desc):
                title_dict = "{"+desc[i]+"}"
                title = eval(title_dict)
                vurl = await search_bili_by_title(title['desc'])
                if vurl:
                    url = await extract(vurl)
                    break
                i += 1
        msg = await video_detail(url)

        # 避免多个机器人解析重复推送
        if group_id not in analysis_stat:
            analysis_stat[group_id] = (msg, False)
        last_msg, is_analysis = analysis_stat[group_id]
        if last_msg == msg:
            if is_analysis:
                analysis_stat[group_id] = (msg, False)
                return
            else:
                analysis_stat[group_id] = (msg, True)
    except Exception as e:
        msg = "Error: {}".format(type(e))
    await bot.send(ev, msg)

async def extract(text:str):
    try:
        aid = re.compile(r'(av|AV)\d+').search(text)
        bvid = re.compile(r'(BV|bv)\w+').search(text)
        b23 = re.compile(r'b23.tv\\/(\w+)').search(text)
        if not b23:
            b23 = re.compile(r'b23.tv/(\w+)').search(text)
        if aid:
            url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}'
        elif bvid:
            url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
        else:
            r = requests.get(f'https://b23.tv/{b23[1]}')
            aid = re.compile(r'av\d+').search(r.url)
            bvid = re.compile(r'BV\w+').search(r.url)
            if bvid:
                url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
            else:
                url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0]}'
        return url
    except:
        return None

async def search_bili_by_title(title: str):
    brackets_pattern = re.compile(r'[()\[\]{}（）【】]')
    title_without_brackets = brackets_pattern.sub(' ', title).strip()
    search_url = f'https://search.bilibili.com/video?keyword={urllib.parse.quote(title_without_brackets)}'

    try:
        async with aiohttp.request('GET', search_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            text = await resp.text(encoding='utf8')
            content: lxml.html.HtmlElement = lxml.html.fromstring(text)
    except asyncio.TimeoutError:
        return None

    for video in content.xpath('//li[@class="video-item matrix"]/a[@class="img-anchor"]'):
        if title == ''.join(video.xpath('./attribute::title')):
            url = ''.join(video.xpath('./attribute::href'))
            break
    else:
        url = None
    return url

async def video_detail(url):
    try:
        res = requests.get(url).json()['data']
        vurl = f"URL：https://www.bilibili.com/video/av{res['aid']}\n"
        title = f"标题：{res['title']}\n"
        up = f"UP主：{res['owner']['name']} (https://space.bilibili.com/{res['owner']['mid']})\n"
        desc = f"简介：{res['desc']}"
        msg = str(vurl)+str(title)+str(up)+str(desc)
        return msg
    except Exception as e:
        msg = "解析出错--Error: {}".format(type(e))
        return msg

    
