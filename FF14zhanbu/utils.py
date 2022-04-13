import csv
import datetime
import hashlib
import random
from pathlib import Path
import json

PATH_Astrologian = Path(__file__).parent.absolute()

EVENT_LIST: list = []

EVENT_LIST_CONTENT: dict = {}

war, magic, land, hand, stains = [], [], [], [], []


async def initialization():
    global war, magic, land, hand, stains, EVENT_LIST_CONTENT, EVENT_LIST
    # create constant vars
    war, magic, land, hand = await get_jobs()
    stains = await get_stain()
    EVENT_LIST_CONTENT = await _get_event()
    EVENT_LIST = list(EVENT_LIST_CONTENT.keys())


# 读取职业列表，计划返回4组list
async def get_jobs() -> tuple:
    war_jobs = []
    magic_jobs = []
    land_jobs = []
    hand_jobs = []
    with open(PATH_Astrologian / "data" / "ClassJob.csv", mode="r", encoding="utf-8") as f:
        jobs_csv = csv.reader(f)
        for job in jobs_csv:
            if job[4] == "战斗精英":
                if job[1] == job[39].split("之")[0]:
                    # print(job[1])
                    war_jobs.append(job[1])
            elif job[4] == "魔法导师":
                if job[1] == job[39].split("之")[0]:
                    # print(job[1])
                    magic_jobs.append(job[1])
            elif job[4] == "能工巧匠":
                hand_jobs.append(job[1])
            elif job[4] == "大地使者":
                land_jobs.append(job[1])
    return war_jobs, magic_jobs, land_jobs, hand_jobs


# 读取染剂列表
async def get_stain() -> list:
    stains = []
    with open(PATH_Astrologian / "data" / "StainTransient.csv", mode="r", encoding="utf-8") as f:
        stains_csv = csv.reader(f)
        for stain in stains_csv:
            if "染剂" in stain[1]:
                # print(stain[1])
                stains.append(stain[1])
    return stains


# 读取事件列表，以及对应一言
async def _get_event() -> dict:
    with open(PATH_Astrologian / "data" / "events.json", mode="r", encoding="utf-8") as f:
        events = json.load(f)

    # 每个event有一个组list，其中按从大到小顺序储存了对应的一言，默认luck为50，unluck为0
    # 为了后续判断，请将luck_event的数字满足 50<=num<=100; 而unluck满足 0<=num<50
    return events


# 特殊职业创建特殊语句
async def sub_event(key: str) -> str:
    if key == "舞者":
        partner = war + magic
        return key + "--> 最佳舞伴: " + random.choice(partner)
    else:
        return key


# copy from https://github.com/Bluefissure/OtterBot
# 针对每个qq用户，通过QQ号和日期生成一个种子
async def get_seed(qq_num: int) -> int:
    # 众所周知ff14玩家的一天从国内23:00开始
    utc_today = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    ffxiv_today = utc_today.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

    formatted_ffxiv_today = int(ffxiv_today.strftime('%y%m%d'))
    str_num = str(formatted_ffxiv_today * qq_num)

    md5 = hashlib.md5()
    md5.update(str_num.encode('utf-8'))
    res = md5.hexdigest()

    return int(res.upper(), 16) % 100 + 1


# 通过传入的参数来确定一言
async def get_hint(luck_number: str, luck_job: str, luck_event: str, unlucky_event: str, stain: str) -> str:
    luck_number = int(luck_number)
    # 根据一些特殊值生成语句
    special_event: str = ""
    if luck_number > 95:
        special_event += "是欧皇(*′▽｀)ノノ\n"
    elif luck_number < 5:
        special_event += "是非酋︿(￣︶￣)︿\n"
    elif luck_job == "占星术士":
        if luck_number > 80:
            special_event += "你抽卡必定日月星三连(￣︶￣)\n"
        elif luck_number < 20:
            special_event += "即使同色，也要勇敢的挑战命运ヾ(◍°∇°◍)ﾉﾞ\n"
    elif luck_job == "忍者":
        if luck_number > 70:
            special_event += "Duang Duang Duang 天地人一气呵成\n"
        elif luck_number < 20:
            special_event += "兔兔在头顶的样子很可爱的(✺ω✺)"

    if luck_number >= 50:
        events = EVENT_LIST_CONTENT[luck_event]
    else:
        events = EVENT_LIST_CONTENT[unlucky_event]

    # 根据每个event储存的一组list，来选择返回一言，要求达到第一个小于luck_number(运势)的值跳出
    event_content = ""
    for content in events:
        if content[0] <= luck_number:
            event_content = content[1]
            break
    if event_content == "":
        event_content = "诶诶，咱没有料到呢？肯定是笨蛋梦魇偷懒了[○･｀Д´･ ○]"
    return special_event + event_content


async def luck_daily(user_id: int, redraw: bool = False, group_message: bool = True) -> str:
    """
    :param user_id caller's QQ
    :param redraw make other result if True
    :param group_message create a different return if True
    :return message that send to caller
    """

    if len(war or magic or land or hand or stains) == 0:
        await initialization()

    # 生成当天种子, 重抽判断
    r = random.Random(await get_seed(user_id * (user_id if redraw else 1)))
    # content
    # @QQ 不需要，nonebot有命令
    # at = "[CQ:at,qq=%s]" % caller_qq_number
    # 运势 1-100
    luck_number: str = str(r.randint(1, 100))
    # 职业 ff14全部职业
    luck_job: str = await sub_event(str(r.choice(war + magic + land + hand)))
    # 宜
    luck_event = r.choice(EVENT_LIST)
    # 忌
    unlucky_event_list: list = EVENT_LIST.copy()
    unlucky_event_list.remove(luck_event)
    unlucky_event: str = r.choice(unlucky_event_list)
    # 宜忌互锁 诸事 与 无
    if luck_event == "诸事":
        unlucky_event = "无"
    elif unlucky_event == "诸事":
        luck_event = "无"
    # 染剂
    stain: str = r.choice(stains)
    # 一言
    hint: str = await get_hint(luck_number, luck_job, luck_event, unlucky_event, stain)
    # 群消息特殊化
    if group_message:
        message: str = "\n运势: " + luck_number + "%  幸运职业: " + luck_job + \
                       "\n宜: " + luck_event + "  忌: " + unlucky_event + "  幸运染剂: " + stain + "\n" + hint
    else:
        message: str = "运势: " + luck_number + \
                       "%\n幸运职业: " + luck_job + \
                       "\n宜: " + luck_event + "  忌: " + unlucky_event + "\n幸运染剂: " + stain + "\n" + hint

    # print(r.randint(0, len(EVENT_LIST) - 2))

    return message
