import os
import shutil
from pathlib import Path
from subprocess import Popen, PIPE
from rich.console import Console
from modules.logger import server, error

def start_server(novnc_dir: Path, token_conf: Path, port: int, console: Console):
    exe = shutil.which("websockify.exe") or shutil.which("websockify")
    if exe:
        cmd = [exe, "--web", "./", f"--target-config=./{token_conf.name}", str(port)]
        cmd = [exe, "--web", "./", f"--target-config=./{token_conf.name}", str(port)]
    else:
        py = shutil.which("py") or shutil.which("python") or "python"
        cmd = [py, "-m", "websockify", "--web", "./", f"--target-config=./{token_conf.name}", str(port)]
    proc = Popen(cmd, cwd=str(novnc_dir), stdout=PIPE, stderr=PIPE, text=True)
    try:
        for line in proc.stdout:
            server(console, line.rstrip())
    except Exception as e:
        error(console, str(e))
    finally:
        err = proc.stderr.read()
        if err:
            error(console, err)

def start_server_new_console(novnc_dir: Path, token_conf: Path, port: int, console: Console):
    exe = shutil.which("websockify.exe") or shutil.which("websockify")
    if exe:
        cmd_str = f"& '{exe}' --web ./ --target-config=./{token_conf.name} {port}"
    else:
        py = shutil.which("py") or shutil.which("python") or "python"
        cmd_str = f"& '{py}' -m websockify --web ./ --target-config=./{token_conf.name} {port}"
    pwsh = shutil.which("powershell") or "powershell"
    CREATE_NEW_CONSOLE = 0x00000010
    Popen([pwsh, "-NoExit", "-Command", f"Set-Location -Path '{str(novnc_dir)}'; {cmd_str}"], creationflags=CREATE_NEW_CONSOLE)
