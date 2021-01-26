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
    for key in CRdata.data:
        if key == msg:
            await bot.send(ctx, CRdata.data[key])
            break
        
