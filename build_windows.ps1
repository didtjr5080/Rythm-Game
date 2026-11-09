param(
    [string]$Version = "2026.11.09.3",
    [switch]$SkipBuild
)
$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    $python = Join-Path $projectRoot ".venv311/Scripts/python.exe"
    if (-not $SkipBuild) {
        & $python packaging/make_icon.py
        if ($LASTEXITCODE -ne 0) { throw "Icon generation failed." }
        & $python -m PyInstaller --noconfirm --distpath dist_windows --workpath build/windows EMG-Motion-Rhythm.spec
        if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }
    }
    $bundle = Join-Path $projectRoot "dist_windows/EMG-Motion-Rhythm"
    $exe = Join-Path $bundle "EMG-Motion-Rhythm.exe"
    if (-not (Test-Path -LiteralPath $exe)) { throw "Built executable not found." }
    $releaseDir = Join-Path $projectRoot "release"
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    Copy-Item -LiteralPath "packaging/README-WINDOWS.txt" -Destination $bundle
    $report = Join-Path $releaseDir "self-test.json"
    $previousPlatform = $env:QT_QPA_PLATFORM
    try {
        $env:QT_QPA_PLATFORM = "offscreen"
        $process = Start-Process -FilePath $exe -ArgumentList @('--self-test',('"{0}"' -f $report)) -WindowStyle Hidden -PassThru
        if (-not $process.WaitForExit(180000)) {
            $process.Kill()
            throw "Executable self-test timed out."
        }
        $process.Refresh()
        if ($process.ExitCode -ne 0) { throw "Executable self-test failed. See release/self-test.json." }
        $result = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
        if (-not $result.ok) { throw "Executable self-test reported failure." }
    } finally {
        $env:QT_QPA_PLATFORM = $previousPlatform
    }
    $archive = Join-Path $releaseDir "EMG-Motion-Rhythm-windows-x64-$Version.zip"
    & $python packaging/archive_release.py $bundle $archive
    if ($LASTEXITCODE -ne 0) { throw "Release archive failed." }
    $hash = Get-FileHash -LiteralPath $archive -Algorithm SHA256
    "$($hash.Hash.ToLower())  $([IO.Path]::GetFileName($archive))" | Set-Content -LiteralPath "$archive.sha256" -Encoding ascii
    Write-Output "Ready: $archive"
} finally { Pop-Location }
