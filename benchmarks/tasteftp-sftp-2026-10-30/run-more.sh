#!/usr/bin/env bash
# 1차에서 3회였던 묶음은 2회를 더해 5회로, 실패한 업로드 · 작은 파일은 예열 1회 + 5회.
cd "$(dirname "$0")"
export MSYS_NO_PATHCONV=1
PY=${PY:-python}
for combo in "download big" "upload big" "download small"; do
  for order in "filezilla tasteftp" "tasteftp filezilla"; do
    for app in $order; do BENCH_LABEL=measure $PY bench.py $app $combo; done
  done
done
BENCH_LABEL=warmup $PY bench.py tasteftp upload small
BENCH_LABEL=warmup $PY bench.py filezilla upload small
for order in "tasteftp filezilla" "filezilla tasteftp" "tasteftp filezilla" "filezilla tasteftp" "tasteftp filezilla"; do
  for app in $order; do BENCH_LABEL=measure $PY bench.py $app upload small; done
done
echo ALL-DONE
