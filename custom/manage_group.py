import nonebot
from nonebot.argparse import ArgumentParser
from nonebot import on_command, CommandSession
from hoshino.typing import NoticeSession
from nonebot.permission import SUPERUSER

USAGE = r"""
USAGE: group [OPTIONS] 

OPTIONS：
    -h, --help  显示本使用帮助
    -ls, --list  显示群列表
    -l <group_id>, --leave <group_id>  退出某个群聊
""".strip()

@on_command('group', permission=SUPERUSER, only_to_me=False, shell_like=True)
async def set_group(session: CommandSession):
    parser = ArgumentParser(session=session, usage=USAGE)
    parser.add_argument('-ls', '--list', action='store_true')
    parser.add_argument('-l', '--leave', type=int, default=0)
    args = parser.parse_args(session.argv)
    if args.list:
        await ls_group(session)
    elif args.leave:
        gid = args.leave
        await leave_group(session, gid)
    else:
        await session.finish(USAGE)

async def ls_group(session: CommandSession):
    bot = session.bot
    self_ids = bot._wsr_api_clients.keys()
    for sid in self_ids:
        gl = await bot.get_group_list(self_id=sid)
        msg = [ "{group_id} {group_name}".format_map(g) for g in gl ]
        msg = "\n".join(msg)
        msg = f"bot:{sid}\n| 群号 | 群名 | 共{len(gl)}个群\n" + msg
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=msg)

async def leave_group(session: CommandSession, gid:int):
    if session.ctx['user_id'] in session.bot.config.SUPERUSERS:
        if not gid:
            session.finish(USAGE)
    else:
        return
    await session.bot.set_group_leave(group_id=gid)



