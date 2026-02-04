#!/usr/bin/env python3
"""Check connectivity to the GPU parser server (22159)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

def main():
    url = getattr(settings, "PARSER_API_BASE_URL", "http://194.68.245.19:22159")
    enabled = getattr(settings, "PARSER_API_ENABLED", False)
    print(f"PARSER_API_ENABLED = {enabled}")
    print(f"PARSER_API_BASE_URL = {url}")
    if not enabled:
        print("Remote parser is DISABLED. Set PARSER_API_ENABLED=True to use GPU server.")
        return 1

    try:
        import httpx
        base = url.rstrip("/")
        r = httpx.get(base, timeout=10.0)
        print(f"GET {base} -> {r.status_code}")
        print("OK: GPU server is reachable from this machine.")
        return 0
    except httpx.ConnectError as e:
        print(f"CONNECTION FAILED: Cannot reach {url}")
        print(f"  (Check network/firewall. Worker runs on this machine and must reach 22159.)")
        print(f"  {e}")
        return 1
    except httpx.TimeoutException as e:
        print(f"TIMEOUT: {url} did not respond in 10s")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
