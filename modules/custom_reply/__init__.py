import os, json


class CRdata():
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
