$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host @"
  _____                  _   _   _   _  __
 | ____| __ _  ___  ___| \ | | | \ | |/ /
 |  _|  / _` |/ _ \/ __|  \| | |  \| ' / 
 | |___| (_| |  __/\__ \ |\  | | |\  . \ 
 |_____| \__,_|\___||___/_| \_| |_| \_|\_\
"@ -ForegroundColor Magenta
Write-Host "EasyNovnc Setup Script" -ForegroundColor Cyan
Write-Host "扫描磁盘 �?下载整合�?�?安装 rich �?运行配置程序" -ForegroundColor Cyan

Function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
Function Write-Ok($msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
Function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
Function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Info "扫描本机可用磁盘"
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 }
if (-not $drives -or $drives.Count -eq 0) { Write-Err "未发现可用磁�?; exit 1 }

for ($i=0; $i -lt $drives.Count; $i++) {
  $d = $drives[$i]
  $freeGB = [math]::Round($d.Free/1GB, 2)
  Write-Host ("  [{0}] {1}  可用 {2} GB" -f ($i+1), $d.Root, $freeGB) -ForegroundColor White
}

$sel = Read-Host "请输入要使用的磁盘编�?
if (-not ($sel -as [int]) -or [int]$sel -lt 1 -or [int]$sel -gt $drives.Count) { Write-Err "选择无效"; exit 1 }
$drive = $drives[[int]$sel - 1]
Write-Ok ("已选择磁盘: {0}" -f $drive.Root)

$base = Join-Path $drive.Root "EasyNovnc"
Write-Info ("创建目录: {0}" -f $base)
New-Item -ItemType Directory -Path $base -Force | Out-Null

$zipUrl = 'https://gh.llkk.cc/https://github.com/sywdn-001/EasyNovnc/raw/refs/heads/main/main.zip'
$outZip = Join-Path $base 'main.zip'

Write-Info "下载部署包到: $outZip"
try {
  Invoke-WebRequest -Uri $zipUrl -OutFile $outZip
} catch {
  Write-Err ("下载失败: {0}" -f $_.Exception.Message)
  exit 1
}
Write-Ok "下载完成"

Write-Info "解压部署包到: $base"
try {
  Expand-Archive -Path $outZip -DestinationPath $base -Force
} catch {
  Write-Err ("解压失败: {0}" -f $_.Exception.Message)
  exit 1
}
Write-Ok "解压完成"

Write-Info "删除下载文件"
try { Remove-Item $outZip -Force } catch { Write-Warn ("删除失败: {0}" -f $_.Exception.Message) }

Set-Location $base

Write-Info "安装 rich �?
$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $pyCmd = 'py -3' }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $pyCmd = 'python' }
else { Write-Err "未找�?Python，请先安�?Python"; exit 1 }

try {
  if ($pyCmd -eq 'py -3') { & py -3 -m pip install --disable-pip-version-check rich }
  else { & python -m pip install --disable-pip-version-check rich }
} catch {
  Write-Err ("pip 安装失败: {0}" -f $_.Exception.Message)
  exit 1
}
Write-Ok "rich 安装完成"

$cfg = Join-Path $base 'configure_novnc.py'
if (-not (Test-Path $cfg)) { Write-Err "未找�?configure_novnc.py"; exit 1 }

Write-Info "启动 configure_novnc.py"
try {
  if ($pyCmd -eq 'py -3') { & py -3 $cfg }
  else { & python $cfg }
} catch {
  Write-Err ("运行失败: {0}" -f $_.Exception.Message)
  exit 1
}
