import re

from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class
from .show_dy import handle_rss_list


@on_command(
    "showall",
    aliases=("show_all", "selectall", "select_all", "所有订阅"),
    permission=GROUP_ADMIN | SUPERUSER,
)
async def rssShowAll(session: CommandSession):
    args = session.current_arg_text
    if args:
        search_keyword = args  # 如果用户发送了参数则直接赋值
    else:
        search_keyword = None
    group_id = session.ctx.get("group_id")

    rss = rss_class.Rss()
    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.send("❌ 当前群组没有任何订阅！")
            return
    else:
        rss_list = rss.read_rss()

    result = []
    if search_keyword:
        for i in rss_list:
            test = re.search(search_keyword, i.name, flags=re.I) or re.search(
                search_keyword, i.url, flags=re.I
            )
            if not group_id and search_keyword.isdigit():
                if i.user_id:
                    test = test or search_keyword in i.user_id
                if i.group_id:
                    test = test or search_keyword in i.group_id
            if test:
                result.append(i)
    else:
        result = rss_list

    if result:
        msg_str = await handle_rss_list(result)
        await session.send(msg_str)
    else:
        await session.send("❌ 当前没有任何订阅！")
