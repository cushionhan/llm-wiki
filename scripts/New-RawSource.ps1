param(
    [Parameter(Mandatory = $true)]
    [string]$Title,

    [string]$Slug,

    [ValidateSet("article", "paper", "meeting", "book", "note", "dataset", "other")]
    [string]$Kind = "article",

    [string]$RawRoot = (Join-Path $PSScriptRoot "..\\raw")
)

function Convert-ToSlug {
    param([string]$Value)

    $slug = $Value.ToLowerInvariant()
    $slug = $slug -replace '[^a-z0-9]+', '-'
    $slug = $slug.Trim('-')

    if ([string]::IsNullOrWhiteSpace($slug)) {
        throw "Unable to derive slug from title."
    }

    return $slug
}

if ([string]::IsNullOrWhiteSpace($Slug)) {
    $Slug = Convert-ToSlug -Value $Title
}

$date = Get-Date -Format "yyyy-MM-dd"
$sourceDir = Join-Path (Resolve-Path $RawRoot).Path $Slug
$assetsDir = Join-Path $sourceDir "assets"
$sourceNotePath = Join-Path $sourceDir "source.md"

if (Test-Path $sourceDir) {
    Write-Error "Source directory already exists: $sourceDir"
    exit 1
}

New-Item -ItemType Directory -Path $sourceDir | Out-Null
New-Item -ItemType Directory -Path $assetsDir | Out-Null

$content = @"
---
title: $Title
kind: $Kind
created: $date
status: inbox
links: []
tags: []
---

# $Title

## Source Info

- kind: $Kind
- created: $date

## Summary

## Notes

## Extraction TODO

- [ ] source note 생성
- [ ] 관련 wiki 페이지 갱신
- [ ] index/log 반영
"@

Set-Content -Path $sourceNotePath -Value $content -Encoding UTF8

Write-Output "Created:"
Write-Output $sourceDir
Write-Output $sourceNotePath
