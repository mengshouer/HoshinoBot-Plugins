from nonebot import on_command
from hoshino import Service, util

sv_help = '''
让群员使用bot来@全体成员，前提bot得有管理员(叫人用
只要前缀为"@全员"就触发，默认关闭
'''.strip()
sv = Service('atall', enable_on_default=False)

@sv.on_prefix('@全员')
async def atall(bot, ev):
    try:
        msg = ev.message.extract_plain_text()
        msg = "[CQ:at,qq=all]"+str(msg)
        await bot.send(ev, msg)
    except:
        await bot.send(ev, '[CQ:at,qq=all]')
