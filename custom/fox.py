import httpx
from nonebot import on_command, CommandSession, MessageSegment


@on_command("/fox", aliases=("!fox", "\\fox"), only_to_me=False)
async def fox(session: CommandSession):
    try:
        api_url = "https://randomfox.ca/floof/"
        with httpx.Client(proxies={}) as client:
            r = client.get(api_url, timeout=5)
        img_url = r.json()["image"]
        msg = MessageSegment.image(img_url)
    except Exception as e:
        msg = "Error: {}".format(type(e))
    await session.send(msg)
