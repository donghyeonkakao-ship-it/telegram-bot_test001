#!/usr/bin/env bash
# 검증용 스틸: 0, 3, 6, 9초 (24fps)
set -euo pipefail
mkdir -p out/stills
for sec in 0 3 6 9; do
  npx remotion still Main "out/stills/t${sec}s.png" --frame=$((sec * 24)) --log=error
done
