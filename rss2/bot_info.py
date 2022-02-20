from typing import List


async def get_bot_qq(bot) -> List[int]:
    return bot._wsr_api_clients.keys()


async def get_bot_friend_list(bot, sid) -> List[int]:
    friend_list = await bot.get_friend_list(self_id=sid)
    return [i["user_id"] for i in friend_list]


async def get_bot_group_list(bot, sid) -> List[int]:
    group_list = await bot.get_group_list(self_id=sid)
    return [i["group_id"] for i in group_list]


async def get_bot_guild_channel_list(bot, guild_id: str = None) -> List[str]:
    if guild_id is None:
        guild_list = await bot.get_guild_list()
        return [i["guild_id"] for i in guild_list]
    else:
        guild_list = await bot.get_guild_list()
        if guild_id in [i["guild_id"] for i in guild_list]:
            channel_list = await bot.get_guild_channel_list(guild_id=guild_id)
            return [i["channel_id"] for i in channel_list]
        else:
            return []
