@echo off
echo ========================================
echo 启动路径规划服务器
echo ========================================
echo.

cd /d %~dp0

echo 检查Python环境...
C:\Users\19534\.conda\envs\myenv\python.exe --version
if errorlevel 1 (
    echo 错误: Python环境未找到
    pause
    exit /b 1
)

echo.
echo 启动服务器...
echo 监听地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

C:\Users\19534\.conda\envs\myenv\python.exe server.py

pause
