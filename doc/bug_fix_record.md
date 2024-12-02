# Bug Fix Record

## solve method

- bugs 1 : 在类方法中不能使用@logger.catch注解方法，会出现以下错误：

```shell
> File "C:\Users\Administrator\PycharmProjects\calmcar_sf_server\src\test\gui\ui_main.py", line 130, in ui_paint
    app.exec_()
    │   └ <built-in method exec_>
    └ <PyQt5.QtWidgets.QApplication object at 0x000002045EF19AF0>

TypeError: next_img() takes 1 positional argument but 3 were given
```

- solve method:

> Qt (或者 PyQt、PySide 等 Qt 的 Python 绑定) 中，当你使用信号和槽机制（即 clicked.connect()）时，槽函数（即你连接到的函数或方法）通常会接收一个额外的参数，这个参数代表了触发信号的发送者（sender）。因此，即使你的 next_img 方法在类定义中只接受一个参数（self），当它被用作一个槽时，Qt 会自动传递一个额外的参数，通常是发出信号的对象的引用。
> 为了解决这个 TypeError，你需要修改你的 next_img 方法，让它能够接受这个额外的参数。这里是一个简单的修改示例：

```python
class MyClass(QWidget):  # 假设 MyClass 继承自 QWidget 或其他 Qt 控件
    def __init__(self, parent=None):
        super(MyClass, self).__init__(parent)
        # 假设 next_button 是一个 QPushButton 的实例
        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.next_img)

    @logger.catch()
    def next_img(self, _=None):  # 添加一个额外的参数 _ 来接收发送者
        """
        跳转下一页
        :return:
        """
        # 你的代码逻辑
        pass
```

> 在这个例子中，next_img 方法现在接受一个额外的参数 _。这个参数名 _ 是一个常见的约定，用于表示这个参数在方法体内不会被使用。当然，你可以选择其他名称，但 _ 是一个通用的占位符，表明这个参数是“不需要的”。

> 现在，当 next_button 被点击时，next_img 方法会被调用，并且 Qt 会自动传递一个参数（通常是 next_button 的引用）给这个方法。由于我们已经在方法定义中包含了这个额外的参数，所以不会再出现 TypeError。

> 如果你确实需要在方法体内使用这个发送者对象（比如检查是哪个按钮被点击了），你可以给这个参数一个更有意义的名称，并在方法体内使用它。但在这个例子中，看起来我们并不需要这个发送者对象，所以使用 _ 作为参数名是一个合适的解决方案。

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

## 带有--windows-disable-console选项打包exe后无法打开
```shell
python -m nuitka --onefile --mingw64 --standalone --follow-import-to=file,http_tools,image,log,model,run,ui_event,utils,jmcomic --output-dir=out  --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/ui_main.py --windows-disable-console
```
- 解决措施
> 删除所有代码，清除缓存，重新拉取代码，安装第三方库，再次尝试打包，问题解决。
> 使用命令行模式检查问题，修复后重新打包尝试


## 自动模式抓取时，报错；手动模式抓取正常

```log
2024-12-02 15:28:30.003 | ERROR    | utils.spider_param:initialize_driver:280 - An error has been caught in function 'initialize_driver', process 'MainProcess' (21280), thread 'Thread-3' (30280):
Traceback (most recent call last):

  File "C:\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
    │    └ <function Thread._bootstrap_inner at 0x000002576ADBC4A0>
    └ <SISThreading(Thread-3, started 30280)>
  File "C:\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
    │    └ <function SISThreading.run at 0x00000257185B3380>
    └ <SISThreading(Thread-3, started 30280)>

  File "D:\pythonProject\spider_image_system\src\utils\sis_therading.py", line 61, in run
    self.target(*self.args, **self.kwargs)
    │    │       │    │       │    └ {}
    │    │       │    │       └ <SISThreading(Thread-3, started 30280)>
    │    │       │    └ (<ui_event.pyqt_main_ui.UIMainWindows object at 0x00000257187ECDD0>,)
    │    │       └ <SISThreading(Thread-3, started 30280)>
    │    └ <function auto_spider_img_thread at 0x000002571876B060>
    └ <SISThreading(Thread-3, started 30280)>

  File "D:\pythonProject\spider_image_system\src\ui_event\base_event.py", line 185, in auto_spider_img_thread
    spider_artworks_url(self, keyword)
    │                   │     └ 'klee'
    │                   └ <ui_event.pyqt_main_ui.UIMainWindows object at 0x00000257187ECDD0>
    └ <function spider_artworks_url at 0x0000025718578540>

  File "D:\pythonProject\spider_image_system\src\ui_event\get_url.py", line 187, in spider_artworks_url
    driver, url, cur_page = spider_param_config(key_word)
                            │                   └ 'klee'
                            └ <function spider_param_config at 0x00000257185660C0>

  File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 347, in spider_param_config
    driver = initialize_driver(options, system_info)
             │                 │        └ 'Windows'
             │                 └ <selenium.webdriver.edge.options.Options object at 0x000002571862EE40>
             └ <function initialize_driver at 0x0000025718565580>

> File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 280, in initialize_driver
    driver = create_driver(system_info, options)
             │             │            └ <selenium.webdriver.edge.options.Options object at 0x000002571862EE40>
             │             └ 'Windows'
             └ <function create_driver at 0x0000025718565D00>

  File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 326, in create_driver
    return driver_class(service=service, options=options) if service else driver_class(options=options)
           │                    │                │           │            │                    └ <selenium.webdriver.edge.options.Options object at 0x000002571862EE40>
           │                    │                │           │            └ <class 'selenium.webdriver.edge.webdriver.WebDriver'>
           │                    │                │           └ None
           │                    │                └ <selenium.webdriver.edge.options.Options object at 0x000002571862EE40>
           │                    └ None
           └ <class 'selenium.webdriver.edge.webdriver.WebDriver'>

  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\edge\webdriver.py", line 45, in __init__
    super().__init__(
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\chromium\webdriver.py", line 61, in __init__
    super().__init__(command_executor=executor, options=options)
                                      │                 └ <selenium.webdriver.edge.options.Options object at 0x000002571862EE40>
                                      └ <selenium.webdriver.chromium.remote_connection.ChromiumRemoteConnection object at 0x000002571865BBF0>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 209, in __init__
    self.start_session(capabilities)
    │    │             └ {'browserName': 'MicrosoftEdge', 'pageLoadStrategy': 'none', 'browserVersion': None, 'ms:edgeOptions': {'excludeSwitches': ['...
    │    └ <function WebDriver.start_session at 0x0000025718371760>
    └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 293, in start_session
    response = self.execute(Command.NEW_SESSION, caps)["value"]
               │    │       │       │            └ {'capabilities': {'firstMatch': [{}], 'alwaysMatch': {'browserName': 'MicrosoftEdge', 'pageLoadStrategy': 'none', 'browserVer...
               │    │       │       └ 'newSession'
               │    │       └ <class 'selenium.webdriver.remote.command.Command'>
               │    └ <function WebDriver.execute at 0x00000257183719E0>
               └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 348, in execute
    self.error_handler.check_response(response)
    │    │             │              └ {'status': 500, 'value': '{"value":{"error":"timeout","message":"timeout: Timed out receiving message from renderer: 600.000\...
    │    │             └ <function ErrorHandler.check_response at 0x0000025718310400>
    │    └ <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000025717A5A1E0>
    └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py", line 229, in check_response
    raise exception_class(message, screen, stacktrace)
          │               │        │       └ ['\t(No symbol) [0x00007FF711796B15]', '\tMicrosoft::Applications::Events::EventProperty::empty [0x00007FF711ABF4A4+1437348]'...
          │               │        └ None
          │               └ 'timeout: Timed out receiving message from renderer: 600.000\n  (Session info: MicrosoftEdge=131.0.2903.70)'
          └ <class 'selenium.common.exceptions.TimeoutException'>

selenium.common.exceptions.TimeoutException: Message: timeout: Timed out receiving message from renderer: 600.000
  (Session info: MicrosoftEdge=131.0.2903.70)
Stacktrace:
	(No symbol) [0x00007FF711796B15]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711ABF4A4+1437348]
	sqlite3_dbdata_init [0x00007FF711B62DE6+643190]
	(No symbol) [0x00007FF711667528]
	(No symbol) [0x00007FF711667278]
	(No symbol) [0x00007FF7116654BC]
	(No symbol) [0x00007FF71166591C]
	(No symbol) [0x00007FF711664636]
	sqlite3_dbdata_init [0x00007FF711B5D2B1+619841]
	(No symbol) [0x00007FF7116644C4]
	(No symbol) [0x00007FF711666FE3]
	(No symbol) [0x00007FF7116654BC]
	(No symbol) [0x00007FF71166591C]
	(No symbol) [0x00007FF711664636]
	(No symbol) [0x00007FF71165C9DB]
	(No symbol) [0x00007FF7116644C4]
	(No symbol) [0x00007FF711663E9D]
	(No symbol) [0x00007FF711663AD8]
	(No symbol) [0x00007FF711676FE3]
	(No symbol) [0x00007FF711656D35]
	(No symbol) [0x00007FF711656809]
	(No symbol) [0x00007FF7116E61D7]
	(No symbol) [0x00007FF7116DBE03]
	(No symbol) [0x00007FF7116B2984]
	(No symbol) [0x00007FF7116B1E30]
	(No symbol) [0x00007FF7116B2571]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6BB34+1094964]
	(No symbol) [0x00007FF7117D32C8]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6AF73+1091955]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6AAD9+1090777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF711870CE1+461569]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF71186CA04+444452]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF71186CB49+444777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF7118621C6+401382]
	BaseThreadInitThunk [0x00007FFA00A7DBE7+23]
	RtlUserThreadStart [0x00007FFA0141FBEC+44]

2024-12-02 15:28:33.195 | ERROR    | utils.spider_param:initialize_driver:280 - An error has been caught in function 'initialize_driver', process 'MainProcess' (21280), thread 'Thread-9' (15212):
Traceback (most recent call last):

  File "C:\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
    │    └ <function Thread._bootstrap_inner at 0x000002576ADBC4A0>
    └ <SISThreading(Thread-9, started 15212)>
  File "C:\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
    │    └ <function SISThreading.run at 0x00000257185B3380>
    └ <SISThreading(Thread-9, started 15212)>

  File "D:\pythonProject\spider_image_system\src\utils\sis_therading.py", line 61, in run
    self.target(*self.args, **self.kwargs)
    │    │       │    │       │    └ {}
    │    │       │    │       └ <SISThreading(Thread-9, started 15212)>
    │    │       │    └ (<ui_event.pyqt_main_ui.UIMainWindows object at 0x00000257187ECDD0>,)
    │    │       └ <SISThreading(Thread-9, started 15212)>
    │    └ <function auto_spider_img_thread at 0x000002571876B060>
    └ <SISThreading(Thread-9, started 15212)>

  File "D:\pythonProject\spider_image_system\src\ui_event\base_event.py", line 185, in auto_spider_img_thread
    spider_artworks_url(self, keyword)
    │                   │     └ 'klee'
    │                   └ <ui_event.pyqt_main_ui.UIMainWindows object at 0x00000257187ECDD0>
    └ <function spider_artworks_url at 0x0000025718578540>

  File "D:\pythonProject\spider_image_system\src\ui_event\get_url.py", line 187, in spider_artworks_url
    driver, url, cur_page = spider_param_config(key_word)
                            │                   └ 'klee'
                            └ <function spider_param_config at 0x00000257185660C0>

  File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 347, in spider_param_config
    driver = initialize_driver(options, system_info)
             │                 │        └ 'Windows'
             │                 └ <selenium.webdriver.edge.options.Options object at 0x0000025718872DE0>
             └ <function initialize_driver at 0x0000025718565580>

> File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 280, in initialize_driver
    driver = create_driver(system_info, options)
             │             │            └ <selenium.webdriver.edge.options.Options object at 0x0000025718872DE0>
             │             └ 'Windows'
             └ <function create_driver at 0x0000025718565D00>

  File "D:\pythonProject\spider_image_system\src\utils\spider_param.py", line 326, in create_driver
    return driver_class(service=service, options=options) if service else driver_class(options=options)
           │                    │                │           │            │                    └ <selenium.webdriver.edge.options.Options object at 0x0000025718872DE0>
           │                    │                │           │            └ <class 'selenium.webdriver.edge.webdriver.WebDriver'>
           │                    │                │           └ None
           │                    │                └ <selenium.webdriver.edge.options.Options object at 0x0000025718872DE0>
           │                    └ None
           └ <class 'selenium.webdriver.edge.webdriver.WebDriver'>

  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\edge\webdriver.py", line 45, in __init__
    super().__init__(
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\chromium\webdriver.py", line 61, in __init__
    super().__init__(command_executor=executor, options=options)
                                      │                 └ <selenium.webdriver.edge.options.Options object at 0x0000025718872DE0>
                                      └ <selenium.webdriver.chromium.remote_connection.ChromiumRemoteConnection object at 0x0000025718343D70>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 209, in __init__
    self.start_session(capabilities)
    │    │             └ {'browserName': 'MicrosoftEdge', 'pageLoadStrategy': 'none', 'browserVersion': None, 'ms:edgeOptions': {'excludeSwitches': ['...
    │    └ <function WebDriver.start_session at 0x0000025718371760>
    └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 293, in start_session
    response = self.execute(Command.NEW_SESSION, caps)["value"]
               │    │       │       │            └ {'capabilities': {'firstMatch': [{}], 'alwaysMatch': {'browserName': 'MicrosoftEdge', 'pageLoadStrategy': 'none', 'browserVer...
               │    │       │       └ 'newSession'
               │    │       └ <class 'selenium.webdriver.remote.command.Command'>
               │    └ <function WebDriver.execute at 0x00000257183719E0>
               └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 348, in execute
    self.error_handler.check_response(response)
    │    │             │              └ {'status': 500, 'value': '{"value":{"error":"timeout","message":"timeout: Timed out receiving message from renderer: 600.000\...
    │    │             └ <function ErrorHandler.check_response at 0x0000025718310400>
    │    └ <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000025718873980>
    └ <selenium.webdriver.edge.webdriver.WebDriver (session="None")>
  File "D:\pythonProject\spider_image_system\venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py", line 229, in check_response
    raise exception_class(message, screen, stacktrace)
          │               │        │       └ ['\t(No symbol) [0x00007FF711796B15]', '\tMicrosoft::Applications::Events::EventProperty::empty [0x00007FF711ABF4A4+1437348]'...
          │               │        └ None
          │               └ 'timeout: Timed out receiving message from renderer: 600.000\n  (Session info: MicrosoftEdge=131.0.2903.70)'
          └ <class 'selenium.common.exceptions.TimeoutException'>

selenium.common.exceptions.TimeoutException: Message: timeout: Timed out receiving message from renderer: 600.000
  (Session info: MicrosoftEdge=131.0.2903.70)
Stacktrace:
	(No symbol) [0x00007FF711796B15]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711ABF4A4+1437348]
	sqlite3_dbdata_init [0x00007FF711B62DE6+643190]
	(No symbol) [0x00007FF711667528]
	(No symbol) [0x00007FF711667278]
	(No symbol) [0x00007FF7116654BC]
	(No symbol) [0x00007FF71166591C]
	(No symbol) [0x00007FF711664636]
	sqlite3_dbdata_init [0x00007FF711B5D2B1+619841]
	(No symbol) [0x00007FF7116644C4]
	(No symbol) [0x00007FF711666FE3]
	(No symbol) [0x00007FF7116654BC]
	(No symbol) [0x00007FF71166591C]
	(No symbol) [0x00007FF711664636]
	(No symbol) [0x00007FF71165C9DB]
	(No symbol) [0x00007FF7116644C4]
	(No symbol) [0x00007FF711663E9D]
	(No symbol) [0x00007FF711663AD8]
	(No symbol) [0x00007FF711676FE3]
	(No symbol) [0x00007FF711656D35]
	(No symbol) [0x00007FF711656809]
	(No symbol) [0x00007FF7116E61D7]
	(No symbol) [0x00007FF7116DBE03]
	(No symbol) [0x00007FF7116B2984]
	(No symbol) [0x00007FF7116B1E30]
	(No symbol) [0x00007FF7116B2571]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6BB34+1094964]
	(No symbol) [0x00007FF7117D32C8]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6AF73+1091955]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF711A6AAD9+1090777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF711870CE1+461569]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF71186CA04+444452]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF71186CB49+444777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF7118621C6+401382]
	BaseThreadInitThunk [0x00007FFA00A7DBE7+23]
	RtlUserThreadStart [0x00007FFA0141FBEC+44]
```