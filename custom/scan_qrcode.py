import aiohttp
import re
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
from hoshino import Service

sv = Service("qrcode", help_="二维码识别")


def get_reply_images(msg):
    ret = re.findall(r"\[CQ:image,file=.*?,url=(.*?)\]", msg)
    if ret:
        return ret
    return None


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


async def get_image_content(url) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()


async def decode_qrcode(content: bytes) -> str:
    img = Image.open(BytesIO(content))
    result = decode(img)
    if result:
        return f"解析结果：{result[0].data.decode('utf-8')}\n"
    return ""


@sv.on_rex(r"\/qr|\/qrcode|\/二维码|\/二维码识别")
async def qrcode(bot, ev):
    images = []
    msg = ""
    for m in ev.message:
        if m.type == "reply":
            content = await bot.get_msg(
                self_id=ev.self_id, message_id=int(m.data["id"])
            )
            reply_images = get_reply_images(content["message"])
            if not reply_images:
                await bot.send(ev, "未找到图片")
                return
            images.extend(reply_images)
        elif m.type == "image":
            images.append(m.data["url"])
    if not images:
        await bot.send(ev, "未找到图片")
        return
    for i in images:
        url = await get_universal_img_url(i)
        content = await get_image_content(url)
        msg += await decode_qrcode(content)
    await bot.send(ev, msg)
