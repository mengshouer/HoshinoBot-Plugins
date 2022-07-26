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

    # 私聊发送图片立即搜图，否则需要先发送搜图命令
    search_immediately = True
    # 隐藏所有搜索结果的缩略图
    hide_img: bool = False
    # saucenao 得到低相似度结果时隐藏结果缩略图（包括 ascii2d 和 whatanime）
    hide_img_when_low_acc: bool = False
    # whatanime 得到 R18 结果时隐藏结果缩略图
    hide_img_when_whatanime_r18: bool = False
    # 对 saucenao 的搜索结果进行 NSFW 判断的严格程度(依次递增), 启用后自动隐藏相应的 NSFW 结果的缩略图
    # 0 表示不判断， 1 只判断明确的， 2 包括可疑的， 3 非明确为 SFW 的
    saucenao_nsfw_hide_level: int = 0
    # saucenao 相似度低于这个百分比将被认定为相似度过低
    saucenao_low_acc: int = 70
    # 是否在 saucenao 相似度过低时自动使用 ascii2d
    use_ascii2d_when_low_acc: bool = True
    # 若结果消息有多条，采用合并转发方式发送搜图结果
    forward_search_result: bool = True
    # 大部分请求所使用的代理: http(s)://
    proxy: Optional[str] = None
    # 搜图结果缓存过期时间（天）
    cache_expire: int = 7
    # saucenao APIKEY，必填，否则无法使用 saucenao 搜图
    saucenao_api_key: str = ""
    # exhentai cookies，选填，没有的情况下自动改用 e-hentai 搜图
    exhentai_cookies: str = ""

    # 若结果消息有多条，群聊采用合并转发方式发送搜图结果
    group_forward_search_result: bool = True
    # 此项暂时无用
    private_forward_search_result: bool = False
    # 是否判断手机截屏
    check_screenshot: bool = True
    # 连续搜索模式超时时长
    search_timeout: int = 60
    # SauceNAO搜索结果显示数量
    saucenao_result_num: int = 3
    # ascii2d搜索结果显示数量
    ascii2d_result_num: int = 3
    # 是否忽略表情搜图
    ignore_stamp: bool = True
    # 搜图每日限额
    daily_limit: int = 10
    # 群聊消息撤回时间，为0则不撤回
    recall_time: int = 120


config = Config()
print(f"PicSearchConcig：{config!r}")
