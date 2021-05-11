import os
from pathlib import Path

from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class
from .RSS import my_trigger as tr

# 存储目录
FILE_PATH = str(str(Path.cwd()) + os.sep + "data" + os.sep)

@on_command('deldy', aliases=('drop', '删除订阅'), permission=GROUP_ADMIN|SUPERUSER)
async def deldy(session: CommandSession):
    rss_name = session.get('deldy', prompt='输入要删除的订阅名或订阅地址')
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None

    rss = rss_class.Rss("", "", "-1", "-1")
    if rss.find_name(name=rss_name):
        rss = rss.find_name(name=rss_name)
    else:
        await session.send('❌ 删除失败！不存在该订阅！')
        return

    if group_id:
        if rss.delete_group(group=group_id):
            await tr.add_job(rss)
            await session.send('👏 当前群组取消订阅 {} 成功！'.format(rss.name))
        else:
            await session.send('❌ 当前群组没有订阅： {} ！'.format(rss.name))
    else:
        rss.delete_rss(rss)
        await tr.delete_job(rss)
        await session.send('👏 订阅 {} 删除成功！'.format(rss.name))

@deldy.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['deldy'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的订阅（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('输入不能为空！')

    # 如果当前正在向用户询问更多信息，且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg