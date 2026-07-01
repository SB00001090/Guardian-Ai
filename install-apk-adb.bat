@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File scripts\guardian\install-apk-adb.ps1