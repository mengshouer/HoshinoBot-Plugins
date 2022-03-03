import nonebot

from nonebot import logger

from ....RSS import rss_class
from ....bot_info import (
    get_bot_qq,
    get_bot_friend_list,
    get_bot_group_list,
    get_bot_guild_channel_list,
)


# 发送消息
async def send_msg(rss: rss_class.Rss, msg: str, item: dict) -> bool:
    bot = nonebot.get_bot()
    flag = False
    if not msg:
        return False
    bot_qq = list(await get_bot_qq(bot))
    error_msg = f"消息发送失败，已达最大重试次数！\n链接：[{item['link']}]"
    if rss.user_id:
        for sid in bot_qq:
            friend_list = await get_bot_friend_list(bot, sid)
            for user_id in rss.user_id:
                if int(user_id) not in friend_list:
                    logger.warning(f"QQ号[{user_id}]不是Bot[{sid}]的好友 链接：[{item['link']}]")
                    continue
                try:
                    await bot.send_msg(
                        self_id=sid,
                        message_type="private",
                        user_id=int(user_id),
                        message=str(msg),
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item['link']}]")
                    if item.get("count") == 3:
                        await bot.send_private_msg(
                            user_id=int(user_id), message=f"{error_msg}\nE: {repr(e)}"
                        )

    if rss.group_id:
        for sid in bot_qq:
            group_list = await get_bot_group_list(bot, sid)
            for group_id in rss.group_id:
                if int(group_id) not in group_list:
                    logger.warning(f"Bot[{sid}]未加入群组[{group_id}] 链接：[{item['link']}]")
                    continue
                try:
                    await bot.send_msg(
                        self_id=sid,
                        message_type="group",
                        group_id=int(group_id),
                        message=str(msg),
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item['link']}]")
                    if item.get("count") == 3:
                        await bot.send_group_msg(
                            group_id=int(group_id), message=f"E: {repr(e)}\n{error_msg}"
                        )

    if rss.guild_channel_id:
        for sid in bot_qq:
            for guild_channel_id in rss.guild_channel_id:
                id = guild_channel_id.split("@")
                guild_id = str(id[0])
                channel_id = str(id[1])

                guild_list = await get_bot_guild_channel_list(sid, bot)
                if guild_id not in guild_list:
                    guild_name = (
                        await bot.get_guild_meta_by_guest(
                            self_id=sid, guild_id=guild_id
                        )
                    )["guild_name"]
                    logger.error(
                        f"Bot[{bot.self_id}]未加入频道 {guild_name}[{guild_id}] 链接：[{item['link']}]"
                    )
                    continue

                channel_list = await get_bot_guild_channel_list(
                    sid, bot, guild_id=guild_id
                )
                if channel_id not in channel_list:
                    guild_name = (
                        await bot.get_guild_meta_by_guest(
                            self_id=sid, guild_id=guild_id
                        )
                    )["guild_name"]
                    logger.error(
                        f"Bot[{bot.self_id}]未加入频道[{guild_id}]的子频道[{channel_id}] 链接：[{item['link']}]"
                    )
                    continue

                try:
                    await bot.send_guild_channel_msg(
                        self_id=sid,
                        message=str(msg),
                        guild_id=guild_id,
                        channel_id=channel_id,
                    )
                    flag = True
                except Exception as e:
                    logger.error(f"E: {repr(e)} 链接：[{item['link']}]")
                    if item.get("count") == 3:
                        await bot.send_guild_channel_msg(
                            self_id=sid,
                            message=f"E: {repr(e)}\n{error_msg}",
                            guild_id=guild_id,
                            channel_id=channel_id,
                        )
    return flag
