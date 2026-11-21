$ErrorActionPreference = "Continue"
$repo = $PSScriptRoot
$hostfile = Join-Path $repo "host.txt"
$cfg = Join-Path $repo "cloudflared.exe"
if (-not (Test-Path $cfg)) { $cfg = "cloudflared" }

while ($true) {
    Write-Host "[tunel] subindo"
    $log = Join-Path $env:TEMP "cf.err"
    $out = Join-Path $env:TEMP "cf.out"
    if (Test-Path $log) { Remove-Item $log -Force }
    $p = Start-Process -FilePath $cfg -ArgumentList "tunnel","--no-autoupdate","--url","http://localhost:8080" -RedirectStandardError $log -RedirectStandardOutput $out -PassThru -WindowStyle Hidden
    $url = $null
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 700
        if (Test-Path $log) {
            $m = Select-String -Path $log -Pattern "https://([a-z0-9-]+\.trycloudflare\.com)" -AllMatches
            if ($m) { $url = $m.Matches[0].Groups[1].Value; break }
        }
        if ($p.HasExited) { break }
    }
    if ($url) {
        Write-Host "[tunel] host: $url" -ForegroundColor Green
        Set-Content -Path $hostfile -Value $url -NoNewline -Encoding ascii
        Push-Location $repo
        git add host.txt | Out-Null
        git -c user.name="aval" -c user.email="aval@local" commit -m "host $url" | Out-Null
        git push origin main | Out-Null
        Pop-Location
        Write-Host "[tunel] painel: https://$url/?t=m4t7k2p9x6v3n8b5z1q0w7r2"
    } else {
        Write-Host "[tunel] sem URL, repetindo" -ForegroundColor Yellow
    }
    Wait-Process -Id $p.Id
    Start-Sleep -Seconds 5
}