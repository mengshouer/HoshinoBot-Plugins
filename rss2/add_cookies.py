from nonebot import on_command, CommandSession
from .permission import admin_permission
from .RSS import my_trigger as tr
from .RSS import rss_class

prompt = """\
请输入：
    名称 cookies
空格分割

获取方式：
    PC端 Chrome 浏览器按 F12
    找到Console选项卡，输入:
        document.cookie
    输出的字符串就是了\
"""


@on_command(
    "add_cookies", aliases=("添加cookies"), permission=admin_permission, only_to_me=False
)
async def add_cookies(session: CommandSession):
    rss_cookies = session.get("add_cookies", prompt=prompt)

    dy = rss_cookies.split(" ", 1)

    rss = rss_class.Rss()
    # 判断是否有该名称订阅
    try:
        name = dy[0]
    except IndexError:
        await session.finish("❌ 输入的订阅名为空！")

    rss = rss.find_name(name=name)

    if rss is None:
        await session.finish(f"❌ 不存在该订阅: {name}")
    else:
        try:
            cookies = dy[1]
        except IndexError:
            await session.finish("❌ 输入的cookies为空！")

        rss.name = name
        if rss.set_cookies(cookies):
            await tr.add_job(rss)
            await session.finish(f"👏 {rss.name}的Cookies添加成功！\nCookies:{rss.cookies}\n")
        else:
            await session.finish(f"❌ {rss.name}的Cookies添加失败！\nCookies:{rss.cookies}\n")


@add_cookies.args_parser
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
