del /s/f/q ../logic/setting/staticdata/*.pyc
python del_setting_pyc.py
cd ../bin
start "database" launcher.exe database
start "master" launcher.exe master
start "chat" launcher.exe chat
start "dbworker 01" launcher.exe dbworker 01
start "gateway 01" launcher.exe gateway 01
start "login" launcher.exe login
start "game 01" launcher.exe game 01
start "game 02" launcher.exe game 02
