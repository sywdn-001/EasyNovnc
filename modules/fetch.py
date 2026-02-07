from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile
from rich.progress import Progress, BarColumn, DownloadColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn, SpinnerColumn
from rich.console import Console
from modules.logger import info

RES_URL = "https://gh.llkk.cc/https://github.com/sywdn-001/EasyNovnc/raw/refs/heads/main/vnc_res.zip"

def ensure_resources(base_dir: Path, console: Console):
    novnc = base_dir / "noVNC-1.6.0"
    ws = base_dir / "websockify-0.13.0"
    if novnc.exists() and ws.exists():
        return
    info(console, "未检测到资源文件，开始下载")
    target = base_dir / "vnc_res.zip"
    with Progress(
        SpinnerColumn(),
        TextColumn("[blue]下载 noVNC 整合包[/blue]"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("download", total=None)
        req = Request(RES_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp, open(target, "wb") as f:
            total = resp.headers.get("Content-Length")
            total_int = None
            try:
                total_int = int(total) if total else None
            except Exception:
                total_int = None
            if total_int:
                progress.update(task_id, total=total_int, completed=0)
            downloaded = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                progress.update(task_id, advance=len(chunk))
    with Progress(
        SpinnerColumn(),
        TextColumn("[green]解压 noVNC 整合包[/green]"),
        BarColumn(),
        console=console,
    ) as progress:
        task2 = progress.add_task("extract", total=100, completed=0)
        with ZipFile(target, "r") as z:
            namelist = z.namelist()
            count = len(namelist) or 1
            done = 0
            for name in namelist:
                z.extract(name, base_dir)
                done += 1
                progress.update(task2, completed=int(done / count * 100))
    try:
        target.unlink()
    except Exception:
        pass
