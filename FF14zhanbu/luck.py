from nonebot import logger
from hoshino import Service
from .utils import luck_daily

sv = Service("ff14zhanbu")


@sv.on_prefix(("/luck", "/占卜", "/zhanbu"))
async def ff14luck(bot, ev) -> None:
    args = ev.message.extract_plain_text()
    if args:
        if "help" in args:
            await bot.finish(
                ev,
                "使用命令/luck，/占卜，/zhanbu获得日常占卜结果\n"
                '对结果不满意，可以使用"/luck r"来重抽\n'
                "插件名：onebot_Astrologian_FFXIV",
            )
        elif ("r" in args) or ("重抽" in args) or ("redraw" in args):
            await bot.send(ev, message="开拓命运吧", at_sender=True)
            await bot.finish(
                ev,
                await luck_daily(user_id=int(ev.user_id), group_message=True),
                at_sender=True,
            )
    else:
        msg = await luck_daily(user_id=int(ev.user_id), redraw=True, group_message=True)
        try:
            await bot.send(ev, msg, at_sender=True)
        except:
            logger.info(msg)

