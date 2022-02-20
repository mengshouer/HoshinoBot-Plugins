import re

from nonebot import on_command, CommandSession

from .RSS import rss_class
from .show_dy import handle_rss_list
from .permission import admin_permission


@on_command(
    "showall",
    aliases=("show_all", "selectall", "select_all", "所有订阅"),
    permission=admin_permission,
    only_to_me=False,
)
async def rssShowAll(session: CommandSession):
    args = session.current_arg_text
    if args:
        search_keyword = args  # 如果用户发送了参数则直接赋值
    else:
        search_keyword = None
    group_id = session.ctx.get("group_id")
    guild_channel_id = session.ctx.get("guild_id")
    if guild_channel_id:
        group_id = None
        guild_channel_id = guild_channel_id + "@" + session.ctx.get("channel_id")

    rss = rss_class.Rss()

    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.finish("❌ 当前群组没有任何订阅！")
    elif guild_channel_id:
        rss_list = rss.find_guild_channel(guild_channel=str(guild_channel_id))
        if not rss_list:
            await session.finish("❌ 当前子频道没有任何订阅！")
    else:
        rss_list = rss.read_rss()

    result = []
    if search_keyword:
        for i in rss_list:
            test = re.search(search_keyword, i.name, flags=re.I) or re.search(
                search_keyword, i.url, flags=re.I
            )
            if not group_id and not guild_channel_id and search_keyword.isdigit():
                if i.user_id:
                    test = test or search_keyword in i.user_id
                if i.group_id:
                    test = test or search_keyword in i.group_id
                if i.guild_channel_id:
                    test = test or search_keyword in i.guild_channel_id
            if test:
                result.append(i)
    else:
        result = rss_list

    if result:
        msg_str = await handle_rss_list(result)
        await session.finish(msg_str)
    else:
        await session.finish("❌ 当前没有任何订阅！")
