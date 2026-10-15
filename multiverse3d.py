# -*- coding: utf-8 -*-
"""
=====================================================================
  M U L T I V E R S E   3 D
  7 dimensi paralel dalam ruang 3D sungguhan, saling terhubung portal.
=====================================================================
Target  : Windows 10 + VS Code + Python 3.14.x   |   60 FPS
Install : pip install pygame-ce numpy
Jalankan: python multiverse3d.py
HTML    : taruh index.html, saran.html, cek.html, profile.html, snk.html, news.html,
          sosmed.html di FOLDER YANG SAMA dengan file ini (atau atur HTML_FOLDER).
Ubah judul/file/warna : lihat bagian 'PUSAT PENGATURAN' tepat di bawah docstring ini.

KONTROL
  Drag kiri ................ putar kamera (orbit) mengelilingi target
  Drag kanan / tengah ...... geser kamera
  Klik kiri (tanpa drag) ... terbang ke dimensi yang diklik
  Tombol BUKA .............. (muncul di kanan-bawah, kiri minimap) animasi partikel + buka HTML
  ENTER / SPASI ............ sama seperti menekan tombol BUKA
  Scroll mouse ............. zoom in / out
  W A S D .................. gerak maju / kiri / mundur / kanan
  Q / E .................... turun / naik
  Panah .................... putar kamera
  1-6 ...................... fokus ke dimensi 1-6
  C ........................ fokus ke THE NEXUS (pusat)
  0 / Home ................. tampilan keseluruhan
  TAB ...................... dimensi berikutnya
  T ........................ tur otomatis ON/OFF
  O ........................ orbit kamera otomatis ON/OFF
  B ........................ ledakan energi multiverse
  F ........................ ganti target FPS 60 <-> 45
  H ........................ tampil/sembunyi HUD
  P ........................ pause
  F11 ...................... layar penuh
  ESC ...................... keluar

Detail visual otomatis diturunkan bila komputer tidak sanggup 60 FPS,
lalu dinaikkan lagi kalau ada ruang tersisa (lihat "DETAIL" di HUD).
"""
import colorsys
import math
import os
import pathlib
import random
import sys
import threading
import time
import webbrowser

try:
    import numpy as np
except ImportError:
    print("numpy belum terpasang.\nJalankan di terminal VS Code:\n\n"
          "    pip install pygame-ce numpy\n")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("pygame belum terpasang.\nJalankan di terminal VS Code:\n\n"
          "    pip install pygame-ce numpy\n")
    sys.exit(1)

# =====================================================================
#  PUSAT PENGATURAN  -  EDIT BAGIAN INI UNTUK MENGUBAH ISI TAMPILAN
#  (judul, sub-judul, file HTML, warna, teks tombol, jumlah partikel, dll.)
#  Setelah diubah: simpan file, lalu jalankan ulang  ->  python multiverse3d.py
# =====================================================================

# ---- 1. TEKS UMUM ---------------------------------------------------
WINDOW_TITLE = "Multiverse"                       # judul di title bar jendela
APP_TITLE = "M U L T I V E R S E  3D"             # judul besar di pojok kiri-atas layar
APP_SUBTITLE = "Mesin Simulasi Dimensi Paralel"   # teks kecil di bawah judul besar
HUD_HINT = ("Drag=Putar  Klik=Pilih  ENTER=Buka  Scroll=Zoom  WASD/QE=Gerak  [1-6] Dimensi  "
            "[C] Nexus  [0] Ringkas  [T] Tur  [O] Orbit  [B] Ledak  [H] HUD")   # baris petunjuk paling bawah

# ---- 2. LOKASI FILE HTML --------------------------------------------
# ""  = file HTML berada di folder yang SAMA dengan multiverse3d.py
# Boleh diisi nama sub-folder ("web") atau path lengkap (r"D:\situs\html").
HTML_FOLDER = ""
BROWSER_TAB = 2          # 2 = buka di tab baru | 1 = jendela browser baru | 0 = jendela yang sama

# ---- 3. ANIMASI TOMBOL BUKA -----------------------------------------
PARTICLE_MULT = 1.0      # jumlah partikel: 0.5 = separuh (PC lemah), 1.0 = normal, 2.0 = dobel (sangat ramai)
FX_SPEED = 1.0           # kecepatan animasi: 0.7 = lebih pelan/dramatis, 1.5 = lebih cepat
OPEN_BUTTON_DEFAULT = "BUKA DIMENSI"              # tulisan tombol jika "button" pada universe dikosongkan
OPEN_TEXT_DEFAULT = "Menembus dimensi..."         # kalimat animasi jika "opening" dikosongkan

# ---- 4. DAFTAR 7 DIMENSI --------------------------------------------
# Urutan:  [0] = THE NEXUS (bola pusat, tombol C)
#          [1]..[6] = enam dimensi di cincin (tombol angka 1..6)
# Jumlah entri HARUS tepat 7 - jangan dihapus / ditambah, cukup ubah isinya.
#
# Arti setiap kunci:
#   "name"    : JUDUL universe (label di layar, panel bawah, dan teks saat animasi)
#   "sub"     : sub-judul / deskripsi singkat di bawah judul
#   "file"    : halaman yang dibuka. Bisa nama file ("index.html"), path ("web/saran.html"),
#               path lengkap (r"D:\situs\saran.html"), atau alamat web ("https://...")
#   "color"   : warna universe (R, G, B) tiap angka 0-255 -> ikut mewarnai partikel & animasi
#   "button"  : tulisan pada tombol BUKA (usahakan maks. 16 huruf agar muat)
#   "caption" : teks kecil di bawah tulisan tombol ("" = otomatis menampilkan nama file)
#   "opening" : kalimat di tengah layar saat animasi berjalan
#   "stats"   : 3 nama bar pada panel bawah (hanya hiasan)
UNIVERSES = [
    {   # [0] PUSAT  ->  index.html
        "name": "THE NEXUS",
        "sub": "Inti Omniverse · Titik Temu Semua Dimensi",
        "file": "index.html",
        "color": (190, 190, 255),
        "button": "BUKA BERANDA",
        "caption": "",
        "opening": "Menuju inti omniverse...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [1] tombol angka 1  ->  saran.html
        "name": "AETHER PRIME",
        "sub": "Galaksi Spiral · Dimensi α-01",
        "file": "saran.html",
        "color": (120, 160, 255),
        "button": "BUKA SARAN",
        "caption": "",
        "opening": "Melintasi galaksi spiral...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [2] tombol angka 2  ->  cek.html
        "name": "NEON SOL",
        "sub": "Tata Surya Neon · Dimensi β-02",
        "file": "cek.html",
        "color": (255, 110, 200),
        "button": "BUKA CEK",
        "caption": "",
        "opening": "Mendekati bintang neon...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [3] tombol angka 3  ->  profile.html
        "name": "VOID SINGULARITY",
        "sub": "Lubang Hitam · Dimensi γ-03",
        "file": "profile.html",
        "color": (255, 170, 80),
        "button": "BUKA PROFIL",
        "caption": "",
        "opening": "Jatuh ke horizon peristiwa...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [4] tombol angka 4  ->  snk.html
        "name": "CRYSTAL NEXUS",
        "sub": "Realitas Kristal · Dimensi δ-04",
        "file": "snk.html",
        "color": (90, 255, 240),
        "button": "BUKA S&K",
        "caption": "",
        "opening": "Memasuki realitas kristal...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [5] tombol angka 5  ->  news.html
        "name": "EMBER STORM",
        "sub": "Badai Bara · Dimensi ε-05",
        "file": "news.html",
        "color": (255, 120, 50),
        "button": "BUKA BERITA",
        "caption": "",
        "opening": "Menembus badai bara...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
    {   # [6] tombol angka 6  ->  sosmed.html
        "name": "GLITCH MATRIX",
        "sub": "Simulasi Rusak · Dimensi ζ-06",
        "file": "sosmed.html",
        "color": (60, 255, 140),
        "button": "BUKA SOSMED",
        "caption": "",
        "opening": "Meretas simulasi...",
        "stats": ("ENTROPI", "ENERGI", "STABILITAS"),
    },
]
# =====================================================================
#  (akhir pusat pengaturan - di bawah ini tidak perlu diubah)
# =====================================================================

# ---------------------------------------------------------------------
#  KONFIGURASI
# ---------------------------------------------------------------------
W, H = 1280, 720
HW, HH = W / 2.0, H / 2.0
TAU = math.tau
FOV_DEG = 62.0
FOCAL = HH / math.tan(math.radians(FOV_DEG) / 2.0)
NEAR = 25.0
DMIN, DMAX = 110.0, 7000.0
OVERVIEW_DIST = 2550.0
RING_DIST = 1050.0
FOCUS_K = 2.5
TOUR_SECONDS = 7.0
FPS_OPTIONS = (60, 45)
QUALITY = (1.0, 1.5, 2.0, 3.0)
QUALITY_NAME = ("TINGGI", "SEDANG", "RENDAH", "MINIMAL")
ADD = pygame.BLEND_RGB_ADD
UP = np.array([0.0, 1.0, 0.0])
BTN_RECT = pygame.Rect(W - 200 - 20 - 236, H - 132, 236, 62)   # posisi tombol BUKA (kiri minimap)


# ---------------------------------------------------------------------
#  UTILITAS
# ---------------------------------------------------------------------
def clamp(v, a, b):
    return a if v < a else b if v > b else v


def mul(c, f):
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def hue(h, s=0.65, v=1.0):
    r, g, b = colorsys.hsv_to_rgb((int(h) % 360) / 360.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def unit_circle(n, closed=True):
    a = np.linspace(0, TAU, n + (1 if closed else 0), endpoint=closed)
    return np.stack((np.cos(a), np.zeros_like(a), np.sin(a)), axis=1)


# ---------------------------------------------------------------------
#  SPRITE GLOW (di-cache -> kunci utama FPS tinggi)
# ---------------------------------------------------------------------
SIZES = (2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64,
         80, 96, 112, 128, 160, 192, 224, 256, 320)
MAXR = SIZES[-1]
SNAP = np.zeros(MAXR + 2, dtype=np.int32)
_j = 0
for _i in range(MAXR + 2):
    while SIZES[_j] < _i and _j < len(SIZES) - 1:
        _j += 1
    SNAP[_i] = SIZES[_j]
SNAP_L = SNAP.tolist()


def make_glow(color, r):
    n = r * 2
    ax = (np.arange(n, dtype=np.float32) - r + 0.5) / r
    d = np.sqrt(ax[:, None] ** 2 + ax[None, :] ** 2)
    p = 1.15 if r <= 3 else (1.6 if r <= 6 else 2.2)
    a = np.clip(1.0 - d, 0.0, 1.0) ** p
    arr = (a[:, :, None] * np.array(color, dtype=np.float32)).astype(np.uint8)
    return pygame.surfarray.make_surface(arr).convert()


class GlowSet(dict):
    """Kumpulan sprite glow satu warna, dibuat malas per ukuran."""

    def __init__(self, color):
        super().__init__()
        self.color = color

    def __missing__(self, r):
        s = make_glow(self.color, r)
        self[r] = s
        return s

    def warm(self, maxr=12):
        for r in SIZES:
            if r <= maxr:
                self[r]


_GLOWS = {}


def glowset(color):
    color = (int(color[0]), int(color[1]), int(color[2]))
    g = _GLOWS.get(color)
    if g is None:
        g = _GLOWS[color] = GlowSet(color)
    return g


def palette(colors, warm=24):
    out = [glowset(c) for c in colors]
    for g in out:
        g.warm(warm)
    return out


# ---------------------------------------------------------------------
#  CACHE TEKS
# ---------------------------------------------------------------------
class TextCache:
    FONT = "consolas,dejavusansmono,couriernew,monospace"

    def __init__(self):
        self.fonts = {}
        self.cache = {}

    def font(self, size, bold=False):
        f = self.fonts.get((size, bold))
        if f is None:
            f = self.fonts[(size, bold)] = pygame.font.SysFont(self.FONT, size, bold=bold)
        return f

    def get(self, text, size, color, bold=False):
        key = (text, size, color, bold)
        s = self.cache.get(key)
        if s is None:
            if len(self.cache) > 700:
                self.cache.clear()
            s = self.cache[key] = self.font(size, bold).render(text, True, color)
        return s


TXT = TextCache()


# ---------------------------------------------------------------------
#  BANTUAN: teks, pencarian file HTML, validasi pengaturan
# ---------------------------------------------------------------------
def smoothstep(x):
    x = 0.0 if x < 0.0 else 1.0 if x > 1.0 else x
    return x * x * (3.0 - 2.0 * x)


def fit_text(text, sizes, maxw, color, bold=True):
    """Render teks dengan ukuran terbesar (dari daftar 'sizes') yang masih muat di maxw piksel."""
    img = None
    for sz in sizes:
        img = TXT.get(text, sz, color, bold)
        if img.get_width() <= maxw:
            break
    return img


def blit_alpha(dst, img, pos, alpha):
    img.set_alpha(max(0, min(255, int(alpha))))
    dst.blit(img, pos)
    img.set_alpha(255)


def safe_print(*args):
    try:
        print(*args)
    except UnicodeEncodeError:
        print(" ".join(str(a) for a in args).encode("ascii", "replace").decode("ascii"))


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def html_dir():
    d = os.path.expanduser(HTML_FOLDER.strip()) if HTML_FOLDER else ""
    if not d:
        return SCRIPT_DIR
    return d if os.path.isabs(d) else os.path.join(SCRIPT_DIR, d)


def find_html(name):
    """Cari file HTML. Toleran terhadap salah ketik ekstensi (.hmtl <-> .html) dan besar/kecil huruf."""
    fn = name.strip()
    cands = [fn]
    low = fn.lower()
    if low.endswith(".html"):
        cands.append(fn[:-5] + ".hmtl")
        cands.append(fn[:-5] + ".htm")
    elif low.endswith(".hmtl"):
        cands.append(fn[:-5] + ".html")
    elif low.endswith(".htm"):
        cands.append(fn + "l")
    else:
        cands.append(fn + ".html")
    for c in cands:
        p = c if os.path.isabs(c) else os.path.join(html_dir(), c)
        if os.path.isfile(p):
            return p
        d, b = os.path.split(p)
        try:
            for f in os.listdir(d or "."):
                if f.lower() == b.lower() and os.path.isfile(os.path.join(d, f)):
                    return os.path.join(d, f)
        except OSError:
            pass
    return None


def resolve_target(file):
    """-> (url, error). 'file' = nama file HTML, path, atau alamat http(s)."""
    f = (file or "").strip()
    if not f:
        return None, "Belum ada 'file' untuk dimensi ini (isi pada UNIVERSES)."
    if f.lower().startswith(("http://", "https://")):
        return f, None
    p = find_html(f)
    if p is None:
        return None, f"File tidak ditemukan: {f}  (taruh di folder yang sama dengan multiverse3d.py)"
    return pathlib.Path(p).resolve().as_uri(), None


def validate_config():
    problems = []
    if not isinstance(UNIVERSES, (list, tuple)) or len(UNIVERSES) != 7:
        n = len(UNIVERSES) if hasattr(UNIVERSES, "__len__") else "?"
        problems.append(f"UNIVERSES harus berisi TEPAT 7 entri (sekarang {n}).")
    else:
        for i, u in enumerate(UNIVERSES):
            if not isinstance(u, dict):
                problems.append(f"UNIVERSES[{i}] harus berupa dictionary {{...}}.")
                continue
            col = u.get("color")
            if not (isinstance(col, (tuple, list)) and len(col) == 3
                    and all(isinstance(v, (int, float)) for v in col)):
                problems.append(f"UNIVERSES[{i}]: 'color' harus berbentuk (R, G, B), contoh (120, 160, 255).")
            if not u.get("name"):
                problems.append(f"UNIVERSES[{i}]: 'name' tidak boleh kosong.")
    if problems:
        print("\nPengaturan di bagian atas multiverse3d.py belum benar:\n")
        for p in problems:
            safe_print("  - " + p)
        print()
        sys.exit(1)


def report_files():
    """Tampilkan status file HTML di terminal saat program dimulai."""
    safe_print("=" * 62)
    safe_print(" MULTIVERSE 3D  -  cek file HTML")
    safe_print(" folder :", html_dir())
    for i, u in enumerate(UNIVERSES):
        url, err = resolve_target(u.get("file", ""))
        tag = "[ OK ]" if err is None else "[ !! ]"
        note = "" if err is None else "  <-- TIDAK DITEMUKAN"
        safe_print(f" {tag} {i}. {str(u.get('name', '?')):<20} -> {u.get('file', '')}{note}")
    safe_print("=" * 62)


# ---------------------------------------------------------------------
#  KAMERA 3D (orbit + terbang)
# ---------------------------------------------------------------------
class Camera:
    def __init__(self):
        self.tgt = np.zeros(3)
        self.goal = np.zeros(3)
        self.yaw, self.pitch, self.dist = 0.35, 0.95, 9000.0       # intro: terbang dari jauh
        self.gyaw, self.gpitch, self.gdist = 0.35, 0.62, OVERVIEW_DIST
        self.shake = 0.0
        self.pos = np.zeros(3)
        self.M = np.eye(3)
        self.MT = np.eye(3)
        self.build()

    def update(self, dt):
        k = 1.0 - math.exp(-dt * 4.2)
        self.tgt += (self.goal - self.tgt) * k
        self.yaw += (self.gyaw - self.yaw) * k
        self.pitch += (self.gpitch - self.pitch) * k
        ld = math.log(self.dist)
        self.dist = math.exp(ld + (math.log(self.gdist) - ld) * k)
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 1.8)
        self.build()

    def build(self):
        self.pitch = clamp(self.pitch, -1.35, 1.35)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        off = np.array([cp * math.sin(self.yaw), sp, cp * math.cos(self.yaw)])
        pos = self.tgt + off * self.dist
        if self.shake > 0:
            pos = pos + np.random.uniform(-1.0, 1.0, 3) * (self.shake * self.dist * 0.012)
        fwd = -off
        right = np.array([-fwd[2], 0.0, fwd[0]])
        right /= math.sqrt(right[0] * right[0] + right[2] * right[2])
        up = np.cross(right, fwd)
        self.pos = pos
        self.M = np.array([right, up, fwd])
        self.MT = self.M.T.copy()

    def orbit(self, dyaw, dpitch):
        self.yaw += dyaw
        self.gyaw += dyaw
        self.pitch = clamp(self.pitch + dpitch, -1.35, 1.35)
        self.gpitch = self.pitch

    def spin(self, dyaw):
        self.yaw += dyaw
        self.gyaw += dyaw

    def pan(self, rx, ry):
        right, up = self.M[0], self.M[1]
        d = (-right * rx + up * ry) * (self.dist / FOCAL)
        self.tgt += d
        self.goal += d

    def move(self, d):
        self.tgt += d
        self.goal += d


# ---------------------------------------------------------------------
#  RENDERER 3D  (proyeksi perspektif + gambar glow aditif massal)
# ---------------------------------------------------------------------
class Ren:
    def __init__(self, surf):
        self.s = surf
        self.cam = None
        self.has_fblits = hasattr(pygame.Surface, "fblits")

    def begin(self, surf, cam):
        self.s = surf
        self.cam = cam
        self.cpos = cam.pos
        self.MT = cam.MT
        r, u, f = cam.M
        self.pr, self.pu, self.pf = tuple(r.tolist()), tuple(u.tolist()), tuple(f.tolist())
        self.pp = tuple(cam.pos.tolist())

    # ---- blit massal ----
    def blit_many(self, seq):
        if self.has_fblits:
            self.s.fblits(seq, ADD)
        else:
            self.s.blits([(a, b, None, ADD) for a, b in seq], False)

    # ---- proyeksi ----
    def proj(self, P):
        c = (P - self.cpos) @ self.MT
        z = c[:, 2]
        k = FOCAL / np.maximum(z, NEAR)
        return HW + c[:, 0] * k, HH - c[:, 1] * k, z, k

    def p1(self, p):
        """Proyeksi satu titik -> (sx, sy, z, k). z<NEAR berarti di belakang kamera."""
        px, py, pz = self.pp
        dx, dy, dz = p[0] - px, p[1] - py, p[2] - pz
        f = self.pf
        z = dx * f[0] + dy * f[1] + dz * f[2]
        k = FOCAL / (z if z > NEAR else NEAR)
        r, u = self.pr, self.pu
        return (HW + (dx * r[0] + dy * r[1] + dz * r[2]) * k,
                HH - (dx * u[0] + dy * u[1] + dz * u[2]) * k, z, k)

    # ---- glow ----
    def glow1(self, p, size, gs):
        sx, sy, z, k = self.p1(p)
        if z < NEAR:
            return
        r = size * k
        if sx + r < 0 or sx - r > W or sy + r < 0 or sy - r > H:
            return
        rs = SNAP_L[int(r) if r < MAXR else MAXR]
        self.s.blit(gs[rs], (int(sx) - rs, int(sy) - rs), None, ADD)

    def glow(self, P, size, ci, pal, zsplit=None, mode=0):
        """Glow untuk banyak titik 3D. ci=None -> pal adalah satu GlowSet."""
        c = (P - self.cpos) @ self.MT
        z = c[:, 2]
        ok = z > NEAR
        if zsplit is not None:
            ok &= (z > zsplit) if mode > 0 else (z < zsplit)
        k = FOCAL / np.maximum(z, NEAR)
        sx = HW + c[:, 0] * k
        sy = HH - c[:, 1] * k
        r = k * size
        ok &= (sx + r > 0) & (sx - r < W) & (sy + r > 0) & (sy - r < H)
        idx = np.flatnonzero(ok)
        if idx.size == 0:
            return
        rs = SNAP[np.minimum(r[idx], MAXR).astype(np.int32)]
        xs = (sx[idx] - rs).astype(np.int32).tolist()
        ys = (sy[idx] - rs).astype(np.int32).tolist()
        rl = rs.tolist()
        if ci is None:
            seq = [(pal[a], (x, y)) for a, x, y in zip(rl, xs, ys)]
        else:
            cl = ci[idx].tolist()
            seq = [(pal[c_][a], (x, y)) for c_, a, x, y in zip(cl, rl, xs, ys)]
        self.blit_many(seq)

    def glow2d(self, xs, ys, rs, gs):
        """Glow di koordinat layar (array)."""
        rs = SNAP[np.clip(rs, 0, MAXR).astype(np.int32)]
        px = (xs - rs).astype(np.int32).tolist()
        py = (ys - rs).astype(np.int32).tolist()
        self.blit_many([(gs[a], (x, y)) for a, x, y in zip(rs.tolist(), px, py)])

    # ---- garis ----
    def poly(self, P, layers, closed=False):
        c = (P - self.cpos) @ self.MT
        z = c[:, 2]
        ok = z > NEAR
        if not ok.any():
            return
        k = FOCAL / np.maximum(z, NEAR)
        x = np.clip(HW + c[:, 0] * k, -3000, 3000)
        y = np.clip(HH - c[:, 1] * k, -3000, 3000)
        xo, yo = x[ok], y[ok]
        if xo.max() < 0 or xo.min() > W or yo.max() < 0 or yo.min() > H:
            return
        if ok.all():
            runs = [list(zip(x.tolist(), y.tolist()))]
        else:
            runs, cur = [], []
            okl, xl, yl = ok.tolist(), x.tolist(), y.tolist()
            for i in range(len(okl)):
                if okl[i]:
                    cur.append((xl[i], yl[i]))
                else:
                    if len(cur) >= 2:
                        runs.append(cur)
                    cur = []
            if len(cur) >= 2:
                runs.append(cur)
            closed = False
        for col, w in layers:
            for pts in runs:
                pygame.draw.lines(self.s, col, closed, pts, w)

    def edges(self, P, E, color, width=1):
        c = (P - self.cpos) @ self.MT
        z = c[:, 2]
        k = FOCAL / np.maximum(z, NEAR)
        x = np.clip(HW + c[:, 0] * k, -3000, 3000)
        y = np.clip(HH - c[:, 1] * k, -3000, 3000)
        ok = (z[E[:, 0]] > NEAR) & (z[E[:, 1]] > NEAR)
        ia, ib = E[ok, 0], E[ok, 1]
        draw = pygame.draw.line
        for x0, y0, x1, y1 in zip(x[ia].tolist(), y[ia].tolist(), x[ib].tolist(), y[ib].tolist()):
            draw(self.s, color, (x0, y0), (x1, y1), width)

    def segs(self, P0, P1, color, width=1):
        n = len(P0)
        E = np.stack((np.arange(n), np.arange(n) + n), axis=1)
        self.edges(np.vstack((P0, P1)), E, color, width)


# ---------------------------------------------------------------------
#  LATAR: NEBULA PANORAMA + BINTANG SKYBOX 3D
# ---------------------------------------------------------------------
class Starfield:
    PW, PH = 2560, 1220

    def __init__(self):
        rnd = random.Random(7)
        rng = np.random.default_rng(7)
        n = 1100
        v = rng.normal(size=(n, 3))
        v /= np.linalg.norm(v, axis=1)[:, None]
        self.dirs = v
        self.ph = rng.random(n) * TAU
        palette_ = np.array([(255, 255, 255), (190, 210, 255), (255, 230, 200), (200, 190, 255)],
                            dtype=np.float64)
        self.col = palette_[rng.integers(0, 4, n)]
        self.big = rng.random(n) > 0.88
        self.neb = pygame.Surface((self.PW, self.PH)).convert()
        self.neb.fill((3, 3, 10))
        cols = [(60, 20, 110), (20, 50, 120), (110, 20, 70), (15, 90, 110), (80, 40, 20)]
        for i in range(16):
            g = glowset(cols[i % 5])
            r = rnd.choice((200, 256, 320))
            x = rnd.randint(0, self.PW)
            y = rnd.randint(200, self.PH - 200)
            for dx in (0, -self.PW):
                self.neb.blit(g[r], (x - r + dx, y - r), None, ADD)

    def draw(self, s, cam, t):
        ox = -((cam.yaw * self.PW / TAU) % self.PW)
        oy = -250 + clamp(cam.pitch * 220.0, -250, 250)
        s.blit(self.neb, (int(ox), int(oy)))
        s.blit(self.neb, (int(ox + self.PW), int(oy)))
        c = self.dirs @ cam.MT
        z = c[:, 2]
        ok = z > 0.02
        inv = FOCAL / np.where(ok, z, 1.0)
        sx = (HW + c[:, 0] * inv).astype(np.int32)
        sy = (HH - c[:, 1] * inv).astype(np.int32)
        ok &= (sx >= 0) & (sx < W - 1) & (sy >= 0) & (sy < H - 1)
        idx = np.flatnonzero(ok)
        if idx.size == 0:
            return
        b = 0.62 + 0.38 * np.sin(t * 1.7 + self.ph[idx])
        rgb = (self.col[idx] * b[:, None]).astype(np.uint32)
        xs, ys, bg = sx[idx], sy[idx], self.big[idx]
        arr = None
        try:
            rsh, gsh, bsh, _ = s.get_shifts()
            packed = (rgb[:, 0] << rsh) | (rgb[:, 1] << gsh) | (rgb[:, 2] << bsh)
            arr = pygame.surfarray.pixels2d(s)
            arr[xs, ys] = packed
            xb, yb, pb = xs[bg], ys[bg], packed[bg]
            arr[xb + 1, yb] = pb
            arr[xb, yb + 1] = pb
            arr[xb + 1, yb + 1] = pb
            arr = None                                   # lepas kunci surface
        except Exception:
            arr = None
            for x, y, cc, bb in zip(xs.tolist(), ys.tolist(), rgb.tolist(), bg.tolist()):
                s.fill(cc, (x, y, 2 if bb else 1, 2 if bb else 1))


# ---------------------------------------------------------------------
#  BASE CLASS DIMENSI
# ---------------------------------------------------------------------
class Universe:
    def __init__(self, idx, name, sub, pos, R, color, seed):
        self.idx = idx
        self.name = name
        self.sub = sub
        self.p = np.array(pos, dtype=np.float64)
        self.pt = (float(pos[0]), float(pos[1]), float(pos[2]))
        self.R = float(R)
        self.color = color
        self.dim = mul(color, 0.30)
        self.mid = mul(color, 0.55)
        self.gs = glowset(color)
        self.halo = glowset(mul(color, 0.13))
        self.halo.warm(16)
        self.flash = 0.0
        self.rnd = random.Random(seed)
        self.rng = np.random.default_rng(seed)
        self.stats = [("ENTROPI", self.rnd.random() * TAU, self.rnd.uniform(0.3, 0.8)),
                      ("ENERGI", self.rnd.random() * TAU, self.rnd.uniform(0.4, 0.9)),
                      ("STABILITAS", self.rnd.random() * TAU, self.rnd.uniform(0.3, 0.85))]
        self.scr = None
        self.circle = unit_circle(64)
        self.tilts = (np.eye(3), rot_x(1.05), rot_z(1.05))
        tk = np.linspace(0, TAU, 36, endpoint=False)
        self.tick_dir = np.stack((np.cos(tk), np.zeros(36), np.sin(tk)), axis=1)
        self.tick_len = np.where(np.arange(36) % 6 == 0, 1.14, 1.09)[:, None]
        self.build()

    def build(self):
        pass

    def render(self, ren, t, qmul):
        self.scr = None
        sx, sy, z, k = ren.p1(self.pt)
        R = self.R
        if z < -R:
            return
        sr = R * k
        m = sr * 1.3
        if sx + m < 0 or sx - m > W or sy + m < 0 or sy - m > H:
            return
        self.scr = (sx, sy, sr, z)
        base = 1 if sr > 170 else (2 if sr > 70 else 3)
        step = max(1, int(base * qmul + 0.5))
        if sr < 400:
            ren.glow1(self.pt, R * 1.1, self.halo)
        self.body(ren, t, sr, step)
        self.frame(ren, t, sr)

    def body(self, ren, t, sr, step):
        pass

    def frame(self, ren, t, sr):
        if sr < 12:
            return
        fl = self.flash
        spin = t * 0.15 * (1 if self.idx % 2 else -1)
        c0 = mul(self.color, 0.16 + 0.75 * fl)
        c1 = mul(self.color, 0.30 + 0.70 * fl)
        Rr = self.R * 1.06
        for i, tilt in enumerate(self.tilts):
            Rm = rot_y(spin * (1.0 + 0.35 * i)) @ tilt
            P = (self.circle @ Rm.T) * Rr + self.p
            ren.poly(P, [(c1 if i == 0 else c0, 1)], False)
        if sr > 55:
            Ry = rot_y(spin).T
            d = self.tick_dir @ Ry
            P0 = d * (self.R * 1.05) + self.p
            P1 = d * (self.R * self.tick_len) + self.p
            ren.segs(P0, P1, self.mid, 1)


# ---------------------------------------------------------------------
#  1. GALAKSI SPIRAL 3D
# ---------------------------------------------------------------------
class Galaxy(Universe):
    def build(self):
        rng = self.rng
        n1, n2 = 900, 260
        arm = np.arange(n1) % 3
        r1 = 0.06 + 0.94 * rng.random(n1) ** 0.8
        b1 = arm * TAU / 3 + r1 * 5.0 + rng.normal(size=n1) * (0.16 + 0.12 * r1)
        h1 = rng.normal(size=n1) * (0.012 + 0.05 * (1 - r1) ** 2)
        r2 = 0.03 + 0.22 * rng.random(n2) ** 1.4
        b2 = rng.random(n2) * TAU
        h2 = rng.normal(size=n2) * 0.07
        r = np.concatenate((r1, r2))
        base = np.concatenate((b1, b2))
        h = np.concatenate((h1, h2))
        perm = rng.permutation(n1 + n2)
        r, base, h = r[perm], base[perm], h[perm]
        self.base = base
        self.spd = 0.28 / (r ** 0.55 + 0.2)
        self.rr = r * self.R * 0.92
        self.hy = h * self.R
        big = rng.random(n1 + n2) < 0.25
        self.size = np.where(big, rng.choice([3.0, 4.0, 5.5, 7.0], n1 + n2),
                             rng.choice([1.6, 2.2, 3.0], n1 + n2))
        self.ci = np.minimum(7, (r * 8).astype(np.int32))
        cols = [(255, 230, 190), (255, 205, 150), (255, 180, 140), (210, 170, 255),
                (150, 170, 255), (110, 150, 255), (90, 120, 230), (70, 100, 200)]
        self.pal = palette(cols)
        self.core1 = glowset((255, 200, 150))
        self.core2 = glowset((255, 240, 220))
        self.core1.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        sq = math.sqrt(step)
        Rm = rot_x(0.75 + 0.10 * math.sin(t * 0.2)) @ rot_z(0.25)
        a = self.base[::step] + t * self.spd[::step]
        rr = self.rr[::step]
        loc = np.stack((np.cos(a) * rr, self.hy[::step], np.sin(a) * rr), axis=1)
        P = loc @ Rm.T + self.p
        ren.glow(P, self.size[::step] * sq, self.ci[::step], self.pal)
        pulse = 1 + 0.08 * math.sin(t * 2)
        ren.glow1(self.pt, R * 0.26 * pulse, self.core1)
        ren.glow1(self.pt, R * 0.10, self.core2)


# ---------------------------------------------------------------------
#  2. TATA SURYA NEON 3D (orbit miring)
# ---------------------------------------------------------------------
class Solar(Universe):
    def build(self):
        rng = self.rng
        # (orbit, ukuran, kecepatan, warna, jumlah bulan, inklinasi, node)
        self.planets = [
            (0.28, 7, 1.40, (90, 255, 220), 0, 0.00, 0.0),
            (0.42, 11, 0.95, (255, 120, 190), 1, 0.38, 1.0),
            (0.58, 9, 0.65, (120, 160, 255), 2, -0.30, 2.1),
            (0.76, 14, 0.42, (255, 200, 110), 1, 0.55, 3.0),
            (0.92, 8, 0.28, (190, 120, 255), 0, -0.48, 4.2),
        ]
        self.rm = [rot_y(p[6]) @ rot_x(p[5]) for p in self.planets]
        self.phase = [self.rnd.random() * TAU for _ in self.planets]
        self.gpl = [glowset(p[3]) for p in self.planets]
        for g in self.gpl:
            g.warm(24)
        n = 170
        self.b_a0 = rng.random(n) * TAU
        self.b_r = rng.uniform(0.63, 0.71, n) * self.R
        self.b_y = rng.normal(size=n) * 0.018 * self.R
        self.b_spd = rng.uniform(0.25, 0.5, n)
        self.b_size = rng.choice([1.4, 1.8, 2.4], n)
        self.belt_rm = rot_x(0.12) @ rot_z(0.05)
        self.oc = unit_circle(64)
        self.belt_gs = glowset((120, 130, 190))
        self.sun1, self.sun2, self.sun3 = glowset((255, 110, 190)), glowset((255, 200, 230)), glowset((255, 255, 255))
        self.moon = glowset((220, 225, 255))
        self.core_w = glowset((255, 255, 255))
        for g in (self.sun1, self.moon, self.core_w, self.belt_gs):
            g.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        sq = math.sqrt(step)
        pulse = 1 + 0.06 * math.sin(t * 3)
        ren.glow1(self.pt, R * 0.17 * pulse, self.sun1)
        ren.glow1(self.pt, R * 0.09, self.sun2)
        ren.glow1(self.pt, R * 0.045, self.sun3)
        if sr > 40:
            for i, pl in enumerate(self.planets):
                P = (self.oc @ self.rm[i].T) * (pl[0] * R) + self.p
                ren.poly(P, [((58, 46, 105), 1)], False)
        a = self.b_a0[::step] + t * self.b_spd[::step]
        rr = self.b_r[::step]
        loc = np.stack((np.cos(a) * rr, self.b_y[::step], np.sin(a) * rr), axis=1)
        ren.glow((loc @ self.belt_rm.T) + self.p, self.b_size[::step] * sq, None, self.belt_gs)
        for i, (of, size, spd, col, moons, inc, node) in enumerate(self.planets):
            ang = t * spd + self.phase[i]
            rr_ = of * R
            loc = np.array([math.cos(ang) * rr_, 0.0, math.sin(ang) * rr_])
            pp = (self.rm[i] @ loc + self.p).tolist()
            ren.glow1(pp, size * 1.5, self.gpl[i])
            ren.glow1(pp, size * 0.55, self.core_w)
            for k in range(moons):
                ma = t * 3.2 * (k + 1) + i
                d = size * 2.3 + 7 * k
                mp = (pp[0] + math.cos(ma) * d, pp[1] + math.sin(ma) * d * 0.45,
                      pp[2] + math.sin(ma) * d * 0.9)
                ren.glow1(mp, 2.4, self.moon)


# ---------------------------------------------------------------------
#  3. LUBANG HITAM 3D
# ---------------------------------------------------------------------
class BlackHole(Universe):
    def build(self):
        rng = self.rng
        n = 760
        r = 0.27 + 0.68 * rng.random(n) ** 1.3
        self.a0 = rng.random(n) * TAU
        self.dr = r * self.R
        self.spd = 0.45 / (r ** 1.5)
        self.ci = np.minimum(6, ((r - 0.27) / 0.68 * 7).astype(np.int32))
        self.size = rng.uniform(1.8, 4.2, n)
        self.dy = rng.normal(size=n) * 0.012 * self.R
        cols = [(255, 250, 220), (255, 225, 150), (255, 190, 90), (255, 140, 50),
                (230, 90, 60), (180, 50, 110), (120, 30, 140)]
        self.pal = palette(cols)
        nj = 240
        self.j_off = rng.random(nj)
        self.j_rad = np.abs(rng.normal(size=nj)) * 0.05 + 0.01
        self.j_spd = rng.uniform(0.3, 0.6, nj)
        self.j_sgn = np.where(np.arange(nj) % 2 == 0, 1.0, -1.0)
        self.j_ph = rng.random(nj) * TAU
        self.jet_pal = palette([(255, 255, 255), (110, 160, 255)])
        nh = 56
        self.h_ang = np.linspace(0, TAU, nh, endpoint=False)
        self.h_n = rng.uniform(-0.02, 0.03, nh)
        self.h_s = rng.uniform(1.5, 2.6, nh)
        self.h_gs = glowset((255, 210, 150))
        self.dust = glowset((90, 45, 15))
        self.dust.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        sx, sy, z0, k = ren.p1(self.pt)
        sq = math.sqrt(step)
        Rm = rot_z(-0.28) @ rot_x(0.32 + 0.07 * math.sin(t * 0.13))
        # ring shockwave halus
        for i in range(3):
            u = (t * 0.18 + i / 3.0) % 1.0
            rr = (0.3 + 0.9 * u) * R * k
            if 4 < rr < 1500:
                pygame.draw.circle(ren.s, mul(self.color, 0.22 * (1 - u)), (int(sx), int(sy)), int(rr), 1)
        ren.glow1(self.pt, 0.62 * R, self.dust)
        # cakram
        a = self.a0[::step] + t * self.spd[::step]
        dr = self.dr[::step]
        loc = np.stack((np.cos(a) * dr, self.dy[::step], np.sin(a) * dr), axis=1)
        P = loc @ Rm.T + self.p
        size, ci = self.size[::step] * sq, self.ci[::step]
        if z0 > NEAR:
            ren.glow(P, size, ci, self.pal, zsplit=z0, mode=1)          # sisi belakang
            rh = int(0.22 * R * k)
            if 1 < rh < 2500:
                pygame.draw.circle(ren.s, (0, 0, 0), (int(sx), int(sy)), rh)
                pygame.draw.circle(ren.s, (255, 200, 130), (int(sx), int(sy)),
                                   int(0.235 * R * k), max(1, int(2.2 * k)))
                hr = 0.245 * R * k + self.h_n * R * k
                ren.glow2d(sx + np.cos(self.h_ang + t * 0.8) * hr, sy + np.sin(self.h_ang + t * 0.8) * hr,
                           self.h_s * sq * k, self.h_gs)
            ren.glow(P, size, ci, self.pal, zsplit=z0, mode=-1)         # sisi depan
        else:
            ren.glow(P, size, ci, self.pal)
        # jet relativistik (heliks 3D sepanjang sumbu putar)
        js = max(1, step)
        u = (t * self.j_spd[::js] + self.j_off[::js]) % 1.0
        ang = u * 9.0 + self.j_ph[::js] + t * 2.0
        rad = self.j_rad[::js] * R * (0.4 + 1.6 * u) + 0.015 * R
        jl = np.stack((np.cos(ang) * rad, self.j_sgn[::js] * (0.22 + 1.1 * u) * R, np.sin(ang) * rad), axis=1)
        jsz = ((1 - u) * 5.5 + 1.2) * math.sqrt(js)
        ren.glow(jl @ Rm.T + self.p, jsz, (u >= 0.25).astype(np.int32), self.jet_pal)


# ---------------------------------------------------------------------
#  4. REALITAS KRISTAL (wireframe 3D)
# ---------------------------------------------------------------------
class Crystal(Universe):
    def build(self):
        rng = self.rng
        cube = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
        cube_e = [(i, j) for i in range(8) for j in range(i + 1, 8)
                  if np.sum(cube[i] != cube[j]) == 1]
        octa = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)], float)
        octa_e = [(i, j) for i in range(6) for j in range(i + 1, 6)
                  if not np.allclose(octa[i], -octa[j])]
        phi = (1 + 5 ** 0.5) / 2
        ico = []
        for a in (-1, 1):
            for b in (-phi, phi):
                ico += [(0, a, b), (a, b, 0), (b, 0, a)]
        ico = np.array(ico, float)
        ico_e = [(i, j) for i in range(12) for j in range(i + 1, 12)
                 if abs(np.sum((ico[i] - ico[j]) ** 2) - 4) < 1e-6]
        self.shapes = [
            (cube, np.array(cube_e), 0.40 / 1.732, (80, 255, 255), (0.5, 0.8, 0.2)),
            (octa, np.array(octa_e), 0.72, (255, 90, 220), (-0.6, 0.4, 0.3)),
            (ico, np.array(ico_e), 0.92 / 1.902, (110, 130, 210), (0.15, -0.25, 0.1)),
        ]
        self.vgs = [glowset(s[3]) for s in self.shapes]
        for g in self.vgs:
            g.warm(12)
        n = 40
        self.s_rad = rng.uniform(0.55, 1.0, n) * self.R
        self.s_ph = rng.random(n) * TAU
        self.s_inc = rng.uniform(0.15, 0.9, n)
        self.s_sp = rng.uniform(0.3, 1.1, n) * rng.choice([-1, 1], n)
        self.s_size = rng.choice([2.4, 3.2, 4.4], n)
        self.s_ci = (rng.random(n) < 0.5).astype(np.int32)
        self.s_pal = palette([(150, 255, 240), (255, 150, 240)])
        self.core1, self.core2 = glowset((60, 190, 200)), glowset((230, 255, 255))
        self.core1.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        pulse = 1 + 0.1 * math.sin(t * 2.6)
        ren.glow1(self.pt, 0.30 * R * pulse, self.core1)
        ren.glow1(self.pt, 0.08 * R, self.core2)
        width = 1 if sr < 120 else 2
        vs = 3.2 * math.sqrt(step)
        for (verts, E, sc, col, (wx, wy, wz)), gs in zip(self.shapes, self.vgs):
            Rm = rot_z(t * wz) @ rot_y(t * wy) @ rot_x(t * wx)
            P = (verts @ Rm.T) * (sc * R) + self.p
            ren.edges(P, E, col, width)
            ren.glow(P, vs, None, gs)
        a = self.s_ph[::step] + t * self.s_sp[::step]
        rad, inc = self.s_rad[::step], self.s_inc[::step]
        loc = np.stack((rad * np.cos(a), rad * np.sin(a) * np.sin(inc), rad * np.sin(a) * np.cos(inc)), axis=1)
        ren.glow(loc + self.p, self.s_size[::step] * math.sqrt(step), self.s_ci[::step], self.s_pal)


# ---------------------------------------------------------------------
#  5. BADAI BARA (pusaran 3D + petir)
# ---------------------------------------------------------------------
class Ember(Universe):
    def build(self):
        rng = self.rng
        n = 1000
        self.off = rng.random(n)
        self.rate = rng.uniform(0.08, 0.20, n)
        self.spin = rng.uniform(0.8, 1.6, n)
        self.a0 = rng.random(n) * TAU
        self.rad = rng.uniform(0.55, 1.0, n)
        self.size = rng.choice([2.2, 3.0, 4.0, 5.5], n)
        cols = [(255, 255, 220), (255, 220, 120), (255, 160, 50),
                (240, 90, 30), (180, 40, 25), (110, 25, 30)]
        self.pal = palette(cols)
        self.g_base = glowset((255, 110, 40))
        self.g_base.warm(16)
        self.g_cloud = glowset((120, 40, 60))
        self.g_flash = glowset((60, 80, 190))

    def body(self, ren, t, sr, step):
        R = self.R
        sq = math.sqrt(step)
        kk = sr / R
        ren.glow1((self.pt[0], self.pt[1] - 0.8 * R, self.pt[2]), 0.32 * R * (1 + 0.1 * math.sin(t * 5)), self.g_base)
        ren.glow1((self.pt[0], self.pt[1] + 0.85 * R, self.pt[2]), 0.42 * R, self.g_cloud)
        u = (t * self.rate[::step] + self.off[::step]) % 1.0
        a = self.a0[::step] + t * self.spin[::step] * (2.4 - 1.6 * u)
        r = (0.10 + 0.80 * u) * self.rad[::step] * R
        P = np.stack((np.cos(a) * r, (-0.8 + 1.6 * u) * R, np.sin(a) * r), axis=1) + self.p
        ci = np.minimum(5, (u * 6).astype(np.int32))
        ren.glow(P, self.size[::step] * sq * (1.0 - 0.55 * u), ci, self.pal)
        # petir
        k = int(t * 1.6)
        ph = t * 1.6 - k
        if ph < 0.16 and k % 3 != 1:
            rr = random.Random(k * 131 + 7)
            x0, z0 = rr.uniform(-0.3, 0.3) * R, rr.uniform(-0.3, 0.3) * R
            x1, z1 = rr.uniform(-0.2, 0.2) * R, rr.uniform(-0.2, 0.2) * R
            y0, y1 = 0.85 * R, -0.8 * R
            n = 10
            pts = []
            for i in range(n + 1):
                f = i / n
                j = 0.0 if i in (0, n) else 0.08 * R
                pts.append((x0 + (x1 - x0) * f + rr.uniform(-j, j), y0 + (y1 - y0) * f,
                            z0 + (z1 - z0) * f + rr.uniform(-j, j)))
            P = np.array(pts) + self.p
            ren.glow1(P[0].tolist(), 0.5 * R, self.g_flash)
            ren.poly(P, [((120, 150, 255), max(2, int(4 * kk))), ((235, 245, 255), max(1, int(2 * kk)))])


# ---------------------------------------------------------------------
#  6. SIMULASI RUSAK (torus 3D + hujan kode + glitch)
# ---------------------------------------------------------------------
class Matrix(Universe):
    GLYPHS = "01ABCDEF<>/|\\#$"

    def build(self):
        rng = self.rng
        R = self.R
        uu = np.repeat(np.arange(18) * TAU / 18, 12)
        vv = np.tile(np.arange(12) * TAU / 12, 18)
        Rm_, rn = 0.52, 0.24
        rr = Rm_ + rn * np.cos(vv)
        self.base = np.stack((rr * np.cos(uu), rr * np.sin(uu), rn * np.sin(vv)), axis=1) * R
        self.pal = palette([(0, 90, 50), (0, 170, 90), (60, 255, 150), (210, 255, 235), (255, 60, 200)])
        n = 44
        self.r_x = rng.uniform(-0.7, 0.7, n)
        self.r_z = rng.uniform(-0.7, 0.7, n)
        self.r_sp = rng.uniform(0.15, 0.4, n)
        self.r_off = rng.random(n)
        self.rain_pal = palette([(120, 255, 180), (0, 150, 80), (0, 150, 80), (0, 80, 45), (0, 80, 45)])
        cube = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float) * 0.9 * R
        self.cube = cube
        self.cube_e = np.array([(i, j) for i in range(8) for j in range(i + 1, 8)
                                if np.sum(cube[i] != cube[j]) == 1])
        self.core = glowset((0, 120, 70))
        self.core.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        sq = math.sqrt(step)
        cam = ren.cam
        Ry = rot_y(t * 0.12)
        ren.glow1(self.pt, 0.25 * R * (1 + 0.1 * math.sin(t * 3)), self.core)
        if sr > 30:
            ren.edges(((self.cube @ Ry.T) + self.p), self.cube_e, (0, 70, 42), 1)
        # hujan kode 3D
        if step < 3 and sr > 40:
            K = np.arange(5)
            frac = (t * self.r_sp + self.r_off) % 1.0
            yh = (1.0 - 2.0 * frac) * 0.9 * R
            yk = yh[:, None] + K[None, :] * 0.11 * R
            valid = np.abs(yk) <= 0.9 * R
            xz = np.stack((self.r_x * R, self.r_z * R), axis=1)
            pos = np.empty((len(frac), 5, 3))
            pos[:, :, 0] = xz[:, 0:1]
            pos[:, :, 1] = yk
            pos[:, :, 2] = xz[:, 1:2]
            pos = (pos.reshape(-1, 3) @ Ry.T).reshape(-1, 5, 3) + self.p
            ci = np.broadcast_to(K[None, :], (len(frac), 5))
            sz = np.broadcast_to(3.2 - 0.4 * K[None, :], (len(frac), 5))
            v = valid
            ren.glow(pos[v], sz[v], ci[v], self.rain_pal)
            if sr > 170:
                heads = pos[:, 0, :]
                hv = valid[:, 0]
                sx, sy, z, k = ren.proj(heads)
                for i in np.flatnonzero(hv & (z > NEAR))[:16].tolist():
                    ch = self.GLYPHS[(int(t * 9) + i * 7) % len(self.GLYPHS)]
                    g = TXT.get(ch, 14, (210, 255, 235), True)
                    ren.s.blit(g, (int(sx[i]) - g.get_width() // 2, int(sy[i]) - g.get_height() // 2))
        # torus
        Rm = rot_y(t * 0.33) @ rot_x(t * 0.55) @ rot_z(t * 0.21)
        P = self.base @ Rm.T + self.p
        if step < 3 and sr > 60:
            rings = P.reshape(18, 12, 3)
            for i in range(0, 18, 3):
                ren.poly(rings[i], [((0, 110, 65), 1)], True)
        g = int(t * 9)
        glitch = (((g * 1103515245 + 12345) >> 8) % 5 == 0)
        d = (P - self.p) @ cam.M[2]                      # >0 = menjauh dari kamera
        ci = 3 - np.clip(((d / R + 0.75) / 1.5 * 4).astype(np.int32), 0, 3)
        Q = P
        if glitch:
            m = (np.arange(len(P)) % 7) == (g % 7)
            Q = P.copy()
            Q[m, 0] += 0.13 * R
            ci = ci.copy()
            ci[m] = 4
        ren.glow(Q[::step], 4.4 * sq, ci[::step], self.pal)


# ---------------------------------------------------------------------
#  THE NEXUS (hub pusat, gyroscope 3D)
# ---------------------------------------------------------------------
class Hub(Universe):
    def build(self):
        self.polys = [(3, 0.96, 1.0), (4, 0.80, -1.3), (5, 0.66, 0.9), (6, 0.52, -0.7), (8, 0.38, 1.6)]
        self.pl = []
        for n, _, _ in self.polys:
            a = np.arange(n) * TAU / n
            self.pl.append(np.stack((np.cos(a), np.sin(a), np.zeros(n)), axis=1))
        sp = np.arange(10) * TAU / 10
        self.spark = np.stack((np.cos(sp), np.zeros(10), np.sin(sp)), axis=1)
        self.white = glowset((255, 255, 255))
        self.white.warm(16)

    def body(self, ren, t, sr, step):
        R = self.R
        hq = int(t * 22) // 15 * 15
        pulse = 1 + 0.1 * math.sin(t * 2.4)
        ren.glow1(self.pt, 0.95 * R, glowset(hue(hq, 0.6, 0.5)))
        width = 2 if sr > 50 else 1
        for i, (n, rf, sp) in enumerate(self.polys):
            col = hue(hq + i * 40, 0.65, 1.0)
            Rm = rot_y(t * sp * 0.45 + i * 0.9) @ rot_x(t * 0.35 * (1 if i % 2 else -1) + i * 0.7)
            P = (self.pl[i] @ Rm.T) * (rf * R) + self.p
            ren.poly(P, [(col, width)], True)
            ren.glow(P, 3.5, None, glowset(col))
        ren.glow1(self.pt, 0.34 * R * pulse, glowset(hue(hq, 0.5, 1.0)))
        ren.glow1(self.pt, 0.18 * R * pulse, self.white)
        Rm = rot_x(0.6) @ rot_y(t * 0.9)
        P = (self.spark @ Rm.T) * R + self.p
        ren.glow(P, 3.0, None, glowset(hue(hq + 120, 0.7, 1.0)))


# ---------------------------------------------------------------------
#  EFEK "BUKA DIMENSI"  (dipicu tombol BUKA / ENTER)
#    1. KUMPUL  : ribuan partikel terhisap spiral ke inti universe + cincin menyempit
#    2. LEDAKAN : ledakan partikel 3D, gelombang kejut, kamera bergetar
#    3. WARP    : terowongan garis cahaya + partikel layar, kamera menembus universe
#    4. FLASH   : layar memutih -> halaman HTML dibuka -> kembali ke ruang multiverse
# ---------------------------------------------------------------------
class OpenFX:
    T_CHARGE = 1.05          # detik fase kumpul energi
    T_GAP = 0.12             # jeda ledakan -> warp penuh
    T_WARP = 1.35            # detik fase warp
    T_FADE = 1.00            # detik fase kembali
    LAUNCH_P = 0.90          # browser dibuka saat warp mencapai 90%
    RMAX = 1250.0            # radius terowongan warp (piksel)

    def __init__(self, app, ent, url):
        self.app, self.e, self.url = app, ent, url
        self.t = 0.0
        self.launched = False
        self.burst_done = False
        self.fade_started = False
        self.done = False
        self.hide_hud = False
        self.rings = []
        self.t_burst = self.T_CHARGE
        self.t_warp0 = self.t_burst + self.T_GAP
        self.t_warp1 = self.t_warp0 + self.T_WARP
        self.t_end = self.t_warp1 + self.T_FADE

        rng = np.random.default_rng()
        pm = max(0.05, float(PARTICLE_MULT))
        R = ent.R
        c = ent.color
        bright = tuple(int(v + (255 - v) * 0.55) for v in c)
        h = colorsys.rgb_to_hsv(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)[0] * 360.0
        alt = hue(h + 45, 0.75, 1.0)
        self.c_base, self.c_bright = c, bright
        # palet partikel: warna dasar, terang, putih, warna sekutu, redup
        self.pal = palette([c, bright, (255, 255, 255), alt, mul(c, 0.6)], warm=32)
        self.core, self.white = self.pal[0], self.pal[2]
        self.g2 = [self.pal[0], self.pal[1], self.pal[2]]
        # sprite besar dibuat bertahap (1 per frame) agar tidak tersendat
        q = [(r, gs) for r in SIZES if 64 < r <= 256 for gs in self.pal[:3]]
        q += [(320, self.core), (320, self.white)]
        q.sort(key=lambda a: a[0])
        self.warm_q = [(gs, r) for r, gs in q]           # pop() -> ukuran terbesar dulu

        def unit(n):
            v = rng.normal(size=(n, 3))
            return v / np.maximum(np.linalg.norm(v, axis=1), 1e-9)[:, None]

        # --- fase 1: partikel terhisap spiral ---
        n1 = max(60, int(1800 * pm))
        self.c_dir = unit(n1)
        self.c_r0 = R * rng.uniform(1.4, 4.8, n1)
        self.c_delay = (rng.random(n1) ** 1.3) * 0.55
        self.c_spin = rng.uniform(2.0, 6.0, n1) * rng.choice((-1.0, 1.0), n1)
        self.c_col = rng.integers(0, 5, n1)
        self.c_size = R * rng.uniform(0.012, 0.040, n1)
        self.circ0 = unit_circle(72)

        # --- fase 2: partikel ledakan ---
        n2 = max(60, int(2600 * pm))
        d2 = unit(n2)
        sp = R * (1.2 + 7.0 * rng.random(n2) ** 1.5)
        self.b_pos = d2 * (R * 0.08) + ent.p
        self.b_vel = d2 * sp[:, None]
        self.b_life = rng.uniform(1.0, 2.6, n2)
        self.b_age = np.zeros(n2)
        self.b_col = rng.integers(0, 5, n2)
        self.b_size = R * rng.uniform(0.014, 0.050, n2)

        # --- fase 3: terowongan warp (koordinat layar) ---
        ns = max(40, int(460 * pm))
        a = rng.random(ns) * TAU
        self.w_ca, self.w_sa = np.cos(a), np.sin(a)
        self.w_z0 = rng.random(ns)
        self.w_spd = rng.uniform(0.6, 1.5, ns)
        self.w_mix = rng.uniform(0.3, 1.0, ns)
        ng = max(40, int(650 * pm))
        a = rng.random(ng) * TAU
        self.g_ca, self.g_sa = np.cos(a), np.sin(a)
        self.g_z0 = rng.random(ng)
        self.g_spd = rng.uniform(0.6, 1.5, ng)
        self.g_grp = rng.integers(0, 3, ng)

        self.back = pygame.Surface((600, 150), pygame.SRCALPHA)
        pygame.draw.rect(self.back, (4, 6, 16, 195), self.back.get_rect(), border_radius=14)

    # ---------------- logika ----------------
    def cancel(self):
        if self.done:
            return
        self.done = True
        self.app.focus_on(self.e.idx)

    def update(self, dt):
        app, e, cam = self.app, self.e, self.app.cam
        dt *= FX_SPEED
        self.t += dt
        t, R = self.t, e.R
        if self.warm_q:
            gs, r = self.warm_q.pop()
            gs[r]
        self.hide_hud = t >= self.t_burst - 0.2

        if t < self.t_burst:
            tau = t / self.t_burst
            e.flash = max(e.flash, tau * tau)
            cam.shake = max(cam.shake, 0.04 + 0.30 * tau * tau)
            cam.gdist = clamp(R * (2.5 - 0.8 * tau), DMIN, DMAX)
        elif not self.burst_done:
            self.burst_done = True
            cam.shake = 1.3
            cam.gdist = clamp(R * 0.55, DMIN, DMAX)
            cam.gpitch = 0.2
            for o in app.ents:
                o.flash = max(o.flash, 1.0 if o is e else 0.6)
            self.rings = [0.0, -0.16]

        if t >= self.t_burst:
            self.b_age += dt
            self.b_pos += self.b_vel * dt
            self.b_vel *= math.exp(-0.9 * dt)
            self.rings = [a + dt for a in self.rings]
            if t < self.t_warp1:
                cam.shake = max(cam.shake, 0.16 * smoothstep((t - self.t_burst) / 0.5))
                e.flash = max(e.flash, 0.8)

        if not self.launched and t >= self.t_warp0 + self.LAUNCH_P * self.T_WARP:
            self.launched = True
            app.launch(self.url, e)
        if not self.fade_started and t >= self.t_warp1:
            self.fade_started = True
            app.focus_on(e.idx)                        # kamera mundur kembali
        if t >= self.t_end:
            self.done = True

    @staticmethod
    def _cap(ren, P, sz, px):
        """Batasi radius partikel di layar (px) agar yang lewat dekat kamera tidak jadi bola raksasa."""
        z = (P - ren.cpos) @ ren.MT
        return np.minimum(sz, px / (FOCAL / np.maximum(z[:, 2], NEAR)))

    # ---------------- gambar 3D (partikel & cincin di dalam ruang) ----------------
    def draw3d(self, ren):
        e, t, R, app = self.e, self.t, self.e.R, self.app
        qs = 1.0 / QUALITY[app.qi]
        c, bright = self.c_base, self.c_bright
        if t < self.t_burst:
            tau = t / self.t_burst
            n = max(60, int(len(self.c_dir) * qs))
            d, dl = self.c_dir[:n], self.c_delay[:n]
            u = np.clip((tau - dl) / (1.0 - dl + 1e-6), 0.0, 1.0)
            eu = u ** 1.6
            r = self.c_r0[:n] * (1.0 - eu)
            ang = self.c_spin[:n] * u
            ca, sa = np.cos(ang), np.sin(ang)
            P = np.stack((d[:, 0] * ca + d[:, 2] * sa, d[:, 1], -d[:, 0] * sa + d[:, 2] * ca),
                         axis=1) * r[:, None] + e.p
            vis = (u > 0.0) & (r > R * 0.10)
            if vis.any():
                sz = self.c_size[:n] * (0.55 + 0.6 * (1.0 - eu)) * np.minimum(1.0, u * 12.0)
                Pv = P[vis]
                ren.glow(Pv, self._cap(ren, Pv, sz[vis], 14.0), self.c_col[:n][vis], self.pal)
            for k in range(3):                                  # cincin menyempit
                q = (tau * 1.6 + k / 3.0) % 1.0
                rho = R * (3.4 * (1.0 - q) + 0.22)
                b = math.sin(math.pi * q) * (0.4 + tau)
                Rm = rot_y(t * 2.2 + k * 2.1) @ rot_x(0.9 + k * 0.55)
                ren.poly((self.circ0 @ Rm.T) * rho + e.p,
                         [(mul(c, 0.10 * b), 4), (mul(bright, 0.70 * b), 1)], True)
            core = R * (0.45 + 0.30 * tau ** 2.2)
            ren.glow1(e.pt, core, self.core)
            ren.glow1(e.pt, core * 0.45, self.white)
            return
        # ---- ledakan ----
        tb = t - self.t_burst
        fl = math.exp(-tb * 2.2)
        core = R * (0.45 + 0.45 * fl)
        ren.glow1(e.pt, core, self.core)
        ren.glow1(e.pt, core * 0.4, self.white)
        n = max(60, int(len(self.b_pos) * qs))
        frac = 1.0 - self.b_age[:n] / self.b_life[:n]
        vis = frac > 0.0
        if vis.any():
            sz = self.b_size[:n] * np.maximum(frac, 0.0) ** 0.6
            Pv = self.b_pos[:n][vis]
            ren.glow(Pv, self._cap(ren, Pv, sz[vis], 24.0), self.b_col[:n][vis], self.pal)
            m = np.flatnonzero(vis[:min(n, 380)])                # goresan cahaya
            if m.size:
                P1 = self.b_pos[m]
                ren.segs(P1 - self.b_vel[m] * 0.05, P1, bright, 1)
        for age in self.rings:                                   # gelombang kejut
            if age <= 0.0 or age > 1.5:
                continue
            f = 1.0 - age / 1.5
            rho = age * R * 6.0
            for cc in app.circ_shock:
                ren.poly(cc * rho + e.p, [(mul(c, 0.30 * f), 5), (mul(bright, f), 2)], False)

    # ---------------- gambar 2D (terowongan warp, teks, flash) ----------------
    def draw2d(self, s, ren):
        e, t, app = self.e, self.t, self.app
        c, bright = self.c_base, self.c_bright
        tb = t - self.t_burst
        qs = 1.0 / QUALITY[app.qi]
        p = clamp((t - self.t_warp0) / self.T_WARP, 0.0, 1.0)
        if tb > 0.0:
            fade = 1.0 if t < self.t_warp1 else max(0.0, 1.0 - (t - self.t_warp1) / (self.T_FADE * 0.6))
            A = smoothstep(tb / 0.45) * fade
            if A > 0.01:
                self._warp(s, ren, tb, p, A, qs)
            cx, cy = int(HW), int(HH)
            for t0 in (0.0, 0.14, 0.30):                         # cincin kejut di layar
                age = tb - t0
                f = 1.0 - age / 1.1
                rad = int(age * 1400)
                if age > 0.0 and f > 0.0 and rad > 8:
                    pygame.draw.circle(s, mul(c, 0.35 * f), (cx, cy), rad, 7)
                    pygame.draw.circle(s, mul(bright, f), (cx, cy), rad, 2)
            if tb > 0.25 and t < self.t_warp1:
                self._title(s, tb)
        # ---- flash layar ----
        if tb < 0.0:
            f = 0.10 * (t / self.t_burst) ** 5
        else:
            if t < self.t_warp1:
                wo = smoothstep((p - 0.5) / 0.5)
            else:
                wo = 1.0 - smoothstep((t - self.t_warp1) / self.T_FADE)
            f = max(wo, 0.45 * math.exp(-tb * 5.0))
        if f > 0.003:
            s.fill(tuple(min(255, int((0.72 * 255 + 0.28 * v) * f)) for v in c), special_flags=ADD)

    def _warp(self, s, ren, tb, p, A, qs):
        c = self.c_base
        D = 0.9 * tb + 1.6 * tb * tb
        # -- garis cahaya --
        n = max(40, int(len(self.w_ca) * qs))
        zz = (self.w_z0[:n] - D * self.w_spd[:n]) % 1.0
        tl = 0.03 + 0.10 * min(1.0, tb / 2.0)
        z2 = np.minimum(zz + tl, 1.0)
        ro = 30.0 + self.RMAX * (1.0 - zz) ** 2.2
        ri = 30.0 + self.RMAX * (1.0 - z2) ** 2.2
        b = np.clip((1.0 - zz) ** 0.8 * 1.25, 0.0, 1.0) * A
        idx = np.flatnonzero(b > 0.05)
        if idx.size:
            bb = b[idx][:, None]
            mix = self.w_mix[:n][idx][:, None]
            base = np.array(c, dtype=np.float64)[None, :]
            col = np.clip(base * bb + (255.0 - base) * np.clip(bb - 0.35, 0.0, 1.0) * mix, 0.0, 255.0)
            cols = col.astype(np.uint8).tolist()
            ca, sa = self.w_ca[:n][idx], self.w_sa[:n][idx]
            x0 = (HW + ca * ri[idx]).tolist()
            y0 = (HH + sa * ri[idx]).tolist()
            x1 = (HW + ca * ro[idx]).tolist()
            y1 = (HH + sa * ro[idx]).tolist()
            wd = (1 + (bb[:, 0] > 0.5) + (bb[:, 0] > 0.85)).tolist()
            line = pygame.draw.line
            for i in range(len(cols)):
                line(s, cols[i], (x0[i], y0[i]), (x1[i], y1[i]), wd[i])
        # -- partikel glow di layar --
        m = max(40, int(len(self.g_ca) * qs))
        gz = (self.g_z0[:m] - D * self.g_spd[:m]) % 1.0
        gr = 24.0 + self.RMAX * (1.0 - gz) ** 2.0
        gx = HW + self.g_ca[:m] * gr
        gy = HH + self.g_sa[:m] * gr
        gsz = 2.0 + 9.0 * (1.0 - gz) ** 2.2 * A
        ok = (gx > -20) & (gx < W + 20) & (gy > -20) & (gy < H + 20) & (gz < 0.97)
        grp = self.g_grp[:m]
        for gi in range(3):
            sel = ok & (grp == gi)
            if sel.any():
                ren.glow2d(gx[sel], gy[sel], gsz[sel], self.g2[gi])
        # -- pusat portal --
        ps = 40.0 + 170.0 * smoothstep(p)
        ox, oy = np.array([HW]), np.array([HH])
        ren.glow2d(ox, oy, np.array([ps]), self.g2[0])
        ren.glow2d(ox, oy, np.array([ps * 0.6]), self.g2[1])
        pw = ps * 0.3 * smoothstep((p - 0.55) / 0.45)
        if pw >= 2.0:
            ren.glow2d(ox, oy, np.array([pw]), self.g2[2])

    def _title(self, s, tb):
        e, bright = self.e, self.c_bright
        a = 255 * smoothstep((tb - 0.25) / 0.35)
        blit_alpha(s, self.back, (int(HW - 300), int(HH - 72)), a * 0.9)
        title = fit_text(e.name, (34, 26, 22), 560, bright, True)
        blit_alpha(s, title, (int(HW - title.get_width() / 2), int(HH - 60)), a)
        sub = TXT.get(e.opening, 16, (205, 212, 245), True)
        blit_alpha(s, sub, (int(HW - sub.get_width() / 2), int(HH - 14)), a)
        prog = clamp(tb / (self.t_warp1 - self.t_burst), 0.0, 1.0)
        bx, by, bw = int(HW - 180), int(HH + 24), 360
        pygame.draw.rect(s, (30, 34, 60), (bx, by, bw, 6))
        pygame.draw.rect(s, e.color, (bx, by, int(bw * prog), 6))
        pct = TXT.get(f"{int(prog * 100)}%", 13, (220, 225, 255))
        blit_alpha(s, pct, (int(HW - pct.get_width() / 2), by + 12), a)


# ---------------------------------------------------------------------
#  APLIKASI
# ---------------------------------------------------------------------
class App:
    def __init__(self, screen):
        self.s = screen
        self.clock = pygame.time.Clock()
        self.fps_idx = 0
        self.cam = Camera()
        self.ren = Ren(screen)
        for size, bold in ((12, False), (13, False), (14, False), (14, True), (15, True),
                           (16, True), (20, True), (22, True), (26, True), (34, True)):
            TXT.font(size, bold)
        self.stars = Starfield()
        self.t = 0.0
        self.paused = False
        self.show_hud = True
        self.focus = None
        self.tour = False
        self.tour_timer = 0.0
        self.auto_orbit = True
        self.idle = 10.0
        self.drag = None
        self.drag_moved = 0
        self.shocks = []
        self.fps_disp = 0.0
        self.cap_timer = 0.0
        self.work_ema = 0.008
        self.qi = 0
        self.q_cool = 2.0
        self.q_good = 0.0
        self.fx = None
        self.toast = None
        self.btn_hover = False
        self.press_btn = False
        self.build_world()
        self.panel = pygame.Surface((430, 150), pygame.SRCALPHA)
        self.panel.fill((6, 8, 20, 190))
        self.mini = pygame.Surface((180, 180), pygame.SRCALPHA)
        self.mini.fill((6, 8, 20, 170))
        self.btn_bg = pygame.Surface(BTN_RECT.size, pygame.SRCALPHA)
        pygame.draw.rect(self.btn_bg, (6, 8, 20, 205), self.btn_bg.get_rect(), border_radius=9)
        self.btn_hl = pygame.Surface(BTN_RECT.size, pygame.SRCALPHA)

    # ---------------- dunia ----------------
    def build_world(self):
        classes = (Galaxy, Solar, BlackHole, Crystal, Ember, Matrix)
        cfg = UNIVERSES

        def col_of(c):
            return tuple(int(clamp(v, 0, 255)) for v in c["color"])

        heights = (120, -150, 190, -100, 160, -190)
        c0 = cfg[0]
        self.ents = [Hub(0, str(c0["name"]), str(c0.get("sub", "")), (0, 0, 0), 150, col_of(c0), 1)]
        for i, cls in enumerate(classes):
            c = cfg[i + 1]
            ang = math.radians(-90 + i * 60)
            pos = (math.cos(ang) * RING_DIST, heights[i], math.sin(ang) * RING_DIST)
            self.ents.append(cls(i + 1, str(c["name"]), str(c.get("sub", "")), pos, 260, col_of(c), 100 + i))
        for e, c in zip(self.ents, cfg):                 # teks & file dari pusat pengaturan
            e.file = str(c.get("file", "") or "")
            e.button = str(c.get("button") or OPEN_BUTTON_DEFAULT)
            fname = e.file if len(e.file) <= 28 else "..." + e.file[-25:]
            e.caption = str(c.get("caption") or ("» " + fname))
            e.opening = str(c.get("opening") or OPEN_TEXT_DEFAULT)
            labs = c.get("stats")
            if labs:
                e.stats = [(str(lab), ph, base) for lab, (_, ph, base) in zip(labs, e.stats)]
        self.pos = np.array([e.pt for e in self.ents])
        self.rad = np.array([e.R for e in self.ents])
        self.pal_ents = [e.gs for e in self.ents]

        # tautan portal: 6 jari-jari + 6 cincin
        la, lb, curve, lift = [], [], [], []
        for i in range(1, 7):
            la.append(0)
            lb.append(i)
            curve.append(0.05)
            lift.append(150.0 if i % 2 else -150.0)
        for i in range(1, 7):
            la.append(i)
            lb.append(i % 6 + 1)
            curve.append(0.22)
            lift.append(50.0 if i % 2 else -50.0)
        self.la, self.lb = np.array(la), np.array(lb)
        self.curve, self.lift = np.array(curve), np.array(lift)
        L = len(la)
        pa, pb = self.pos[self.la], self.pos[self.lb]
        u = pb - pa
        u /= np.linalg.norm(u, axis=1)[:, None]
        perp = np.stack((-u[:, 2], np.zeros(L), u[:, 0]), axis=1)
        perp /= np.maximum(np.linalg.norm(perp, axis=1), 1e-6)[:, None]
        mid = (pa + pb) / 2
        sign = np.where((perp * mid).sum(axis=1) >= 0, 1.0, -1.0)
        sign[:6] = np.where(np.arange(6) % 2 == 0, 1.0, -1.0)
        self.sign = sign
        self.link_col = [tuple((self.ents[a].color[k] + self.ents[b].color[k]) // 2 for k in range(3))
                         for a, b in zip(la, lb)]
        self.U = np.linspace(0, 1, 21)
        self.U0 = (1 - self.U) ** 2
        self.U1 = 2 * (1 - self.U) * self.U
        self.U2 = self.U ** 2
        self.ring_uc = np.stack((np.cos(np.linspace(0, TAU, 17)), np.sin(np.linspace(0, TAU, 17))), axis=1)
        self.A = self.B = self.C = None

        # pulsa energi
        rnd = random.Random(5)
        self.pulse_li, self.pulse_u, self.pulse_sp, self.pulse_dir = [], [], [], []
        for li in range(L):
            for k in range(2):
                self.pulse_li.append(li)
                self.pulse_u.append(rnd.random())
                self.pulse_sp.append(rnd.uniform(0.12, 0.28))
                self.pulse_dir.append(1 if k == 0 else -1)
        self.pulse_li = np.array(self.pulse_li)
        self.pulse_u = np.array(self.pulse_u)
        self.pulse_sp = np.array(self.pulse_sp)
        self.pulse_dir = np.array(self.pulse_dir)
        self.white = glowset((255, 255, 255))
        self.white.warm(12)
        self.trail = np.arange(6)
        self.trail_size = (6 - self.trail) * 4.5
        self.circ_shock = [unit_circle(72), unit_circle(72) @ rot_x(TAU / 4).T, unit_circle(72) @ rot_z(TAU / 4).T]

    def compute_links(self, t):
        L = len(self.la)
        pa, pb = self.pos[self.la], self.pos[self.lb]
        d = pb - pa
        u = d / np.linalg.norm(d, axis=1)[:, None]
        A = pa + u * (self.rad[self.la] * 1.04)[:, None]
        B = pb - u * (self.rad[self.lb] * 1.04)[:, None]
        mid = (A + B) * 0.5
        Lb = np.linalg.norm(B - A, axis=1)
        perp = np.stack((-u[:, 2], np.zeros(L), u[:, 0]), axis=1)
        perp /= np.maximum(np.linalg.norm(perp, axis=1), 1e-6)[:, None]
        ph = np.arange(L)
        off = Lb * self.curve * (1 + 0.25 * np.sin(t * 0.5 + ph)) * self.sign
        lift = self.lift + 45.0 * np.sin(t * 0.4 + ph * 1.3)
        C = mid + perp * off[:, None] + UP * lift[:, None]
        self.A, self.B, self.C = A, B, C

    # ---------------- kontrol kamera ----------------
    def focus_on(self, i):
        e = self.ents[i]
        cam = self.cam
        cam.goal = e.p.copy()
        cam.gdist = clamp(e.R * FOCUS_K, DMIN, DMAX)
        cam.gpitch = 0.30
        cam.shake = max(cam.shake, 0.25)
        self.focus = i

    def overview(self):
        cam = self.cam
        cam.goal = np.zeros(3)
        cam.gdist = OVERVIEW_DIST
        cam.gpitch = 0.62
        self.focus = None

    def pick(self, mx, my):
        best, bz = None, 1e18
        for e in self.ents:
            if e.scr is None:
                continue
            sx, sy, sr, z = e.scr
            if z > 0 and math.hypot(mx - sx, my - sy) < sr * 1.1 and z < bz:
                best, bz = e.idx, z
        if best is not None:
            self.focus_on(best)

    def burst(self):
        self.shocks.append(0.0)
        for e in self.ents:
            e.flash = 1.0
        self.cam.shake = 0.6

    def poke(self):
        self.idle = 0.0

    # ---------------- buka halaman HTML ----------------
    def toast_msg(self, text, color=(255, 225, 140), secs=3.2):
        if len(text) > 105:
            text = text[:102] + "..."
        img = TXT.get(text, 14, color, True)
        box = pygame.Surface((img.get_width() + 36, img.get_height() + 16), pygame.SRCALPHA)
        pygame.draw.rect(box, (6, 8, 20, 225), box.get_rect(), border_radius=8)
        pygame.draw.rect(box, color, box.get_rect(), 1, border_radius=8)
        box.blit(img, (18, 8))
        self.toast = [box, secs, secs]

    def draw_toast(self):
        if not self.toast:
            return
        box, left, total = self.toast
        a = min(1.0, left / 0.5, (total - left) / 0.15 + 0.01)
        box.set_alpha(int(255 * clamp(a, 0.0, 1.0)))
        self.s.blit(box, ((W - box.get_width()) // 2, 78))

    def open_focus(self):
        """Dipanggil tombol BUKA / ENTER / SPASI: buka halaman HTML dimensi yang sedang dipilih."""
        if self.fx is not None:
            return
        if self.focus is None:
            self.toast_msg("Pilih dimensi dulu: klik salah satu, atau tekan 1-6 / C")
            return
        e = self.ents[self.focus]
        url, err = resolve_target(e.file)
        if err:
            self.toast_msg(err, (255, 110, 110), 5.0)
            self.cam.shake = 0.5
            return
        self.press_btn = False
        self.fx = OpenFX(self, e, url)

    def launch(self, url, ent):
        def _run():
            try:
                webbrowser.open(url, new=BROWSER_TAB)
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()
        self.toast_msg(f"Membuka {ent.name}  ->  {ent.file}", ent.color, 4.0)

    def draw_open_button(self, t):
        if self.focus is None or self.fx is not None:
            return
        s = self.s
        e = self.ents[self.focus]
        r = BTN_RECT.copy()
        down = self.press_btn and self.btn_hover
        if down:
            r.move_ip(0, 2)
        pulse = 0.5 + 0.5 * math.sin(t * 3.2)
        s.blit(self.btn_bg, r.topleft)
        if self.btn_hover:
            self.btn_hl.fill((0, 0, 0, 0))
            pygame.draw.rect(self.btn_hl, (e.color[0], e.color[1], e.color[2], 150 if down else 90),
                             self.btn_hl.get_rect(), border_radius=9)
            s.blit(self.btn_hl, r.topleft)
        glow = 0.55 + 0.45 * pulse + (0.30 if self.btn_hover else 0.0)
        pygame.draw.rect(s, mul(e.color, glow), r, 2, border_radius=9)
        pygame.draw.rect(s, e.color, (r.x + 9, r.y + 12, 3, r.h - 24))
        lc = tuple(int(v + (255 - v) * 0.6) for v in e.color) if self.btn_hover else e.color
        lab = fit_text(e.button, (20, 16, 14), r.w - 44, lc, True)
        s.blit(lab, (r.x + 20 + (r.w - 30 - lab.get_width()) // 2, r.y + 10))
        cap = fit_text(e.caption, (12,), r.w - 44, (150, 158, 195), False)
        s.blit(cap, (r.x + 20 + (r.w - 30 - cap.get_width()) // 2, r.y + 38))

    # ---------------- event ----------------
    def handle(self, ev):
        cam = self.cam
        if ev.type == pygame.QUIT:
            return False
        if self.fx is not None:                          # saat animasi buka: input dikunci
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and not self.fx.launched:
                    self.fx.cancel()
                elif ev.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            return True
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k == pygame.K_ESCAPE:
                return False
            elif k == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif k == pygame.K_f:
                self.fps_idx = (self.fps_idx + 1) % len(FPS_OPTIONS)
            elif k == pygame.K_h:
                self.show_hud = not self.show_hud
            elif k == pygame.K_p:
                self.paused = not self.paused
            elif k == pygame.K_t:
                self.tour = not self.tour
                self.tour_timer = TOUR_SECONDS
            elif k == pygame.K_o:
                self.auto_orbit = not self.auto_orbit
            elif k == pygame.K_b:
                self.burst()
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.open_focus()
            elif k == pygame.K_c:
                self.focus_on(0)
            elif k in (pygame.K_0, pygame.K_HOME):
                self.overview()
            elif k == pygame.K_TAB:
                self.focus_on(1 if self.focus is None else self.focus % 6 + 1)
            elif pygame.K_1 <= k <= pygame.K_6:
                self.focus_on(k - pygame.K_0)
        elif ev.type == pygame.MOUSEWHEEL:
            cam.gdist = clamp(cam.gdist * (1.13 ** (-ev.y)), DMIN, DMAX)
            self.poke()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 2, 3):
            if ev.button == 1 and self.focus is not None and BTN_RECT.collidepoint(ev.pos):
                self.press_btn = True                    # menekan tombol BUKA (bukan drag kamera)
                return True
            self.drag = ev.button
            self.drag_moved = 0
        elif ev.type == pygame.MOUSEMOTION and self.drag:
            rx, ry = ev.rel
            self.drag_moved += abs(rx) + abs(ry)
            if self.drag_moved > 6:
                if self.drag == 1:
                    cam.orbit(-rx * 0.0055, ry * 0.0055)
                else:
                    cam.pan(rx, ry)
                    self.focus = None
                self.poke()
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button in (1, 2, 3):
            if self.press_btn and ev.button == 1:
                self.press_btn = False
                if BTN_RECT.collidepoint(ev.pos):
                    self.open_focus()
                return True
            if self.drag == 1 and ev.button == 1 and self.drag_moved <= 6:
                self.pick(*ev.pos)
            self.drag = None
        return True

    # ---------------- update ----------------
    def update(self, dt):
        cam = self.cam
        mx, my = pygame.mouse.get_pos()                  # hover tombol BUKA -> kursor tangan
        over = self.focus is not None and self.fx is None and BTN_RECT.collidepoint(mx, my)
        if over != self.btn_hover:
            self.btn_hover = over
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if over else pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass
        if self.toast:
            self.toast[1] -= dt
            if self.toast[1] <= 0:
                self.toast = None
        keys = pygame.key.get_pressed()
        mvf = (keys[pygame.K_w]) - (keys[pygame.K_s])
        mvs = (keys[pygame.K_d]) - (keys[pygame.K_a])
        mvv = (keys[pygame.K_e]) - (keys[pygame.K_q])
        if self.fx is None and (mvf or mvs or mvv):
            sp = cam.dist * 0.9 * dt
            cy, sy = math.cos(cam.yaw), math.sin(cam.yaw)
            gf = np.array([-sy, 0.0, -cy])
            rt = np.array([cy, 0.0, -sy])
            cam.move((gf * mvf + rt * mvs + UP * mvv) * sp)
            self.focus = None
            self.poke()
        ry = (keys[pygame.K_RIGHT]) - (keys[pygame.K_LEFT])
        rp = (keys[pygame.K_UP]) - (keys[pygame.K_DOWN])
        if self.fx is None and (ry or rp):
            cam.orbit(-ry * 1.5 * dt, rp * 1.0 * dt)
            self.poke()
        self.idle += dt
        if self.fx is not None:
            self.idle = 0.0                              # tahan orbit otomatis selama animasi
            self.fx.update(dt)
            if self.fx.done:
                self.fx = None
        if self.auto_orbit and self.idle > 3.0 and self.drag is None:
            cam.spin(0.06 * dt)
        cam.update(dt)
        if self.tour and self.fx is None:
            self.tour_timer += dt
            if self.tour_timer >= TOUR_SECONDS:
                self.tour_timer = 0.0
                self.focus_on(1 if self.focus is None else self.focus % 6 + 1)
        if self.paused:
            return
        self.t += dt
        for e in self.ents:
            e.flash = max(0.0, e.flash - dt * 1.4)
        self.pulse_u += self.pulse_sp * dt
        for i in np.flatnonzero(self.pulse_u >= 1.0).tolist():
            li = int(self.pulse_li[i])
            dst = self.ents[int(self.lb[li] if self.pulse_dir[i] > 0 else self.la[li])]
            dst.flash = min(1.0, dst.flash + 0.55)
            if self.focus == dst.idx:
                cam.shake = max(cam.shake, 0.06)
            self.pulse_u[i] = 0.0
            self.pulse_dir[i] = -self.pulse_dir[i]
        self.shocks = [a + dt for a in self.shocks if a + dt < 2.4]

    # ---------------- gambar ----------------
    def draw_links(self, t):
        ren = self.ren
        self.compute_links(t)
        A, B, C = self.A, self.B, self.C
        PP = (self.U0[None, :, None] * A[:, None, :] + self.U1[None, :, None] * C[:, None, :]
              + self.U2[None, :, None] * B[:, None, :])
        L = len(A)
        for li in range(L):
            col = self.link_col[li]
            mx, my, mz, mk = ren.p1(PP[li, 10].tolist())
            wide = max(1, min(8, int(7 * mk)))
            ren.poly(PP[li], [(mul(col, 0.10), wide), (mul(col, 0.38), 1)], False)
        # portal di kedua ujung
        ends = np.vstack((A, B))
        tang = np.vstack((C - A, B - C))
        tang /= np.maximum(np.linalg.norm(tang, axis=1), 1e-6)[:, None]
        e1 = np.stack((-tang[:, 2], np.zeros(len(tang)), tang[:, 0]), axis=1)
        e1 /= np.maximum(np.linalg.norm(e1, axis=1), 1e-6)[:, None]
        e2 = np.cross(tang, e1)
        rp = 46.0 + 8.0 * math.sin(t * 3)
        ring = ends[:, None, :] + rp * (self.ring_uc[None, :, 0:1] * e1[:, None, :]
                                        + self.ring_uc[None, :, 1:2] * e2[:, None, :])
        for i in range(len(ends)):
            li = i % L
            ent = self.ents[int(self.la[li] if i < L else self.lb[li])]
            sx, sy, z, k = ren.p1(ends[i].tolist())
            if z < NEAR:
                continue
            ren.glow1(ends[i].tolist(), (14 + 3 * math.sin(t * 3 + i)), ent.gs)
            if k * rp > 3:
                ren.poly(ring[i], [(mul(ent.color, 0.55), 1)], True)
        # pulsa energi
        li, u, d = self.pulse_li, self.pulse_u, self.pulse_dir
        uu = u[:, None] - self.trail[None, :] * 0.014
        valid = uu >= 0
        q = np.where(d[:, None] > 0, uu, 1.0 - uu)[..., None]
        pos = ((1 - q) ** 2 * A[li][:, None, :] + 2 * (1 - q) * q * C[li][:, None, :]
               + q ** 2 * B[li][:, None, :])
        cid = np.where(d > 0, self.la[li], self.lb[li])                        # warna sumber
        cid = np.broadcast_to(cid[:, None], valid.shape)
        sz = np.broadcast_to(self.trail_size[None, :], valid.shape)
        ren.glow(pos[valid], sz[valid], cid[valid], self.pal_ents)
        hv = valid[:, 0]
        ren.glow(pos[hv, 0, :], 8.0, None, self.white)

    def draw_shocks(self):
        ren = self.ren
        for age in self.shocks:
            rho = age * 1100.0
            col = mul((170, 190, 255), max(0.0, 1 - age / 2.4))
            for c in self.circ_shock:
                ren.poly(c * rho, [(col, 2)], False)

    def draw_labels(self):
        s = self.s
        for e in self.ents:
            if e.scr is None:
                continue
            sx, sy, sr, z = e.scr
            if z < NEAR or sr <= 18:
                continue
            ly = sy + sr * 1.16 + 4
            if ly > H - 30:
                continue
            lab = TXT.get(e.name, 15, e.color, True)
            s.blit(lab, (int(sx - lab.get_width() / 2), int(ly)))
            if sr > 110 and ly + 20 < H - 26:
                sub = TXT.get(e.sub, 12, (150, 158, 195))
                s.blit(sub, (int(sx - sub.get_width() / 2), int(ly + 20)))

    def draw_minimap(self):
        s, cam = self.s, self.cam
        x0, y0 = W - 200, H - 200
        s.blit(self.mini, (x0, y0))
        pygame.draw.rect(s, (60, 66, 110), (x0, y0, 180, 180), 1)
        k = 0.072
        mx, my = x0 + 90, y0 + 90
        s.set_clip(pygame.Rect(x0, y0, 180, 180))
        for li in range(len(self.la)):
            a, b = self.ents[int(self.la[li])], self.ents[int(self.lb[li])]
            pygame.draw.line(s, mul(self.link_col[li], 0.3), (mx + a.pt[0] * k, my + a.pt[2] * k),
                             (mx + b.pt[0] * k, my + b.pt[2] * k))
        for e in self.ents:
            r = 5 if e.idx == 0 else 4
            pos = (int(mx + e.pt[0] * k), int(my + e.pt[2] * k))
            pygame.draw.circle(s, e.color, pos, r)
            if e.idx == self.focus:
                pygame.draw.circle(s, (255, 255, 255), pos, r + 3, 1)
        f = cam.M[2]
        h = math.atan2(f[2], f[0])
        cx, cy = mx + cam.pos[0] * k, my + cam.pos[2] * k
        half = math.radians(FOV_DEG) * 0.9 * 0.5
        for sgn in (-1, 1):
            pygame.draw.line(s, (220, 225, 255), (cx, cy),
                             (cx + math.cos(h + sgn * half) * 34, cy + math.sin(h + sgn * half) * 34))
        pygame.draw.circle(s, (255, 255, 255), (int(cx), int(cy)), 3)
        s.set_clip(None)

    def draw_focus_panel(self, t):
        if self.focus is None:
            return
        s = self.s
        e = self.ents[self.focus]
        x0, y0 = 20, H - 176
        s.blit(self.panel, (x0, y0))
        pygame.draw.rect(s, mul(e.color, 0.6), (x0, y0, 430, 150), 1)
        pygame.draw.rect(s, e.color, (x0, y0, 4, 150))
        s.blit(TXT.get(e.name, 22, e.color, True), (x0 + 16, y0 + 10))
        s.blit(TXT.get(e.sub, 13, (170, 178, 210)), (x0 + 16, y0 + 40))
        for i, (label, ph, base) in enumerate(e.stats):
            v = clamp(base + 0.18 * math.sin(t * 0.8 + ph), 0.05, 0.99)
            yy = y0 + 68 + i * 26
            s.blit(TXT.get(label, 12, (140, 150, 190)), (x0 + 16, yy))
            pygame.draw.rect(s, (30, 34, 60), (x0 + 120, yy + 2, 240, 10))
            pygame.draw.rect(s, e.color, (x0 + 120, yy + 2, int(240 * v), 10))
            s.blit(TXT.get(f"{int(v * 100)}%", 12, (220, 225, 255)), (x0 + 370, yy))

    def draw_hud(self, t):
        s, cam = self.s, self.cam
        target = FPS_OPTIONS[self.fps_idx]
        s.blit(TXT.get(APP_TITLE, 26, (230, 235, 255), True), (20, 14))
        s.blit(TXT.get(APP_SUBTITLE, 14, (120, 130, 170)), (22, 46))
        good = self.fps_disp >= target - 3
        fcol = (90, 255, 150) if good else (255, 210, 90)
        a = TXT.get(f"FPS {self.fps_disp:.0f}/{target}", 16, fcol, True)
        s.blit(a, (W - a.get_width() - 20, 14))
        b = TXT.get(f"JARAK {cam.dist:.0f}  |  DETAIL {QUALITY_NAME[self.qi]}", 13, (150, 158, 200))
        s.blit(b, (W - b.get_width() - 20, 38))
        flags = []
        if self.tour:
            flags.append("TUR OTOMATIS")
        if self.auto_orbit:
            flags.append("ORBIT")
        if self.paused:
            flags.append("PAUSE")
        if flags:
            c = TXT.get("  ".join(flags), 13, (255, 210, 120), True)
            s.blit(c, (W - c.get_width() - 20, 58))
        self.draw_focus_panel(t)
        self.draw_minimap()
        hint = HUD_HINT
        s.blit(TXT.get(hint, 13, (100, 108, 145)), (20, H - 24))

    def draw(self):
        s = pygame.display.get_surface()
        self.s = s
        cam, t, ren = self.cam, self.t, self.ren
        self.stars.draw(s, cam, t)
        ren.begin(s, cam)
        self.draw_links(t)
        f, p = cam.M[2], cam.pos
        order = sorted(self.ents, key=lambda e: -((e.pt[0] - p[0]) * f[0] + (e.pt[1] - p[1]) * f[1]
                                                  + (e.pt[2] - p[2]) * f[2]))
        qmul = QUALITY[self.qi]
        for e in order:
            e.render(ren, t, qmul)
        self.draw_shocks()
        if self.fx is not None:
            self.fx.draw3d(ren)
        self.draw_labels()
        if self.show_hud and not (self.fx is not None and self.fx.hide_hud):
            self.draw_hud(t)
        self.draw_open_button(t)
        if self.fx is not None:
            self.fx.draw2d(s, ren)
        self.draw_toast()

    # ---------------- kualitas adaptif ----------------
    def adapt(self, work, dt):
        self.work_ema += (work - self.work_ema) * 0.08
        self.q_cool = max(0.0, self.q_cool - dt)
        budget = (1.0 / FPS_OPTIONS[self.fps_idx]) * 0.82
        if self.work_ema > budget and self.qi < len(QUALITY) - 1 and self.q_cool <= 0:
            self.qi += 1
            self.q_cool = 1.5
            self.q_good = 0.0
        elif self.work_ema < budget * 0.55 and self.qi > 0:
            self.q_good += dt
            if self.q_good > 5.0 and self.q_cool <= 0:
                self.qi -= 1
                self.q_cool = 3.0
                self.q_good = 0.0
        else:
            self.q_good = 0.0

    # ---------------- loop utama ----------------
    def run(self):
        running = True
        perf = time.perf_counter
        while running:
            target = FPS_OPTIONS[self.fps_idx]
            dt = min(self.clock.tick(target) / 1000.0, 0.05)
            for ev in pygame.event.get():
                if not self.handle(ev):
                    running = False
            t0 = perf()
            self.update(dt)
            self.draw()
            work = perf() - t0
            pygame.display.flip()
            self.adapt(work, dt)
            self.cap_timer += dt
            if self.cap_timer >= 0.25:
                self.cap_timer = 0.0
                self.fps_disp = self.clock.get_fps()
                pygame.display.set_caption(
                    f"{WINDOW_TITLE}  |  {self.fps_disp:.0f} FPS (target {target})  |  "
                    f"{work * 1000:.1f} ms/frame")


def main():
    validate_config()
    report_files()
    pygame.init()
    flags = pygame.SCALED | pygame.RESIZABLE
    try:
        screen = pygame.display.set_mode((W, H), flags, vsync=1)
    except Exception:
        screen = pygame.display.set_mode((W, H), flags)
    pygame.display.set_caption(WINDOW_TITLE)
    App(screen).run()
    pygame.quit()


if __name__ == "__main__":
    main()
