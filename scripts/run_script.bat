@echo off

:: Get the current time with the format y-m-d_h-m-s
for /f "tokens=1-5 delims=/: " %%a in ('echo %date% %time%') do set CURRENT_TIME=%%c-%%a-%%b_%%d-%%e
echo Start time: %CURRENT_TIME% 

echo Checking arguments...

:: Check if the ROOT_DIR environment variable is set
if "%ROOT_DIR%"=="" (
    echo Environment variable ROOT_DIR is not set. Please set it before running the script.
    exit /b 1
)

:: Check if the correct number of arguments is passed
if "%~1"=="" (
    echo Usage: %0 -i input_folder -o output_folder
    exit /b 1
)

:: Parse the input arguments
set input_folder=
set output_folder=

:parse_args
if "%1"=="" goto done_args
if "%1"=="-i" (
    set input_folder=%~2
)
if "%1"=="-o" (
    set output_folder=%~2
)
shift
shift
goto parse_args

:done_args

:: Check if the input folder exists
if not exist "%input_folder%" (
    echo Error: The input folder "%input_folder%" does not exist.
    exit /b 1
)

:: Check if the output folder exists
if not exist "%output_folder%" (
    echo Error: The output folder "%output_folder%" does not exist.
    exit /b 1
)

echo Change to the working directory...

:: Change to the directory where your Python code resides
cd /d "%ROOT_DIR%" || exit /b 1

:: Activate Miniconda environment
echo Activating Conda environment 'thesis-master'...
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" thesis-master

set SCRIPT_DIR=%ROOT_DIR%\scripts
set LOG_DIR=%SCRIPT_DIR%\logs
set LOG_FILE=%LOG_DIR%\output_%CURRENT_TIME%.log

echo Running command ...
:: Run the Python script with the provided arguments
python phase1\start.py -i "%input_folder%" -o "%output_folder%" > "%LOG_FILE%" 2>&1

echo Deactivating Conda environment 'thesis-master'...

:: Deactivate the environment (optional, but a good practice)
call conda deactivate

echo Logging to %LOG_FILE%

echo End python script.
