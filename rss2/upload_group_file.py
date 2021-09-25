import re
import nonebot
from nonebot import on_command, CommandSession, logger
from qbittorrent import Client
from .config import config

async def get_qb(session: CommandSession):
    try:
        qb = Client(config.qb_web_url)
        qb.login()
    except Exception as e:
        msg = (
            "❌ 无法连接到 qbittorrent ，请检查：\n"
            "1. 是否启动程序\n"
            "2. 是否勾选了“Web用户界面（远程控制）”\n"
            f"3. 连接地址、端口是否正确\n{e}"
        )
        logger.error(msg)
        await session.send(msg)
        return None
    try:
        qb.get_default_save_path()
    except Exception as e:
        msg = f"❌ 无法连登录到 qbittorrent ，请检查是否勾选“对本地主机上的客户端跳过身份验证”\n{e}"
        logger.error(msg)
        await session.send(msg)
        return None
    return qb


def get_size(size: int) -> str:
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    tb = gb * 1024

    if size >= tb:
        return "%.2f TB" % float(size / tb)
    if size >= gb:
        return "%.2f GB" % float(size / gb)
    if size >= mb:
        return "%.2f MB" % float(size / mb)
    if size >= kb:
        return "%.2f KB" % float(size / kb)


# 检查下载状态
async def check_down_status(hash_str: str, group_id: int, session: CommandSession):
    qb = await get_qb(session)
    if not qb:
        return
    info = qb.get_torrent(hash_str)
    files = qb.get_torrent_files(hash_str)
    bot = nonebot.get_bot()
    if info["total_downloaded"] - info["total_size"] >= 0.000000:
        for tmp in files:
            # 异常包起来防止超时报错导致后续不执行
            try:
                if config.qb_down_path and len(config.qb_down_path) > 0:
                    path = config.qb_down_path + tmp["name"]
                else:
                    path = info["save_path"] + tmp["name"]
                await upload_group_file.send(
                    f"{tmp['name']}\n"
                    f"大小：{get_size(info['total_size'])}\n"
                    f"Hash: {hash_str}\n"
                    "开始上传"
                )
                await bot.call_action(
                    action="upload_group_file", group_id=group_id, file=path, name=tmp["name"]
                )
            except Exception:
                continue
    else:
        await session.send(
            f"Hash: {hash_str}\n"
            f"下载了 {round(info['total_downloaded'] / info['total_size'] * 100, 2)}%\n"
            f"平均下载速度：{round(info['dl_speed_avg'] / 1024, 2)} KB/s"
        )


@on_command('uploadfile', only_to_me=True)
async def upload_group_file(session: CommandSession):
    hash_str = re.search('[a-f0-9]{40}', str(session.event.message))[0]
    if session.event.message_type == 'private':
        await session.finish('请在群聊中使用哦')
    await check_down_status(hash=hash, group_id=session.event.group_id, session=session)
