param(
    [Parameter(Mandatory=$true)][string]$CurrentDist,
    [Parameter(Mandatory=$true)][string]$PreviousDist,
    [Parameter(Mandatory=$true)][string]$CurrentVersion,
    [Parameter(Mandatory=$true)][string]$PreviousVersion,
    [Parameter(Mandatory=$true)][string]$BackupDirectory,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$rootPrefix = $projectRoot + [IO.Path]::DirectorySeparatorChar
function Checked-Path([string]$path) {
    $full = [IO.Path]::GetFullPath($path)
    if (-not $full.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Outside project: $full" }
    return $full
}
function Relative-Path([string]$full) { return $full.Substring($rootPrefix.Length) }
function Blob-Path([string]$hash, [string]$name) {
    $extension = [IO.Path]::GetExtension($name).ToLower()
    if ($extension -notmatch '^\.[a-z0-9]{1,10}$') { $extension = '.data' }
    return Checked-Path (Join-Path $backup ('runtime-blobs/'+$hash.ToLower()+$extension))
}
$keep = @($CurrentDist,$PreviousDist)
foreach ($name in $keep) {
    if ([IO.Path]::GetFileName($name) -ne $name -or -not $name.StartsWith('dist')) { throw 'Expected a root dist directory name.' }
    $full = Checked-Path (Join-Path $projectRoot $name)
    if (-not (Test-Path -LiteralPath $full -PathType Container)) { throw "Missing retained build: $name" }
    if (-not (Get-ChildItem -LiteralPath $full -Recurse -File -Filter 'EMG-Motion-Rhythm*.exe' | Select-Object -First 1)) { throw "Missing retained EXE: $name" }
}
$keepArchives = @()
foreach ($version in @($CurrentVersion,$PreviousVersion)) {
    $zip = "EMG-Motion-Rhythm-windows-x64-$version.zip"
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot "release/$zip"))) { throw "Missing retained ZIP: $zip" }
    $keepArchives += $zip
    $keepArchives += "$zip.sha256"
}
$backup = Checked-Path (Join-Path $projectRoot $BackupDirectory)
$backupPrefix = (Join-Path $projectRoot 'backups') + [IO.Path]::DirectorySeparatorChar
if (-not $backup.StartsWith($backupPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Backup must stay in backups/.' }
if (Test-Path -LiteralPath $backup) { throw 'Backup already exists; refusing overwrite.' }
$directories = @(Get-ChildItem -LiteralPath $projectRoot -Directory -Filter 'dist*' | Where-Object { $_.Name -notin $keep } | ForEach-Object { $_.FullName })
$oldArtifacts = Join-Path $projectRoot 'backups/codex-audio-rollback-20261118/artifacts'
if (Test-Path -LiteralPath $oldArtifacts) {
    $directories += @(Get-ChildItem -LiteralPath $oldArtifacts -Directory -Filter 'dist*' | ForEach-Object { $_.FullName })
}
# Only PyInstaller work folders and deployment tests; firmware and data backups stay.
foreach ($workRoot in @((Join-Path $projectRoot 'build'),(Join-Path $oldArtifacts 'build'))) {
    if (-not (Test-Path -LiteralPath $workRoot)) { continue }
    foreach ($folder in Get-ChildItem -LiteralPath $workRoot -Directory) {
        if ($folder.Name -eq 'portability' -or (Get-ChildItem -LiteralPath $folder.FullName -Recurse -File -Filter '*.toc' | Select-Object -First 1)) {
            $directories += $folder.FullName
        }
    }
}
$archives = @()
foreach ($releaseRoot in @((Join-Path $projectRoot 'release'),(Join-Path $oldArtifacts 'release'))) {
    if (-not (Test-Path -LiteralPath $releaseRoot)) { continue }
    $archives += @(Get-ChildItem -LiteralPath $releaseRoot -File | Where-Object {
        $_.Name -like 'EMG-Motion-Rhythm*' -and ($_.Name -like '*.zip' -or $_.Name -like '*.zip.sha256' -or $_.Name -like '*.exe') -and $_.Name -notin $keepArchives
    } | ForEach-Object { $_.FullName })
}
$directories = @($directories | Sort-Object -Unique)
$archives = @($archives | Sort-Object -Unique)
foreach ($target in @($directories)+@($archives)) {
    $null = Checked-Path $target
    if ((Get-Item -LiteralPath $target -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse target: $target" }
}
foreach ($target in $directories) {
    if (Get-ChildItem -LiteralPath $target -Recurse -Force -Attributes ReparsePoint | Select-Object -First 1) { throw "Reparse point inside build: $target" }
}
foreach ($process in @(Get-Process -Name 'EMG-Motion-Rhythm*' -ErrorAction SilentlyContinue)) {
    foreach ($target in $directories) {
        if ($process.Path -and $process.Path.StartsWith($target+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {
            throw "Older build is running (PID $($process.Id)); no cleanup performed."
        }
    }
}
if ($DryRun) {
    [pscustomobject]@{retained=$keep;directories=$directories;archives=$archives;backup=$backup} | ConvertTo-Json -Depth 4
    exit 0
}
New-Item -ItemType Directory -Path $backup | Out-Null
$saved = [Collections.Generic.List[object]]::new()
foreach ($target in $directories) {
    $dataRoots = @(Get-ChildItem -LiteralPath $target -Recurse -Directory -Filter 'data' | Where-Object { $_.FullName -match '[\\/]app[\\/]data$' })
    # Some deployment backups store data directly rather than in a bundle.
    foreach ($dataRoot in $dataRoots) {
        foreach ($file in Get-ChildItem -LiteralPath $dataRoot.FullName -Recurse -File) {
            if ($file.FullName -match '[\\/]__pycache__[\\/]') { continue }
            $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            $destination = Blob-Path $hash $file.Name
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
            if (-not (Test-Path -LiteralPath $destination)) { Copy-Item -LiteralPath $file.FullName -Destination $destination }
            if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $hash -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne $hash) { throw 'Runtime backup verification failed.' }
            $saved.Add([pscustomobject]@{source=$file.FullName;destination=$destination;sha256=$hash.ToLower()})
        }
    }
}
# Preserve any personal data accidentally included in historical ZIPs as well.
Add-Type -AssemblyName System.IO.Compression.FileSystem
foreach ($archive in $archives) {
    if (-not $archive.EndsWith('.zip',[StringComparison]::OrdinalIgnoreCase)) { continue }
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        foreach ($entry in $zip.Entries) {
            $member = $entry.FullName.Replace('\','/')
            if (-not $entry.Name -or $entry.Name -eq '.gitkeep' -or $member -notmatch '(^|/)app/data/' -or $member -match '(^|/)__pycache__/') { continue }
            $stream = $entry.Open(); $sha = [Security.Cryptography.SHA256]::Create()
            try { $hash = [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLower() } finally { $stream.Dispose(); $sha.Dispose() }
            $destination = Blob-Path $hash $entry.Name
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
            if (-not (Test-Path -LiteralPath $destination)) {
                $stream = $entry.Open(); $output = [IO.File]::Create($destination)
                try { $stream.CopyTo($output) } finally { $stream.Dispose(); $output.Dispose() }
            }
            if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $hash) { throw 'ZIP runtime backup verification failed.' }
            $saved.Add([pscustomobject]@{source=($archive+'::'+$member);destination=$destination;sha256=$hash})
        }
    } finally { $zip.Dispose() }
}
ConvertTo-Json -InputObject @($saved.ToArray()) -Depth 5 | Set-Content -LiteralPath (Join-Path $backup 'runtime-manifest.json') -Encoding UTF8
$plan = [pscustomobject]@{retained=$keep;directories=$directories;archives=$archives}
$plan | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backup 'removal-plan.json') -Encoding UTF8
# All backups have been verified before the first recursive deletion.
foreach ($target in $directories) {
    $null = Checked-Path $target
    Remove-Item -LiteralPath $target -Recurse -Force
    Write-Output ('Removed build: '+(Relative-Path $target))
}
foreach ($target in $archives) {
    $null = Checked-Path $target
    Remove-Item -LiteralPath $target -Force
}
$summary = [pscustomobject]@{ok=$true;retained=$keep;removed_directories=$directories.Count;removed_archives=$archives.Count;backed_up_runtime_files=$saved.Count;backup=$backup}
$summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backup 'cleanup-result.json') -Encoding UTF8
$summary | ConvertTo-Json -Depth 4
