import time
from nonebot import on_command, CommandSession

@on_command('/ping', only_to_me=False)
async def ping(session: CommandSession):
    time_from_receive = session.event['time']
    if time_from_receive > 3000000000:
        time_from_receive = time_from_receive / 1000
    session.finish("->"+str(time.time() - time_from_receive)+"s", at_sender=True)
