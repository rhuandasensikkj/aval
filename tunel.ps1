$ErrorActionPreference = "Continue"
$repo = $PSScriptRoot
$hostfile = Join-Path $repo "host.txt"
$local = Join-Path $repo "painel-url.txt"
$cfg = Join-Path $repo "cloudflared.exe"
if (-not (Test-Path $cfg)) { $cfg = "cloudflared" }

while ($true) {
    Write-Host "[tunel] abrindo"
    $log = Join-Path $env:TEMP "cf.err"
    if (Test-Path $log) { Remove-Item $log -Force }
    $p = Start-Process -FilePath $cfg -ArgumentList "tunnel","--no-autoupdate","--protocol","http2","--edge-ip-version","4","--url","http://127.0.0.1:8080" -RedirectStandardError $log -RedirectStandardOutput (Join-Path $env:TEMP "cf.out") -PassThru -WindowStyle Hidden

    $url = $null
    for ($i = 0; $i -lt 80; $i++) {
        Start-Sleep -Milliseconds 750
        if (Test-Path $log) {
            $m = Select-String -Path $log -Pattern "https://([a-z0-9-]+\.trycloudflare\.com)" -AllMatches
            if ($m) { $url = $m.Matches[0].Groups[1].Value; break }
        }
        if ($p.HasExited) { break }
    }

    if ($url) {
        $link = "https://$url/?t=m4t7k2p9x6v3n8b5z1q0w7r2"
        Write-Host "[tunel] $link" -ForegroundColor Green
        Set-Content -Path $hostfile -Value $url -NoNewline -Encoding ascii
        Set-Content -Path $local -Value $link -NoNewline -Encoding ascii
        Push-Location $repo
        git add host.txt 2>$null | Out-Null
        git -c user.name="aval" -c user.email="aval@local" commit -m "host $url" 2>$null | Out-Null
        git push origin main 2>$null | Out-Null
        Pop-Location
    } else {
        Write-Host "[tunel] sem endereco, repetindo" -ForegroundColor Yellow
    }
    Wait-Process -Id $p.Id
    Start-Sleep -Seconds 3
}