$repo = $PSScriptRoot
Set-Location $repo
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue) }
if (-not $py) { Write-Host "python nao encontrado no PATH" -ForegroundColor Red; exit 1 }
Start-Process -FilePath $py.Source -ArgumentList "server.py" -WorkingDirectory $repo
Start-Sleep -Seconds 2
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-File","$repo\tunel.ps1" -WorkingDirectory $repo
Write-Host "local: http://localhost:8080/?t=m4t7k2p9x6v3n8b5z1q0w7r2"