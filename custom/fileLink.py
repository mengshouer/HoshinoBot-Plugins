import re
import urllib

try:
    from hoshino import Service
    from nonebot import MessageSegment

    _sv = Service("groupFileLink")
    sv = _sv.on_notice
except:
    from nonebot import on_notice, MessageSegment

    sv = on_notice


@sv("group_upload")
async def groupFileLink(session):
    link = session.ctx["file"]["url"]
    file_name = session.ctx["file"]["name"]
    size = session.ctx["file"]["size"]
    link = re.sub(r"fname=.*", f"fname={urllib.parse.quote(file_name)}", link)
    if (
        link[-4:].lower() in [".jpg", ".png", ".gif", ".bmp", "jfif", "webp"]
        and size < 31457280
    ):
        await session.send(MessageSegment.image(link))
    elif (
        link[-4:].lower()
        in [".mp4", ".avi", ".mkv", ".rmvb", ".flv", ".wmv", ".mpg", ".mpeg"]
        and size < 104857600
    ):
        await session.send(MessageSegment.video(link))
    elif (
        link[-4:].lower() in [".mp3", ".wav", ".wma", ".ogg", ".ape", ".flac"]
        and size < 31457280
    ):
        await session.send(MessageSegment.record(link))
    else:
        await session.send(f"文件：{file_name}\n直链：{link}")
