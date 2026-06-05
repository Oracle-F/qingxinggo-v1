@echo off
setlocal
set MODE=%1
if "%MODE%"=="" set MODE=mock
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" -Mode %MODE%