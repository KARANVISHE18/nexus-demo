#!/usr/bin/env bash
# Runs one pipeline stage, saves its log (<name>.log) and its duration in seconds (<name>.dur).
# Usage: bash scripts/stage.sh <name> <command...>
name="$1"; shift
start=$(date +%s)
"$@" 2>&1 | tee "$name.log"
rc=${PIPESTATUS[0]}
echo $(( $(date +%s) - start )) > "$name.dur"
exit $rc
