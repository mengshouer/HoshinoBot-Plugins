import asyncio
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Tuple, Union

import arrow
import nonebot
from nonebot import logger

from ..rss_class import Rss
from ..utils import (
    get_bot_friend_list,
    get_bot_group_list,
    get_bot_guild_channel_list,
    get_bot_qq,
)

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
        all_friend, friend_list = await get_friend_info(bot)
        if invalid_user_id_list := [
            user_id for user_id in rss.user_id if int(user_id) not in friend_list
        ]:
            logger.error(
                f"QQ号[{','.join(invalid_user_id_list)}]不是Bot的好友"
                f" 链接：[{item.get('link')}]"
            )
        flag = any(
            await asyncio.gather(
                *[
                    send_private_msg(
                        bot, msg, int(user_id), item, error_msg, all_friend
                    )
                    for user_id in rss.user_id
                    if int(user_id) in friend_list
                ]
            )
        )

    if rss.group_id:
        all_group, group_list = await get_group_info(bot)
        if invalid_group_id_list := [
            group_id for group_id in rss.group_id if int(group_id) not in group_list
        ]:
            logger.error(
                f"Bot未加入群组[{','.join(invalid_group_id_list)}]"
                f" 链接：[{item.get('link')}]"
            )
        flag = (
            any(
                await asyncio.gather(
                    *[
                        send_group_msg(
                            bot, msg, int(group_id), item, error_msg, all_group
                        )
                        for group_id in rss.group_id
                        if int(group_id) in group_list
                    ]
                )
            )
            or flag
        )

    if rss.guild_channel_id:
        (
            valid_guild_channel_id_list,
            all_channel,
        ) = await filter_valid_guild_channel_id_list(
            bot=bot, guild_channel_id_list=rss.guild_channel_id, item=item
        )
        flag = (
            any(
                await asyncio.gather(
                    *[
                        send_guild_channel_msg(
                            bot, msg, guild_channel_id, item, error_msg, all_channel
                        )
                        for guild_channel_id in valid_guild_channel_id_list
                    ]
                )
            )
            or flag
        )
    return flag


async def get_friend_info(bot):
    bot_qq = list(get_bot_qq(bot))
    # 获取好友列表
    all_friend = {}
    friend_list = []
    for sid in bot_qq:
        f = await get_bot_friend_list(sid, bot)
        all_friend[sid] = f
        friend_list.extend(f)
    friend_list = set(friend_list)
    return all_friend, friend_list


async def get_group_info(bot):
    bot_qq = list(get_bot_qq(bot))
    # 获取群列表
    all_group = {}
    group_list = []
    for sid in bot_qq:
        g = await get_bot_group_list(sid, bot)
        all_group[sid] = g
        group_list.extend(g)
    group_list = set(group_list)
    return all_group, group_list


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
    while True:
        async with sending_lock[(user_id, "private")]:
            try:
                await bot.send_msg(
                    self_id=sid,
                    message_type="private",
                    user_id=user_id,
                    message=msg,
                )
                await asyncio.sleep(
                    max(1 - (arrow.now() - start_time).total_seconds(), 0)
                )
                flag = True
            except Exception as e:
                logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                if item.get("to_send"):
                    flag = True
                    try:
                        await bot.send_msg(
                            self_id=sid,
                            message_type="private",
                            user_id=user_id,
                            message=f"{error_msg}\nE: {repr(e)}",
                        )
                    except Exception:
                        pass
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
    while True:
        async with sending_lock[(group_id, "group")]:
            try:
                await bot.send_msg(
                    self_id=sid,
                    message_type="group",
                    group_id=group_id,
                    message=msg,
                )
                await asyncio.sleep(
                    max(1 - (arrow.now() - start_time).total_seconds(), 0)
                )
                flag = True
            except Exception as e:
                logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                if item.get("to_send"):
                    flag = True
                    try:
                        await bot.send_msg(
                            self_id=sid,
                            message_type="group",
                            group_id=group_id,
                            message=f"E: {repr(e)}\n{error_msg}",
                        )
                    except Exception:
                        pass
            return flag


# 过滤合法频道
async def filter_valid_guild_channel_id_list(
    bot, guild_channel_id_list: List[str], item: Dict[str, Any]
) -> List[str]:
    bot_qq = list(get_bot_qq(bot))
    # 获取频道列表
    all_guild = {}
    guild_list = []
    for sid in bot_qq:
        g = await get_bot_guild_channel_list(sid, bot)
        all_guild[sid] = g
        guild_list.extend(g)
    guild_list = set(guild_list)
    valid_guild_channel_id_list = []
    for guild_channel_id in guild_channel_id_list:
        guild_id, channel_id = guild_channel_id.split("@")
        if guild_id not in guild_list:
            guild_name = (await bot.get_guild_meta_by_guest(guild_id=guild_id))[
                "guild_name"
            ]
            logger.error(f"Bot未加入频道 {guild_name}[{guild_id}] 链接：[{item.get('link')}]")
            continue

        # 获取子频道列表
        sid = [k for k, v in all_guild.items() if guild_id in v]
        all_channel = {}
        channel_list = []
        for s in sid:
            c = await get_bot_guild_channel_list(s, bot, guild_id=guild_id)
            all_channel[s] = c
            channel_list.extend(c)
        channel_list = set(channel_list)
        if channel_id not in channel_list:
            guild_name = (await bot.get_guild_meta_by_guest(guild_id=guild_id))[
                "guild_name"
            ]
            logger.error(
                f"Bot未加入频道 {guild_name}[{guild_id}]的子频道[{channel_id}] 链接：[{item.get('link')}]"
            )
            continue
        valid_guild_channel_id_list.append(guild_channel_id)
    return valid_guild_channel_id_list, all_channel


# 发送频道消息
async def send_guild_channel_msg(
    bot,
    msg: str,
    guild_channel_id: str,
    item: Dict[str, Any],
    error_msg: str,
    all_channel: Dict,
) -> bool:
    flag = False
    start_time = arrow.now()
    guild_id, channel_id = guild_channel_id.split("@")
    sid = [k for k, v in all_channel.items() if channel_id in v][0]
    while True:
        async with sending_lock[(guild_channel_id, "guild_channel")]:
            try:
                await bot.send_guild_channel_msg(
                    self_id=sid,
                    message=msg,
                    guild_id=guild_id,
                    channel_id=channel_id,
                )
                await asyncio.sleep(
                    max(1 - (arrow.now() - start_time).total_seconds(), 0)
                )
                flag = True
            except Exception as e:
                logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                if item.get("to_send"):
                    flag = True
                    try:
                        await bot.send_guild_channel_msg(
                            self_id=sid,
                            message=f"E: {repr(e)}\n{error_msg}",
                            guild_id=guild_id,
                            channel_id=channel_id,
                        )
                    except Exception:
                        pass
            return flag
