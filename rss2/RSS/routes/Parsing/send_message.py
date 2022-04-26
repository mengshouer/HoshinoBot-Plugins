from typing import Any, Dict

import nonebot
from nonebot import logger

from ....bot_info import (
    get_bot_qq,
    get_bot_friend_list,
    get_bot_group_list,
    get_bot_guild_channel_list,
)
from ....RSS.rss_class import Rss

# 发送消息
async def send_msg(rss: Rss, msg: str, item: Dict[str, Any]) -> bool:
    try:
        bot = nonebot.get_bot()
    except Exception:
        return False
    if not msg:
        return False
    flag = False
    try:
        bot_qq = list(await get_bot_qq(bot))
        error_msg = f"消息发送失败，已达最大重试次数！\n链接：[{item.get('link')}]"
        if rss.user_id:
            all_friend = {}
            friend_list = []
            for sid in bot_qq:
                f = await get_bot_friend_list(sid, bot)
                all_friend[sid] = f
                friend_list.extend(f)
            friend_list = set(friend_list)
            for user_id in rss.user_id:
                if int(user_id) not in friend_list:
                    logger.error(f"QQ号[{user_id}]不是Bot的好友 链接：[{item.get('link')}]")
                    continue
                try:
                    sid = [k for k, v in all_friend.items() if int(user_id) in v][0]
                    await bot.send_msg(
                        self_id=sid,
                        message_type="private",
                        user_id=int(user_id),
                        message=msg,
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                    if item.get("count") == 3:
                        await bot.send_private_msg(
                            user_id=int(user_id), message=f"{error_msg}\nE: {repr(e)}"
                        )
    except Exception as e:
        logger.error(f"RSS推送好友私聊发送错误：E: {repr(e)} 链接：[{item.get('link')}]")

    try:
        if rss.group_id:
            all_group = {}
            group_list = []
            for sid in bot_qq:
                g = await get_bot_group_list(sid, bot)
                all_group[sid] = g
                group_list.extend(g)
            group_list = set(group_list)
            for group_id in rss.group_id:
                if int(group_id) not in group_list:
                    logger.error(f"Bot未加入群组[{group_id}] 链接：[{item.get('link')}]")
                    continue
                try:
                    sid = [k for k, v in all_group.items() if int(group_id) in v][0]
                    await bot.send_msg(
                        self_id=sid,
                        message_type="group",
                        group_id=int(group_id),
                        message=msg,
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                    if item.get("count") == 3:
                        await bot.send_group_msg(
                            group_id=int(group_id), message=f"E: {repr(e)}\n{error_msg}"
                        )
    except Exception as e:
        logger.error(f"RSS推送群组发送错误：E: {repr(e)} 链接：[{item.get('link')}]")

    try:
        if rss.guild_channel_id:
            all_guild = {}
            guild_list = []
            for sid in bot_qq:
                g = await get_bot_guild_channel_list(sid, bot)
                all_guild[sid] = g
                guild_list.extend(g)
            guild_list = set(guild_list)
            for guild_channel_id in rss.guild_channel_id:
                guild_id, channel_id = guild_channel_id.split("@")

                if guild_id not in guild_list:
                    guild_name = (await bot.get_guild_meta_by_guest(guild_id=guild_id))[
                        "guild_name"
                    ]
                    logger.error(
                        f"Bot未加入频道 {guild_name}[{guild_id}] 链接：[{item.get('link')}]"
                    )
                    continue

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

                s = [k for k, v in all_channel.items() if channel_id in v][0]
                try:
                    await bot.send_guild_channel_msg(
                        self_id=s,
                        message=msg,
                        guild_id=guild_id,
                        channel_id=channel_id,
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item.get('link')}]")
                    if item.get("count") == 3:
                        await bot.send_guild_channel_msg(
                            self_id=s,
                            message=f"E: {repr(e)}\n{error_msg}",
                            guild_id=guild_id,
                            channel_id=channel_id,
                        )
    except Exception as e:
        logger.error(f"RSS推送频道消息发送错误！ E: {repr(e)} 链接：[{item.get('link')}]")
    return flag
