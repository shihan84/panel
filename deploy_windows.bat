@echo off
REM Flussonic Dashboard - Windows Deployment Helper
REM This script helps prepare files for upload to your aaPanel server

echo ========================================
echo Flussonic Dashboard - Deployment Helper
echo ========================================
echo.
echo Server: 82.180.144.106
echo Backend: backend.imagetv.in
echo Frontend: ott.imagetv.in
echo.

echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.6+
    pause
    exit /b 1
)

echo [INFO] Running pre-deployment checks...
python check_setup.py
if %errorlevel% neq 0 (
    echo [WARNING] Some checks failed. Review the output above.
    echo.
)

echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Upload this entire project folder to your server
echo 2. SSH to your server (82.180.144.106)
echo 3. Run one of these commands:
echo.
echo    Option A - Python Deployment:
echo    python3 deploy_aapanel.py
echo.
echo    Option B - Bash Quick Deploy:
echo    sudo ./quick_deploy.sh
echo.
echo    Option C - Manual Deployment:
echo    Follow AAPANEL_DEPLOYMENT_GUIDE.md
echo.
echo 4. Configure aaPanel projects as instructed
echo 5. Setup SSL certificates
echo 6. Test your deployment
echo.
echo ========================================
echo Files Ready for Deployment:
echo ========================================
echo.
dir /b *.py *.sh *.md
echo.
echo For detailed instructions, see:
echo - DEPLOYMENT_README.md
echo - AAPANEL_DEPLOYMENT_GUIDE.md
echo.
pause
