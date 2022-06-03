import re
import aiohttp
from typing import Optional
from PIL import Image
from io import BytesIO
from random import randint
from pyquery import PyQuery
from yarl import URL

from hoshino.util import pic2b64


def randcolor():
    return (randint(0, 255), randint(0, 255), randint(0, 255))


def ats_pic(img):
    if img.mode != "RGB":
        img = img.convert("RGB")
    width = img.size[0] - 1  # 长度
    height = img.size[1] - 1  # 宽度
    img.putpixel((0, 0), randcolor())
    img.putpixel((0, height), randcolor())
    img.putpixel((width, 0), randcolor())
    img.putpixel((width, height), randcolor())
    return img


# 将图片转化为 base64
async def get_pic_base64_by_url(
    url: str, proxy: Optional[str], cookies: Optional[str] = None
) -> str:
    headers = {}
    if cookies:
        headers["Cookie"] = cookies
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, proxy=proxy) as resp:
            if resp.status == 200:
                return pic2b64(ats_pic(Image.open(BytesIO(await resp.read()))))
    return ""


async def handle_img(
    url: str, proxy: Optional[str], hide_img: bool, cookies: Optional[str] = None
) -> str:
    if hide_img:
        return ""
    img_base64 = await get_pic_base64_by_url(url, proxy, cookies)
    if img_base64:
        return f"[CQ:image,file={img_base64}]"
    return f"图片下载失败: {url}"


async def get_source(url: str, proxy: Optional[str]) -> str:
    source = ""
    async with aiohttp.ClientSession() as session:
        if URL(url).host == "danbooru.donmai.us":
            async with session.get(url, proxy=proxy) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    source = PyQuery(html)(".image-container").attr(
                        "data-normalized-source"
                    )
        elif URL(url).host in ["yande.re", "konachan.com"]:
            async with session.get(url, proxy=proxy) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    source = PyQuery(html)("#stats li:contains(Source) a").attr("href")
        elif URL(url).host == "gelbooru.com":
            async with session.get(url, proxy=proxy) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    source = PyQuery(html)("#tag-list li:contains(Source) a").attr(
                        "href"
                    )
    return str(source)


def shorten_url(url: str) -> str:
    pid_search = re.compile(
        r"(?:pixiv.+(?:illust_id=|artworks/)|/img-original/img/(?:\d+/){6})(\d+)"
    )
    if pid_search.search(url):
        return f"https://pixiv.net/i/{pid_search.search(url)[1]}"  # type: ignore
    if URL(url).host == "danbooru.donmai.us":
        return url.replace("/post/show/", "/posts/")
    return url


async def check_screenshot(bot, file, imgurl):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(imgurl) as resp:
                if resp.headers.get("Content-Type") == "image/gif":
                    # gif pic, not likely a screen shot
                    return 0
                image = Image.open(BytesIO(await resp.read()))
    except:
        # download failed
        return 0
    cord = image.size[0] / image.size[1]
    height = image.size[1]
    # print(cord)
    if cord > 0.565:
        # print("too short, not likely a screen shot")
        return 0
    if cord < 0.2:
        # print("too long, might be long screen shot")
        return 2
    # print("size checked, next ocr")
    try:
        ocr_result = await bot.call_action(action=".ocr_image", image=file)
    except:
        # print("ocr failed")
        return False
    flag = 0
    for result in ocr_result["texts"]:
        key1 = re.search("[0-9]{1,2}:[0-9]{2}", result["text"])  # 时间
        key2 = re.search("移动|联通|电信", result["text"])
        key3 = re.search("4G|5G", result["text"])
        key4 = re.search("[0-9]{1,2}%", result["text"])  # 电量
        key5 = re.search("[0-9]{0,3}[\\\/][0-9]{0,3}", result["text"])  # 页数
        if key2 or key3 or key4:
            # print(str(result))
            loc = result["coordinates"][2]["y"]
            if int(loc) < (int(height) / 19):
                flag = 1
        if key1 or key5:
            # print(str(result))
            loc = result["coordinates"][2]["y"]
            if int(loc) < (int(height) / 19) or int(loc) > (int(height) * 18 / 20):
                flag = 1
        if flag:
            break
    if flag:
        # print(f"time mark found:{string}")
        return 1
    else:
        return 0
