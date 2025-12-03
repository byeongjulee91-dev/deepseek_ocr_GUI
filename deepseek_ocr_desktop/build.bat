@echo off
REM Build script for DeepSeek-OCR Desktop (Windows)
REM Creates a standalone executable using PyInstaller

echo =========================================
echo DeepSeek-OCR Desktop - Build Script
echo =========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv not found! Please install uv first:
    echo powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found!
    echo Installing PyInstaller with uv...
    uv pip install pyinstaller>=6.0.0
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Clean complete
echo.

REM Run PyInstaller
echo Building with PyInstaller...
echo This may take several minutes...
echo.

pyinstaller deepseek_ocr.spec --clean

REM Check if build was successful
if exist "dist\DeepSeek-OCR" (
    echo.
    echo =========================================
    echo Build successful!
    echo =========================================
    echo.
    echo Executable location: dist\DeepSeek-OCR\
    echo Main executable: dist\DeepSeek-OCR\DeepSeek-OCR.exe
    echo.
    echo Note: Model files (~5-10GB) will be downloaded on first run
    echo       to %%USERPROFILE%%\.cache\huggingface\
    echo.
    echo To run the application:
    echo   cd dist\DeepSeek-OCR
    echo   DeepSeek-OCR.exe
    echo.
    echo To create a distributable archive:
    echo   Right-click dist\DeepSeek-OCR folder and select "Compress to ZIP"
    echo.
) else (
    echo.
    echo =========================================
    echo Build failed!
    echo =========================================
    echo Check the error messages above.
    pause
    exit /b 1
)

pause
