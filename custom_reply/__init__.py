try:
    import ujson as json
except:
    import json
import os
import shutil
from nonebot.log import logger
class CRdata():
    # 仅回复带有自定义前缀的信息(能减少占用,为空默认关闭)
    # 例：custom_prefix = "/!" 这里就是匹配/和!开头的自定义回复，不用分隔开
    custom_prefix = ""
    
    # 大小写敏感(True/False)，默认为True即敏感，对自定义回复的字母大小写敏感
    sensitive = True
    
    
    # 初始化
    try:
        if not os.path.exists("./data/"):
            os.mkdir("./data")
        if not os.path.exists("./data/custom_reply"):
            os.mkdir("./data/custom_reply")
        if os.path.exists("CustomReplyData.json"):
            shutil.move("./CustomReplyData.json", "./data/custom_reply/CustomReplyData.json")
        if os.path.exists("HideCustomReplyList.json"):
            shutil.move("./HideCustomReplyList.json", "./data/custom_reply/HideCustomReplyList.json")
        with open('./data/custom_reply/CustomReplyData.json', 'r', encoding="GB2312") as f:
            data = json.load(f)
    except:
        if os.path.exists("./data/custom_reply/CustomReplyData.json"):
            logger.error("自定义回复数据文件格式有误")
        else:
            data = {}
            with open('./data/custom_reply/CustomReplyData.json', 'w', encoding="GB2312") as f:
                json.dump(data, f, ensure_ascii=False)
                logger.info("未发现自定义回复数据文件，新建数据文件")
