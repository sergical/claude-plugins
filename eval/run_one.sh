#!/bin/zsh
# usage: run_one.sh <type> <size> <rep>
ROOT="${0:A:h}"
t=$1; n=$2; r=$3
out="$ROOT/raw/${t}_${n}_r${r}.json"
[ -s "$out" ] && grep -q '"is_error":false' "$out" && exit 0
prompt=$(python3 "$ROOT/prompt.py" "$t" "$ROOT/sizes/${t}_${n}.png")
cd "$ROOT"
for attempt in 1 2; do
  claude -p --model claude-opus-5-5 --output-format json --safe-mode --strict-mcp-config \
    --tools Read --allowedTools Read --no-session-persistence "$prompt" > "$out" 2> "$ROOT/raw/${t}_${n}_r${r}.err"
  grep -q '"is_error":false' "$out" && exit 0
  echo "retry $t $n $r" >> "$ROOT/raw/retries.log"
done
