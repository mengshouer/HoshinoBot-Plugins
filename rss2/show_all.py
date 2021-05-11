from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class

@on_command('showall', aliases=('selectall','所有订阅'), permission=GROUP_ADMIN|SUPERUSER)
async def rssShowAll(session: CommandSession):
    user_id = session.ctx['user_id']
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None

    rss = rss_class.Rss("", "", "-1", "-1")
    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.send('当前群组没有任何订阅！')
            return
    else:
        rss_list = rss.read_rss()
    if rss_list:
        if len(rss_list) == 1:
            await session.send(str(rss_list[0]))
        else:
            flag = 0
            info = ""
            for rss_tmp in rss_list:
                if flag % 5 == 0 and flag != 0:
                    await session.send(str(info[:-2]))
                    info = ""
                info += "Name：{}\nURL：{}\n\n".format(rss_tmp.name, rss_tmp.url)
                flag += 1
            await session.send(info + '共 {} 条订阅'.format(flag))

    else:
        await session.send('当前没有任何订阅！')
