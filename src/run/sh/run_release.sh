
pip install Nuitka

cd ../../
ls -l
python -m nuitka --mingw64 --standalone --follow-import-to=config,file,http_tools,image,log,model,router,run,ui_event,utils,view --output-dir=out --output=sis-v1.1.2.exe --plugin-enable=pyqt5 --windows-icon-from-ico=./run/favicon.ico --show-progress ./run/ui_main.py
