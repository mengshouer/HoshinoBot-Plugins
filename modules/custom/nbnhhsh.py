import requests

from nonebot import on_command

from hoshino import Service, priv, util

sv_help = '''
nhnhhsh-能不能好好说话
web:https://lab.magiconch.com/nbnhhsh/
前缀sx或者直接@bot触发
'''.strip()
sv = Service('nbnhhsh', visible=True)
aliases = ('sx', '缩写', 'zy', '转义', 'nhnhhsh')

@sv.on_prefix(aliases)
async def nbnhhsh(bot, ev):
    try:
        episode = ev.message.extract_plain_text()
        print(episode)
        if not episode:
            await bot.send(ev, '请输入要转义的缩写', at_sender=True)
            return
        url = f'https://lab.magiconch.com/api/nbnhhsh/guess'
        data = {
            "text" : episode
        }
        r = requests.post(url,data=data,timeout=5)
        data = r.json()[0]["trans"]
        msg = "可能拼音缩写的是："+str(data)
        await bot.send(ev, msg, at_sender=True)
    except:
        await bot.send(ev, "未查询到转义，可前往https://lab.magiconch.com/nbnhhsh/ 查询/贡献词条", at_sender=True)


@sv.on_rex(r'^[CQ:at,qq=[0-9]([A-Za-z0-9]+)$', only_to_me=True)
async def nbnhhsh(bot, ev):
    try:
        episode = ev.message.extract_plain_text()
        print(episode)
        if not episode:
            await bot.send(ev, '请输入要转义的缩写', at_sender=True)
            return
        url = f'https://lab.magiconch.com/api/nbnhhsh/guess'
        data = {
            "text" : episode
        }
        r = requests.post(url,data=data,timeout=5)
        data = r.json()[0]["trans"]
        msg = "可能拼音缩写的是："+str(data)
        await bot.send(ev, msg, at_sender=True)
    except:
        await bot.send(ev, "未查询到转义，可前往https://lab.magiconch.com/nbnhhsh/ 查询/贡献词条", at_sender=True)

