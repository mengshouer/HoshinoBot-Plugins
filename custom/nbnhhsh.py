import aiohttp
from nonebot import CommandSession
from hoshino import Service, util

sv = Service("nbnhhsh")


@sv.on_command(
    "sx", aliases=("缩写", "zy", "转义", "nhnhhsh", "/sx", "\sx"), only_to_me=False
)
async def nbnhhsh(session: CommandSession):
    episode = session.current_arg_text.strip()
    if not episode:
        await session.send(
            "请输入缩写的内容，缩写-nhnhhsh-能不能好好说话，web:https://lab.magiconch.com/nbnhhsh/，前缀sx触发",
            at_sender=True,
        )
    else:
        try:
            url = f"https://lab.magiconch.com/api/nbnhhsh/guess"
            data = {"text": episode}
            async with aiohttp.request("POST", url, json=data) as r:
                try:
                    data = (await r.json())[0]["trans"]
                except:
                    await session.send(
                        "未查询到转义，可前往https://lab.magiconch.com/nbnhhsh/ 查询/贡献词条",
                        at_sender=True,
                    )
                    return
                msg = "可能拼音缩写的是：" + str(data)
                msg += "\n如果带有屏蔽词自行前往 web:https://lab.magiconch.com/nbnhhsh/ 查询"
                await session.send(util.filt_message(msg), at_sender=True)
        except Exception as e:
            msg = "Error: {}".format(type(e))
            await session.send(msg)
