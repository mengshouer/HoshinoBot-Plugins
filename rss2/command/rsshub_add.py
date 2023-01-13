from typing import Any, Dict

import aiohttp
from nonebot import on_command, CommandSession
from yarl import URL

from ..config import config
from ..permission import admin_permission
from ..rss_class import Rss
from .add_dy import add_feed

rsshub_routes: Dict[str, Any] = {}


@on_command(
    "rsshub_add",
    only_to_me=False,
    permission=admin_permission,
)
async def rsshub_add(session: CommandSession):
    t = session.event.message.extract_plain_text()[10:].strip()
    if t:
        session.state["router"] = t
        await handle_rsshub_routes(session)
    else:
        await handle_feed_name(session)


async def handle_feed_name(session: CommandSession) -> None:
    name = session.state.get("name")
    while not name:
        name = (await session.aget("name", prompt="请输入要订阅的订阅名")).strip()
    while _ := Rss.get_one_by_name(name=name):
        del session.state["name"]
        name = await session.aget("name", prompt=f"已存在名为 {name} 的订阅，请重新输入")
    await handle_rsshub_routes(session)


async def handle_rsshub_routes(session: CommandSession) -> None:
    route = session.state.get("router")
    while not route:
        route = (await session.aget("router", prompt="请输入要订阅的 RSSHub 路由名")).strip()
    rsshub_url = URL(config.rsshub)
    # 对本机部署的 RSSHub 不使用代理
    local_host = [
        "localhost",
        "127.0.0.1",
    ]
    if config.rss_proxy and rsshub_url.host not in local_host:
        proxy = f"http://{config.rss_proxy}"
    else:
        proxy = None

    global rsshub_routes
    if not rsshub_routes:
        async with aiohttp.ClientSession() as s:
            resp = await s.get(rsshub_url.with_path("api/routes"), proxy=proxy)
            if resp.status != 200:
                await session.finish("获取路由数据失败，请检查 RSSHub 的地址配置及网络连接")
            rsshub_routes = await resp.json()

    while route not in rsshub_routes["data"]:
        del session.state["router"]
        route = (await session.aget("router", prompt="没有这个路由，请重新输入")).strip()

    route_list = rsshub_routes["data"][route]["routes"]
    session.state["route_list"] = route_list
    if not session.state.get("name"):
        await handle_feed_name(session)
    if len(route_list) > 1:
        await session.send(
            "请输入序号来选择要订阅的 RSSHub 路由：\n"
            + "\n".join(
                f"{index + 1}. {__route}" for index, __route in enumerate(route_list)
            )
        )
        (await session.aget("route_index")).strip()
    else:
        session.state["route_index"] = "0"
    await handle_route_index(session)


async def handle_route_index(session: CommandSession) -> None:
    route_index = session.state.get("route_index")
    route = session.state["route_list"][int(route_index) - 1]
    if args := [i for i in route.split("/") if i.startswith(":")]:
        await session.send(
            '请依次输入要订阅的 RSSHub 路由参数，并用 "/" 分隔：\n'
            + "/".join(
                f"{i.rstrip('?')}(可选)" if i.endswith("?") else f"{i}" for i in args
            )
            + "\n要置空请输入#或直接留空"
        )
        await session.aget("route_args")
    else:
        session.state["route_args"] = ""
    await handle_route_args(session)


async def handle_route_args(session: CommandSession) -> None:
    name = session.state.get("name")
    route_index = session.state.get("route_index")
    route_args = session.state.get("route_args")
    route = session.state["route_list"][int(route_index) - 1]
    feed_url = "/".join([i for i in route.split("/") if not i.startswith(":")])
    for i in route_args.split("/"):
        if len(i.strip("#")) > 0:
            feed_url += f"/{i}"

    await add_feed(name, feed_url.lstrip("/"), session)
