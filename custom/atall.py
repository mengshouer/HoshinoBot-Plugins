from hoshino import Service, MessageSegment

sv_help = """
让群员使用bot来@全体成员，前提bot得有管理员(叫人用
只要前缀为"@全员"就触发，默认关闭
""".strip()
sv = Service("atall", enable_on_default=False)


@sv.on_prefix("@全员")
async def atall(bot, ev):
    try:
        msg = ev.message.extract_plain_text()
        msg = f"{MessageSegment.at('all')} {msg}"
        await bot.send(ev, msg)
        # 一个一个群员进行@，慎用
        # try:
        #     await bot.send(ev, msg)
        # except:
        #     try:
        #         m = await bot.get_group_member_list(group_id=ev.group_id)
        #         msg = ""
        #         for i in range(0, len(m)):
        #             u = m[i]["user_id"]
        #             if u != ev.self_id:
        #                 msg += f"{MessageSegment.at(u)} "
        #         msg += ev.message.extract_plain_text()
        #         await bot.send(ev, msg)
        #     except:
        #         await bot.send(ev, "at all send fail!!!")
    except:
        # 可能发送内容被风控，只发送@全体成员
        await bot.send(ev, MessageSegment.at("all"))
