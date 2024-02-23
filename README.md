# Spider Image System Use Guide
## Struct design
1. Spider pixiv.net img -> search img -> get url.
2. Replace domain -> save url to txt.
3. According to url download image from txt content.
4. Spider gif image generate video.
5. Download gofile file.
## Execute method
1. Run sis_v1.0.x.exe.
## Position
- If not visit pixiv.net website, could visit sd.2021.host or other url replace.
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
- Install third-party libraries for project
```shell
# recommend use
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- Build project and publish pack
```shell
Pyinstaller main_test.spec #使用spec文件打包exe
```

