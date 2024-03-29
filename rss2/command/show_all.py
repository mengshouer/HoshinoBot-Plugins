import asyncio
import re

from nonebot import on_command, CommandSession

from ..rss_class import Rss
from .show_dy import handle_rss_list
from ..permission import admin_permission


@on_command(
    "showall",
    aliases=("show_all", "selectall", "select_all", "所有订阅"),
    permission=admin_permission,
    only_to_me=False,
)
async def rssShowAll(session: CommandSession) -> None:
    args = session.current_arg_text
    if args:
        search_keyword = args  # 如果用户发送了参数则直接赋值
    else:
        search_keyword = None
    group_id = session.ctx.get("group_id")
    guild_channel_id = session.ctx.get("guild_id")
    if guild_channel_id:
        group_id = None
        guild_channel_id = f"{guild_channel_id}@{session.ctx.get('channel_id')}"

    if group_id:
        rss_list = Rss.get_by_group(group_id=group_id)
        if not rss_list:
            await session.finish("❌ 当前群组没有任何订阅！")
    elif guild_channel_id:
        rss_list = Rss.get_by_guild_channel(guild_channel_id=guild_channel_id)
        if not rss_list:
            await session.finish("❌ 当前子频道没有任何订阅！")
    else:
        rss_list = Rss.read_rss()

    result = []
    if search_keyword:
        for i in rss_list:
            test = bool(
                re.search(search_keyword, i.name, flags=re.I)
                or re.search(search_keyword, i.url, flags=re.I)
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
        await session.send(f"当前共有 {len(result)} 条订阅")
        result.sort(key=lambda x: x.get_url())
        await asyncio.sleep(0.5)
        page_size = 30
        while result:
            current_page = result[:page_size]
            msg_str = handle_rss_list(current_page)
            try:
                await session.send(msg_str)
            except Exception:
                page_size -= 5
                continue
            result = result[page_size:]
    else:
        await session.finish("❌ 当前没有任何订阅！")
