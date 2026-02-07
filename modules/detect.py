import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from subprocess import Popen, PIPE
import subprocess

console = Console()

def find_novnc_dir(base: Path) -> Optional[Path]:
    candidates = [p for p in base.iterdir() if p.is_dir() and p.name.lower().startswith("novnc-")]
    return candidates[0] if candidates else None

def find_websockify_src_dir(base: Path) -> Optional[Path]:
    candidates = [p for p in base.iterdir() if p.is_dir() and p.name.lower().startswith("websockify-")]
    return candidates[0] if candidates else None

def is_websockify_installed() -> bool:
    base = Path.cwd()
    src = find_websockify_src_dir(base)
    if not src:
        return False
    return (src / "install.txt").exists()

def python_cmd() -> str:
    return shutil.which("py") or shutil.which("python") or "python"

def install_websockify(src_dir: Path) -> Tuple[bool, str]:
    setup = src_dir / "setup.py"
    if not setup.exists():
        return False, "未找到 setup.py"
    cmd = [python_cmd(), str(setup), "install"]
    try:
        proc = Popen(cmd, cwd=str(src_dir), stdout=PIPE, stderr=PIPE, text=True)
        out, err = proc.communicate()
        if proc.returncode == 0:
            return True, out or "安装成功"
        return False, err or "安装失败"
    except Exception as e:
        return False, str(e)

def install_websockify_new_console(src_dir: Path) -> Tuple[bool, str]:
    setup = src_dir / "setup.py"
    if not setup.exists():
        return (False, "未找到 setup.py")
    py = python_cmd()
    pwsh = shutil.which("powershell") or "powershell"
    CREATE_NEW_CONSOLE = 0x00000010
    try:
        subprocess.Popen([pwsh, "-Command", f"$ErrorActionPreference='Stop'; Set-Location -Path '{str(src_dir)}'; & '{py}' '{str(setup)}' install; 'installed' | Out-File -FilePath 'install.txt' -Encoding utf8 -Force; Write-Host '安装流程已执行'; $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"], creationflags=CREATE_NEW_CONSOLE)
        return (True, "已在新窗口启动安装")
    except Exception as e:
        return (False, str(e))

def mark_websockify_installed(src_dir: Path) -> Tuple[bool, str]:
    try:
        (src_dir / "install.txt").write_text("installed", encoding="utf-8")
        return True, "已创建 install.txt"
    except Exception as e:
        return False, str(e)
