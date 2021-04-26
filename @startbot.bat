ECHO OFF
cls

:start
ECHO --------------------------------------
ECHO Inicializing bot...
python botexe.py
ECHO. & ECHO.
ECHO --------------------------------------
set /p try=Restart bot?
ECHO. & ECHO.
GOTO start