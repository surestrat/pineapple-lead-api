@echo off
setlocal

echo Pineapple API Test Runner
echo =========================

:menu
echo.
echo Please select a test to run:
echo 1. Test lead creation
echo 2. Test quote creation
echo 3. Run all tests
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto lead
if "%choice%"=="2" goto quote
if "%choice%"=="3" goto all
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
goto menu

:lead
echo.
echo Running lead creation test...
python test_api.py --lead
pause
goto menu

:quote
echo.
echo Running quote creation test...
python test_api.py --quote
pause
goto menu

:all
echo.
echo Running all tests...
python test_api.py --all
pause
goto menu

:end
echo.
echo Thank you for using the test runner.
exit /b
