import nonebot,os
try:
    import ujson as json
except:
    import json
from . import *

bot = nonebot.get_bot()

@bot.on_message()
async def custom_reply(ctx):
    msg = ctx['raw_message']
    if msg[0] in CRdata.custom_prefix or not CRdata.custom_prefix:
        for key in CRdata.data:
            if not CRdata.sensitive:
                ckey = key.lower()
                cmsg = msg.lower()
            if ckey == cmsg:
                await bot.send(ctx, CRdata.data[key])
                break
