import httpx
from nonebot import on_command, CommandSession


@on_command("!cat", only_to_me=False)
async def cat(session: CommandSession):
    url = "https://api.thecatapi.com/v1/images/search"
    with httpx.Client(proxies={}) as client:
        r = client.get(url, timeout=5)
    picurl = r.json()[0]["url"]
    await session.send(f"[CQ:image,file={picurl}]")
