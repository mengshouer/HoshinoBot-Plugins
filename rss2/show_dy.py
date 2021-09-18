import copy

from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class

async def handle_rss_list(rss_list: list) -> str:
    rss_info_list = [f"{i.name}：{i.url}" for i in rss_list]
    rss_info_list.sort()
    msg_str = f"当前共有 {len(rss_info_list)} 条订阅：\n\n" + "\n\n".join(rss_info_list)
    rss_stopped_info_list = [f"{i.name}：{i.url}" for i in rss_list if i.stop]
    if rss_stopped_info_list:
        rss_stopped_info_list.sort()
        msg_str += (
            f"\n----------------------\n"
            f"其中共有 {len(rss_stopped_info_list)} 条订阅已停止更新：\n\n"
            + "\n\n".join(rss_stopped_info_list)
        )
    return msg_str


# 不带订阅名称默认展示当前群组或账号的订阅
# 带订阅名称就显示该订阅的
@on_command('show', aliases=('查看订阅'), permission=GROUP_ADMIN|SUPERUSER)
async def rssShow(session: CommandSession):
    args = session.current_arg.strip()
    if args:
        rss_name = args
    else:
        rss_name = None

    user_id = session.ctx['user_id']
    group_id = session.ctx.get('group_id')

    rss = rss_class.Rss()
    if rss_name:
        rss = rss.find_name(rss_name)
        if not rss:
            await session.send(f"❌ 订阅 {rss_name} 不存在！")
            return
        rss_msg = str(rss)
        if group_id:
            # 隐私考虑，群组下不展示除当前群组外的群号和QQ
            if not str(group_id) in rss.group_id:
                await session.send(f"❌ 当前群组未订阅 {rss_name} ")
                return
            rss_tmp = copy.deepcopy(rss)
            rss_tmp.group_id = [str(group_id), "*"]
            rss_tmp.user_id = ["*"]
            rss_msg = str(rss_tmp)
        await session.send(rss_msg)
        return

    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.send("❌ 当前群组没有任何订阅！")
            return
    else:
        rss_list = rss.find_user(user=user_id)

    if rss_list:
        msg_str = await handle_rss_list(rss_list)
        await session.send(msg_str)
    else:
        await session.send("❌ 当前没有任何订阅！")