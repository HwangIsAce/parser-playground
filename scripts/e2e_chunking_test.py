#!/usr/bin/env python3
"""E2E Chunking test via Python (no curl). Run from playground root."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("pip/uv install httpx first")
    sys.exit(1)

API_BASE = "http://localhost:8000/api/v1"
SAMPLE = Path(__file__).parent.parent / "sample_excel.xlsx"
TIMEOUT_POST = 70.0   # backend -> Peter-parser can take ~60s
TIMEOUT_GET = 10.0
POLL_INTERVAL = 2
POLL_ATTEMPTS = 60


def main() -> int:
    if not SAMPLE.is_file():
        print(f"Error: {SAMPLE} not found")
        return 1

    print("=== E2E Chunking Test (Python) ===")
    print(f"1. POST {API_BASE}/chunking/parse ...")
    try:
        with open(SAMPLE, "rb") as f:
            content = f.read()
        r = httpx.post(
            f"{API_BASE}/chunking/parse",
            files={"file": (SAMPLE.name, content)},
            data={"document_type": "excel"},
            timeout=TIMEOUT_POST,
        )
    except httpx.ConnectError as e:
        print(f"   Connection failed: {e}")
        print("   Ensure Playground backend is running on 8000.")
        return 1
    except httpx.TimeoutException as e:
        print(f"   Timeout: {e}")
        return 1

    if r.status_code != 202:
        print(f"   HTTP {r.status_code}: {r.text[:300]}")
        return 1

    data = r.json()
    job_id = data.get("job_id") or ""
    doc_id = data.get("document_id") or ""
    if not job_id:
        print("   No job_id in response:", data)
        return 1
    print(f"   job_id={job_id} document_id={doc_id}")

    print(f"2. Polling GET /chunking/status/{job_id} ...")
    for i in range(POLL_ATTEMPTS):
        try:
            r2 = httpx.get(f"{API_BASE}/chunking/status/{job_id}", timeout=TIMEOUT_GET)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            print(f"   Attempt {i+1}: request failed: {e}")
            time.sleep(POLL_INTERVAL)
            continue
        st = r2.json().get("status", "")
        print(f"   Attempt {i+1}: status={st}")
        if st == "completed":
            break
        if st == "failed":
            err = r2.json().get("error", "")
            print(f"   Job failed: {err}")
            return 1
        time.sleep(POLL_INTERVAL)
    else:
        print("   Timeout waiting for completed")
        return 1

    print(f"3. GET /chunking/result/{job_id} ...")
    try:
        r3 = httpx.get(f"{API_BASE}/chunking/result/{job_id}", timeout=TIMEOUT_GET)
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        print(f"   Failed: {e}")
        return 1
    if r3.status_code != 200:
        print(f"   HTTP {r3.status_code}: {r3.text[:200]}")
        return 1
    result = r3.json()
    chunks = result.get("chunks") or []
    print(f"   Chunks: {len(chunks)}")
    for i, c in enumerate(chunks[:3]):
        text = (c.get("chunk") or "")[:80]
        print(f"   - #{i+1}: {text}...")

    print("=== E2E Test Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
