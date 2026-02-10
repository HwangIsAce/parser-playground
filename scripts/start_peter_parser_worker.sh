#!/usr/bin/env bash
# Peter-parser RQ worker 시작 (Chunking 작업 처리)
# playground 루트 또는 scripts 폴더에서 실행: ./scripts/start_peter_parser_worker.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYGROUND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PETER_PARSER_DIR="${PETER_PARSER_DIR:-$PLAYGROUND_ROOT/../pipelines/parsing-pipeline/peter-parser}"

if [[ ! -d "$PETER_PARSER_DIR" ]]; then
  echo "Peter-parser not found at: $PETER_PARSER_DIR"
  echo "Set PETER_PARSER_DIR or place playground next to pipelines."
  exit 1
fi

cd "$PETER_PARSER_DIR"
echo "Starting Peter-parser RQ worker (default queue) in $(pwd)"
exec uv run python -m peter_parser.worker
