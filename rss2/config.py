import os
from typing import List, Any
from pydantic import AnyHttpUrl, Extra

class config:
    # 代理地址
    rss_proxy: str = '127.0.0.1:7890'
    # rsshub订阅地址
    rsshub: AnyHttpUrl = 'https://rsshub.app'
    # 备用rsshub地址 填写示例 ['https://rsshub.app','https://rsshub.app']
    rsshub_backup: List[AnyHttpUrl] = []
    
    # 缓存rss条数
    limit = 50
    
    # 图片压缩大小 kb * 1024 = MB
    zip_size: int = 2 * 1024
    gif_zip_size: int = 6 * 1024
    
    #是否显示转发的内容，默认显示转发内容(即False)
    blockquote: bool = False
    #屏蔽词填写(只要订阅包含关键词就不推送) 支持正则,看里面格式就明白怎么添加了吧(
    black_word: List[str] = []
    #例子：black_word: List[str] = ["互动抽奖", "微博抽奖平台"]

    #使用百度翻译API 可选，填的话两个都要填，不填默认使用谷歌翻译(需墙外？)
    #百度翻译接口appid和secretKey，前往http://api.fanyi.baidu.com/获取
    #一般来说申请标准版免费就够了，想要好一点可以认证上高级版，有月限额，rss用也足够了
    #可选，百度翻译接口appid，http://api.fanyi.baidu.com/获取
    baiduid: str = ''
    #可选，百度翻译接口secretKey，http://api.fanyi.baidu.com/获取
    baidukey: str = ''

    # 是否打开自动下载种子
    is_open_auto_down_torrent: bool = False
    #qbittorrent 客户端默认是关闭状态，请打开并设置端口号为 8081，同时勾选 “对本地主机上的客户端跳过身份验证”
    qb_web_url: str = 'http://127.0.0.1:8081'
    # qb的文件下载地址，这个地址必须是 go-cqhttp能访问到的
    qb_down_path: str = ''
    # 下载进度消息提示群组 示例 [12345678] 注意：最好是将该群设置为免打扰(撤回失效中...)(刷屏警告.jpg)
    down_status_msg_group: List[int] = []
    # 下载进度检查及提示间隔时间，秒，不建议小于 10s
    down_status_msg_date: int = 30

    # 去重数据库的记录清理限定天数
    db_cache_expire = 30

    # 正文长度限制，防止消息太长刷屏
    max_length: int = 0

    # 正向HTTP服务器的地址，如果不一致需自己改，否则无法上传文件到群，并且需求开启
    API_ROOT = 'http://127.0.0.1:5700'

    # 当前系统是否为Linux(自动获取)
    islinux: bool = (os.name != 'nt')
