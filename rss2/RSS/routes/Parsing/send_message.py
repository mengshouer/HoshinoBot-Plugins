import nonebot

from nonebot import logger

from ....RSS import rss_class


# 发送消息
async def send_msg(rss: rss_class.Rss, msg: str, item: dict) -> bool:
    bot = nonebot.get_bot()
    flag = False
    if not msg:
        return False
    if rss.user_id:
        for user_id in rss.user_id:
            try:
                await bot.send_msg(
                    message_type="private", user_id=user_id, message=str(msg)
                )
                flag = True
            except Exception as e:
                logger.error(f'发送QQ号[{user_id}]错误！ E: {e}')

    if rss.group_id:
        for group_id in rss.group_id:
            try:
                await bot.send_msg(
                    message_type="group", group_id=group_id, message=str(msg)
                )
                flag = True
            except Exception as e:
                logger.error(f'发送QQ号[{user_id}]错误！ E: {e}')
    return flag
