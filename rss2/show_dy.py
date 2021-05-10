from nonebot import on_command, CommandSession
from nonebot.permission import *

from .RSS import rss_class

# 不带订阅名称默认展示当前群组或账号的订阅
# 带订阅名称就显示该订阅的
@on_command('show', aliases=('查看订阅'), permission=GROUP_ADMIN|SUPERUSER)
async def rssShow(session: CommandSession):
    args = session.current_arg.strip()
    if args:
        rss_name = args
    else:
        rss_name = None
    user_id = session.ctx['user_id']
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None

    rss = rss_class.Rss('', '', '-1', '-1')

    if rss_name:
        rss = rss.find_name(str(rss_name))
        if not rss:
            await session.send('❌ 订阅 {} 不存在！'.format(rss_name))
            return
        if group_id:
            # 隐私考虑，群组下不展示除当前群组外的群号和QQ
            if not str(group_id) in rss.group_id:
                await session.send('❌ 当前群组未订阅 {} '.format(rss_name))
                return
            rss.group_id = [str(group_id), '*']
            rss.user_id = ['*']
        await session.send(str(rss))
        return

    if group_id:
        rss_list = rss.find_group(group=str(group_id))
        if not rss_list:
            await session.send('❌ 当前群组没有任何订阅！')
            return
    else:
        rss_list = rss.find_user(user=str(user_id))
    if rss_list:
        if len(rss_list) == 1:
            await session.send(str(rss_list[0]))
        else:
            flag = 0
            info = ''
            for rss_tmp in rss_list:
                if flag % 5 == 0 and flag != 0:
                    await session.send(str(info))
                    info = ''
                info += 'Name：{}\nURL：{}\n\n'.format(rss_tmp.name, rss_tmp.url)
                flag += 1
            await session.send(info+'共 {} 条订阅'.format(flag))

    else:
        await session.send('❌ 当前没有任何订阅！')