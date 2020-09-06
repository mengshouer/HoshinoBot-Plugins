import random

from nonebot import on_command

from hoshino import R, Service, priv, util


sv = Service('custom_chat', visible=False)

@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


@sv.on_keyword(('有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        msg = f'有一说一,这件事大家懂得都懂,不懂得,说了你也不明白,不如不说。你们也别来问我怎么了,利益牵扯太大,说了对你们也没什么好处,当不知道就行了,其余的我只能说这里面水很深,牵扯到很多大人物。详细资料你们自己找是很难找的,网上大部分已经删除干净了,所以我只能说懂得都懂,不懂得也没办法。'
        await bot.send(ctx, msg)
