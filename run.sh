#!/bin/bash
echo "booting.."
py -m mpremote run esp32/boot.py
echo "finished boot, running main.."
py -m mpremote run esp32/main.py