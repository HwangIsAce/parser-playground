#!/usr/bin/env python3
"""Run RQ worker with backend as cwd and config loaded.

Use this so the worker always runs from the backend directory and uses
the same config (PARSER_API_BASE_URL, etc.) as the API. Prevents
Job polling timeout and ensures Docling/Chandra requests go to the
remote parser API (e.g. http://194.68.245.19:22159).

On macOS, RQ forks a work-horse process; Objective-C runtime can crash
the child (SIGABRT). The env var must be set before the process starts,
so we re-exec with OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES.

Usage (from repo root or anywhere):
  cd backend && uv run python scripts/run_rq_worker.py

Or from backend:
  uv run python scripts/run_rq_worker.py
"""
import os
import sys

# macOS: re-exec with OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES so the env var
# is present before any ObjC/fork (RQ work-horse would otherwise get SIGABRT).
if sys.platform == "darwin" and os.environ.get("OBJC_DISABLE_INITIALIZE_FORK_SAFETY") != "YES":
    env = os.environ.copy()
    env["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    os.execve(sys.executable, [sys.executable] + sys.argv, env)
    # not reached

import logging

# Ensure we run from the backend directory (parent of scripts/)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.getcwd() != backend_dir:
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)

# Configure logging so we see ParserAPIClient and parse_worker messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# Load config and log so we can confirm remote API is used
from config import settings
logging.getLogger(__name__).info(
    "Worker config: PARSER_API_ENABLED=%s PARSER_API_BASE_URL=%s",
    settings.PARSER_API_ENABLED,
    settings.PARSER_API_BASE_URL,
)

# Start RQ worker (parse_queue)
sys.argv = ["rq", "worker", "parse_queue"]
from rq.cli import main
main()
