from nonebot.permission import *
from .config import config


def admin_permission(sender) -> bool:
    return bool(
        SUPERUSER
        or GROUP_OWNER
        or GROUP_ADMIN
        or config.guild_superusers
    )
