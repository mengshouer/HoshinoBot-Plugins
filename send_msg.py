import asyncio
import arrow

from collections import defaultdict
from typing import DefaultDict, List, Tuple, Union

from aiocqhttp import ActionFailed

from .config import config

sending_lock: DefaultDict[Tuple[Union[int, str], str], asyncio.Lock] = defaultdict(
    asyncio.Lock
)


async def send_result_message(bot, event, msg_list: List[str]) -> None:
    if event.message_type == "group":
        flag = config.group_forward_search_result and len(msg_list) > 1
        if flag:
            try:
                start_time = arrow.now()
                async with sending_lock[(event.group_id, "group")]:
                    await send_forward_msg(bot, event, msg_list)
                    await asyncio.sleep(
                        max(1 - (arrow.now() - start_time).total_seconds(), 0)
                    )
            except ActionFailed:
                await bot.send(event, "喜报：合并转发(群)消息发送失败：账号可能被风控.  尝试单独发送")
                flag = False
        if not flag:
            msg_ids = []
            for msg in msg_list:
                try:
                    start_time = arrow.now()
                    async with sending_lock[(event.group_id, "group")]:
                        msg_ids.append(
                            (
                                await bot.send_group_msg(
                                    group_id=event.group_id, message=msg
                                )
                            )["message_id"]
                        )
                        await asyncio.sleep(
                            max(1 - (arrow.now() - start_time).total_seconds(), 0)
                        )
                except ActionFailed:
                    pass
            if msg_ids:
                if len(msg_ids) != len(msg_list):
                    await bot.send(event, f"喜报：有{len(msg_list)-len(msg_ids)}条消息发送失败")
                if config.recall_time:
                    await asyncio.sleep(config.recall_time)
                    for msg_id in msg_ids:
                        try:
                            await bot.call_action("delete_msg", message_id=msg_id)
                        except ActionFailed:
                            pass
            else:
                await bot.send(event, "喜报：群消息发送失败：账号可能被风控.")
    elif event.message_type == "private":
        n = 0
        for msg in msg_list:
            try:
                start_time = arrow.now()
                async with sending_lock[(event.user_id, "private")]:
                    await bot.send_private_msg(user_id=event.user_id, message=msg)
                    await asyncio.sleep(
                        max(1 - (arrow.now() - start_time).total_seconds(), 0)
                    )
            except ActionFailed:
                n += 1
        if n:
            await bot.send(event, f"有{n}条消息发送失败！")


async def send_forward_msg(bot, event, msg_list: List[str]) -> None:
    msg = [
        {
            "type": "node",
            "data": {
                "name": "小冰",
                "user_id": "2854196306",
                "content": msg,
            },
        }
        for msg in msg_list
    ]
    await bot.send_group_forward_msg(group_id=event.group_id, messages=msg)
