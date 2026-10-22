# burn_windows.ps1 - token burner buat Windows PowerShell
# Paste seluruh isi file ini ke PowerShell, atau jalankan: powershell -ExecutionPolicy Bypass -File burn_windows.ps1
# Default: ~1 juta token input per request, loop sampai limit/Ctrl-C.

$ErrorActionPreference = "Continue"

$url   = "https://9router.haviq.dev/v1/chat/completions"
$key   = "sk-6b3ac6ef8e3b70c9-vr88tq-8a4cba7f"
$model = "kl/deepseek-v4.1-flash"

$promptTokens = 1000000
$sleepSec     = 10
$maxTokens    = 64

$logDir   = Join-Path $env:TEMP "token_burner"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$payload  = Join-Path $logDir "payload.json"
$codesLog = Join-Path $logDir "codes.log"

# Bangun prompt besar. PENTING: pakai -join, karena "str" * n di PowerShell bikin ARRAY.
$unit = "Jelaskan secara sangat panjang dan mendetail topik berikut dari sudut teknis, historis, praktis, ekonomi, sosial, dan filosofis: "
$reps = [Math]::Max(1, [int](($promptTokens * 4) / $unit.Length))
$content = ($unit * $reps) -join ''

$body = @{
  model      = $model
  messages   = @(@{ role = "user"; content = $content })
  max_tokens = $maxTokens
  stream     = $false
} | ConvertTo-Json -Depth 10 -Compress

[System.IO.File]::WriteAllText($payload, $body, [System.Text.Encoding]::UTF8)
Write-Host ("payload siap: {0} bytes (~{1} token input)" -f $body.Length, [int]($content.Length / 4))
Write-Host "mulai loop. Ctrl-C buat stop. log: $codesLog"

while ($true) {
  try {
    $code = & curl.exe -sS -o NUL -w "%{http_code}" -X POST $url `
        -H "Authorization: Bearer $key" `
        -H "Content-Type: application/json" `
        --max-time 300 `
        --data-binary "@$payload"
  } catch {
    $code = "ERR"
  }

  $stamp = Get-Date -Format "HH:mm:ss"
  $line  = "$stamp code=$code"
  Write-Host $line
  Add-Content -Path $codesLog -Value $line

  if ($code -eq "429" -or $code -eq "403") {
    Write-Host "LIMIT - stop"
    break
  }
  Start-Sleep -Seconds $sleepSec
}
