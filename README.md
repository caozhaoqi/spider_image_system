# Spider Image System User Guide

## Struct design

1. Spider pixiv.net img -> search img -> get url.
2. Replace domain -> save url to txt.
3. According to url download image from txt content.

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
9. plugin_jm_server
10. Other(Read requirements.txt).

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

## Function

1. Self config constant val(Done).
2. Play all video(Done).
3. Autoplay all image(Done).
4. Auto spider image(Done).
5. System performance monitor(Done).
6. Online show image(Done).
7. Gif and image process download(Done).
8. Face detect from downloaded image folder(Done).
9. pid and users image spider and download(Done).
10. Image analyze tools(Done).
11. system monitor(Done).
12. timer restart spider(Done).
13. Other small tools(log,decode,convert,unzip,All Done).
14. AI detect image(nsfw).
15. jm download image.
16. Other...(to be continued...).

- Install third-party libraries for project on Windows

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
