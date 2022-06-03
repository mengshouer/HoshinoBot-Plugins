import os

from typing import Optional
from pydantic import BaseSettings

path = os.path.split(os.path.realpath(__file__))[0]


class Config(BaseSettings):
    class Config:
        extra = "ignore"
        env_file = f"{path}/.env.picsearch"
        env_file_encoding = "utf-8"

    run_path = path

    search_immediately = True  # 私聊发送图片立即搜图，否则需要先发送搜图命令
    hide_img: bool = False  # 隐藏所有搜索结果的缩略图
    saucenao_low_acc: int = 70  # saucenao 相似度低于这个百分比将被认定为相似度过低
    use_ascii2d_when_low_acc: bool = True  # 是否在 saucenao 相似度过低时自动使用 ascii2d
    group_forward_search_result: bool = True  # 若结果消息有多条，群聊采用合并转发方式发送搜图结果
    private_forward_search_result: bool = False  # 此项暂时无用
    proxy: Optional[str] = None  # 大部分请求所使用的代理: http(s)://
    cache_expire: int = 7  # 搜图结果缓存过期时间（天）
    saucenao_api_key: str = ""  # saucenao APIKEY，必填，否则无法使用 saucenao 搜图
    exhentai_cookies: str = ""  # exhentai cookies，选填，没有的情况下自动改用 e-hentai 搜图
    check_screenshot: bool = True  # 是否判断手机截屏
    search_timeout: int = 60  # 连续搜索模式超时时长
    saucenao_result_num: int = 3  # SauceNAO搜索结果显示数量
    ascii2d_result_num: int = 3  # ascii2d搜索结果显示数量
    ignore_stamp: bool = True  # 是否忽略表情搜图
    daily_limit: int = 10  # 搜图每日限额
    recall_time: int = 120  # 群聊消息撤回时间，为0则不撤回


config = Config()
print(f"PicSearchConcig：{config!r}")
