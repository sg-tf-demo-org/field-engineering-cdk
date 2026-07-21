#!/usr/bin/env bash
# Synthesize a CDK project to CloudFormation, THEN hand off to the governance scanner.
#
# Core principle: we never scan CDK source directly. Any CDK (Python or TS) is first
# synthesized to CloudFormation, and the resulting templates in cdk.out/ are scanned
# by governance/scan-cfn.sh — the exact same gate CFN goes through.
#
# Usage:  governance/synth-cdk.sh <cdk-project-dir> [--scan]
#   <cdk-project-dir>  directory containing cdk.json
#   --scan             run governance/scan-cfn.sh on the synthesized cdk.out
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="${1:-}"
DO_SCAN="${2:-}"

if [[ -z "$PROJ" || ! -f "$PROJ/cdk.json" ]]; then
  echo "usage: $0 <cdk-project-dir with cdk.json> [--scan]" >&2
  exit 2
fi

cd "$PROJ"
echo "== CDK synth in $PROJ =="

# Python vs TypeScript project detection.
if [[ -f requirements.txt || -f app.py || -f setup.py ]]; then
  echo "-> Python CDK project"
  python3 -m venv .venv >/dev/null 2>&1 || true
  # shellcheck disable=SC1091
  source .venv/bin/activate 2>/dev/null || true
  [[ -f requirements.txt ]] && pip install --quiet -r requirements.txt 2>/dev/null || true
fi
if [[ -f package.json ]]; then
  echo "-> installing node deps"
  npm ci --silent 2>/dev/null || npm install --silent 2>/dev/null || true
fi

OUT="cdk.out"
echo "-> synthesizing to $OUT"
if command -v cdk >/dev/null 2>&1; then
  cdk synth --all -o "$OUT" -c env=dev -c owner=platform -c costCenter=FE-DEMO >/dev/null
else
  npx --yes aws-cdk synth --all -o "$OUT" -c env=dev -c owner=platform -c costCenter=FE-DEMO >/dev/null
fi
rc=$?
if [[ $rc -ne 0 ]]; then
  echo "cdk synth FAILED (rc=$rc)" >&2
  exit $rc
fi

echo "-> synthesized templates:"
find "$OUT" -maxdepth 1 -name '*.template.json' | sed 's/^/     /'

if [[ "$DO_SCAN" == "--scan" ]]; then
  echo
  "$SCRIPT_DIR/scan-cfn.sh" "$OUT"
  exit $?
fi
echo "Done. Scan with: governance/scan-cfn.sh $PROJ/$OUT"
