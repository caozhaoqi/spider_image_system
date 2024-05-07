# info

- 1.spider pid url.(exists skip)
- 2.pid url get image url.(exists skip)
- 3.according url download image.(exists skip) finished write to txt, start skip finished txt
- 4.cur method: delete finish.txt re download.
- 5.other method:

# publish method

## first (in src dir)

```shell
python -m nuitka --mingw64 --standalone --follow-import-to=config,file,http_tools,image,log,model,router,run,ui_event,utils,view --output-dir=out --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/ui_main.py
#link
https://caozhaoqi.github.io/2024/04/09/nuitka-publish-python/
```

## second(in src dir)

```shell
# VNISEdit 可视化 打包发布
#link :
https://caozhaoqi.github.io/2024/04/10/setup-tools-python/
```

## notice

> In order to achieve a rapid startup for the spider image executable, please add the chrome_path to the config.ini file.

```shell
# ...
chrome_path = C:/Users\Administrator/.cache/selenium/chromedriver/win64/124.0.6367.91/chromedriver.exe
chrome_version = 1
# ... 
```

## TODO

- GUI显示抓取进度
- GUI显示下载进度
- GUI提示抓取，下载完成dialog
- other
