# Guardian Ai — USB install latest APK + adb reverse
# Developed by Suckbob | Guardian Ai
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$apk = Join-Path $root "apps\guardian-ai-android\app\build\outputs\apk\release\app-release.apk"
if (-not (Test-Path $apk)) {
    $apk = Join-Path $root "dist\guardian-ai-android-release.apk"
}
if (-not (Test-Path $apk)) {
    Write-Host "APK not found. Build: cd apps/guardian-ai-android && ./gradlew assembleRelease"
    exit 1
}
adb reverse tcp:7860 tcp:7860
adb install -r $apk
Write-Host "Installed Guardian Ai APK. Tunnel or USB reverse to http://127.0.0.1:7860"