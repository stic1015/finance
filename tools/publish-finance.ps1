[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Completed,
    [Parameter(Mandatory = $true)]
    [string]$Remaining,
    [Parameter(Mandatory = $true)]
    [string]$NextStep,
    [string]$RepoRoot = "D:\Codex\Finance",
    [string]$RemoteName,
    [string]$TargetRef,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([string[]]$Arguments)

    $command = @("--git-dir=$script:GitDir", "--work-tree=$script:RepoRoot") + $Arguments
    & git @command
    if ($LASTEXITCODE -ne 0) {
        throw "git command failed: git $($Arguments -join ' ')"
    }
}

function Get-GitDirPath {
    param([string]$RepoPath)

    $dotGit = Join-Path $RepoPath ".git"
    if (-not (Test-Path $dotGit)) {
        throw "Missing .git entry at $dotGit"
    }

    $content = Get-Content -Path $dotGit -Raw
    if ($content -match 'gitdir:\s*(.+)') {
        $candidate = $Matches[1].Trim()
        if ([System.IO.Path]::IsPathRooted($candidate)) {
            return [System.IO.Path]::GetFullPath($candidate)
        }
        return [System.IO.Path]::GetFullPath((Join-Path $RepoPath $candidate))
    }

    throw "Unable to resolve gitdir from $dotGit"
}

function Get-UpstreamRef {
    $result = & git "--git-dir=$script:GitDir" "--work-tree=$script:RepoRoot" rev-parse --abbrev-ref --symbolic-full-name "@{upstream}" 2>$null
    if ($LASTEXITCODE -eq 0 -and $result) {
        return ($result | Select-Object -First 1).Trim()
    }
    return $null
}

function Test-RemoteRefExists {
    param([string]$RefName)

    & git "--git-dir=$script:GitDir" "--work-tree=$script:RepoRoot" rev-parse --verify --quiet "refs/remotes/$RefName" *> $null
    return $LASTEXITCODE -eq 0
}

function Get-UnpushedCommitCount {
    param(
        [string]$BranchName,
        [string]$ComparisonRef
    )

    if ($ComparisonRef -and (Test-RemoteRefExists -RefName $ComparisonRef)) {
        $count = & git "--git-dir=$script:GitDir" "--work-tree=$script:RepoRoot" rev-list --count "$ComparisonRef..HEAD"
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to compare HEAD with $ComparisonRef"
        }
        return [int]($count | Select-Object -First 1)
    }

    $headCount = & git "--git-dir=$script:GitDir" "--work-tree=$script:RepoRoot" rev-list --count HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to count local commits for $BranchName"
    }
    return [int]($headCount | Select-Object -First 1)
}

function Update-HandoffFile {
    param(
        [string]$FilePath,
        [string]$CompletedText,
        [string]$RemainingText,
        [string]$NextStepText,
        [string]$ReleaseMarker
    )

    if (-not (Test-Path $FilePath)) {
        throw "Missing handoff file: $FilePath"
    }

    $content = Get-Content -Path $FilePath -Raw
    if ($content -notmatch '## Current Snapshot') {
        throw "The handoff file does not contain a '## Current Snapshot' section."
    }

    $snapshot = @"
## Current Snapshot

- Completed This Release: $CompletedText
- Remaining Work: $RemainingText
- Recommended Next Step: $NextStepText
- Latest Release Marker: `$ReleaseMarker
"@

    $updated = [System.Text.RegularExpressions.Regex]::Replace(
        $content,
        '## Current Snapshot[\s\S]*$',
        $snapshot
    )

    Set-Content -Path $FilePath -Value ($updated.TrimEnd() + "`r`n") -NoNewline
}

$script:RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$script:GitDir = Get-GitDirPath -RepoPath $script:RepoRoot
$handoffPath = Join-Path $script:RepoRoot "docs\context\finance-handoff.md"
$backendPython = Join-Path $script:RepoRoot "backend\.venv\Scripts\python.exe"
$frontendPath = Join-Path $script:RepoRoot "frontend"

if (-not (Test-Path $backendPython)) {
    throw "Backend virtualenv Python is missing: $backendPython"
}

$branch = ((Invoke-Git -Arguments @("rev-parse", "--abbrev-ref", "HEAD")) | Select-Object -First 1).Trim()
if ($branch -eq "HEAD") {
    throw "Detached HEAD is not supported by publish-finance.ps1"
}

$status = Invoke-Git -Arguments @("status", "--porcelain")
if ($status) {
    throw "Working tree must be clean before publish. Commit or stash existing changes first."
}

$upstream = Get-UpstreamRef
$resolvedTarget = $TargetRef
if (-not $resolvedTarget) {
    if ($upstream) {
        $resolvedTarget = $upstream
    }
    else {
        $resolvedRemote = if ($RemoteName) { $RemoteName } else { "origin" }
        $resolvedTarget = "$resolvedRemote/$branch"
    }
}

$unpushedCount = Get-UnpushedCommitCount -BranchName $branch -ComparisonRef $resolvedTarget
if ($unpushedCount -le 0) {
    throw "Publish requires at least one local commit that has not been pushed yet."
}

$headSha = ((Invoke-Git -Arguments @("rev-parse", "--short", "HEAD")) | Select-Object -First 1).Trim()
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
$releaseMarker = "$timestamp | $branch | $headSha"

Write-Host "Running backend tests..."
$backendPath = Join-Path $script:RepoRoot "backend"
Push-Location $backendPath
try {
    & $backendPython -m pytest tests
    if ($LASTEXITCODE -ne 0) {
        throw "Backend pytest run failed."
    }
}
finally {
    Pop-Location
}

Write-Host "Running frontend build..."
Push-Location $frontendPath
try {
    & npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed."
    }
}
finally {
    Pop-Location
}

Update-HandoffFile -FilePath $handoffPath -CompletedText $Completed -RemainingText $Remaining -NextStepText $NextStep -ReleaseMarker $releaseMarker

$relativeHandoffPath = "docs/context/finance-handoff.md"
Invoke-Git -Arguments @("add", "--", $relativeHandoffPath)

$handoffCommitMessage = "docs: update finance handoff for publish"

if ($DryRun) {
    Write-Host "Dry run complete."
    Write-Host "Branch: $branch"
    Write-Host "Comparison ref: $resolvedTarget"
    Write-Host "Release marker: $releaseMarker"
    Write-Host "Would commit: $handoffCommitMessage"
    if ($upstream -and -not $RemoteName -and -not $TargetRef) {
        Write-Host "Would push with upstream tracking."
    }
    else {
        $pushRemote = if ($resolvedTarget -match '^([^/]+)/(.+)$') { $Matches[1] } else { "origin" }
        $pushBranch = if ($resolvedTarget -match '^([^/]+)/(.+)$') { $Matches[2] } else { $branch }
        Write-Host "Would push: $pushRemote HEAD:refs/heads/$pushBranch"
    }
    exit 0
}

Invoke-Git -Arguments @("commit", "-m", $handoffCommitMessage)

if ($upstream -and -not $RemoteName -and -not $TargetRef) {
    Invoke-Git -Arguments @("push")
}
else {
    $pushRemote = if ($resolvedTarget -match '^([^/]+)/(.+)$') { $Matches[1] } else { "origin" }
    $pushBranch = if ($resolvedTarget -match '^([^/]+)/(.+)$') { $Matches[2] } else { $branch }
    Invoke-Git -Arguments @("push", $pushRemote, "HEAD:refs/heads/$pushBranch")
}

Write-Host "Publish completed successfully."
