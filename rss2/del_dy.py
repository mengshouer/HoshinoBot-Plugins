import os
from pathlib import Path

from nonebot import on_command, CommandSession
from .permission import admin_permission

from .RSS import my_trigger as tr
from .RSS import rss_class

# 存储目录
FILE_PATH = str(str(Path.cwd()) + os.sep + "data" + os.sep)


@on_command(
    "deldy", aliases=("drop", "删除订阅"), permission=admin_permission, only_to_me=False
)
async def deldy(session: CommandSession):
    rss_name = session.get("deldy", prompt="输入要删除的订阅名")
    group_id = session.ctx.get("group_id")
    guild_channel_id = session.ctx.get("guild_id")
    if guild_channel_id:
        group_id = None
        guild_channel_id = guild_channel_id + "@" + session.ctx.get("channel_id")

    rss = rss_class.Rss()
    rss = rss.find_name(name=rss_name)

    if rss is None:
        await session.finish("❌ 删除失败！不存在该订阅！")
    else:
        if group_id:
            if rss.delete_group(group=str(group_id)):
                if not rss.group_id and not rss.user_id and not rss.guild_channel_id:
                    rss.delete_rss()
                    await tr.delete_job(rss)
                else:
                    await tr.add_job(rss)
                await session.finish(f"👏 当前群组取消订阅 {rss.name} 成功！")
            else:
                await session.finish(f"❌ 当前群组没有订阅： {rss.name} ！")
        elif guild_channel_id:
            if rss.delete_guild_channel(guild_channel=guild_channel_id):
                if not rss.group_id and not rss.user_id and not rss.guild_channel_id:
                    rss.delete_rss()
                    await tr.delete_job(rss)
                else:
                    await tr.add_job(rss)
                await session.finish(f"👏 当前子频道取消订阅 {rss.name} 成功！")
            else:
                await session.finish(f"❌ 当前子频道没有订阅： {rss.name} ！")
        else:
            rss.delete_rss()
            await tr.delete_job(rss)
            await session.finish(f"👏 订阅 {rss.name} 删除成功！")


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
