import datetime
from nonebot import on_command, CommandSession
from hoshino import Service, util

sv = Service("et")


@sv.on_prefix(("/et", "/ET"))
async def ltToET(bot, ev):
    epochTimeFactor = (
        3600.0 / 175.0
    )  # 60 * 24 Eorzean minutes (one day) per 70 real-world minutes.
    lt = datetime.datetime.now()
    et_stamp = lt.timestamp() * epochTimeFactor
    et_year = int(et_stamp / 33177600) + 1
    et_month = int(et_stamp / 2764800 % 12) + 1
    et_day = int(et_stamp / 86400 % 32) + 1
    et_hour = int(et_stamp / 3600 % 24)
    et_minute = int(et_stamp / 60 % 60)
    et_second = int(et_stamp % 60)
    # date = f"{et_year}/{et_month}/{et_day} {et_hour}:{et_minute}:{et_second}"
    msg = f"ET {et_month}-{et_day} {et_hour}:{et_minute} --- {et_year}-{et_month}-{et_day} {et_hour}:{et_minute}:{et_second}"
    await bot.send(ev, msg)
