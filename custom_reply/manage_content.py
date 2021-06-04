try:
    import ujson as json
except:
    import json
import os
from nonebot import on_command, CommandSession
from nonebot.permission import *
from . import *

@on_command('addCR', aliases=('CRadd', 'addcr', 'cradd', 'add_custom_reply'), permission=SUPERUSER, only_to_me=True)
async def add_custom_reply_content(session: CommandSession):
    content = session.current_arg_text.strip()
    content = content.split('|||')
    with open('./data/custom_reply/CustomReplyData.json', 'r', encoding="GB2312") as f:
        data = json.load(f)
    key = content[0]
    data[key] = content[1]
    hidetext = ""
    hidedata = {}
    # 处理隐藏的回复
    if len(content) > 2:
        if os.path.exists("./data/custom_reply/HideCustomReplyList.json"):
            with open('./data/custom_reply/HideCustomReplyList.json', 'r', encoding="GB2312") as f:
                hidedata = json.load(f)
        hidedata[key] = ""
        with open('./data/custom_reply/HideCustomReplyList.json', 'w', encoding="GB2312") as f:
            json.dump(hidedata, f, indent=4, ensure_ascii=False)
        hidetext = "隐藏的"
    # 最终写入文件
    with open('./data/custom_reply/CustomReplyData.json', 'w', encoding="GB2312") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        CRdata.data = data
        await session.finish(f'{hidetext}自定义回复"{key}"添加成功！')

@on_command('delCR', aliases=('CRdel', 'delcr', 'crdel', 'del_custom_reply'), permission=SUPERUSER, only_to_me=True)
async def del_custom_reply_content(session: CommandSession):
    content = session.current_arg_text.strip()
    with open('./data/custom_reply/CustomReplyData.json', 'r', encoding="GB2312") as f:
        data = json.load(f)
    try:
        del data[content]
        CRdata.data = data
        with open('./data/custom_reply/CustomReplyData.json', 'w', encoding="GB2312") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            await session.send(f'自定义回复"{content}"删除成功！')
        if os.path.exists("./data/custom_reply/HideCustomReplyList.json"):
            try:
                with open('./data/custom_reply/HideCustomReplyList.json', 'r', encoding="GB2312") as f:
                    data = json.load(f)
                del data[content]
                with open('./data/custom_reply/HideCustomReplyList.json', 'w', encoding="GB2312") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                pass
    except Exception as e:
        logger.warning(repr(e))
        await session.finish(f'不存在该自定义回复"{content}"')

@on_command('/crlist', aliases=('/CRlist', '/CRLIST', 'crlist', 'CRLIST'), only_to_me=False)
async def show_custom_reply_list(session: CommandSession):
    content = session.current_arg_text.strip()
    with open('./data/custom_reply/CustomReplyData.json', 'r', encoding="GB2312") as f:
        data = json.load(f)
    if os.path.exists("./data/custom_reply/HideCustomReplyList.json"):
        with open('./data/custom_reply/HideCustomReplyList.json', 'r', encoding="GB2312") as f:
            hide_list = json.load(f)
        for i in list(hide_list.keys()):
            del data[i]
    crlist = list(data.keys())
    try:
        limit = int(len(crlist) / 50) + 1
        if int(content) > limit:
            await session.send("输入参数无效，超过最大页数！")
            return
        count = int(content) * 50
        crlist = crlist[count-50:count]
    except Exception as e:
        content = 1
        crlist = crlist[0:50]
    await session.finish(str(crlist)+f"\n每页最多显示50个,当前为第{content}页,总共{limit}页。")
