import random, os, time
from nonebot import on_command
from nonebot import permission as perm
from hoshino import R, Service, priv, util

PRIV_TIP = f'群主={priv.OWNER} 群管={priv.ADMIN} 群员={priv.NORMAL} bot维护组={priv.SUPERUSER}'

sv = Service('restart',visible=True)

@sv.on_command('reboot', aliases=('重启'), only_to_me=True)
async def reboot(session):
    u_priv = priv.get_user_priv(session.ctx)
    if u_priv >= sv.manage_priv:
        await session.send('正在重启...')
        working_path = os.path.abspath(".")
        pid = os.getpid()
        cmd = '''
            mode con cols=120 lines=13
            ping 127.0.0.1 -n 2 >nul
            taskkill /pid {} /f >nul
            ping 127.0.0.1 -n 3 >nul
            powershell Start-Process -FilePath "py.exe" -ArgumentList '{}'
            '''.format(pid, os.path.join(working_path, "run.py"))
        with open(os.path.join("restart.bat"), "w") as f:
            f.write(cmd)
        #os.system("powershell Start-Process -FilePath '{}'".format(
        #    os.path.join("setposition.bat")))
        os.system("powershell Start-Process -FilePath '{}'".format(
            os.path.join("restart.bat")))
        sys.exit(10)
    else:
        await session.send('权限不足')

@sv.on_command('update', aliases=('更新'), only_to_me=True)
async def update(session):
    u_priv = priv.get_user_priv(session.ctx)
    if u_priv >= sv.manage_priv:
        await session.send('正在更新...')
        working_path = os.path.abspath(".")
        pid = os.getpid()
        cmd = '''
            mode con cols=120 lines=13
            ping 127.0.0.1 -n 2 >nul
            taskkill /pid {} /f >nul
            ping 127.0.0.1 -n 3 >nul
            git pull
            ping 127.0.0.1 -n 3 >nul
            powershell Start-Process -FilePath "py.exe" -ArgumentList '{}'
            '''.format(pid, os.path.join(working_path, "run.py"))
        with open(os.path.join("update.bat"), "w") as f:
            f.write(cmd)
        #os.system("powershell Start-Process -FilePath '{}'".format(
        #    os.path.join("setposition.bat")))
        os.system("powershell Start-Process -FilePath '{}'".format(
            os.path.join("update.bat")))
        sys.exit(10)
    else:
        await session.send('权限不足')

