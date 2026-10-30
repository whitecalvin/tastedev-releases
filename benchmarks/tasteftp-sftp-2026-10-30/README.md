# TASTEFTP vs FileZilla — SFTP transfer benchmark (2026-10-30)

> **English** — Same PC, same LAN server, same synthetic files, SFTP only, 2 concurrent transfers (FileZilla's default).
> Measured by GXSOFT (the maker of TASTEFTP). Median of 5 runs after 1 warm-up per app. All 40 measured runs succeeded; 0 SHA-256 mismatches.
>
> | Transfer | TASTEFTP 0.2.50 | FileZilla 3.71.1 | Result |
> | --- | ---: | ---: | --- |
> | Download 1 GiB × 1 | 13.73 s (74.6 MiB/s) | 23.87 s (42.9 MiB/s) | ≈1.7× faster |
> | Download 64 KiB × 1,000 | 26.71 s | 47.57 s | ≈1.8× faster |
> | Upload 64 KiB × 1,000 | 11.17 s | 34.73 s | ≈3.1× faster |
> | Upload 1 GiB × 1 | 14.68 s | 16.77 s | **no clear difference** (run-to-run ranges overlap) |
>
> Limits: one network and one server; FTP/FTPS not measured; WinSCP/Cyberduck not measured; TASTEFTP was driven through its
> command-line batch transfer (same transfer engine as the GUI), FileZilla through its GUI transfer queue. Details below (Korean).

GXSOFT 가 TASTEFTP 와 FileZilla Client 의 SFTP 전송 시간을 같은 조건에서 잰 결과입니다. **만든 회사가 직접 잰 값**이므로,
아래 조건과 원본 기록(`results.jsonl`) · 측정 스크립트를 함께 공개합니다.

## 결과

측정 5회의 중앙값입니다. 앱마다 예열 1회는 뺐습니다.

| 방향 | 파일 | TASTEFTP 중앙값 | FileZilla 중앙값 | TASTEFTP 범위 | FileZilla 범위 | FileZilla ÷ TASTEFTP | 보수적 비율¹ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 다운로드 | 1 GiB × 1 | 13.73초 (74.6 MiB/s) | 23.87초 (42.9 MiB/s) | 12.35~15.94초 | 23.15~24.52초 | 1.74 | 1.47 |
| 다운로드 | 64 KiB × 1,000 | 26.71초 | 47.57초 | 22.35~31.05초 | 40.95~99.52초 | 1.78 | 1.76 |
| 업로드 | 1 GiB × 1 | 14.68초 (69.8 MiB/s) | 16.77초 (61.1 MiB/s) | 13.12~25.50초 | 9.52~21.24초 | 1.14 — 범위가 겹쳐 **차이 없음**으로 봅니다 | 1.05 |
| 업로드 | 64 KiB × 1,000 | 11.17초 | 34.73초 | 10.77~11.49초 | 31.75~37.73초 | 3.11 | 3.02 |

¹ TASTEFTP 시간을 명령줄 프로세스가 끝난 때(전송 뒤 SHA-256 확인 포함)로 잡은 값입니다. 가장 불리하게 잡아도 결론이 같은지 보려는 열입니다.

측정 40회가 모두 성공했고, 대상 파일 SHA-256 불일치는 0건입니다. 첫 실행에서 업로드 · 작은 파일 묶음은 측정 스크립트 오류(명령줄 길이 초과)로
기록되지 않아, 고친 뒤 예열부터 다시 쟀습니다.

## 조건

| 항목 | 값 |
| --- | --- |
| 클라이언트 | Windows 11 Pro PC, 유선 1 Gbps |
| 서버 | 같은 LAN 의 Ubuntu 서버, OpenSSH 10.2p1, 유선 1 Gbps |
| 프로토콜 · 인증 | SFTP, 같은 ed25519 키, 두 앱 모두 같은 호스트 키를 미리 신뢰 |
| TASTEFTP | 0.2.50 Windows 설치본(`tasteftp.exe` SHA-256 `4c14a525b6be1c3962b1f323466190063709359a7b2009337e0d4a1138634655`), `tasteftp cli batch --connections 2` |
| FileZilla | 3.71.1 Windows(`filezilla.exe` SHA-256 `84ade0a797ffab4771eb4b0521b4404ec0be86e91824bbe0dafb69c099d74828`), GUI 전송 대기열, 동시 전송 2(기본값) |
| 속도 제한 · 미리 공간 확보 | 두 앱 모두 끔 |
| 파일 | `/dev/urandom` 으로 만든 합성 파일(압축되지 않음): 1 GiB 1개, 64 KiB 1,000개(합 62.5 MiB) |
| 순서 | 묶음마다 앱별 예열 1회, 측정 5회. 앱 순서를 번갈아 바꿈 |
| 캐시 | 서버 원본은 예열로 페이지 캐시에 올라간 상태. 대상 폴더는 매 회 비움 |

### 시간을 잰 방법

- **시작**: 전송 명령을 보낸 때. TASTEFTP 는 명령줄 프로세스를 시작한 때라 실행 · 접속 시간이 포함됩니다. FileZilla 는 이미 떠 있는 창에
  '전송 → 대기열 처리' 메뉴 명령을 보낸 때라 앱 시작 시간이 빠집니다(접속 시간은 포함). TASTEFTP 쪽이 불리합니다.
- **끝**: 모든 대상 파일이 제 크기가 된 때. 다운로드는 PC 에서 20 ms, 업로드는 서버에서 50 ms 간격으로 두 앱 모두 같은 방법으로 감시했습니다.
- FileZilla 는 대기열(`queue.sqlite3`)을 미리 채우고 창을 최소화로 띄운 뒤 메뉴 명령(WM_COMMAND)으로 시작했습니다. 마우스 · 키보드 입력은 쓰지 않았습니다.

## 한계 · 재지 않은 것

- 한 PC · 한 서버 · 한 LAN 의 결과입니다. 지연이 큰 인터넷 너머 서버에서는 재지 않았습니다.
- FTP · FTPS 는 재지 않았습니다.
- WinSCP · Cyberduck 은 재지 않았습니다.
- TASTEFTP 는 화면판과 같은 전송 엔진을 쓰는 명령줄 묶음 전송으로 쟀습니다. 화면 조작을 거친 시간은 재지 않았습니다.
- 큰 파일 업로드는 두 앱 모두 회차마다 편차가 커서(9.5~25.5초) 우열을 말할 수 없습니다.
- FileZilla 작은 파일 다운로드의 한 회(99.52초)는 튀는 값입니다. 중앙값에는 영향이 작습니다.

## 파일

| 파일 | 내용 |
| --- | --- |
| `results.jsonl` | 회차별 원본 기록. `label` = `smoke`(동작 확인) · `warmup`(예열) · `measure`(측정). `seconds` = 위 방법으로 잰 시간, `exitSeconds` = TASTEFTP 프로세스가 끝난 때 |
| `bench.py` | 한 회를 재는 스크립트(Python 3, Windows). 환경 변수 `BENCH_DIR` · `BENCH_REMOTE` · `BENCH_HOST` · `BENCH_USER` · `BENCH_KEY` 를 씁니다 |
| `run-all.sh` · `run-more.sh` | 회차 순서(1차 3회, 2차에서 5회로 채움) |
| `summarize.py` | `results.jsonl` 에서 위 표를 만듭니다 |

다시 재려면 서버에 `src/big.bin` · `src/small/s000.bin`~`s999.bin` 과 그 SHA-256 목록(`big.sha256` · `small.sha256`)을 만들고, 같은 파일을
`BENCH_DIR/up` 에 두고, TASTEFTP 접속 설정 `conn.json`(명령줄 안내 참고)과 비어 있는 FileZilla `queue.sqlite3` 사본(`queue-user-backup.sqlite3`)을 준비합니다.
FileZilla 를 쓰는 중이면 측정하지 마세요 — 스크립트가 FileZilla 대기열 파일을 바꿉니다(끝난 뒤 사본으로 되돌리세요).

TASTEFTP: https://tastedev.net/products/ftp · FileZilla 는 FileZilla Project 의 상표입니다.
