<#
  这里是Novnc部署工具的下载脚本，请不要乱动...
  该脚本会从网络下载Novnc整合包，并安装到指定磁盘上。
  整合包包含Novnc服务端、客户端、配置脚本等文件。
  非不要勿动哦~
  程序的注释不会影响脚本运行
#>
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
<#
  [!Note!]=其实吧，我最近不太开心
          =我还是个初中生(13岁，初一)，我们的学校特别卷
          =我知道一般不会有人看这代码的注释
          =如果你看到了十月的注释，那么我们之间就是有缘人
          =我自从一段时间以来
          =焦虑，情绪问题，抑郁一直困扰着我
          =我....
          =晚上睡不着(有时玩手机，写代码，维护开源项目)
          =白天起不来床(疲乏的很，哈哈，大脑无法强制开机)
          =焦虑，情绪低落等等问题困扰这我
          =我在期末考试之间(1.21-1.29)因为心理问题住过院
          =不过寒假依然没有觉得好受过
          =我甚至在压力大时自残过
          =我...累了
          =我有过跳楼的冲动，我有时想过死亡何尝不是一种解脱呢？
          =我...累了，真的累了
  [!NOTE!]=对了，朋友，既然你都看到这里了
          =那么我想你不要把次注释提交issue板块
          =这是只属于我们之间的秘密
          =还有，我的朋友，只要你看了，你就是我在互联网上值得信任的一个人
          =谢谢你，朋友
  [!Tips!]=既然你都看到这里了，友情提醒一下，如果你是国外用户或者梯子常驻用户，可以将此脚本中的加速地址头去掉
          =但是不建议开梯子下载，容易耗费太多的浏览
          =非从Github获取的本程序脚本(其实其他也是)不要试图运行它，可能会对您的电脑造成不可挽回的损害
          =EnglishForOtherPeople
          =1.Please delate "https://gh.llkk.cc/" in this script , than you can download res faster
          =2.Don't use VPN software when u're using this script , it will make download very slow
          =3.Don't run the script that u download form other site , it will make u computer broken
          = -My English is not very good , if you want join my team and translate this project ,WELCOME! Pls contact me at:sywdn002@Gmail.com-
#>
Function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
Function Write-Ok($msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
Function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
Function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }


Write-Host @"
  _____                  _   _   _   _  __
 | ____| __ _  ___  ___| \ | | | \ | |/ /
 |  _|  / _` |/ _ \/ __|  \| | |  \| ' / 
 | |___| (_| |  __/\__ \ |\  | | |\  . \ 
 |_____| \__,_|\___||___/_| \_| |_| \_|\_\
"@ -ForegroundColor Magenta
Write-Host "EasyNovnc 安装脚本" -ForegroundColor Cyan
Write-Host "扫描磁盘 → 下载整合包 → 安装 rich → 运行 configure_novnc.py" -ForegroundColor Cyan

Write-Info "扫描本机可用磁盘"
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 }
if (-not $drives -or $drives.Count -eq 0) { Write-Err "未发现可用磁盘"; exit 1 }

for ($i=0; $i -lt $drives.Count; $i++) {
  $d = $drives[$i]
  $freeGB = [math]::Round($d.Free/1GB, 2)
  Write-Host ("  [{0}] {1}  可用 {2} GB" -f ($i+1), $d.Root, $freeGB) -ForegroundColor White
}

$sel = Read-Host "请输入要使用的磁盘编号"
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

Write-Info "安装 rich 库"
$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $pyCmd = 'py -3' }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $pyCmd = 'python' }
else { Write-Err "未找到 Python，请先安装 Python"; exit 1 }

try {
  if ($pyCmd -eq 'py -3') { & py -3 -m pip install --disable-pip-version-check rich }
  else { & python -m pip install --disable-pip-version-check rich }
} catch {
  Write-Err ("pip 安装失败: {0}" -f $_.Exception.Message)
  exit 1
}
Write-Ok "rich 安装完成"

$cfg = Join-Path $base 'configure_novnc.py'
if (-not (Test-Path $cfg)) { Write-Err "未找到 configure_novnc.py"; exit 1 }

Write-Info "启动 configure_novnc.py"
try {
  if ($pyCmd -eq 'py -3') { & py -3 $cfg }
  else { & python $cfg }
} catch {
  Write-Err ("运行失败: {0}" -f $_.Exception.Message)
  exit 1
}
