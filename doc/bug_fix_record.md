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
