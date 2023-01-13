import base64
import functools
import math
import re
from contextlib import suppress
from typing import Any, Dict, List, Mapping, Optional, Tuple

from cachetools import TTLCache
from cachetools.keys import hashkey
import nonebot
from nonebot.log import logger
from .config import config


def get_http_caching_headers(
    headers: Optional[Mapping[str, Any]],
) -> Dict[str, Optional[str]]:
    return (
        {
            "Last-Modified": headers.get("Last-Modified") or headers.get("Date"),
            "ETag": headers.get("ETag"),
        }
        if headers
        else {"Last-Modified": None, "ETag": None}
    )


def convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def cached_async(cache, key=hashkey):  # type: ignore
    """
    https://github.com/tkem/cachetools/commit/3f073633ed4f36f05b57838a3e5655e14d3e3524
    """

    def decorator(func):  # type: ignore
        if cache is None:

            async def wrapper(*args, **kwargs):  # type: ignore
                return await func(*args, **kwargs)

        else:

            async def wrapper(*args, **kwargs):  # type: ignore
                k = key(*args, **kwargs)
                with suppress(KeyError):  # key not found
                    return cache[k]
                v = await func(*args, **kwargs)
                with suppress(ValueError):  # value too large
                    cache[k] = v
                return v

        return functools.update_wrapper(wrapper, func)

    return decorator


def get_bot_qq(bot) -> List[int]:
    return bot._wsr_api_clients.keys()


@cached_async(TTLCache(maxsize=1, ttl=300))  # type: ignore
async def get_bot_friend_list(bot) -> Tuple[List[int], Dict[int, List[int]]]:
    bot_qq = list(get_bot_qq(bot))
    all_friends = {}
    friend_list = []
    for sid in bot_qq:
        f = await bot.get_friend_list(self_id=sid)
        all_friends[sid] = [i["user_id"] for i in f]
        friend_list.extend(all_friends[sid])
    return set(friend_list), all_friends


@cached_async(TTLCache(maxsize=1, ttl=300))  # type: ignore
async def get_bot_group_list(bot) -> Tuple[List[int], Dict[int, List[int]]]:
    bot_qq = list(get_bot_qq(bot))
    all_groups = {}
    group_list = []
    for sid in bot_qq:
        g = await bot.get_group_list(self_id=sid)
        all_groups[sid] = [i["group_id"] for i in g]
        group_list.extend(all_groups[sid])
    return set(group_list), all_groups


@cached_async(TTLCache(maxsize=1, ttl=300))  # type: ignore
async def get_all_bot_guild_list(bot) -> Tuple[List[int], Dict[int, List[str]]]:
    bot_qq = list(get_bot_qq(bot))
    # 获取频道列表
    all_guilds = {}
    guild_list = []
    for sid in bot_qq:
        g = await bot.get_guild_list(self_id=sid)
        all_guilds[sid] = [i["guild_id"] for i in g]
        guild_list.extend(all_guilds[sid])
    return set(guild_list), all_guilds


@cached_async(TTLCache(maxsize=1, ttl=300))  # type: ignore
async def get_all_bot_channel_list(bot) -> Tuple[List[str], Dict[int, List[str]]]:
    guild_list, all_guilds = await get_all_bot_guild_list(bot)
    # 获取子频道列表
    all_channels = {}
    channel_list = []
    for guild in guild_list:
        sid = [k for k, v in all_guilds.items() if guild in v][0]
        c = await bot.get_guild_channel_list(self_id=sid, guild_id=guild)
        all_channels[sid] = [i["channel_id"] for i in c]
        channel_list.extend(all_channels[sid])
    return set(channel_list), all_channels


@cached_async(TTLCache(maxsize=1, ttl=300))  # type: ignore
async def get_bot_guild_channel_list(bot, guild_id: Optional[str] = None) -> List[str]:
    guild_list, all_guilds = await get_all_bot_guild_list(bot)
    if guild_id is None:
        return guild_list
    if guild_id in guild_list:
        # 获取子频道列表
        sid = [k for k, v in all_guilds.items() if guild_id in v][0]
        channel_list = await bot.get_guild_channel_list(self_id=sid, guild_id=guild_id)
        return [i["channel_id"] for i in channel_list]
    return []


def get_torrent_b16_hash(content: bytes) -> str:
    import magneturi

    # mangetlink = magneturi.from_torrent_file(torrentname)
    manget_link = magneturi.from_torrent_data(content)
    # print(mangetlink)
    ch = ""
    n = 20
    b32_hash = n * ch + manget_link[20:52]
    # print(b32Hash)
    b16_hash = base64.b16encode(base64.b32decode(b32_hash))
    b16_hash = b16_hash.lower()
    # print("40位info hash值：" + '\n' + b16Hash)
    # print("磁力链：" + '\n' + "magnet:?xt=urn:btih:" + b16Hash)
    return str(b16_hash, "utf-8")


async def send_message_to_admin(message: str, bot=nonebot.get_bot()) -> None:
    await bot.send_private_msg(user_id=str(list(config.superusers)[0]), message=message)


async def send_msg(
    msg: str,
    user_ids: Optional[List[str]] = None,
    group_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    msg: str
    user: List[str]
    group: List[str]

    发送消息到私聊或群聊
    """
    bot = nonebot.get_bot()
    msg_id = []
    if group_ids:
        for group_id in group_ids:
            msg_id.append(await bot.send_group_msg(group_id=int(group_id), message=msg))
    if user_ids:
        for user_id in user_ids:
            msg_id.append(await bot.send_private_msg(user_id=int(user_id), message=msg))
    return msg_id


# 校验正则表达式合法性
def regex_validate(regex: str) -> bool:
    try:
        re.compile(regex)
        return True
    except re.error:
        return False


# 过滤合法好友
async def filter_valid_user_id_list(bot, user_id_list: List[str]) -> List[str]:
    friend_list, _ = await get_bot_friend_list(bot)
    valid_user_id_list = [
        user_id for user_id in user_id_list if int(user_id) in friend_list
    ]
    if invalid_user_id_list := [
        user_id for user_id in user_id_list if user_id not in valid_user_id_list
    ]:
        logger.warning(f"QQ号[{','.join(invalid_user_id_list)}]不是Bot[{bot.self_id}]的好友")
    return valid_user_id_list


# 过滤合法群组
async def filter_valid_group_id_list(bot, group_id_list: List[str]) -> List[str]:
    group_list, _ = await get_bot_group_list(bot)
    valid_group_id_list = [
        group_id for group_id in group_id_list if int(group_id) in group_list
    ]
    if invalid_group_id_list := [
        group_id for group_id in group_id_list if group_id not in valid_group_id_list
    ]:
        logger.warning(f"Bot[{bot.self_id}]未加入群组[{','.join(invalid_group_id_list)}]")
    return valid_group_id_list


# 过滤合法频道
async def filter_valid_guild_channel_id_list(
    bot, guild_channel_id_list: List[str]
) -> List[str]:
    valid_guild_channel_id_list = []
    for guild_channel_id in guild_channel_id_list:
        guild_id, channel_id = guild_channel_id.split("@")
        guild_list = await get_bot_guild_channel_list(bot)
        if guild_id not in guild_list:
            guild_name = (await bot.get_guild_meta_by_guest(guild_id=guild_id))[
                "guild_name"
            ]
            logger.warning(f"Bot[{bot.self_id}]未加入频道 {guild_name}[{guild_id}]")
            continue

        channel_list = await get_bot_guild_channel_list(bot, guild_id=guild_id)
        if channel_id not in channel_list:
            guild_name = (await bot.get_guild_meta_by_guest(guild_id=guild_id))[
                "guild_name"
            ]
            logger.warning(
                f"Bot[{bot.self_id}]未加入频道 {guild_name}[{guild_id}]的子频道[{channel_id}]"
            )
            continue
        valid_guild_channel_id_list.append(guild_channel_id)
    return valid_guild_channel_id_list
