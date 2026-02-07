from rich.console import Console

def info(console: Console, msg: str):
    console.print("[blue][INFO][/blue] " + msg)

def warn(console: Console, msg: str):
    console.print("[yellow][WARN][/yellow] " + msg)

def error(console: Console, msg: str):
    console.print("[red][ERROR][/red] " + msg)

def server(console: Console, msg: str):
    console.print("[green][SERVER][/green] " + msg)

def log(console: Console, msg: str):
    console.print("[magenta][LOG][/magenta] " + msg)

