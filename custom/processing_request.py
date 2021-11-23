from nonebot import on_request, RequestSession, on_command, CommandSession
from nonebot.permission import SUPERUSER, check_permission

try:
    from hoshino import config

    flag = 1
except:
    flag = 0

if flag:
    send_msg_user = config.SUPERUSERS[0]
else:
    # 消息提醒发送的用户，不填默认使用hoshino配置的第一个管理员
    # 如果没有hoshino，必须修改下面的0为推送的QQ号
    send_msg_user = 0

# 默认同意好友的群配置，如果申请的人在下列群里，默认同意好友请求
allow_group = []  # [123, 234, 567]


@on_request("friend")
async def friend_req(session: RequestSession):
    userlist = []
    hasgroup = await session.bot.get_group_list()
    hasgroup = [i["group_id"] for i in hasgroup]
    for g in range(0, len(allow_group)):
        if allow_group[g] in hasgroup:
            m = await session.bot.get_group_member_list(group_id=allow_group[g])
            for i in range(0, len(m)):
                u = m[i]["user_id"]
                userlist.append(u)
    if session.event.user_id in userlist:
        await session.approve()
        await session.bot.send_msg(
            message_type="private",
            user_id=send_msg_user,
            message=f"已同意{session.event.user_id}的好友请求！",
        )
    else:
        global flag
        if flag != session.event.flag:
            await session.bot.send_msg(
                message_type="private",
                user_id=send_msg_user,
                message=f"获取到{session.event.user_id} -> {session.self_id}好友请求\n同意好友请求：/approve friend {session.event.flag}",
            )
        flag = session.event.flag


@on_request("group.invite")
async def group_invite(session: RequestSession):
    if await check_permission(session.bot, session.event, SUPERUSER):
        await session.bot.set_group_add_request(
            flag=session.event.flag, sub_type="invite", approve=True
        )
    else:
        await session.bot.send_msg(
            message_type="private",
            user_id=send_msg_user,
            message=f"获取到{session.event.user_id} -> {session.event.group_id}({session.self_id})群请求\n同意群请求：/approve group {session.event.flag}",
        )


@on_command("/approve", permission=SUPERUSER)
async def processing_request(session: CommandSession):
    args = session.current_arg.strip()
    args = args.split(" ")
    if len(args) == 1:
        await session.send("格式错误！例：/approve friend/group (flag)")
        return
    t = args[0]
    flag = args[1]
    if t == "friend":
        await session.bot.call_action(
            action="set_friend_add_request", flag=flag, approve=True
        )
    elif t == "group":
        await session.bot.call_action(
            action="set_group_add_request", flag=flag, approve=True, sub_type="invite"
        )
    await session.finish("请求已处理！")
