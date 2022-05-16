from nonebot import SenderRoles
from .config import config


def admin_permission(sender: SenderRoles):
    return (
        sender.is_superuser
        or sender.is_admin
        or sender.is_owner
        or sender.sent_by(config.guild_superusers)
    )

