"""
这是一份rss配置文件
"""

# ------RSS------
# 图片压缩大小 kb * 1024 = MB
ZIP_SIZE = 3 * 1024
appid = ""  # 可选，百度翻译接口appid，http://api.fanyi.baidu.com/获取
secretKey = ""  # 可选，百度翻译接口secretKey，http://api.fanyi.baidu.com/获取

showBlockword = True  # 是否显示内含屏蔽词的信息信息，默认打开
Blockword = ["互动抽奖", "微博抽奖平台"]  # 屏蔽词填写 支持正则,看里面格式就明白怎么添加了吧(

blockquote = True  # 是否显示转发的内容(主要是微博)，默认打开，如果关闭还有转发的信息的话，可以自行添加进屏蔽词(但是这整条消息就会没)
API_ROOT = "http://127.0.0.1:5700"
RSS_PROXY = "127.0.0.1:10809"  # 代理地址
###废弃ROOTUSER,只使用SUPERUSERS
# ROOTUSER = []    # 管理员qq,支持多管理员，逗号分隔 如 [1,2,3] 注意
RSSHUB = "https://rsshub.app"  # rsshub订阅地址
RSSHUB_backup = []  # 备用rsshub地址 填写示例 ['https://rsshub.app','https://rsshub.app']
# 群组订阅的默认参数
add_uptime = 10  # 默认订阅更新时间
add_proxy = False  # 默认是否启用代理

DELCACHE = 3  # 缓存删除间隔 天
LIMT = 50  # 缓存rss条数

# 解决pixiv.cat无法访问问题
CLOSE_PIXIV_CAT = False  # 是否关闭使用 pixiv.cat，关闭后必须启用代理
# 以下两项在关闭使用 pixiv.cat时有效，如果你有自己反代pixiv，填上你自己的反代服务器地址即可，没有不要填
PIXIV_REFERER = "http://www.pixiv.net"  # 请求头 referer 设置
PIXIV_PROXY = "http://pixivic.com"  # 反代图片服务器地址
# 此处推荐一个反代网站 http://pixivic.com   original.img.cheerfun.dev
IsLinux = False
# ------RSS------
