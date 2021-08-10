import re

from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class
from .show_dy import handle_rss_list

@on_command('showall', aliases=('selectall','所有订阅'), permission=GROUP_ADMIN|SUPERUSER)
async def rssShowAll(session: CommandSession):
    args = session.current_arg_text
    if args:
        rss_name_search = args  # 如果用户发送了参数则直接赋值
    else:
        rss_name_search = None
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None

    rss = rss_class.Rss("", "", "-1", "-1")
    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.send('❌ 当前群组没有任何订阅！')
            return
    else:
        rss_list = rss.read_rss()

    if rss_name_search:
        rss_list = [
            i for i in rss_list if re.search(rss_name_search, f"{i.name}|{i.url}")
        ]

    if rss_list:
        msg_str = await handle_rss_list(rss_list)
        await session.send(msg_str)

    else:
        await session.send('❌ 当前群组没有任何订阅！')
