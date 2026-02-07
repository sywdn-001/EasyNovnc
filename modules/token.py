from pathlib import Path
from typing import List, Tuple, Optional
import ipaddress
import secrets
import string

class TokenEntry:
    def __init__(self, token_id: str, ip: str, port: int):
        self.id = token_id
        self.ip = ip
        self.port = port

def validate_id(token_id: str) -> bool:
    return isinstance(token_id, str) and len(token_id) > 360

def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def validate_port(port_str: str) -> Optional[int]:
    try:
        p = int(port_str)
        if 1 <= p <= 65535:
            return p
        return None
    except Exception:
        return None

def parse_line(line: str) -> Optional[TokenEntry]:
    if ":" not in line:
        return None
    first, rest = line.split(":", 1)
    rest = rest.strip()
    if ":" in rest:
        host, port = rest.split(":", 1)
        try:
            port_val = int(port)
        except Exception:
            return None
    else:
        host = rest
        port_val = 5900
    if not validate_id(first) or not validate_ip(host):
        return None
    return TokenEntry(first, host, port_val)

def format_entry(entry: TokenEntry) -> str:
    return f"{entry.id}: {entry.ip}:{entry.port}"

def load_tokens(path: Path) -> List[TokenEntry]:
    if not path or not path.exists():
        return []
    data = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    result: List[TokenEntry] = []
    for line in data:
        line = line.strip()
        if not line:
            continue
        item = parse_line(line)
        if item:
            result.append(item)
    return result

def save_tokens(path: Path, tokens: List[TokenEntry]) -> Tuple[bool, str]:
    try:
        if path.exists():
            backup = path.with_suffix(".conf.bak")
            backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        content = "\n".join(format_entry(t) for t in tokens) + ("\n" if tokens else "")
        path.write_text(content, encoding="utf-8")
        return True, "保存成功"
    except Exception as e:
        return False, f"保存失败: {e}"

def generate_token(length: int = 400) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
