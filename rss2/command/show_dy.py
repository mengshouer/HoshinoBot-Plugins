from typing import List

from nonebot import on_command, CommandSession
from ..permission import admin_permission

from ..rss_class import Rss


def handle_rss_list(rss_list: List[Rss]) -> str:
    rss_info_list = [f"{i.name}：{i.url}" for i in rss_list]
    rss_info_list.sort()
    msg_str = f"当前共有 {len(rss_info_list)} 条订阅：\n\n" + "\n\n".join(rss_info_list)
    if rss_stopped_info_list := [f"{i.name}：{i.url}" for i in rss_list if i.stop]:
        rss_stopped_info_list.sort()
        msg_str += (
            "\n----------------------\n"
            f"其中共有 {len(rss_stopped_info_list)} 条订阅已停止更新：\n\n"
            + "\n\n".join(rss_stopped_info_list)
        )
    return msg_str


# 不带订阅名称默认展示当前群组或账号的订阅，带订阅名称就显示该订阅的
@on_command("show", aliases=("查看订阅"), permission=admin_permission, only_to_me=False)
async def rssShow(session: CommandSession) -> None:
    args = session.current_arg.strip()
    if args:
        rss_name = args
    else:
        rss_name = None

    user_id = session.ctx["user_id"]
    group_id = session.ctx.get("group_id")
    guild_channel_id = session.ctx.get("guild_id")
    if guild_channel_id:
        group_id = None
        guild_channel_id = f"{guild_channel_id}@{session.ctx.get('channel_id')}"

    if rss_name:
        rss = Rss.get_one_by_name(rss_name)
        if (
            rss is None
            or (guild_channel_id and guild_channel_id not in rss.guild_channel_id)
            or (group_id and str(group_id) not in rss.group_id)
        ):
            await session.finish(f"❌ 订阅 {rss_name} 不存在或未订阅！")
        else:
            # 隐私考虑，不展示除当前群组或频道外的群组、频道和QQ
            rss_msg = str(rss.hide_some_infos(group_id, guild_channel_id))
            await session.finish(rss_msg)

    if group_id:
        rss_list = Rss.get_by_group(group_id=group_id)
        if not rss_list:
            await session.finish("❌ 当前群组没有任何订阅！")
    elif guild_channel_id:
        rss_list = Rss.get_by_guild_channel(guild_channel_id=guild_channel_id)
        if not rss_list:
            await session.finish("❌ 当前子频道没有任何订阅！")
    else:
        rss_list = Rss.get_by_user(user=user_id)

    if rss_list:
        msg_str = handle_rss_list(rss_list)
        await session.finish(msg_str)
    else:
        await session.finish("❌ 当前没有任何订阅！")
