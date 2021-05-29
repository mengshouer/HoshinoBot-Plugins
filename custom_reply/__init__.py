import os, json


class CRdata():
    # 仅回复带有自定义前缀的信息(能减少占用,为空默认关闭)
    # 例：custom_prefix = "/!" 这里就是匹配/和!开头的自定义回复，不用分隔开
    custom_prefix = ""
    
    # 大小写敏感(True/False)，默认为True即敏感，对自定义回复的字母大小写敏感
    sensitive = True
    
    # 初始化
    try:
        with open('CustomReplyData.json', 'r', encoding="GB2312") as f:
            data = json.load(f)
    except:
        if os.path.exists("CustomReplyData.json"):
            print("自定义回复数据文件格式有误")
        else:
            data = {}
            with open('CustomReplyData.json', 'w', encoding="GB2312") as f:
                json.dump(data, f, ensure_ascii=False)
                print("未发现数据文件，新建数据文件")
