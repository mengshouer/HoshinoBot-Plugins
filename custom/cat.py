import requests
from nonebot import on_command, CommandSession

@on_command('/cat', aliases=('\\cat', '!cat'), only_to_me=False)
async def cat(session: CommandSession):
    url = "https://api.thecatapi.com/v1/images/search"
    r = requests.get(url)
    picurl = r.json()[0]["url"]
    await session.send(f"[CQ:image,file={picurl}]")
    
