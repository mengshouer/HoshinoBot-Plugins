import re

from nonebot import on_command, CommandSession

from ..qbittorrent_download import start_down
from ..parsing.utils import get_proxy


@on_command("upload_file", aliases=("uploadfile"), only_to_me=True)
async def upload_group_file(session: CommandSession) -> None:
    if session.event.message_type == "private":
        await session.send("请在群聊中使用该命令")
    elif session.event.message_type == "group":
        target = re.search(
            "(magnet:\?xt=urn:btih:([a-fA-F0-9]{40}|[2-7A-Za-z]{32}))|(http.*?\.torrent)",
            str(session.event.message),
        )
        if not target:
            await session.finish("请输入种子链接")
        await start_down(
            url=target[0],
            group_ids=[str(session.event.group_id)],
            name="手动上传",
            proxy=get_proxy(True),
        )
