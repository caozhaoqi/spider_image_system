# How to use sis

## windows platform

- run sis_v*.exe
- add role name to ./data/auto_spider_img spider_img_keyword.txt or menu click "图像" -> "关键字" add keyword
- click menu "图像" -> "自动爬取" start spider
- wait image download finish, example:

```shell
DEBUG     2024-06-07 10:21:35.855 - image.spider_img_save:download_image - Image saved as C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data\img_url/duo1li4_img_result\images\25761678_208cdbbe52143ae2345c22acfc8b08c8_170.gif, cur images index: 60, cur txt images download count: 219
```

- open ./data/img_url/keyword_name/images/master look image!

## linux

- download source code
- run ./src/run/sh/run.sh
- repeat windows platform operate

# other

## pip 换源

```shell
# 清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# 阿里源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# 腾讯源
pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple
# 豆瓣源
pip config set global.index-url http://pypi.douban.com/simple/
# 换回默认源
pip config unset global.index-url
```
 
- todo