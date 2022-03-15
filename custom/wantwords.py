import httpx
import urllib.parse
from nonebot import CommandSession
from hoshino import Service

sv = Service("wantword")


@sv.on_command("ww", aliases=("反向词典"), only_to_me=False)
async def nbnhhsh(session: CommandSession):
    episode = session.current_arg_text.strip()
    if not episode:
        await session.send(
            "请输入想要查找的内容，反向词典：https://wantwords.net/",
            at_sender=True,
        )
    else:
        try:
            url = f"https://wantwords.net/EnglishRD/?m=ZhEn&q={urllib.parse.quote(episode)}"
            with httpx.Client(proxies={}) as client:
                r = (client.get(url, timeout=5)).json()
            msg = "反向词典获取到的前三个的结果：\n"
            for i in range(0, 3):
                data = r[i]
                msg += f"word：{data['w']}  (Part of speech：{data['P']})\ndescription：{data['d']}\n"
            await session.send(msg, at_sendser=True)
        except Exception as e:
            msg = "Error: {}".format(type(e))
            await session.send(msg)
