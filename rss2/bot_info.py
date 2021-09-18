from typing import List

async def get_bot_qq(bot) -> List[int]:
    return bot._wsr_api_clients.keys()


async def get_bot_friend_list(bot, sid) -> List[int]:
    return list(map(lambda x: x["user_id"], await bot.get_friend_list(self_id=sid)))


async def get_bot_group_list(bot, sid) -> List[int]:
    return list(map(lambda x: x["group_id"], await bot.get_group_list(self_id=sid)))
