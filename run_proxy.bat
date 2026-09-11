@echo off
chcp 65001 >nul
set VENV_DIR=.venv
set SCRIPT_NAME=proxy.py

:: Проверка наличия виртуального окружения
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Виртуальное окружение не найдено. Создаем новое...
    python -m venv %VENV_DIR%
    
    echo [INFO] Активация окружения и установка зависимостей...
    call "%VENV_DIR%\Scripts\activate.bat"
    
    python -m pip install --upgrade pip >nul
    pip install fastapi uvicorn pillow httpx
    echo [INFO] Установка завершена.
) else (
    echo [INFO] Виртуальное окружение найдено. Активация...
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo [INFO] Запуск %SCRIPT_NAME%...
echo ===================================================
python %SCRIPT_NAME%
echo ===================================================

pause