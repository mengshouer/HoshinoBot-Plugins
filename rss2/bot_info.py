from typing import List, Optional


async def get_bot_qq(bot) -> List[int]:
    return bot._wsr_api_clients.keys()


async def get_bot_friend_list(sid, bot) -> List[int]:
    friend_list = await bot.get_friend_list(self_id=sid)
    return [i["user_id"] for i in friend_list]


async def get_bot_group_list(sid, bot) -> List[int]:
    group_list = await bot.get_group_list(self_id=sid)
    return [i["group_id"] for i in group_list]


async def get_bot_guild_channel_list(
    sid, bot, guild_id: Optional[str] = None
) -> List[str]:
    guild_list = await bot.get_guild_list(self_id=sid)
    if guild_id is None:
        return [i["guild_id"] for i in guild_list]
    else:
        if guild_id in [i["guild_id"] for i in guild_list]:
            channel_list = await bot.get_guild_channel_list(
                self_id=sid, guild_id=guild_id
            )
            return [i["channel_id"] for i in channel_list]
    return []
