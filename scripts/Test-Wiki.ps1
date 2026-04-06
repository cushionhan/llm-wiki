param(
    [string]$WikiRoot = (Join-Path $PSScriptRoot "..\\wiki"),
    [string]$IndexPath = (Join-Path $PSScriptRoot "..\\wiki\\index.md")
)

function Get-LinkTargets {
    param([string]$Content)

    $matches = [regex]::Matches($Content, '\[\[([^\]]+)\]\]')
    foreach ($match in $matches) {
        $rawTarget = $match.Groups[1].Value
        $target = $rawTarget.Split('|')[0].Split('#')[0].Trim()
        if (-not [string]::IsNullOrWhiteSpace($target)) {
            $target
        }
    }
}

$resolvedWikiRoot = (Resolve-Path $WikiRoot).Path
$resolvedIndexPath = (Resolve-Path $IndexPath).Path
$pages = Get-ChildItem -Path $resolvedWikiRoot -Recurse -File -Filter *.md

if (-not $pages) {
    Write-Error "No markdown files found under $resolvedWikiRoot"
    exit 1
}

$nameToPath = @{}
foreach ($page in $pages) {
    $relativePath = $page.FullName.Substring($resolvedWikiRoot.Length + 1).Replace('\', '/')
    $withoutExtension = [System.IO.Path]::ChangeExtension($relativePath, $null).TrimEnd('.')
    $nameToPath[$withoutExtension] = $page.FullName
}

$brokenLinks = New-Object System.Collections.Generic.List[object]
$inboundCounts = @{}
foreach ($key in $nameToPath.Keys) {
    $inboundCounts[$key] = 0
}

foreach ($page in $pages) {
    $relativePath = $page.FullName.Substring($resolvedWikiRoot.Length + 1).Replace('\', '/')
    $pageKey = [System.IO.Path]::ChangeExtension($relativePath, $null).TrimEnd('.')
    $content = Get-Content -Path $page.FullName -Raw
    $targets = Get-LinkTargets -Content $content

    foreach ($target in $targets) {
        if ($nameToPath.ContainsKey($target)) {
            $inboundCounts[$target]++
        }
        else {
            $brokenLinks.Add([pscustomobject]@{
                Page = $pageKey
                Target = $target
            }) | Out-Null
        }
    }
}

$indexContent = Get-Content -Path $resolvedIndexPath -Raw
$indexedTargets = @(Get-LinkTargets -Content $indexContent)
$missingFromIndex = $nameToPath.Keys |
    Where-Object {
        $_ -notin @("index", "log") -and
        $_ -notin $indexedTargets
    } |
    Sort-Object

$orphanPages = $inboundCounts.GetEnumerator() |
    Where-Object {
        $_.Key -notin @("index", "log", "overview") -and
        $_.Value -eq 0
    } |
    Sort-Object Key |
    Select-Object -ExpandProperty Key

Write-Output "Wiki root: $resolvedWikiRoot"
Write-Output "Page count: $($pages.Count)"
Write-Output ""

Write-Output "[Broken Links]"
if ($brokenLinks.Count -eq 0) {
    Write-Output "None"
}
else {
    $brokenLinks | Format-Table -AutoSize
}

Write-Output ""
Write-Output "[Missing From Index]"
if (-not $missingFromIndex) {
    Write-Output "None"
}
else {
    $missingFromIndex
}

Write-Output ""
Write-Output "[Orphan Pages]"
if (-not $orphanPages) {
    Write-Output "None"
}
else {
    $orphanPages
}

if ($brokenLinks.Count -gt 0) {
    exit 1
}
