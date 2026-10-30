"""TASTEFTP · FileZilla 같은 조건 SFTP 전송 측정(2026-10-30).

같은 PC → 같은 LAN 서버(OpenSSH, 1 Gbps), 같은 합성 파일, 동시 전송 2(FileZilla 기본값).
시작 = 전송 명령을 보낸 때(TASTEFTP 는 명령줄 프로세스 시작, FileZilla 는 이미 떠 있는 창에 '대기열 처리' 메뉴 명령).
끝 = 모든 대상 파일이 제 크기가 된 때(다운로드는 이 PC 에서, 업로드는 서버에서 같은 방법으로 감시).
TASTEFTP 는 프로세스 시작 · 접속 · 끝난 뒤 확인까지 시간에 들어가 불리한 쪽으로 잰다.
"""
import ctypes, ctypes.wintypes as wt, hashlib, json, os, shutil, sqlite3, subprocess, sys, threading, time

SCRATCH = os.environ["BENCH_DIR"]  # up/ · *.sha256 · conn.json · queue-user-backup.sqlite3 이 있는 작업 폴더
UP = os.path.join(SCRATCH, "up")
DOWN = os.path.join(SCRATCH, "down")
REMOTE = os.environ["BENCH_REMOTE"]  # 서버의 시험 폴더(src/ 에 원본)
HOST = os.environ["BENCH_HOST"]  # ssh 로 접속할 시험 서버(사용자@호스트)
TASTEFTP = r"C:\Program Files\tastedev\ftp\tasteftp.exe"
FILEZILLA = r"C:\Program Files\FileZilla FTP Client\filezilla.exe"
FZ_QUEUE = os.path.join(os.environ["APPDATA"], "FileZilla", "queue.sqlite3")
KEY = os.environ["BENCH_KEY"]  # SFTP 개인 키 경로
CONNECTIONS = 2


def sha_table(name):
    table = {}
    with open(os.path.join(SCRATCH, name), encoding="utf-8") as f:
        for line in f:
            h, n = line.split()
            table[n.lstrip("*")] = h
    return table


BIG_SHA = sha_table("big.sha256")
SMALL_SHA = sha_table("small.sha256")


def dataset(name, limit=None):
    """(상대 경로, 바이트, sha256) 목록. 상대 경로의 폴더는 '' 또는 'small'."""
    if name == "big":
        return [("big.bin", 1073741824, BIG_SHA["big.bin"])]
    names = sorted(SMALL_SHA)[: limit or None]
    return [("small/" + n, 65536, SMALL_SHA[n]) for n in names]


def ssh(cmd, check=True):
    return subprocess.run(["ssh", "-o", "BatchMode=yes", HOST, cmd], capture_output=True, text=True, check=check).stdout


def prepare(direction):
    if direction == "download":
        shutil.rmtree(DOWN, ignore_errors=True)
        os.makedirs(os.path.join(DOWN, "small"))
    else:
        ssh(f"rm -rf {REMOTE}/dst && mkdir -p {REMOTE}/dst/small")


def local_done(files):
    for rel, size, _ in files:
        try:
            if os.stat(os.path.join(DOWN, rel)).st_size != size:
                return False
        except FileNotFoundError:
            return False
    return True


class RemoteWatcher:
    """서버에서 대상 파일 크기를 50 ms 마다 보고, 다 차면 DONE 한 줄을 낸다. 줄이 도착한 때를 이 PC 시계로 잰다."""

    def __init__(self, files):
        spec = json.dumps([[rel, size] for rel, size, _ in files])
        script = (
            "import json,os,sys,time\n"
            f"files=json.loads({spec!r});base={REMOTE + '/dst'!r}\n"
            "print('READY',flush=True)\n"
            "while True:\n"
            "  ok=True\n"
            "  for rel,size in files:\n"
            "    try:\n"
            "      if os.stat(base+'/'+rel).st_size!=size: ok=False;break\n"
            "    except FileNotFoundError: ok=False;break\n"
            "  if ok: print('DONE',flush=True);break\n"
            "  time.sleep(0.05)\n"
        )
        # 1,000개 목록은 Windows 명령줄 길이를 넘으므로 스크립트는 표준 입력으로 보낸다
        self.proc = subprocess.Popen(["ssh", "-o", "BatchMode=yes", HOST, "python3 -u -"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.proc.stdin.write(script)
        self.proc.stdin.close()
        assert self.proc.stdout.readline().strip() == "READY"
        self.done_at = None
        self.thread = threading.Thread(target=self._wait, daemon=True)
        self.thread.start()

    def _wait(self):
        line = self.proc.stdout.readline().strip()
        if line == "DONE":
            self.done_at = time.perf_counter()

    def wait(self, timeout):
        self.thread.join(timeout)
        if self.done_at is None:
            self.proc.kill()
        return self.done_at


def shlex_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def wait_local(files, timeout):
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        if local_done(files):
            return time.perf_counter()
        time.sleep(0.02)
    return None


def verify(direction, files):
    if direction == "download":
        bad = 0
        for rel, _, digest in files:
            h = hashlib.sha256()
            with open(os.path.join(DOWN, rel), "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            bad += h.hexdigest() != digest
        return bad
    lines = "\n".join(f"{digest}  {rel}" for rel, _, digest in files) + "\n"
    out = subprocess.run(["ssh", "-o", "BatchMode=yes", HOST, f"cd {REMOTE}/dst && sha256sum -c --quiet - 2>&1 | grep -c FAILED || true"],
                         input=lines, capture_output=True, text=True).stdout.strip()
    return int(out or 0)


# ---------- TASTEFTP (명령줄 묶음 전송, 같은 전송 엔진) ----------

def run_tasteftp(direction, files):
    entries = []
    for rel, size, digest in files:
        if direction == "download":
            entries.append({"local": os.path.join(DOWN, rel).replace("\\", "/"), "remote": f"{REMOTE}/src/{rel}", "bytes": size, "sha256": digest})
        else:
            entries.append({"local": os.path.join(UP, rel).replace("\\", "/"), "remote": f"{REMOTE}/dst/{rel}", "bytes": size, "sha256": digest})
    manifest = os.path.join(SCRATCH, "manifest.json")
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump({"direction": direction, "files": entries}, f)
    watcher = RemoteWatcher(files) if direction == "upload" else None
    t0 = time.perf_counter()
    proc = subprocess.Popen([TASTEFTP, "cli", "batch", "--config", os.path.join(SCRATCH, "conn.json"), "--manifest", manifest,
                             "--connections", str(CONNECTIONS), "--timeout", "900"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    done = watcher.wait(900) if watcher else wait_local(files, 900)
    out, _ = proc.communicate(timeout=900)
    t_exit = time.perf_counter()
    try:
        result = json.loads(out.strip().splitlines()[-1])
    except Exception:
        result = {"raw": out[-500:]}
    return {"seconds": (done - t0) if done else None, "exitSeconds": t_exit - t0, "exitCode": proc.returncode, "ok": result.get("ok"),
            "error": result.get("errorCode")}


# ---------- FileZilla (GUI 대기열, 메뉴 명령으로 시작) ----------

user32 = ctypes.WinDLL("user32", use_last_error=True)
EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def main_window(pid, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        found = []

        def cb(hwnd, _):
            p = wt.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value == pid and user32.GetMenu(hwnd):
                found.append(hwnd)
            return True

        user32.EnumWindows(EnumWindowsProc(cb), 0)
        if found:
            return found[0]
        time.sleep(0.2)
    raise RuntimeError("FileZilla 창을 찾지 못함")


def menu_id(hwnd, text):
    menu = user32.GetMenu(hwnd)
    buf = ctypes.create_unicode_buffer(256)
    for i in range(user32.GetMenuItemCount(menu)):
        sub = user32.GetSubMenu(menu, i)
        for j in range(user32.GetMenuItemCount(sub)):
            user32.GetMenuStringW(sub, j, buf, 256, 0x400)
            if text in buf.value:
                return user32.GetMenuItemID(sub, j)
    raise RuntimeError("메뉴 없음: " + text)


def safe_path(path):
    return "1 0" + "".join(f" {len(s)} {s}" for s in path.strip("/").split("/"))


def write_fz_queue(direction, files):
    if os.path.exists(FZ_QUEUE):
        os.remove(FZ_QUEUE)
    shutil.copy(os.path.join(SCRATCH, "queue-user-backup.sqlite3"), FZ_QUEUE)
    db = sqlite3.connect(FZ_QUEUE)
    cur = db.cursor()
    cur.execute("INSERT INTO servers (host, port, user, keyfile, protocol, type, logontype, timezone_offset, transfer_mode, max_connections, encoding, bypass_proxy, name)"
                " VALUES (?, 22, ?, ?, 1, 0, 5, 0, 'default', 0, 'Auto', 0, 'bench')", (HOST.split('@')[-1], os.environ['BENCH_USER'], KEY))
    server = cur.lastrowid
    paths = {}
    for rel, size, _ in files:
        folder, name = (rel.rsplit("/", 1) if "/" in rel else ("", rel))
        base = UP if direction == "upload" else DOWN
        local = os.path.join(base, folder) if folder else base
        local = local.rstrip("\\") + "\\"
        remote = f"{REMOTE}/{'dst' if direction == 'upload' else 'src'}" + (f"/{folder}" if folder else "")
        if (local, remote) not in paths:
            cur.execute("INSERT INTO local_paths (path) VALUES (?)", (local,))
            lid = cur.lastrowid
            cur.execute("INSERT INTO remote_paths (path) VALUES (?)", (safe_path(remote),))
            paths[(local, remote)] = (lid, cur.lastrowid)
        lid, rid = paths[(local, remote)]
        cur.execute("INSERT INTO files (server, source_file, local_path, remote_path, size, priority, flags) VALUES (?, ?, ?, ?, ?, 2, ?)",
                    (server, name, lid, rid, size, 0x10 if direction == "download" else 0))
    db.commit()
    db.close()


def run_filezilla(direction, files):
    write_fz_queue(direction, files)
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 7  # SW_SHOWMINNOACTIVE: 최소화, 포커스를 가져가지 않음
    proc = subprocess.Popen([FILEZILLA], startupinfo=si)
    hwnd = main_window(proc.pid)
    try:
        mid = menu_id(hwnd, "대기열 처리")
        time.sleep(3)  # 창 · 대기열 불러오기가 끝나도록
        watcher = RemoteWatcher(files) if direction == "upload" else None
        t0 = time.perf_counter()
        user32.PostMessageW(hwnd, 0x0111, mid, 0)  # WM_COMMAND
        done = watcher.wait(900) if watcher else wait_local(files, 900)
        time.sleep(1)
    finally:
        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE — 실패해도 띄운 창은 닫는다
    try:
        proc.wait(30)
    except subprocess.TimeoutExpired:
        return {"seconds": (done - t0) if done else None, "error": "FileZilla 가 닫히지 않음", "pid": proc.pid}
    return {"seconds": (done - t0) if done else None, "error": None if done else "시간 초과"}


def main():
    app, direction, name = sys.argv[1:4]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
    files = dataset(name, limit)
    prepare(direction)
    res = (run_tasteftp if app == "tasteftp" else run_filezilla)(direction, files)
    res.update(label=os.environ.get("BENCH_LABEL", "smoke"), app=app, direction=direction, dataset=name, files=len(files), bytes=sum(s for _, s, _ in files),
               mismatches=verify(direction, files) if res.get("seconds") else None, at=time.strftime("%Y-%m-%d %H:%M:%S"))
    if res.get("seconds"):
        res["MiBps"] = round(res["bytes"] / 1048576 / res["seconds"], 1)
    print(json.dumps(res, ensure_ascii=False))
    with open(os.path.join(SCRATCH, "results.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(res, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
