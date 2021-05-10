from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class
from .RSS import my_trigger as tr

@on_command('add', aliases=('添加订阅', 'sub'), permission=GROUP_ADMIN|SUPERUSER)
async def add(session: CommandSession):
    user_id = session.ctx['user_id']
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None
    
    rss_dy_link = session.get('add', prompt='请输入\n名称 [订阅地址]\n空格分割、[]表示可选\n私聊默认订阅到当前账号，群聊默认订阅到当前群组\n更多信息可通过 change 命令修改\nhttps://github.com/Quan666/ELF_RSS/wiki/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B')

    dy = rss_dy_link.split(' ')

    rss = rss_class.Rss(name='', url='', user_id='-1', group_id='-1')
    # 判断是否有该名称订阅，有就将当前qq或群加入订阅
    try:
        name = dy[0]
    except KeyError:
        await session.send('❌ 输入的订阅名为空！')
        return

    async def add_group_or_user(group_id, user_id):
        if group_id:
            rss.add_group(group=str(group_id))
            await tr.add_job(rss)
            await session.send('👏 订阅到当前群组成功！')
        else:
            rss.add_user(user=user_id)
            await tr.add_job(rss)
            await session.send('👏 订阅到当前账号成功！')

    if rss.find_name(name=name):
        rss = rss.find_name(name=name)
        await add_group_or_user(group_id, user_id)
        return

    try:
        url = dy[1]
    except KeyError:
        await session.send('❌ 输入的订阅地址为空！')
        return

    # 去除判断，订阅链接不再唯一，可不同名同链接
    # # 判断当前订阅地址存在否
    # if rss.findURL(url=url):
    #     rss = rss.findURL(url=url)
    #     if group_id:
    #         rss.add_group(group=group_id)
    #         await tr.add_job(rss)
    #         await session.send('当前订阅地址已存在，将 {} 订阅到当前群组成功！'.format(rss.name))
    #     else:
    #         rss.add_user(user=user_id)
    #         await tr.add_job(rss)
    #         await session.send('当前订阅地址已存在，将 {} 订阅到当前账号成功！'.format(rss.name))
    #     return

    # 当前名称、url都不存在
    rss.name = name
    rss.url = url
    await add_group_or_user(group_id, user_id)

# add.args_parser 装饰器将函数声明为 add 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@add.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将订阅信息跟在命令名后面，作为参数传入
            # 例如用户可能发送了：订阅 test1 /twitter/user/key_official 1447027111 1037939056 1 true true #订阅名 订阅地址 qq 群组 更新时间 代理 第三方
            session.state['add'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的订阅（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('输入不能为空！')

    # 如果当前正在向用户询问更多信息（例如本例中的要压缩的链接），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg