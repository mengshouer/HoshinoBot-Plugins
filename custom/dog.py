import httpx
from nonebot import on_command, CommandSession

@on_command('/dog', aliases=('!dog', '\\dog'), only_to_me=False)
async def dog(session: CommandSession):
    try:
        try:
            api_url = "https://api.thedogapi.com/v1/images/search"
            with httpx.Client(proxies={}) as client:
                r = client.get(api_url, timeout=5)
            img_url = r.json()[0]["url"]
        except Exception as e:
            api_url = "https://dog.ceo/api/breeds/image/random"
            with httpx.Client(proxies={}) as client:
                r = client.get(api_url, timeout=5)
            img_url = r.json()["message"]
        msg = "[CQ:image,file={}]".format(img_url)
    except Exception as e:
        msg = "Error: {}".format(type(e))
    await session.send(msg)
    
