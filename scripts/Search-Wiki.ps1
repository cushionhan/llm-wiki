param(
    [Parameter(Mandatory = $true)]
    [string]$Query,

    [string]$WikiRoot = (Join-Path $PSScriptRoot "..\\wiki")
)

$resolvedWikiRoot = (Resolve-Path $WikiRoot).Path
$files = Get-ChildItem -Path $resolvedWikiRoot -Recurse -File -Filter *.md

if (-not $files) {
    Write-Error "No markdown files found under $resolvedWikiRoot"
    exit 1
}

$results = $files | Select-String -Pattern $Query -SimpleMatch

if (-not $results) {
    Write-Output "No matches for '$Query' in $resolvedWikiRoot"
    exit 0
}

$results |
    Select-Object Path, LineNumber, Line |
    Format-Table -AutoSize
