from pathlib import Path
from typing import Any, List

from nonebot.log import logger
from pydantic import AnyHttpUrl, BaseSettings, Extra

DATA_PATH = Path.cwd() / "data"
JSON_PATH = DATA_PATH / "rss.json"


class ELFConfig(BaseSettings):
    class Config:
        extra = Extra.allow
        env_file = ".env"
        env_file_encoding = "utf-8"

    rss_proxy: str = ""
    rsshub: AnyHttpUrl = "https://rsshub.app"  # type: ignore
    rsshub_backup: List[AnyHttpUrl] = []
    db_cache_expire = 30
    limit = 50

    zip_size: int = 2 * 1024

    gif_zip_size: int = 6 * 1024

    blockquote: bool = True
    black_word: List[str] = []

    baidu_id: str = ""
    baidu_key: str = ""

    is_open_auto_down_torrent: bool = False
    qb_web_url: str = "http://127.0.0.1:8081"
    qb_down_path: str = ""  # qb的文件下载地址，这个地址必须是 go-cqhttp能访问到的
    down_status_msg_group: List[int] = []
    down_status_msg_date: int = 10

    max_length: int = 1024  # 正文长度限制，防止消息太长刷屏，以及消息过长发送失败的情况

    version: str = ""

    def __getattr__(self, name: str) -> Any:
        data = self.dict()
        for k, v in data.items():
            if k.casefold() == name.casefold():
                return v
        return None


config = ELFConfig()
logger.info(f"RSS Config loaded: {config!r}")
