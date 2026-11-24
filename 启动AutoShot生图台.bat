@echo off
chcp 65001 >nul
title AutoShot 生图台 - 本地服务
cd /d "%~dp0auto_image_gen"
echo 正在启动 AutoShot 生图台 (http://127.0.0.1:8765) ...
start "" http://127.0.0.1:8765
python web\server.py
pause
