# TASTEDEV Releases & Issues

> **English** — Signed installers and public issue tracking for the TASTEDEV developer tools by GXSOFT
> (SSH, FTP, archiver, file manager, DWG viewer, mail server, ETL). Product pages and docs: https://tastedev.net/en .
> Source code is not public; every package ships with a `.sig` and `SHA256SUMS.txt` (see *Verifying a download* below).
> Report problems in [Issues](https://github.com/whitecalvin/tastedev-releases/issues) — English or Korean is fine.

TASTEDEV 제품의 **공식 배포 파일과 사용자 문제 신고를 한곳에서 관리하는 저장소**입니다.

- **다운로드:** [Releases](https://github.com/whitecalvin/tastedev-releases/releases)
- **문제 신고·기능 제안·문의:** [Issues](https://github.com/whitecalvin/tastedev-releases/issues)
- **새 Issue 작성:** [New issue](https://github.com/whitecalvin/tastedev-releases/issues/new/choose)

## 지원 제품

| 제품 | 분류 | 릴리스 태그 형식 | 제품 페이지 |
|---|---|---|---|
| TASTECAD | 데스크톱 앱 | `cad-v<버전>` | [tastedev.net/products/cad](https://tastedev.net/products/cad) |
| TASTEFILES | 데스크톱 앱 | `files-v<버전>` | [tastedev.net/products/files](https://tastedev.net/products/files) |
| TASTEFTP | 데스크톱 앱 | `ftp-v<버전>` | [tastedev.net/products/ftp](https://tastedev.net/products/ftp) |
| TASTESSH | 데스크톱 앱 | `ssh-v<버전>` | [tastedev.net/products/ssh](https://tastedev.net/products/ssh) |
| TASTEZIP | 데스크톱 앱 | `zip-v<버전>` | [tastedev.net/products/zip](https://tastedev.net/products/zip) |
| TASTEETL | 웹·백엔드 | `etl-v<버전>` | [tastedev.net/products/etl](https://tastedev.net/products/etl) |
| TASTEMAIL | 웹·백엔드 | `mail-v<버전>` | [tastedev.net/products/mail](https://tastedev.net/products/mail) |

## 다운로드 및 설치

1. [릴리스 목록](https://github.com/whitecalvin/tastedev-releases/releases)에서 원하는 **제품명과 태그 접두사**를 확인합니다.
2. 해당 제품 릴리스의 설명을 읽고 운영체제와 아키텍처에 맞는 파일을 **Assets**에서 선택합니다.
3. 릴리스에 제공된 설치·업데이트 안내를 따릅니다. 체크섬이나 서명 검증 자료가 제공되면 함께 확인합니다.

### 받은 파일 확인 (Verifying a download)

릴리스마다 `SHA256SUMS.txt` 와 파일별 `.sig` 가 함께 올라갑니다. 내려받은 폴더에서:

```bash
sha256sum -c SHA256SUMS.txt --ignore-missing
```

```powershell
Get-FileHash .	astessh_0.1.1_windows_x64.msi -Algorithm SHA256
```

서명 확인 방법은 https://tastedev.net/downloads 에 있습니다.

여러 제품이 이 저장소를 함께 사용하므로 저장소 전체의 **Latest** 표시만으로 특정 제품의 최신 버전을 판단하지 마세요. 지원 운영체제와 설치 파일 형식은 제품·릴리스별로 확인해야 합니다.

## 사용자 문제 신고

제품을 사용하다 발생한 오류, 불편 사항, 기능 제안은 **이 저장소의 Issues**에 등록해 주세요. 먼저 기존 Issue를 검색하고 같은 내용이 있으면 재현 정보나 추가 증거를 해당 Issue에 남겨 주세요.

제목 앞에 제품명을 넣으면 분류에 도움이 됩니다.

```text
[TASTEFILES] 특정 폴더 복사 중 오류 발생
[TASTEFTP] 서버 연결 후 파일 목록이 표시되지 않음
[TASTEMAIL] 메일 검색 기능 개선 제안
```

신고에는 다음 정보를 포함해 주세요.

| 항목 | 작성 내용 |
|---|---|
| 제품·버전 | 제품명과 설치된 정확한 버전 |
| 사용 환경 | 운영체제·버전·아키텍처, 관련 환경 조건 |
| 재현 절차 | 문제가 발생하기까지의 동작을 순서대로 작성 |
| 기대 결과 | 정상적으로 어떤 결과가 나와야 하는지 |
| 실제 결과 | 실제 동작과 오류 메시지 |
| 발생 빈도 | 항상 발생하는지, 특정 조건에서만 발생하는지 |
| 증거 | 필요한 로그 일부, 스크린샷 또는 안전하게 공유할 수 있는 재현 파일 |

이곳은 공개 저장소입니다. 비밀번호·인증 토큰·개인키·쿠키, 개인정보, 고객 데이터 및 비공개 파일 내용은 올리지 마세요. 로그와 스크린샷은 필요한 부분만 남기고 민감한 내용을 가려 주세요.

## 앱에서 보내는 오류 보고

앱에 오류 보고 기능이 제공되는 경우 해당 기능으로 보고서를 보낼 수 있습니다. 사용자 오류 보고의 중앙 Issue 관리 대상도 **`whitecalvin/tastedev-releases`**입니다.

보고 서버의 접수 기록과 GitHub Issue는 별도로 관리됩니다. 보고서 전송이 즉시 새 Issue 하나의 생성으로 이어지는 것은 아니며, 서버 연동 상태와 중복 분류에 따라 기존 Issue로 연결되거나 등록이 지연될 수 있습니다.

## 저장소 역할

| 위치 | 관리 내용 |
|---|---|
| **이 저장소의 Releases** | 제품별 배포 파일과 릴리스 안내 |
| **이 저장소의 Issues** | 사용자가 신고한 문제·문의·기능 제안의 중앙 접수 |
| **각 제품 개발 저장소(비공개)** | 제품 소스, 단위·회귀 테스트, 구현 작업과 제품별 QA Issue |
| **별도 QA 환경** | QA 실행 기록, 상세 로그, 스크린샷과 테스트 상태 |

사용자 신고를 개발 작업으로 연결할 때에는 관련 제품 저장소의 Issue 또는 변경 사항을 서로 참조해 처리 경과를 추적합니다. QA 기록 전체가 이 저장소에 자동으로 공개되는 것은 아닙니다.

Issue가 접수됐다는 사실은 수정 완료를 의미하지 않습니다. 재현·수정·재검증 결과와 수정 버전은 해당 Issue 및 제품 릴리스 안내에서 확인해 주세요.
