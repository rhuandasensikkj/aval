$ErrorActionPreference = 'Stop'
cd C:\rat
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item cf.out -ErrorAction SilentlyContinue
Start-Process cmd.exe -ArgumentList '/c','.\cloudflared.exe tunnel --url http://localhost:8080 > cf.out 2>&1' -WindowStyle Hidden
$h = $null
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-Path cf.out) {
        $m = Select-String -Path cf.out -Pattern 'https://([a-z0-9-]+\.trycloudflare\.com)' -AllMatches
        if ($m) { $h = $m.Matches[0].Groups[1].Value; break }
    }
}
if (-not $h) { 'NAO ACHEI O HOST. Veja cf.out'; exit 1 }
"host: $h"
Set-Content host.txt $h -Encoding ascii -NoNewline
git add host.txt
git commit -m "host $h"
git push
"publicado. os aparelhos vao pegar em ate 1 minuto."