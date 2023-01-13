from nonebot import on_command, CommandSession
from ..permission import admin_permission

from .. import my_trigger as tr
from ..rss_class import Rss


@on_command(
    "deldy", aliases=("drop", "删除订阅"), permission=admin_permission, only_to_me=False
)
async def deldy(session: CommandSession) -> None:
    rss_name = (await session.aget("deldy", prompt="输入要删除的订阅名")).strip()
    group_id = session.ctx.get("group_id")
    guild_channel_id = session.ctx.get("guild_id")
    if guild_channel_id:
        group_id = None
        guild_channel_id = f"{guild_channel_id}@{session.ctx.get('channel_id')}"

    rss_name_list = rss_name.strip().split(" ")
    delete_successes = []
    delete_failures = []
    for rss_name in rss_name_list:
        rss = Rss.get_one_by_name(name=rss_name)
        if rss is None:
            delete_failures.append(rss_name)
        elif guild_channel_id:
            if rss.delete_guild_channel(guild_channel=guild_channel_id):
                if not any([rss.group_id, rss.user_id, rss.guild_channel_id]):
                    rss.delete_rss()
                    tr.delete_job(rss)
                else:
                    await tr.add_job(rss)
                delete_successes.append(rss_name)
            else:
                delete_failures.append(rss_name)
        elif group_id:
            if rss.delete_group(group=str(group_id)):
                if not any([rss.group_id, rss.user_id, rss.guild_channel_id]):
                    rss.delete_rss()
                    tr.delete_job(rss)
                else:
                    await tr.add_job(rss)
                delete_successes.append(rss_name)
            else:
                delete_failures.append(rss_name)
        else:
            rss.delete_rss()
            tr.delete_job(rss)
            delete_successes.append(rss_name)

    result = []
    if delete_successes:
        if guild_channel_id:
            result.append(f'👏 当前子频道成功取消订阅： {"、".join(delete_successes)} ！')
        elif group_id:
            result.append(f'👏 当前群组成功取消订阅： {"、".join(delete_successes)} ！')
        else:
            result.append(f'👏 成功删除订阅： {"、".join(delete_successes)} ！')
    if delete_failures:
        if guild_channel_id:
            result.append(f'❌ 当前子频道没有订阅： {"、".join(delete_successes)} ！')
        elif group_id:
            result.append(f'❌ 当前群组没有订阅： {"、".join(delete_successes)} ！')
        else:
            result.append(f'❌ 未找到订阅： {"、".join(delete_successes)} ！')

    await session.finish("\n".join(result))


@deldy.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state["deldy"] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的订阅（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause("输入不能为空！")

    # 如果当前正在向用户询问更多信息，且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg
