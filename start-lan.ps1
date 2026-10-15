$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverDir = Join-Path $root 'server'
$clientDir = Join-Path $root 'client'

if (-not (Test-Path (Join-Path $serverDir '.venv\Scripts\python.exe'))) {
  throw 'Không tìm thấy server\.venv\Scripts\python.exe. Hãy tạo môi trường Python trước.'
}
if (-not (Test-Path (Join-Path $clientDir 'node_modules'))) {
  throw 'Không tìm thấy client\node_modules. Hãy chạy npm install trong thư mục client trước.'
}

Start-Process powershell -WorkingDirectory $serverDir -ArgumentList @(
  '-NoExit', '-Command', '& .\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000'
)
Start-Process powershell -WorkingDirectory $clientDir -ArgumentList @(
  '-NoExit', '-Command', 'npm run dev'
)

Write-Host 'Frontend: http://192.168.1.93:5173'
Write-Host 'Backend:  http://192.168.1.93:8000/api/v1/health/'
