import psutil
from nonebot.argparse import ArgumentParser
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER

USAGE = r"""
USAGE: status [OPTIONS] 

OPTIONS：
    -h, --help    显示本使用帮助
    -a, --all     显示所有信息
    -m, --memory  显示内存信息
    -d, --disk    显示硬盘信息
    -c, --cpu     显示cpu信息
""".strip()


@on_command("status", permission=SUPERUSER, only_to_me=False, shell_like=True)
async def get_status(session: CommandSession):
    parser = ArgumentParser(session=session, usage=USAGE)
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-m", "--memory", action="store_true")
    parser.add_argument("-d", "--disk", action="store_true")
    parser.add_argument("-c", "--cpu", action="store_true")
    args = parser.parse_args(session.argv)
    if args.all:
        memory_info = await memory_status()
        cpu_info = await cpu_status()
        disk_info = await disk_status()
        msg = str(disk_info) + "\n" + str(cpu_info) + "\n" + str(memory_info)
        await session.finish(str(msg))
    elif args.memory:
        msg = await memory_status()
        await session.finish(str(msg))
    elif args.disk:
        msg = await disk_status()
        await session.finish(str(msg))
    elif args.cpu:
        msg = await cpu_status()
        await session.finish(str(msg))
    else:
        await session.finish(USAGE)


async def memory_status():
    virtual_memory = psutil.virtual_memory()
    used_memory = virtual_memory.used / 1024 / 1024 / 1024
    free_memory = virtual_memory.free / 1024 / 1024 / 1024
    memory_percent = virtual_memory.percent
    msg = "内存使用：%0.2fG，使用率%0.1f%%，剩余内存：%0.2fG" % (
        used_memory,
        memory_percent,
        free_memory,
    )
    return msg


async def cpu_status():
    cpu_percent = psutil.cpu_percent(interval=1)
    msg = "CPU使用率：%i%%" % cpu_percent
    return msg


async def disk_status():
    content = ""
    for disk in psutil.disk_partitions():
        # 读写方式 光盘 or 有效磁盘类型
        if "cdrom" in disk.opts or disk.fstype == "":
            continue
        disk_name_arr = disk.device.split(":")
        disk_name = disk_name_arr[0]
        disk_info = psutil.disk_usage(disk.device)
        # 磁盘剩余空间，单位G
        free_disk_size = disk_info.free // 1024 // 1024 // 1024
        # 当前磁盘使用率和剩余空间G信息
        info = "%s盘使用率：%s%%， 剩余空间：%iG" % (
            disk_name,
            str(disk_info.percent),
            free_disk_size,
        )
        # print(info)
        # 拼接多个磁盘的信息
        content = content + info + "\n"
    msg = content[:-1]
    return msg
