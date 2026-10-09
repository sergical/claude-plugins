#!/bin/zsh
# Regenerates the test images, asks Claude about every image x size x repeat, and writes results.md.
# Needs macOS (sips), Google Chrome, and a logged-in `claude` CLI. Optional arg: random seed (default 4242).
set -eu
ROOT="${0:A:h}"
cd "$ROOT"
SIZES=(2000 1568 1280 1024 768)
python3 gen.py "$@"
mkdir -p sizes raw
for m in masters/*.png; do
  for n in $SIZES; do sips -Z $n $m --out sizes/${m:t:r}_$n.png >/dev/null; done
done
for m in masters/*.png; do for n in $SIZES; do for r in 1 2; do echo "${m:t:r} $n $r"; done; done; done > jobs.txt
xargs -P 4 -L 1 ./run_one.sh < jobs.txt
python3 score.py
