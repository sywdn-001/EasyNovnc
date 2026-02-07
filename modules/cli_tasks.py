import sys
from pathlib import Path
import argparse
from rich.console import Console
from rich.table import Table
from modules.detect import find_novnc_dir, find_websockify_src_dir, is_websockify_installed, install_websockify, mark_websockify_installed
from modules.token import TokenEntry, load_tokens, save_tokens, validate_id, validate_ip, validate_port, generate_token
from modules.run import start_server
from modules.logger import info, warn, error, log
from modules.net import get_lan_ip
from modules.html import generate_index
import os
console = Console()
###########################################################
'''
反乌托邦中的争夺
把愿望敲碎成粉末
心灵也被挂上门锁
看不清灯火
但我还想做些什么
其实还想要说很多
请你等等我
请你等等我
两块五的签字笔
东拼西凑的词句
妄想用它拯救你
顺便拯救我自己
只因为
你那渴望自由的心脏
困在一张没空隙的网
我们的周围并非没光亮
只是太耀眼将我们灼伤
在这个世界难免会迷茫
但别再把小刀带在身上
至少我还在为你而歌唱
在黑暗漫长的反乌托邦
    ————《反乌托邦》 作者: 乌托邦P
'''
###########################################################
def cmd_set_view_password():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        error(console, "未找到 noVNC 目录")
        sys.exit(1)
    info(console, "输入查看页面密码(留空清除密码):")
    pwd = console.input("").strip()
    try:
        (novnc_dir / "pwd.conf").write_text(pwd, encoding="utf-8")
        if pwd:
            info(console, "密码已设置")
        else:
            info(console, "密码已清除")
        try:
            lan_ip = get_lan_ip()
            tokens = load_tokens(novnc_dir / "token.conf")
            generate_index(novnc_dir, tokens, 6080, lan_ip)
            info(console, f"入口页已更新: {novnc_dir / 'index.html'}")
        except Exception as e:
            warn(console, f"入口页更新失败: {e}")
    except Exception as e:
        error(console, f"写入失败: {e}")
def cmd_view_urls():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        error(console, "未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    tokens = load_tokens(token_path)
    if not tokens:
        warn(console, "当前无条目")
        sys.exit(0)
    info(console, "监听端口(默认6080):")
    port_str = console.input("").strip() or "6080"
    try:
        port_val = int(port_str)
    except ValueError:
        error(console, "端口无效")
        sys.exit(1)
    table = Table(title="连接地址", show_lines=True, expand=True)
    table.add_column("ID", overflow="fold")
    table.add_column("URL", overflow="fold")
    lan_ip = get_lan_ip()
    urls = []
    for t in tokens:
        url = f"http://{lan_ip}:{port_val}/vnc.html?path=websockify?token={t.id}"
        urls.append(url)
        table.add_row(t.id, url)
    console.print(table)
    out_file = novnc_dir / "urls.txt"
    try:
        out_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
        info(console, f"已导出: {out_file}")
        try:
            os.startfile(str(out_file))
        except Exception:
            pass
    except Exception as e:
        error(console, f"导出失败: {e}")

def cmd_check_install():
    working_dir = Path.cwd()
    src = find_websockify_src_dir(working_dir)
    if not src:
        error(console, "未找到 websockify 源目录")
        return
    installed = is_websockify_installed()
    if installed:
        info(console, "websockify 已安装")
        return
    ok, msg = install_websockify(src)
    info(console, msg)
    if ok:
        ok2, msg2 = mark_websockify_installed(src)
        info(console, msg2)
    installed2 = is_websockify_installed()
    info(console, "安装后状态: " + ("已安装" if installed2 else "未安装"))

def cmd_add_token_interactive():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        error(console, "未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    info(console, "输入服务器ID(留空自动生成>360字符，默认400):")
    token_id = console.input("").strip()
    if not token_id:
        token_id = generate_token(400)
    info(console, "输入目标 IP(默认127.0.0.1):")
    ip = console.input("").strip() or "127.0.0.1"
    info(console, "输入端口(默认5900):")
    port_str = console.input("").strip() or "5900"
    if not validate_id(token_id):
        error(console, "ID 必须大于64字符")
        sys.exit(1)
    if not validate_ip(ip):
        error(console, "非法 IP")
        sys.exit(1)
    port_val = validate_port(port_str)
    if port_val is None:
        error(console, "非法端口")
        sys.exit(1)
    tokens = load_tokens(token_path)
    tokens.append(TokenEntry(token_id, ip, port_val))
    ok, msg = save_tokens(token_path, tokens)
    info(console, msg)
    lan_ip = get_lan_ip()
    info(console, f"访问地址: http://{lan_ip}:6080/vnc.html?path=websockify?token={token_id}")

def cmd_del_token_interactive():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        error(console, "未找到 noVNC 目录")
        sys.exit(1)
    token_path = novnc_dir / "token.conf"
    tokens = load_tokens(token_path)
    if not tokens:
        warn(console, "当前无条目")
        sys.exit(0)
    table = Table(title="现有 Token", show_lines=True, expand=True)
    table.add_column("序号", width=6)
    table.add_column("ID", overflow="fold")
    table.add_column("目标", overflow="fold")
    for i, t in enumerate(tokens):
        table.add_row(str(i), t.id, f"{t.ip}:{t.port}")
    console.print(table)
    info(console, "输入要删除的序号(默认0):")
    idx_str = console.input("").strip() or "0"
    try:
        idx = int(idx_str)
        if 0 <= idx < len(tokens):
            del tokens[idx]
            ok, msg = save_tokens(token_path, tokens)
            info(console, msg)
        else:
            error(console, "序号无效")
    except ValueError:
        error(console, "请输入数字")

def cmd_start_server_interactive():
    working_dir = Path.cwd()
    novnc_dir = find_novnc_dir(working_dir)
    if not novnc_dir:
        error(console, "未找到 noVNC 目录")
        sys.exit(1)
    token_conf = novnc_dir / "token.conf"
    info(console, "监听端口(默认6080):")
    port_str = console.input("").strip() or "6080"
    try:
        port_val = int(port_str)
    except ValueError:
        error(console, "端口无效")
        sys.exit(1)
    lan_ip = get_lan_ip()
    tokens = load_tokens(token_conf)
    try:
        generate_index(novnc_dir, tokens, port_val, lan_ip)
        info(console, f"已生成入口: {novnc_dir / 'index.html'}")
    except Exception as e:
        warn(console, f"入口生成失败: {e}")
    start_server(novnc_dir, token_conf, port_val, console)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("check-install")
    sub.add_parser("add-token-interactive")
    sub.add_parser("del-token-interactive")
    sub.add_parser("start-server-interactive")
    sub.add_parser("view-urls")
    sub.add_parser("set-view-password")
    args = parser.parse_args()
    if args.cmd == "check-install":
        cmd_check_install()
    elif args.cmd == "add-token-interactive":
        cmd_add_token_interactive()
    elif args.cmd == "del-token-interactive":
        cmd_del_token_interactive()
    elif args.cmd == "start-server-interactive":
        cmd_start_server_interactive()
    elif args.cmd == "view-urls":
        cmd_view_urls()
    elif args.cmd == "set-view-password":
        cmd_set_view_password()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
