import re
from nonebot import on_command, CommandSession
from nonebot.permission import *
from nonebot import scheduler
from nonebot.log import logger

from .RSS import rss_class
from .RSS import my_trigger as tr

helpmsg ='''请输入要修改的订阅
订阅名 属性=,值
如:
test qq=,123,234 qun=-1
对应参数:
订阅链接-url QQ-qq 群-qun 更新频率-time
代理-proxy 翻译-tl 仅title-ot，仅图片-op
下载种子-downopen 白名单关键词-wkey 黑名单关键词-bkey 种子上传到群-upgroup
去重模式-mode
图片数量限制-img_num 最多一条消息只会发送指定数量的图片，防止刷屏
注：
proxy、tl、ot、op、downopen、upgroup 值为 1/0
去重模式分为按链接(link)、标题(title)、图片(image)判断
其中 image 模式,出于性能考虑以及避免误伤情况发生,生效对象限定为只带 1 张图片的消息,
此外,如果属性中带有 or 说明判断逻辑是任一匹配即去重,默认为全匹配    
白名单关键词支持正则表达式，匹配时推送消息及下载，设为空(wkey=)时不生效
黑名单关键词同白名单一样，只是匹配时不推送，两者可以一起用
QQ、群号、去重模式前加英文逗号表示追加,-1设为空
各个属性空格分割
详细：https://oy.mk/ckL'''.strip()

# 处理带多个值的订阅参数
def handle_property(value: str, property_list: list) -> list:
    # 清空
    if value == '-1':
        return []
    value_list = value.split(',')
    # 追加
    if value_list[0] == "":
        value_list.pop(0)
        return property_list + [
            i for i in value_list if i not in property_list
        ]
    # 防止用户输入重复参数,去重并保持原来的顺序
    return list(dict.fromkeys(value_list))


attribute_dict = {
    'qq': 'user_id',
    'qun': 'group_id',
    'url': 'url',
    'time': 'time',
    'proxy': 'img_proxy',
    'tl': 'translation',
    'ot': 'only_title',
    'op': 'only_pic',
    'upgroup': 'is_open_upload_group',
    'downopen': 'down_torrent',
    'downkey': 'down_torrent_keyword',
    'wkey': 'down_torrent_keyword',
    'blackkey': 'black_keyword',
    'bkey': 'black_keyword',
    'mode': 'duplicate_filter_mode',
    'img_num': 'max_image_number'
}


# 处理要修改的订阅参数
def handle_change_list(rss: rss_class.Rss, key_to_change: str,
                       value_to_change: str, group_id: int):
    # 暂时禁止群管理员修改 QQ / 群号，如要取消订阅可以使用 deldy 命令
    if (key_to_change in ['qq', 'qun']
            and not group_id) or key_to_change == 'mode':
        value_to_change = handle_property(
            value_to_change, getattr(rss, attribute_dict[key_to_change]))
    elif key_to_change == 'url':
        rss.delete_file()
    elif key_to_change == 'time':
        if not re.search(r'[_*/,-]', value_to_change):
            if int(float(value_to_change)) < 1:
                value_to_change = '1'
            else:
                value_to_change = str(int(float(value_to_change)))
    elif key_to_change in ['proxy', 'tl', 'ot', 'op', 'upgroup', 'downopen']:
        value_to_change = bool(int(value_to_change))
    elif key_to_change in ['downkey', 'wkey', 'blackkey', 'bkey'] and len(
            value_to_change.strip()) == 0:
        value_to_change = None
    elif key_to_change == 'img_num':
        value_to_change = int(value_to_change)
    setattr(rss, attribute_dict.get(key_to_change), value_to_change)

@on_command('change', aliases=('修改订阅', 'moddy'), permission=GROUP_ADMIN|SUPERUSER)
async def change(session: CommandSession):
    change_info = session.get('change', prompt=helpmsg)
    try:
        group_id = session.ctx['group_id']
    except:
        group_id = None
    change_list = change_info.split(' ')

    name = change_list[0]
    change_list.pop(0)
    rss = rss_class.Rss(name, '', '-1', '-1')
    if not rss.find_name(name=name):
        await session.send(f'❌ 订阅 {name} 不存在！')
        return

    rss = rss.find_name(name=name)
    if group_id and str(group_id) not in rss.group_id:
        await session.send(f'❌ 修改失败，当前群组无权操作订阅：{rss.name}')
        return

    try:
        for change_dict in change_list:
            key_to_change, value_to_change = change_dict.split('=', 1)
            if key_to_change in attribute_dict.keys():
                # 对用户输入的去重模式参数进行校验
                mode_property_set = {'', '-1', 'link', 'title', 'image', 'or'}
                if key_to_change == 'mode' and (
                        set(value_to_change.split(',')) - mode_property_set
                        or value_to_change == 'or'):
                    await session.send(f'❌ 去重模式参数错误！\n{change_dict}')
                    return
                handle_change_list(rss, key_to_change, value_to_change,
                                   group_id)
            else:
                await RSS_CHANGE.send(f'❌ 参数错误或无权修改！\n{change_dict}')
                return
        # 参数解析完毕，写入
        rss.write_rss()
        # 加入定时任务
        await tr.add_job(rss)
        if group_id:
            # 隐私考虑，群组下不展示除当前群组外的群号和QQ
            # 奇怪的逻辑，群管理能修改订阅消息，这对其他订阅者不公平。
            rss.group_id = [str(group_id), '*']
            rss.user_id = ['*']
        await session.send(f'👏 修改成功\n{rss}')
        logger.info(f'👏 修改成功\n{rss}')

    except Exception as e:
        await session.send(f'❌ 参数解析出现错误！\nE: {e}')
        logger.error(f'❌ 参数解析出现错误！\nE: {e}')
        raise


@change.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            session.state['change'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的订阅（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('输入不能为空！')

    # 如果当前正在向用户询问更多信息，且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg