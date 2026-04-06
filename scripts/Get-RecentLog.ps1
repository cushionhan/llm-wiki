param(
    [int]$Count = 10,
    [string]$LogPath = (Join-Path $PSScriptRoot "..\\wiki\\log.md")
)

$resolvedLogPath = (Resolve-Path $LogPath).Path

$entries = Select-String -Path $resolvedLogPath -Pattern '^## \['

if (-not $entries) {
    Write-Output "No log entries found in $resolvedLogPath"
    exit 0
}

$entries |
    Select-Object -Last $Count |
    ForEach-Object { $_.Line }
