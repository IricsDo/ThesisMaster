@echo off

:: Enable ANSI escape sequences for color in Windows 10 or later
for /f "tokens=2 delims=: " %%i in ('reg query HKEY_CURRENT_USER\Console /v VirtualTerminalLevel 2^>nul') do set "VT=%%i"
if not defined VT (
    reg add HKEY_CURRENT_USER\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f
    echo Enabled ANSI color support.
)

:: Define ANSI color codes
set "RED=\033[0;31m"
set "GREEN=\033[0;32m"
set "YELLOW=\033[1;33m"
set "NC=\033[0m"  :: No color / reset

:: Define environment name
set ENV_NAME=thesis-master

:: Check if the environment already exists
conda info --envs | findstr /r /c:"^%ENV_NAME% " >nul
if %errorlevel%==0 (
    echo %GREEN%The environment "%ENV_NAME%" already exists.%NC%
) else (
    echo %YELLOW%The environment "%ENV_NAME%" does not exist. Creating a new environment...%NC%
    :: Create the new environment
    conda create -n %ENV_NAME% python=3.11 -y
    if %errorlevel%==0 (
        echo %GREEN%Environment "%ENV_NAME%" has been created successfully.%NC%
    ) else (
        echo %RED%Failed to create the environment "%ENV_NAME%".%NC%
        pause
        :: Exit the script and close the terminal
        exit
    )
)

:: Activate the environment
call conda activate %ENV_NAME%

:: Install additional packages from the YAML file
set YAML_FILE="%ROOT_WS_DUY%\ThesisMaster\setups\win\environment.yml"
echo %YELLOW%Installing additional packages from %YAML_FILE%...%NC%
conda env update -n %ENV_NAME% -f %YAML_FILE%
if %errorlevel%==0 (
    echo %GREEN%Additional packages installed successfully.%NC%
) else (
    echo %RED%Failed to install additional packages.%NC%
    pause
)

:: Display the message
echo %YELLOW%The program will auto close after 10 seconds from now...%NC%
:: Wait for 10 seconds
timeout /t 10 /nobreak >nul
:: Exit the script and close the terminal
exit
