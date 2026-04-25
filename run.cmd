@echo off

echo booting..
".venv/scripts/python.exe" -m mpremote run esp32/boot.py
echo finished boot, running main..
".venv/scripts/python.exe" -m mpremote run esp32/main.py