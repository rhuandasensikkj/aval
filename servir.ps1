$repo = $PSScriptRoot
Set-Location $repo
Get-Process python,cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) { Write-Host "python nao encontrado" -ForegroundColor Red; exit 1 }
Start-Process -FilePath $py.Source -ArgumentList "server.py" -WorkingDirectory $repo
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try { if ((Invoke-WebRequest "http://127.0.0.1:8080/health?t=m4t7k2p9x6v3n8b5z1q0w7r2" -TimeoutSec 3 -UseBasicParsing).StatusCode -eq 200) { $ok = $true; break } } catch {}
}
if (-not $ok) { Write-Host "servidor nao respondeu" -ForegroundColor Red; exit 1 }
Write-Host "servidor ok" -ForegroundColor Green
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-File","$repo\tunel.ps1" -WorkingDirectory $repo
for ($i = 0; $i -lt 70; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path (Join-Path $repo "painel-url.txt")) {
        $l = (Get-Content (Join-Path $repo "painel-url.txt") -Raw)
        if ($l -and $l.Trim().Length -gt 20) { Write-Host $l.Trim() -ForegroundColor Green; break }
    }
}