import os
import sys
import argparse
from pathlib import Path
import shutil
import subprocess
import shutil
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.text import Text
from modules.detect import find_novnc_dir, find_websockify_src_dir, is_websockify_installed, install_websockify, install_websockify_new_console
from modules.token import TokenEntry, load_tokens, save_tokens, validate_id, validate_ip, validate_port, generate_token
from modules.run import start_server, start_server_new_console
from modules.logger import info, warn, error, log
from modules.net import get_lan_ip, is_port_open
from modules.fetch import ensure_resources

console = Console()
#################################################################
# 这里是一键部署程序代码，听我的话，别乱动哦，嗯~乖宝宝
# 其实，我..累了
# 我知道正常人应该不会看注释的
# 我其实也不开心，我压力大的时候甚至会用小刀划自己
# 我将其作为一种解压的方式
# 我的人生，我的愁绪，就像一个永远递归的压缩文件
# 当然，我也因此住过一段时间的院(心理科)
# 但是问题没有解决，还在寒假加重了...
# 永远无法解压，永远没有尽头
# 但是我相信屏幕前的你不是这样子的
# 你们是热血的青年
# 毛主席眼中初升的红日，朝气蓬勃
# 我相信你们是不会注销地球Online账号的，对吧
# 活下去！活下去！活下去！活下去！在这反乌托邦里！
# 屏幕前的您们，不要走我(十月)的老路，哈哈
#[!NOTE!] Last Modify :2026/2/7 5:17
#[!NOTE!] Author : 十月玩电脑
#[!NOTE!] CodeBeautifuly(修改冗余代码逻辑变量和函数名) : openclaw(model:ClaudeOpus) , trea(model:Kimi-K2.5)
#################################################################
def build_layout(status_text, novnc_dir, websockify_installed, token_count, prompt_text=""):
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )
    header = Text(status_text)
    layout["header"].update(Panel(header, title="状态", border_style="green"))
    body = Layout()
    body.split_row(
        Layout(name="left"),
        Layout(name="right", ratio=2),
    )
    left_table = Table(title="检测结果", show_lines=True)
    left_table.add_column("项目", justify="left")
    left_table.add_column("值", justify="left")
    left_table.add_row("noVNC 目录", str(novnc_dir) if novnc_dir else "未发现")
    left_table.add_row("websockify 安装", "[green]已安装[/green]" if websockify_installed else "[red]未安装[/red]")
    left_table.add_row("token.conf 条目数", str(token_count))
    body["left"].update(Panel(left_table, border_style="cyan"))
    actions = Table(title="操作", show_lines=True)
    actions.add_column("编号", width=6)
    actions.add_column("说明")
    pwd_set = False
    try:
        if novnc_dir:
            p = novnc_dir / "pwd.conf"
            if p.exists() and p.read_text(encoding="utf-8", errors="ignore").strip():
                pwd_set = True
    except Exception:
        pwd_set = False
    actions.add_row("1", "安装 websockify")
    actions.add_row("2", "新增 Token")
    actions.add_row("3", "删除 Token")
    actions.add_row("4", "启动服务器")
    actions.add_row("5", "刷新检测")
    actions.add_row("6", "查看连接网址")
    actions.add_row("7", "[red]设置查看页面密码[/red]" if not pwd_set else "设置查看页面密码")
    actions.add_row("0", "退出")
    body["right"].update(Panel(actions, border_style="magenta"))
    layout["body"].update(body)
    lan_ip = get_lan_ip()
    footer_text = f"查看连接 http://{lan_ip}:6080/" if is_port_open(lan_ip, 6080) else "请先启动服务器"
    if prompt_text:
        footer_text = footer_text + "\n" + prompt_text
    layout["footer"].update(Panel(Text(footer_text), border_style="yellow"))
    return layout

def interactive():
    working_dir = Path.cwd()
    status = "准备就绪"
    script_path = Path(__file__).resolve()
    python_exec = sys.executable or "python"
    def new_console_run(cmd: str, cwd: Path):
        pwsh = shutil.which("powershell") or "powershell"
        CREATE_NEW_CONSOLE = 0x00000010
        subprocess.Popen([pwsh, "-NoExit", "-Command", f"Set-Location -Path '{str(cwd)}'; {cmd}"], creationflags=CREATE_NEW_CONSOLE)
    ensure_resources(working_dir, console)
    while True:
        novnc_dir = find_novnc_dir(working_dir)
        token_path = novnc_dir / "token.conf" if novnc_dir else None
        tokens = load_tokens(token_path) if token_path else []
        websockify_installed = is_websockify_installed()
        console.clear()
        console.print(build_layout(status, novnc_dir, websockify_installed, len(tokens), "[INFO] 请选择操作 [0/1/2/3/4/5/6/7] (默认5):"))
        choice = console.input("").strip() or "5"
        if choice == "0":
            break
        if choice == "5":
            status = "刷新完成"
            continue
        if choice == "1":
            src = find_websockify_src_dir(working_dir)
            if not src:
                error(console, "未找到 websockify 源目录")
                status = "未找到 websockify 源目录"
            else:
                ok, msg = install_websockify_new_console(src)
                info(console, msg)
                status = "已打开安装窗口"
            continue
        if choice == "2":
            if not novnc_dir:
                error(console, "未检测到 noVNC 目录")
                status = "未检测到 noVNC 目录"
                continue
            cmd = f"& '{python_exec}' -m modules.cli_tasks add-token-interactive"
            new_console_run(cmd, working_dir)
            status = "已打开新增窗口"
            continue
        if choice == "3":
            if not novnc_dir:
                error(console, "未检测到 noVNC 目录")
                status = "未检测到 noVNC 目录"
                continue
            cmd = f"& '{python_exec}' -m modules.cli_tasks del-token-interactive"
            new_console_run(cmd, working_dir)
            status = "已打开删除窗口"
            continue
        if choice == "4":
            if not novnc_dir:
                error(console, "未检测到 noVNC 目录")
                status = "未检测到 noVNC 目录"
                continue
            try:
                p = novnc_dir / "pwd.conf"
                if not (p.exists() and p.read_text(encoding="utf-8", errors="ignore").strip()):
                    error(console, "无法启动服务器：未设置查看页面密码")
                    status = "未设置密码"
                    continue
            except Exception:
                error(console, "无法启动服务器：未设置查看页面密码")
                status = "未设置密码"
                continue
            cmd = f"& '{python_exec}' -m modules.cli_tasks start-server-interactive"
            new_console_run(cmd, working_dir)
            status = "已打开启动窗口"
            continue
        if choice == "6":
            if not novnc_dir:
                error(console, "未检测到 noVNC 目录")
                status = "未检测到 noVNC 目录"
                continue
            cmd = f"& '{python_exec}' -m modules.cli_tasks view-urls"
            new_console_run(cmd, working_dir)
            status = "已打开查看网址窗口"
            continue
        if choice == "7":
            if not novnc_dir:
                error(console, "未检测到 noVNC 目录")
                status = "未检测到 noVNC 目录"
                continue
            cmd = f"& '{python_exec}' -m modules.cli_tasks set-view-password"
            new_console_run(cmd, working_dir)
            status = "已打开密码设置窗口"

def cli_add_token_interactive():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        console.print("未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    console.print("输入服务器ID(留空自动生成>360字符，默认400):")
    token_id = console.input("").strip()
    if not token_id:
        token_id = generate_token(400)
    console.print("输入目标 IP(默认127.0.0.1):")
    ip = console.input("").strip() or "127.0.0.1"
    console.print("输入端口(默认5900):")
    port_str = console.input("").strip() or "5900"
    if not validate_id(token_id):
        console.print("ID 必须大于64字符")
        sys.exit(1)
    if not validate_ip(ip):
        console.print("非法 IP")
        sys.exit(1)
    port_val = validate_port(port_str)
    if port_val is None:
        console.print("非法端口")
        sys.exit(1)
    tokens = load_tokens(token_path)
    tokens.append(TokenEntry(token_id, ip, port_val))
    ok, msg = save_tokens(token_path, tokens)
    console.print(msg)
    console.print(f"访问地址: http://localhost:6080/vnc.html?path=websockify?token={token_id}")

def cli_del_token_interactive():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        console.print("未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    tokens = load_tokens(token_path)
    if not tokens:
        console.print("当前无条目")
        sys.exit(0)
    table = Table(title="现有 Token")
    table.add_column("序号")
    table.add_column("ID")
    table.add_column("目标")
    for i, t in enumerate(tokens):
        table.add_row(str(i), t.id, f"{t.ip}:{t.port}")
    console.print(table)
    console.print("输入要删除的序号(默认0):")
    idx_str = console.input("").strip() or "0"
    try:
        idx = int(idx_str)
        if 0 <= idx < len(tokens):
            del tokens[idx]
            ok, msg = save_tokens(token_path, tokens)
            console.print(msg)
        else:
            console.print("序号无效")
    except ValueError:
        console.print("请输入数字")

def cli_add_token(token_id, ip, port):
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        console.print("未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    if not token_id:
        token_id = generate_token(66)
    if not validate_id(token_id):
        console.print("ID 必须大于64字符")
        sys.exit(1)
    if not validate_ip(ip):
        console.print("非法 IP")
        sys.exit(1)
    port_val = validate_port(port)
    if port_val is None:
        console.print("非法端口")
        sys.exit(1)
    tokens = load_tokens(token_path)
    tokens.append(TokenEntry(token_id, ip, port_val))
    ok, msg = save_tokens(token_path, tokens)
    console.print(msg)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    addp = sub.add_parser("add-token")
    addp.add_argument("--id", default="")
    addp.add_argument("--ip", required=True)
    addp.add_argument("--port", default="5900")
    sub.add_parser("add-token-interactive")
    sub.add_parser("del-token-interactive")
    args = parser.parse_args()
    if args.cmd == "add-token":
        cli_add_token(args.id, args.ip, args.port)
    elif args.cmd == "add-token-interactive":
        cli_add_token_interactive()
    elif args.cmd == "del-token-interactive":
        cli_del_token_interactive()
    else:
        interactive()

if __name__ == "__main__":
    main()

