@echo off

rem copies everything from esp32/ directory to the esp32

".venv/scripts/python.exe" -m mpremote fs cp -r esp32/. :
echo deployed to the esp32!