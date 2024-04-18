# Spider Image System User Guide
## Struct design
1. Spider pixiv.net img -> search img -> get url.
2. Replace domain -> save url to txt.
3. According to url download image from txt content.
4. Spider gif image generate video.
5. Download gofile file
## Execute method
1. Run sis_v1.0.x.exe(windows platform).
2. Run ./src/run/sh/run.bat(windows platform).
3. Run ./src/run/sh/run.sh(linux platform).
## Position
- If not visit pixiv.net website, could visit sd.2021.host or other url(example: sd.vv50.de) replace.
- Other.
## GUI
- Pyqt5 paint main ui.
## Technology lib
1. selenium.
2. loguru.
3. requests.
4. opencv.
5. fastapi.
6. nuitka.
7. uvicorn.
8. minio.
9. Other(Read requirements.txt).
## Folder
1. ./data/href_url/ artwork url folder.
2. ./data/img_url/ img url txt folder.
3. ./data/*/images/ save img folder.
4. ./data/video generate video folder.
5. ./data/according_pid_download_image pid image download folder.
6. ./data/face_detect_result face detect result folder.
7. ./data/error_images error images folder.
8. ./log_dir/ script run log folder.
9. Other see ./data/.
## File
1. ./data/download_final_image.json: final download image info.
2. ./data/download_finished_txt.txt: already download keyword txt.
3. ./data/error_image_txt.txt: download fail image save txt.
4. ./data/spider_finished_keyword.txt: already spider finish keyword txt.
5. ./data/spider_img_keyword_final.json: final spider keyword image json.
## Other
1. Self config constant val(Done).
2. Play all video(Done).
3. Autoplay all image(Done).
4. Auto spider image(Done).
5. System performance monitor(Done).
6. Online show image(Done).
7. Gif and image process download(Done).
8. Face detect from downloaded image folder(Done).
9. pid and users image spider and download(Done)
10. Image analyze tools(Done).
11. system monitor(Done).
12. timer restart spider(Done).
13. Other small tools(log,decode,convert,unzip,All Done).
14. Other...(to be continued...)
- bugs 1 : 在类方法中不能使用@logger.catch注解方法，会出现以下错误：
```shell
> File "C:\Users\Administrator\PycharmProjects\calmcar_sf_server\src\test\gui\ui_main.py", line 130, in ui_paint
    app.exec_()
    │   └ <built-in method exec_>
    └ <PyQt5.QtWidgets.QApplication object at 0x000002045EF19AF0>

TypeError: next_img() takes 1 positional argument but 3 were given
```
- problem 1 on ubuntu: opencv-python与pyqt5冲突(问题解决)
```shell
sudo pip3 uninstall opencv-python
sudo pip3 install opencv-python-headless
```
```shell
QObject::moveToThread: Current thread (0x55f29a27e0e0) is not the object's thread (0x55f29a946dd0).
Cannot move to target thread (0x55f29a27e0e0)

qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/usr/local/lib/python3.10/dist-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: xcb, eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl.

Aborted

``` 
- Notice: if cannot start spider image, you need install google chrome explore, detail:
```shell
File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/chrome/webdriver.py", line 45, in __init__
    super().__init__(
  File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/chromium/webdriver.py", line 49, in __init__
    self.service.path = DriverFinder.get_path(self.service, options)
    │    │       │      │            │        │    │        └ <selenium.webdriver.chrome.options.Options object at 0x7f816cf3da20>
    │    │       │      │            │        │    └ <selenium.webdriver.chrome.service.Service object at 0x7f816cf3da80>
    │    │       │      │            │        └ <unprintable WebDriver object>
    │    │       │      │            └ <staticmethod(<function DriverFinder.get_path at 0x7f816eb9cb80>)>
    │    │       │      └ <class 'selenium.webdriver.common.driver_finder.DriverFinder'>
    │    │       └ <property object at 0x7f816eb5ebb0>
    │    └ <selenium.webdriver.chrome.service.Service object at 0x7f816cf3da80>
    └ <unprintable WebDriver object>
  File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/driver_finder.py", line 41, in get_path
    raise NoSuchDriverException(msg) from err
          │                     └ 'Unable to obtain driver for chrome using Selenium Manager.'
          └ <class 'selenium.common.exceptions.NoSuchDriverException'>

selenium.common.exceptions.NoSuchDriverException: Message: Unable to obtain driver for chrome using Selenium Manager.; For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location
```
~ For solve problem, need install follow package:
```shell
apt install chromium-browser
sudo mkdir -p /home/czq/.local/share/applications
sudo touch /home/czq/.local/share/applications/mimeapps.list
chmod -R 777 /home/czq/
xdg-open https://www.baidu.com
# re run ./sh/run.sh to solve the problem
```
- For use face detect, you need run follow command on ubuntu:
```shell
sudo apt-get update
sudo apt-get install libgtk2.0-dev pkg-config
# end run follow command
./sh/run_face_detect.sh # (on ubuntu os)
```
- Install third-party libraries for project
```shell
# recommend use
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# single lib install command
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-contrib-python
```

- Build project and publish pack
```shell
Pyinstaller main_test.spec #使用spec文件打包exe
```

- solve not run on HECS(HuaWei ECS) from huawei cloud
```shell
#see
https://neucrack.com/p/407
```
