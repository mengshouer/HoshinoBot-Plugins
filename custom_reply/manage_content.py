try:
    import ujson as json
except:
    import json
from nonebot import on_command, CommandSession
from nonebot.permission import *
from . import *

@on_command('addCR', aliases=('CRadd', 'addcr', 'cradd', 'add_custom_reply'), permission=SUPERUSER, only_to_me=True)
async def add_custom_reply_content(session: CommandSession):
    content = session.current_arg_text.strip()
    content = content.split('|||')
    with open('CustomReplyData.json', 'r', encoding="GB2312") as f:
        data = json.load(f)
    key = content[0]
    data[key] = content[1]
    with open('CustomReplyData.json', 'w', encoding="GB2312") as f:
        json.dump(data, f, ensure_ascii=False)
        CRdata.data = data
        await session.finish(f'自定义回复"{key}"添加成功！')
        

@on_command('delCR', aliases=('CRdel', 'delcr', 'crdel', 'del_custom_reply'), permission=SUPERUSER, only_to_me=True)
async def del_custom_reply_content(session: CommandSession):
    content = session.current_arg_text.strip()
    with open('CustomReplyData.json', 'r', encoding="GB2312") as f:
        data = json.load(f)
    try:
        del data[content]
        CRdata.data = data
        with open('CustomReplyData.json', 'w', encoding="GB2312") as f:
            json.dump(data, f, ensure_ascii=False)
            await session.send(f'自定义回复"{content}"删除成功！')
    except Exception as e:
        print(repr(e))
        await session.finish(f'不存在该自定义回复"{content}"')
    
