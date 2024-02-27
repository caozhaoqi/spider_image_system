# Spider Image System User Guide
## Struct design
1. Spider pixiv.net img -> search img -> get url.
2. Replace domain -> save url to txt.
3. According to url download image from txt content.
4. Spider gif image generate video.
5. Download gofile file.
## Execute method
1. Run sis_v1.0.x.exe(windows platform).
2. Run ./src/run/sh/run.bat(windows platform).
3. Run ./src/run/sh/run.sh(linux platform).
## Position
- If not visit pixiv.net website, could visit sd.2021.host or other url(sd.vv50.de) replace.
- Other.
## GUI
- Pyqt5 paint main ui.
## Technology lib
1. selenium.
2. loguru.
3. requests.
4. Other(Read requirements.txt).
## Folder
1. ./data/href_url/ artwork url folder.
2. ./data/img_url/ img url txt folder.
3. ./data/*/images/ save img folder.
7. ./log_dir/ script run log folder.
8. Other see ./data/.
## Other
1. Self config constant val(Finished).
2. Play all video(Finished).
3. Autoplay all image(Finished).
4. Auto spider image(Finished).
5. System performance monitor(Finished).
6. Online show image(Finished).
7. Gif and image process(Finished).
8. Other small tools(Finished).
9. Other...(to be continued...)
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
ERROR     2024-02-23 11:56:07.032 - threading:run - An error has been caught in function 'run', process 'MainProcess' (123198), thread 'Thread-1 (spider_artworks_url)' (140194078520896): Traceback (most recent call last):

  File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/driver_finder.py", line 38, in get_path
    path = SeleniumManager().driver_location(options) if path is None else path
           │                                 │           │                 └ None
           │                                 │           └ None
           │                                 └ <selenium.webdriver.chrome.options.Options object at 0x7f816cf3da20>
           └ <class 'selenium.webdriver.common.selenium_manager.SeleniumManager'>
  File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/selenium_manager.py", line 103, in driver_location
    output = self.run(args)
             │    │   └ ['/usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/linux/selenium-manager', '--browser', 'chrome', '--output...
             │    └ <staticmethod(<function SeleniumManager.run at 0x7f816eb9cd30>)>
             └ <selenium.webdriver.common.selenium_manager.SeleniumManager object at 0x7f816cf3db10>
  File "/usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/selenium_manager.py", line 149, in run
    raise WebDriverException(f"Unsuccessful command executed: {command}.\n{result}{stderr}")
          └ <class 'selenium.common.exceptions.WebDriverException'>

selenium.common.exceptions.WebDriverException: Message: Unsuccessful command executed: /usr/local/lib/python3.10/dist-packages/selenium/webdriver/common/linux/selenium-manager --browser chrome --output json.
{'code': 65, 'message': 'request or response body error: operation timed out', 'driver_path': '', 'browser_path': ''}



The above exception was the direct cause of the following exception:


Traceback (most recent call last):

  File "/usr/lib/python3.10/threading.py", line 973, in _bootstrap
    self._bootstrap_inner()
    │    └ <function Thread._bootstrap_inner at 0x7f817e13b6d0>
    └ <Thread(Thread-1 (spider_artworks_url), started 140194078520896)>
  File "/usr/lib/python3.10/threading.py", line 1016, in _bootstrap_inner
    self.run()
    │    └ <function Thread.run at 0x7f817e13b400>
    └ <Thread(Thread-1 (spider_artworks_url), started 140194078520896)>
> File "/usr/lib/python3.10/threading.py", line 953, in run
    self._target(*self._args, **self._kwargs)
    │    │        │    │        │    └ {}
    │    │        │    │        └ <Thread(Thread-1 (spider_artworks_url), started 140194078520896)>
    │    │        │    └ (<ui_event.pyqt_main_ui.UIMainWindows object at 0x7f816d1cab00>, 'klee')
    │    │        └ <Thread(Thread-1 (spider_artworks_url), started 140194078520896)>
    │    └ <function spider_artworks_url at 0x7f816d5fb250>
    └ <Thread(Thread-1 (spider_artworks_url), started 140194078520896)>

  File "/home/czq/spider_image_system/src/ui_event/get_url.py", line 110, in spider_artworks_url
    driver = webdriver.Chrome(options=options)
             │         │              └ <selenium.webdriver.chrome.options.Options object at 0x7f816cf3da20>
             │         └ <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
             └ <module 'selenium.webdriver' from '/usr/local/lib/python3.10/dist-packages/selenium/webdriver/__init__.py'>

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

