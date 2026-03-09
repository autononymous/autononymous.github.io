param(
    [string]$PythonExe = "$env:USERPROFILE\anaconda3\python.exe",
    [string]$TargetDir = "scripts/python"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path $PythonExe)) {
    Write-Error "Python executable not found: $PythonExe"
    exit 1
}

if (-not (Test-Path -Path $TargetDir)) {
    Write-Error "Target directory not found: $TargetDir"
    exit 1
}

$files = Get-ChildItem -Path $TargetDir -Recurse -Filter *.py | ForEach-Object { $_.FullName }

if (-not $files -or $files.Count -eq 0) {
    Write-Host "No Python files found under '$TargetDir'."
    exit 0
}

Write-Host "Using Python: $PythonExe"
& $PythonExe --version

foreach ($file in $files) {
    & $PythonExe -m py_compile $file
}

Write-Host "Compile check passed for $($files.Count) files."