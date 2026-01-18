@echo off
REM Build and Release script for Windows

setlocal enabledelayedexpansion

echo ========================================
echo Synergy.OS - Build Release
echo ========================================

REM Check if version argument provided
if "%1"=="" (
    echo Usage: build-release.bat VERSION
    echo Example: build-release.bat 0.2.0
    exit /b 1
)

set VERSION=%1

echo.
echo Updating version to %VERSION%...

REM Update Cargo.toml (root)
powershell -Command "(Get-Content Cargo.toml) -replace 'version = \".*\"', 'version = \"%VERSION%\"' | Set-Content Cargo.toml"

REM Update src-tauri/Cargo.toml
powershell -Command "(Get-Content src-tauri\Cargo.toml) -replace 'version = \".*\"', 'version = \"%VERSION%\"' | Set-Content src-tauri\Cargo.toml"

REM Update tauri.conf.json
powershell -Command "(Get-Content src-tauri\tauri.conf.json) -replace '\"version\": \".*\"', '\"version\": \"%VERSION%\"' | Set-Content src-tauri\tauri.conf.json"

REM Update package.json
powershell -Command "(Get-Content package.json) -replace '\"version\": \".*\"', '\"version\": \"%VERSION%\"' | Set-Content package.json"

echo ✓ Versions updated to %VERSION%

echo.
echo Building release...
call cargo tauri build

if %ERRORLEVEL% NEQ 0 (
    echo ✗ Build failed!
    exit /b 1
)

echo ✓ Build completed successfully!

echo.
echo ========================================
echo Release artifacts:
echo src-tauri\target\release\bundle\msi\Synergy.OS_%VERSION%_x64.exe
echo src-tauri\target\release\bundle\msi\Synergy.OS_%VERSION%_x64.msi
echo ========================================

echo.
echo To create GitHub Release:
echo   git add .
echo   git commit -m "Release v%VERSION%"
echo   git tag v%VERSION%
echo   git push origin v%VERSION%

endlocal
