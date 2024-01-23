# pixiv img spider online save 
## struct design
1. spider pixiv.net img -> search img -> get url
2. replace domain -> save url to txt
3. according to url download image from txt content
## execute method
1. python test.py
2. python spider_img_save.py
3. set data dir: include txt dir: data and image dir : images
## position
- if not visit pixiv.net , could visit sd.2021.host replace
- other 
## GUI
- pyqt5 paint main ui
## technology lib
1. selenium
2. loguru
3. request
4. os
## folder
1. ./data/href_url/ artwork url folder
2. ./data/img_url/ img url txt folder
3. ./data/*/images save img folder
4. ./all_finish already save img txt folder
5. ./images/* already download image folder 
6. ../test/*.py test script folder
7. ./log_dir script run log folder
## other
1. self config url (to do)
- 第三方库安装
- bugs 1 : 在类方法中不能使用@logger.catch注解方法，会出现以下错误：
```shell
> File "C:\Users\Administrator\PycharmProjects\calmcar_sf_server\src\test\gui\ui_main.py", line 130, in ui_paint
    app.exec_()
    │   └ <built-in method exec_>
    └ <PyQt5.QtWidgets.QApplication object at 0x000002045EF19AF0>

TypeError: next_img() takes 1 positional argument but 3 were given
```

```shell
pip install pyinstaller 
pip install -r requirements.txt #根据requirements文件安装第三方库文件
pip install -i https://pypi.douban.com/simple/ pyinstaller #豆瓣源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller #清华源
```

- 打包

```shell
Pyinstaller -F ui_main.py #打包exe
 
Pyinstaller -F -w ui_main.py #不带控制台的打包
 
Pyinstaller -F -w -i chengzi.ico ui_main.py #打包指定exe图标打包

Pyinstaller main_test.spec #使用spec文件打包exe
```

