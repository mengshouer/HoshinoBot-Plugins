from nonebot import on_command, CommandSession, scheduler
from .RSSHub import rsshub
from .RSSHub import RSS_class
from .RSSHub import RWlist
from .RSSHub import rsstrigger as TR
import logging
from nonebot.log import logger
import nonebot
from apscheduler.triggers.interval import IntervalTrigger # 间隔触发器
from nonebot.permission import *
import copy as cp
# 存储目录
file_path = './data/'

# on_command 装饰器将函数声明为一个命令处理器
# 这里 uri 为命令的名字，同时允许使用别名
@on_command('clearrss', aliases=('cleardy','rssclear') permission=GROUP_ADMIN|SUPERUSER)
async def cleargroup(session: CommandSession):
    bot = session.bot
    try:
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            gl = await bot.get_group_list(self_id=sid)
            gl = [ "{group_id}".format_map(g) for g in gl ]
    except BaseException as e:
        await bot.send("Error!"+str(e))
        return
    
    try:
        list_rss = RWlist.readRss()
        for rss_ in list_rss:
            if rss_.group_id:
                rss_tmp = cp.deepcopy(rss_)
                i,g = 0,0
                while g < len(rss_.group_id):
                    if rss_.group_id[g] not in gl:
                        rss_tmp.group_id.remove(rss_.group_id[g])
                        i += 1
                    g += 1
                if i:
                    await session.send(f'{rss_.name}此次成功清理{i}个群聊！')
                if not rss_tmp.group_id and not rss_tmp.user_id:
                    list_rss.remove(rss_)
                    scheduler.remove_job(rss_.name)
                    try:
                        os.remove(file_path+rss_.name+".json")
                        logger.info(f"订阅{rss_.name}已无订阅目标，删除整个订阅")
                    except BaseException as e:
                        logger.info(e)
                        logger.info(f"订阅{rss_.name}已无订阅目标，删除整个订阅失败！")
                    RWlist.writeRss(list_rss)
                else:
                    list_rss.remove(rss_)
                    list_rss.append(rss_tmp)
                    RWlist.writeRss(list_rss)
    except BaseException as e:
        #logger.info(e)
        await session.send('你还没有任何订阅！')
