"""Pemutar musik lokal. Jalankan: python main.py  (opsional: pip install mutagen)"""
import argparse, hashlib, json, os, re, socket, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

try:
    from mutagen import File as MFile
    from mutagen.id3 import ID3
except ImportError:
    MFile = ID3 = None

BASE = os.path.dirname(os.path.abspath(__file__))
MUSIK = os.path.join(BASE, "musik")
AUDIO = (".mp3", ".m4a", ".flac", ".ogg", ".wav")
cache, PETA = {}, {}


def tebak(path):
    stem = os.path.splitext(os.path.basename(path))[0].replace("_", " ").strip()
    artis, sep, judul = stem.partition(" - ")
    return (artis.strip(), judul.strip()) if sep else ("Artis tidak diketahui", stem)


def baca_meta(path):
    artis, judul = tebak(path)
    m = {"title": judul, "artist": artis, "album": "", "duration": 0, "cover": False, "emb": False}
    if MFile:
        try:
            f = MFile(path, easy=True)
            m["duration"] = round(f.info.length, 1)
            for k in ("title", "artist", "album"):
                if f.tags and f.tags.get(k):
                    m[k] = str(f.tags[k][0])
        except Exception:
            pass
        try:
            tg = ID3(path)
            m["cover"] = bool(tg.getall("APIC"))
            m["emb"] = any(str(x).strip() for x in tg.getall("USLT"))
        except Exception:
            pass
    return m


def file_lirik(path):
    nama = os.path.splitext(os.path.basename(path))[0]
    for d in (os.path.dirname(path), MUSIK):
        for e in (".lrc", ".txt"):
            p = os.path.join(d, nama + e)
            if os.path.isfile(p) and os.path.getsize(p) > 0:
                return p


def pindai():
    os.makedirs(MUSIK, exist_ok=True)
    paths = [os.path.join(BASE, n) for n in os.listdir(BASE)]
    for r, _, fs in os.walk(MUSIK):
        paths += [os.path.join(r, n) for n in fs]
    hasil, peta = [], {}
    for p in sorted(paths, key=str.lower):
        if not p.lower().endswith(AUDIO) or not os.path.isfile(p):
            continue
        mt = os.path.getmtime(p)
        if p not in cache or cache[p][0] != mt:
            cache[p] = (mt, baca_meta(p))
        i = hashlib.md5(os.path.relpath(p, BASE).encode()).hexdigest()[:10]
        m = dict(cache[p][1], id=i, lyrics=bool(file_lirik(p)) or cache[p][1]["emb"])
        peta[i] = p
        hasil.append(m)
    return hasil, peta

def baca_teks(p):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(p, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            pass
    return ""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def lokal(self):
        return self.client_address[0] in ("127.0.0.1", "::1")

    def kirim(self, data, mime="application/json", code=200):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", mime + ("; charset=utf-8" if mime.startswith("text") or "json" in mime else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def kirim_file(self, path, mime):
        size = os.path.getsize(path)
        a, b = 0, size - 1
        m = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range") or "")
        if m:
            a = int(m.group(1))
            b = min(int(m.group(2)), size - 1) if m.group(2) else b
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(b - a + 1))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(a)
                sisa = b - a + 1
                while sisa > 0:
                    buf = f.read(min(65536, sisa))
                    if not buf:
                        break
                    self.wfile.write(buf)
                    sisa -= len(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        global PETA
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), "rb") as f:
                return self.kirim(f.read(), "text/html")
        if p == "/api/info":
            return self.kirim({"readonly": not self.lokal()})
        if p == "/api/library":
            lib, PETA = pindai()
            return self.kirim(lib)
        kind = p.strip("/").split("/")
        path = PETA.get(kind[-1])
        if not path:
            return self.send_error(404)
        if kind[0] == "audio":
            mime = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".flac": "audio/flac", ".ogg": "audio/ogg", ".wav": "audio/wav"}
            return self.kirim_file(path, mime[os.path.splitext(path)[1].lower()])
        if kind[0] == "cover" and ID3:
            try:
                pic = ID3(path).getall("APIC")[0]
                return self.kirim(pic.data, pic.mime or "image/jpeg")
            except Exception:
                return self.send_error(404)
        if kind[:2] == ["api", "lyrics"]:
            lp, teks = file_lirik(path), ""
            if lp:
                teks = baca_teks(lp)
            elif ID3:
                try:
                    teks = "\n".join(str(x) for x in ID3(path).getall("USLT"))
                except Exception:
                    pass
            return self.kirim({"text": teks})
        self.send_error(404)

    def isi(self):
        return self.rfile.read(int(self.headers.get("Content-Length") or 0))

    def do_POST(self):
        if not self.lokal():
            return self.send_error(403)
        path = PETA.get(self.path.strip("/").split("/")[-1])
        if not path or "/api/lyrics/" not in self.path:
            return self.send_error(404)
        teks = self.isi().decode("utf-8", "replace")
        dasar = os.path.splitext(path)[0]
        ext, lain = (".lrc", ".txt") if re.search(r"\[\d+:\d+", teks) else (".txt", ".lrc")
        with open(dasar + ext, "w", encoding="utf-8") as f:
            f.write(teks)
        if os.path.isfile(dasar + lain):
            os.remove(dasar + lain)
        self.kirim({"ok": True})

    def do_PUT(self):
        if not self.lokal():
            return self.send_error(403)
        nama = os.path.basename(parse_qs(urlparse(self.path).query).get("name", [""])[0])
        if not nama.lower().endswith(AUDIO + (".lrc", ".txt")):
            return self.send_error(400)
        os.makedirs(MUSIK, exist_ok=True)
        with open(os.path.join(MUSIK, nama), "wb") as f:
            f.write(self.isi())
        self.kirim({"ok": True})


def ip_lokal():
    """Alamat IP komputer di jaringan Wi-Fi (tidak mengirim data apa pun)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser(description="Pemutar musik lokal")
    ap.add_argument("--lan", action="store_true", help="izinkan perangkat di Wi-Fi yang sama untuk mendengarkan (hanya-dengar)")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    host, port = ("0.0.0.0" if a.lan else "127.0.0.1"), a.port
    while True:
        try:
            srv = ThreadingHTTPServer((host, port), H)
            break
        except OSError:
            port += 1
    pindai()
    url = f"http://127.0.0.1:{port}"
    print(f"Musik berjalan di {url}  (Ctrl+C untuk berhenti)\nTaruh file musik di: {MUSIK}")
    if a.lan:
        print(f"Perangkat lain di Wi-Fi yang sama: http://{ip_lokal()}:{port}")
        print("Perangkat lain hanya bisa mendengarkan. Tambah lagu dan ubah lirik hanya dari komputer ini.")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()