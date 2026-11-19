Add-Type -AssemblyName System.Drawing
$root = "C:\rat\app\src\main\res"
$map = @{ "mipmap-mdpi"=48; "mipmap-hdpi"=72; "mipmap-xhdpi"=96; "mipmap-xxhdpi"=144; "mipmap-xxxhdpi"=192 }
$fmt = New-Object System.Drawing.StringFormat
$fmt.Alignment = [System.Drawing.StringAlignment]::Center
$fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
function Icon($size,$path){
  $bmp = New-Object System.Drawing.Bitmap $size,$size
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::FromArgb(14,122,95))
  $white = [System.Drawing.Brushes]::White
  $soft = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(215,255,255,255))
  $f1 = New-Object System.Drawing.Font "Segoe UI", ($size*0.30), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
  $f2 = New-Object System.Drawing.Font "Segoe UI", ($size*0.125), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
  $r1 = New-Object System.Drawing.RectangleF 0, ($size*0.13), $size, ($size*0.42)
  $r2 = New-Object System.Drawing.RectangleF 0, ($size*0.58), $size, ($size*0.24)
  $g.DrawString("Elo", $f1, $white, $r1, $fmt)
  $g.DrawString("Educa" + [char]0xE7 + [char]0xE3 + "o", $f2, $soft, $r2, $fmt)
  $g.Dispose()
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
}
foreach ($k in $map.Keys) {
  $dir = Join-Path $root $k
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Icon $map[$k] (Join-Path $dir "ic.png")
}
Icon 512 "C:\rat\ic-512.png"
"pronto"
