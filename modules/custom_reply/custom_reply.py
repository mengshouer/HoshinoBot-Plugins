import nonebot,os
try:
    import ujson as json
except:
    import json

bot = nonebot.get_bot()

@bot.on_message()
async def custom_reply(ctx):
    try:
        with open('CustomReplyData.json', 'r', encoding="GB2312") as f:
            data = json.load(f)
        msg = ctx['raw_message']
        for key in data:
            if key == msg:
                await bot.send(ctx, data[key])
                break
    except:
        if os.path.exists("./CustomReplyData.json"):
            print("数据文件格式有误")
        else:
            data = {}
            with open('CustomReplyData.json', 'w', encoding="GB2312") as f:
                json.dump(data, f, ensure_ascii=False)
                print("未发现数据文件，新建数据文件")
        
