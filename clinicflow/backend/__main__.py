import os
import socket
import uvicorn
import urllib.request
import urllib.error
from pathlib import Path


def _find_port(preferred: int = 8000, max_tries: int = 30) -> int:
    host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    p = preferred
    for _ in range(max_tries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, p))
            s.close()
            return p
        except OSError:
            p += 1
        finally:
            try:
                s.close()
            except Exception:
                pass
    return preferred


def _load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" in s:
                k, v = s.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main():
    _load_env()
    host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    port_env = os.environ.get("BACKEND_PORT")
    port = int(port_env) if port_env else _find_port(8000)
    reload = os.environ.get("RELOAD") == "1"

    print(f"Starting ClinicFlow backend on http://{host}:{port} (reload={reload})")
    try:
        uvicorn.run("backend.main:app", host=host, port=port, reload=reload, factory=False)
    except OSError:
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=0.5) as resp:
                if resp.status == 200:
                    print(f"Backend already running at http://{host}:{port}; reusing existing instance")
                    return
        except Exception:
            pass
        alt = _find_port(port + 1)
        print(f"Port {port} busy, retrying on {alt}")
        uvicorn.run("backend.main:app", host=host, port=alt, reload=reload, factory=False)


if __name__ == "__main__":
    main()
