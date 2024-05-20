@echo off
pip install Nuitka
cd ../../
dir
@REM python -m nuitka --mingw64 --standalone --follow-import-to=config,file,http_tools,image,log,model,router,run,ui_event,utils,view --output-dir=out --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/ui_main.py
@REM pause
copy run\favicon.ico out\ui_main.dist\
@REM # 不输出控制台 打包前手动复制favicon.ico到out中
python -m nuitka --mingw64 --standalone --follow-import-to=config,file,http_tools,image,log,model,router,run,ui_event,utils,view --output-dir=out --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/ui_main.py --windows-disable-console
@REM 单个文件
@REM python -m nuitka --onefile --mingw64 --standalone --follow-import-to=log,run,utils --output-dir=out --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/main_ui.py --windows-disable-console  --output-filename=HMAC_calculator_v1.0.3
@REM pass