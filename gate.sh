#!/usr/bin/env bash
# Symposium gate: one entry point, one command per arm.
#
# .github/workflows/*.yml call this script instead of repeating commands, so a
# local run and CI run the same thing. Environment setup (`uv sync --locked
# --extra dev`) is the caller's job; every arm runs with --no-sync.
#
#   ./gate.sh                # default arm: test-fast
#   ./gate.sh list           # arm names, one per line
#   ./gate.sh lint|test|test-fast|build|program|site|docs|gnn|all
#
# `docs/_generated/gate-measurements.md` records this host's wall times; refresh
# it with `uv run --no-sync python scripts/gate_metrics.py refresh`.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PUBLIC_DIR="data/public/2026"
RUFF_TARGETS=(src/ tests/ scripts/ run.py launch.py)
GNN_ENV=".gate/gnn"

arm_lint() {
  uv run --no-sync ruff check "${RUFF_TARGETS[@]}"
  uv run --no-sync ruff format --check "${RUFF_TARGETS[@]}"
}

# Full suite with the pyproject coverage gate (the CI command).
arm_test() {
  uv run --no-sync python -m pytest --no-header
}

# The package-module suites only: fast signal, no artifact/publication pipelines
# and no subprocess-spawning workflow tests. Not a substitute for `test`.
arm_test_fast() {
  uv run --no-sync python -m pytest --no-header -q --no-cov -m "not real_api" \
    tests/test_core tests/test_io tests/test_cli tests/test_analysis \
    tests/test_generation tests/test_calendar
}

arm_build() {
  uv build
}

# Approved-public-tree verification plus site rendering. The renderer refuses an
# existing output directory, so an unset $GATE_SITE_OUT picks a fresh temporary
# path and a set one must not exist yet.
arm_site() {
  local out="${GATE_SITE_OUT:-}"
  if [ -z "$out" ]; then
    out="$(mktemp -d)/site"
    printf 'site: rendering into %s\n' "$out"
  elif [ -e "$out" ]; then
    printf 'site: %s already exists; point GATE_SITE_OUT at a new path\n' "$out" >&2
    return 1
  fi
  uv run --no-sync symposium organize site --public-dir "$PUBLIC_DIR" --output-dir "$out"
}

# Offline scaffolding and the checked-in approved program.
arm_program() {
  local site_root
  uv run --no-sync symposium --version
  uv run --no-sync symposium edition validate --year 2026
  uv run --no-sync symposium organize check-public --public-dir "$PUBLIC_DIR"
  uv run --no-sync symposium organize readiness --public-dir "$PUBLIC_DIR"
  site_root="$(mktemp -d)"
  GATE_SITE_OUT="$site_root/site" arm_site
  rm -rf "$site_root"
}

# Pinned GNN parser in an isolated environment; .github/gnn-pin.json decides the
# revision, so this arm needs no project environment (only network + git).
arm_gnn() {
  local spec
  rm -rf "$GNN_ENV"
  uv venv --quiet "$GNN_ENV"
  uv pip install --quiet --python "$GNN_ENV/bin/python" defusedxml psutil pyyaml
  spec="$("$GNN_ENV/bin/python" scripts/gnn_conformance.py --spec)"
  uv pip install --quiet --python "$GNN_ENV/bin/python" --no-deps "$spec"
  "$GNN_ENV/bin/python" scripts/gnn_conformance.py
}

arm_docs() {
  uv run --no-sync python scripts/check_docs.py
}

arms() {
  printf '%s\n' lint test test-fast build program site docs gnn
}

run_arm() {
  case "$1" in
    lint) "arm_lint" ;;
    test) "arm_test" ;;
    test-fast) "arm_test_fast" ;;
    build) "arm_build" ;;
    program) "arm_program" ;;
    site) "arm_site" ;;
    docs) "arm_docs" ;;
    gnn) "arm_gnn" ;;
    *) printf 'unknown arm: %s\n' "$1" >&2; exit 2 ;;
  esac
}

arm="${1:-test-fast}"
case "$arm" in
  list) arms ;;
  all)
    for name in $(arms); do
      printf '\n== %s ==\n' "$name"
      run_arm "$name"
    done
    ;;
  *) run_arm "$arm" ;;
esac
