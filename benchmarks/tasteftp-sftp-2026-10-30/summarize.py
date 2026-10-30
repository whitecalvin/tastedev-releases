import json, os, statistics, sys

rows = [json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), "results.jsonl"), encoding="utf-8")]
rows = [r for r in rows if r.get("label") == "measure"]
print("| 방향 | 파일 | 앱 | 중앙값(초) | 최소~최대(초) | 중앙값 MiB/s | 해시 불일치 | 오류 |")
print("| --- | --- | --- | ---: | ---: | ---: | ---: | --- |")
for direction in ("download", "upload"):
    for ds in ("big", "small"):
        meds = {}
        for app in ("tasteftp", "filezilla"):
            rs = [r for r in rows if r["direction"] == direction and r["dataset"] == ds and r["app"] == app]
            secs = [r["seconds"] for r in rs if r.get("seconds")]
            if not secs:
                continue
            med = statistics.median(secs)
            meds[app] = med
            mib = rs[0]["bytes"] / 1048576
            print(f"| {'다운로드' if direction == 'download' else '업로드'} | {'1 GiB × 1' if ds == 'big' else '64 KiB × 1,000'} | "
                  f"{'TASTEFTP' if app == 'tasteftp' else 'FileZilla'} | {med:.2f} | {min(secs):.2f}~{max(secs):.2f} | {mib / med:.1f} | "
                  f"{sum(r.get('mismatches') or 0 for r in rs)} | {', '.join(str(r.get('error')) for r in rs if r.get('error')) or '없음'} |")
        if len(meds) == 2:
            print(f"|  |  | **차이** | FileZilla 대비 TASTEFTP {meds['filezilla'] / meds['tasteftp']:.2f}배 |  |  |  |  |", file=sys.stderr)
