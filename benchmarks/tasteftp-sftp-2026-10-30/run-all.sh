#!/usr/bin/env bash
# 방향 · 파일 묶음마다: 앱별 예열 1회, 측정 3회(순서 바꿈 T,F / F,T / T,F).
cd "$(dirname "$0")"
export MSYS_NO_PATHCONV=1
PY=${PY:-python}
for combo in "download big" "upload big" "download small" "upload small"; do
  BENCH_LABEL=warmup $PY bench.py tasteftp $combo
  BENCH_LABEL=warmup $PY bench.py filezilla $combo
  for order in "tasteftp filezilla" "filezilla tasteftp" "tasteftp filezilla"; do
    for app in $order; do
      BENCH_LABEL=measure $PY bench.py $app $combo
    done
  done
done
echo ALL-DONE
