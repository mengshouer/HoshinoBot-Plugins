import asyncio
from collections import defaultdict
from contextlib import suppress
from typing import Any, DefaultDict, Dict, Tuple, Union, List

import arrow
import nonebot
from nonebot import logger

from ..rss_class import Rss
from ..utils import get_bot_friend_list, get_bot_group_list, get_all_bot_channel_list

sending_lock: DefaultDict[Tuple[Union[int, str], str], asyncio.Lock] = defaultdict(
    asyncio.Lock
)

# 发送消息
async def send_msg(rss: Rss, msg: str, item: Dict[str, Any]) -> bool:
    bot = nonebot.get_bot()
    if not msg:
        return False
    flag = False
    error_msg = f"消息发送失败！\n链接：[{item.get('link')}]"
    if rss.user_id:
        all_friend = (await get_bot_friend_list(bot))[1]
        flag = any(
            await asyncio.gather(
                *[
                    send_private_msg(
                        bot, msg, int(user_id), item, error_msg, all_friend
                    )
                    for user_id in rss.user_id
                ]
            )
        )

    if rss.group_id:
        all_group = (await get_bot_group_list(bot))[1]
        flag = (
            any(
                await asyncio.gather(
                    *[
                        send_group_msg(
                            bot, msg, int(group_id), item, error_msg, all_group
                        )
                        for group_id in rss.group_id
                    ]
                )
            )
            or flag
        )

    if rss.guild_channel_id:
        all_channels = (await get_all_bot_channel_list(bot))[1]
        flag = (
            any(
                await asyncio.gather(
                    *[
                        send_guild_channel_msg(
                            bot, msg, guild_channel_id, item, error_msg, all_channels
                        )
                        for guild_channel_id in rss.guild_channel_id
                    ]
                )
            )
            or flag
        )
    return flag


# 发送私聊消息
async def send_private_msg(
    bot,
    msg: str,
    user_id: int,
    item: Dict[str, Any],
    error_msg: str,
    all_friend: Dict[int, List[int]],
) -> bool:
    flag = False
    start_time = arrow.now()
    sid = [k for k, v in all_friend.items() if int(user_id) in v][0]
    async with sending_lock[(user_id, "private")]:
        try:
            await bot.send_msg(
                self_id=sid,
                message_type="private",
                user_id=user_id,
                message=msg,
            )
            await asyncio.sleep(max(1 - (arrow.now() - start_time).total_seconds(), 0))
            flag = True
        except Exception as e:
            logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
            if item.get("to_send"):
                flag = True
                with suppress(Exception):
                    await bot.send_msg(
                        self_id=sid,
                        message_type="private",
                        user_id=user_id,
                        message=f"{error_msg}\nE: {repr(e)}",
                    )
        return flag


# 发送群聊消息
async def send_group_msg(
    bot,
    msg: str,
    group_id: int,
    item: Dict[str, Any],
    error_msg: str,
    all_group: Dict[int, List[int]],
) -> bool:
    flag = False
    start_time = arrow.now()
    sid = [k for k, v in all_group.items() if int(group_id) in v][0]
    async with sending_lock[(group_id, "group")]:
        try:
            await bot.send_msg(
                self_id=sid,
                message_type="group",
                group_id=group_id,
                message=msg,
            )
            await asyncio.sleep(max(1 - (arrow.now() - start_time).total_seconds(), 0))
            flag = True
        except Exception as e:
            logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
            if item.get("to_send"):
                flag = True
                with suppress(Exception):
                    await bot.send_msg(
                        self_id=sid,
                        message_type="group",
                        group_id=group_id,
                        message=f"E: {repr(e)}\n{error_msg}",
                    )
        return flag


# 发送频道消息
async def send_guild_channel_msg(
    bot,
    msg: str,
    guild_channel_id: str,
    item: Dict[str, Any],
    error_msg: str,
    all_channels: Dict,
) -> bool:
    flag = False
    start_time = arrow.now()
    guild_id, channel_id = guild_channel_id.split("@")
    sid = [k for k, v in all_channels.items() if channel_id in v][0]
    async with sending_lock[(guild_channel_id, "guild_channel")]:
        try:
            await bot.send_guild_channel_msg(
                self_id=sid,
                message=msg,
                guild_id=guild_id,
                channel_id=channel_id,
            )
            await asyncio.sleep(max(1 - (arrow.now() - start_time).total_seconds(), 0))
            flag = True
        except Exception as e:
            logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
            if item.get("to_send"):
                flag = True
                with suppress(Exception):
                    await bot.send_guild_channel_msg(
                        self_id=sid,
                        message=f"E: {repr(e)}\n{error_msg}",
                        guild_id=guild_id,
                        channel_id=channel_id,
                    )
        return flag
