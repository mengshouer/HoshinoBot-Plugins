# 简介

缝合了[picfinder_take](https://github.com/pcrbot/picfinder_take)和[YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch)并稍微修改了亿点点的Hoshino bot搜图插件

## 安装依赖
```
pip install -r requirements.txt
```

## 使用说明

在搜图插件目录新建一个.env.picsearch的文件，然后看config.py里面需要啥参数写啥

基本必填的只有saucenao_api_key，在.env.picsearch填入
```
saucenao_api_key = "saucenao APIKEY，否则无法使用 saucenao 搜图"
```

其他使用使用说明看[picfinder_take](https://github.com/pcrbot/picfinder_take)和[YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch/blob/main/docs/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)的使用说明