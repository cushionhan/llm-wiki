param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
}
else {
    $python = "python"
}

$arguments = @("-m", "uvicorn", "app.main:app", "--host", $Host, "--port", $Port.ToString())

if ($Reload.IsPresent) {
    $arguments += "--reload"
}

& $python @arguments
