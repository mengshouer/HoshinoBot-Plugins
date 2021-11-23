import random
import emoji
import re
import hashlib
import httpx

try:
    import deepl
    from langdetect import detect

    flag = 1
except:
    flag = 0

from google_trans_new import google_translator
from nonebot.log import logger

from ....config import config


# 翻译
async def handle_translation(content: str) -> str:
    try:
        if flag == 1:
            sl = detect(content)
            if sl == "zh-cn" or sl == "zh-tw":
                sl = "zh"
            dltext = "\nDeepL翻译：" + deepl.translate(
                source_language=sl, target_language="ZH", text=text
            )
            return dltext
    except Exception as e:
        logger.error(e)
    translator = google_translator()
    appid = config.baiduid
    secretKey = config.baidukey
    text = emoji.demojize(content)
    text = re.sub(r":[A-Za-z_]*:", " ", text)
    try:
        if appid and secretKey:
            url = f"https://api.fanyi.baidu.com/api/trans/vip/translate"
            salt = str(random.randint(32768, 65536))
            sign = hashlib.md5(
                (appid + content + salt + secretKey).encode()
            ).hexdigest()
            params = {
                "q": content,
                "from": "auto",
                "to": "zh",
                "appid": appid,
                "salt": salt,
                "sign": sign,
            }
            async with httpx.AsyncClient(proxies={}) as client:
                r = await client.get(url, params=params, timeout=10)
            try:
                i = 0
                str_tl = ""
                while i < len(r.json()["trans_result"]):
                    str_tl += r.json()["trans_result"][i]["dst"] + "\n"
                    i += 1
                text = "\n百度翻译：\n" + str_tl
            except Exception as e:
                if r.json()["error_code"] == "52003":
                    logger.warning(
                        "无效的appid，尝试使用谷歌翻译，错误信息：" + str(r.json()["error_msg"])
                    )
                    text = "\n谷歌翻译：\n" + str(
                        translator.translate(re.escape(text), lang_tgt="zh")
                    )
                else:
                    logger.warning(
                        "使用百度翻译错误：" + str(r.json()["error_msg"]) + "，开始尝试使用谷歌翻译"
                    )
                    text = "\n谷歌翻译：\n" + str(
                        translator.translate(re.escape(text), lang_tgt="zh")
                    )
        else:
            text = "\n谷歌翻译：\n" + str(
                translator.translate(re.escape(text), lang_tgt="zh")
            )
        text = re.sub(r"\\", "", text)
    except Exception as e:
        text = "\n翻译失败！" + str(e) + "\n"
    return text
