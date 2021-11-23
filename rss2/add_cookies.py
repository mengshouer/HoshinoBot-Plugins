from nonebot import on_command, CommandSession
from nonebot.permission import *
from .RSS import my_trigger as tr
from .RSS import rss_class


@on_command("addcookies", aliases=("添加cookies"), permission=GROUP_ADMIN | SUPERUSER)
async def addcookies(session: CommandSession):
    rss_cookies = session.get(
        "addcookies",
        prompt="请输入\n名称 cookies\n空格分割\n获取方式：\nPC端 chrome 浏览器按 F12\n找到Consle选项卡，输入:\ndocument.cookie\n输出的字符串就是了",
    )

    dy = rss_cookies.split(" ", 1)

    rss = rss_class.Rss(name="", url="", user_id="-1", group_id="-1")
    # 判断是否有该名称订阅
    try:
        name = dy[0]
    except IndexError:
        await session.send("❌ 输入的订阅名为空！")
        return

    if not rss.find_name(name=name):
        await session.send("❌ 不存在该订阅: {}".format(name))
        return
    rss = rss.find_name(name=name)

    try:
        cookies = dy[1]
    except IndexError:
        await session.send("❌ 输入的cookies为空！")
        return

    rss.name = name
    if rss.set_cookies(cookies):
        await tr.add_job(rss)
        await session.send(
            "👏 {}的Cookies添加成功！\nCookies:{}\n".format(rss.name, rss.cookies)
        )
    else:
        await session.send(
            "👏 {}的Cookies添加失败！\nCookies:{}\n".format(rss.name, rss.cookies)
        )


@addcookies.args_parser
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
