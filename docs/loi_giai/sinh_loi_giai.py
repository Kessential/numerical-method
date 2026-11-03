"""
SINH LOI GIAI BAI TAP CAU 3-23 (BaitapPPS_2026): MARKDOWN HOAC TEX, SO LIEU LAY TU THU MUC data/

Luong: sua so lieu trong cac file o data/ (cau nao lay file nao, tham so xbar / ybar / m...: data/loi_giai.ini)
-> chay script nay -> chon 1. Markdown (docs/loi_giai/loi_giai_bai_tap.md)
                      hoac 2. TeX (docs/loi_giai/loi_giai_bai_tap.tex, tu dich PDF neu co xelatex).
Van ban co dinh (thuat toan, cong thuc chung): mau_loi_giai.tex, cho can so lieu ghi <<khoa>>.
Phan ap dung (cau chu phu thuoc so lieu): cac ham cau3() .. cau23() duoi day. So lieu / bang tinh bang
CHINH CAC HAM THUAT TOAN trong interpolation/*.py nen loi giai luon khop voi output cua code.
Du lieu sai (mau trung khac y, khong cach deu khi thuat toan can, file thieu dong...) -> bao loi theo cau, khong ghi file.

Chay:
  python docs/loi_giai/sinh_loi_giai.py                -> hoi dinh dang (Enter = Markdown) va cac cau (Enter = tat ca)
  python docs/loi_giai/sinh_loi_giai.py md             -> Markdown, tat ca cac cau
  python docs/loi_giai/sinh_loi_giai.py tex 11 16 17   -> TeX + PDF, chi Cau 11, 16, 17
  python docs/loi_giai/sinh_loi_giai.py gk             -> DE GIUA KY: hoi file de (mac dinh file *GK*/*test* moi nhat
                                                          trong data/), tung cau theo menu (BPTT, lap, ham nguoc, Newton,
                                                          Gauss, Stirling, Bessel, Lagrange) -> giua_ky_<ten>.md / .pdf
                                                          (form dap an giua ky 20251); luu tra loi vao
                                                          data/giua_ky_<ten>_tra_loi.txt
  python docs/loi_giai/sinh_loi_giai.py gk data/giua_ky_<ten>_tra_loi.txt  -> chay lai theo file tra loi
  Them --data <thu muc> de doc du lieu (va loi_giai.ini) o thu muc khac (mac dinh data/).
"""

import configparser
import contextlib
import importlib.util
import io
import math
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction

import numpy as np

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
DATA = os.path.join(GOC, "data")
TEN_CAU_HINH = "loi_giai.ini"


def nap(ten):
    spec = importlib.util.spec_from_file_location(ten, os.path.join(GOC, "interpolation", ten + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


hn, mt, lg, nw, tt, nsn, sp, bp = (nap(t) for t in (
    "horner", "moc_toi_uu", "lagrange", "newton", "trung_tam", "noi_suy_nguoc", "spline", "binh_phuong_toi_thieu"))

FMT = "tex"                  # "tex" | "md": dinh dang bang (cac phan khac chuyen sang Markdown o buoc cuoi)
V = {}                       # khoa -> doan LaTeX
KT = {}                      # kiem tra (so voi numpy / scipy): chi in ra man hinh
BANG_MD = []                 # bang Markdown (FMT = "md"): bang() tra ve token @@BANGi@@
CAU_CO = set()               # cac cau dang sinh
RONG = 480.0                 # be ngang toi da (pt) cua 1 dong cong thuc hien thi (le trang 493pt)
RONG_KL = 466.0              # ... trong khung Ket luan (481pt)


class LoiDuLieu(Exception):
    """Du lieu cua 1 cau khong dung yeu cau thuat toan: bao loi, khong sinh loi giai."""


# ===== DINH DANG =====

def so(v):
    """So tinh ra -> LaTeX: toi da 6 chu so thap phan; |v| < 1e-4 viet a.bcdefg*10^k (6 chu so sau dau phay)."""
    v = float(v)
    if abs(v) < 1e-12:
        return "0"
    if abs(v) < 1e-4 or abs(v) >= 1e9:
        m, e = f"{v:.6e}".split("e")
        m = m.rstrip("0").rstrip(".")
        return f"{m}\\cdot10^{{{int(e)}}}"
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def se(v):
    """Can sai so (co the rat nho): nhu so() nhung khong bao gio lam tron ve 0."""
    v = float(v)
    if v == 0 or 1e-4 <= abs(v) < 1e9:
        return so(v)
    m, e = f"{v:.6e}".split("e")
    m = m.rstrip("0").rstrip(".")
    return f"{m}\\cdot10^{{{int(e)}}}"


def dmu(k, ky="\\Delta"):
    """Delta^k (k = 1 viet Delta)."""
    return ky + " " if k == 1 else f"{ky}^{{{k}}}"


def sl(v):
    """So lieu de cho: giu nguyen chu so."""
    s = f"{float(v):.10g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m}\\cdot10^{{{int(e)}}}"
    return s


def sd(v, d):
    """So co dinh d chu so thap phan (sai phan cua du lieu d chu so: dung tuyet doi)."""
    s = f"{round(v, d):.{d}f}"
    return "0." + "0" * d if re.fullmatch(r"-0\.0*", s) else s


def sn(v):
    """So trong bieu thuc: so am dat trong ngoac."""
    s = so(v)
    return f"({s})" if s.startswith("-") else s


def chi(i):
    """Chi so 1 ky tu viet lien (x_3), dai hon dat trong ngoac (x_{10}, x_{-1})."""
    s = str(i)
    return s if len(s) == 1 else "{" + s + "}"


def x_tru(v, bien="x"):
    """'x-3.1', 'x+0.5' (v am), 'x' (v = 0)."""
    if v == 0:
        return bien
    return f"{bien}-{sl(v)}" if v > 0 else f"{bien}+{sl(-v)}"


def dh(ten, j):
    """Ten dao ham cap j: f, f', f'', f''', f^{(4)} (ten co the la 'P_5')."""
    return ten + ("'" * j if j <= 3 else f"^{{({j})}}")


def mu10(v):
    """Sai so eps: 1e-06 -> '10^{-6}', 5e-07 -> '5\\cdot10^{-7}'."""
    if 1e-4 <= abs(v) < 1e4:
        return sl(v)
    m, e = f"{v:.6e}".split("e")
    m = m.rstrip("0").rstrip(".")
    return f"10^{{{int(e)}}}" if m == "1" else f"{m}\\cdot10^{{{int(e)}}}"


def mu_gon(e, bien="x"):
    """x^e viet gon: '' (e = 0), 'x', 'x^3', 'x^{12}'."""
    return "" if e == 0 else bien if e == 1 else (f"{bien}^{e}" if e < 10 else f"{bien}^{{{e}}}")


def da_thuc_gon(a, bien="x"):
    """Da thuc so lieu de cho (bac cao -> thap) viet gon: 3x^3-2x-1."""
    n = len(a) - 1
    s = ""
    for i, v in enumerate(a):
        if v == 0:
            continue
        e = n - i
        hs = sl(abs(v))
        t = (hs if hs != "1" or e == 0 else "") + mu_gon(e, bien)
        s += ("-" if v < 0 else ("+" if s else "")) + t
    return s or "0"


def tex_chu(s):
    """Chu tho (ten file, noi dung o loi) -> LaTeX an toan."""
    thay = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "%": r"\%", "$": r"\$", "&": r"\&", "#": r"\#",
            "_": r"\_", "^": r"\^{}", "~": r"\~{}"}
    return "".join(thay.get(ch, ch) for ch in str(s))


def ob(s):
    return r"\ob{" + s + "}"


def vecl(v):
    return r"\left(" + r";\ ".join(so(t) for t in v) + r"\right)"


def boc(c):
    if c is None or c == "":
        return ""
    c = str(c)
    if c.startswith("\\ob") or "$" in c or c.startswith("\\multicolumn"):
        return c
    return "$" + c + "$"


def o_md(c):
    """1 o bang (LaTeX) -> o Markdown: toan dat trong $...$, '|' trong toan -> \\vert."""
    if c is None or c == "":
        return ""
    c = str(c)
    m = re.match(r"\\multicolumn\{\d+\}\{\w\}\{(.*)\}$", c)
    if m:
        c = m.group(1)
    if c.startswith("\\ob{") and c.endswith("}"):
        s = "$\\boxed{" + c[4:-1] + "}$"
    elif "$" in c:
        s = c
    else:
        s = "$" + c + "$"
    s = s.replace("\\ob{", "\\boxed{")
    return re.sub(r"\$(.*?)\$", lambda t: "$" + t.group(1).replace("|", "\\vert ").strip() + "$", s)


def bang_md(dau, hang, can, nhom):
    n = len(dau)
    dong = ["| " + " | ".join(o_md(c) for c in dau) + " |",
            "|" + "|".join({"l": ":---", "c": ":---:"}.get(a, "---:") for a in can) + "|"]
    for h in hang:
        if h is None:
            continue
        o = []
        for c in h:
            o.append(o_md(c))
            m = re.match(r"\\multicolumn\{(\d+)\}", str(c))
            if m:
                o += [""] * (int(m.group(1)) - 1)
        o += [""] * (n - len(o))
        dong.append("| " + " | ".join(o) + " |")
    return ("*" + nhom[2] + "*\n\n" if nhom else "") + "\n".join(dong)


def bang(dau, hang, can=None, co="small", cao=None, nhom=None):
    """Bang LaTeX co gian theo be ngang trang. hang: list (None = ke ngang); o \\multicolumn{k} tinh k cot;
    cao: khoang them duoi moi hang (vd "5pt" cho o co phan so); nhom = (a, b, nhan): tieu de chung cot a..b.
    FMT = "md": luu bang Markdown, tra ve token @@BANGi@@ (thay vao sau khi chuyen van ban)."""
    n = len(dau)
    can = can or ("r" * n)
    if FMT == "md":
        BANG_MD.append(bang_md(dau, hang, can, nhom))
        return f"@@BANG{len(BANG_MD) - 1}@@"
    het = r" \\" if cao is None else r" \\[" + cao + "]"
    out = [r"\begin{center}", "{\\" + co, r"\begin{adjustbox}{max width=\linewidth}",
           r"\begin{tabular}{" + can + "}", r"\toprule"]
    if nhom:
        a, b, nhan = nhom
        out += ["& " * (a - 1) + r"\multicolumn{%d}{c}{%s}" % (b - a + 1, nhan) + " &" * (n - b) + r" \\",
                r"\cmidrule(lr){%d-%d}" % (a, b)]
    out += [" & ".join(boc(c) for c in dau) + r" \\", r"\midrule"]
    for h in hang:
        if h is None:
            out.append(r"\midrule")
            continue
        rong_h = sum(int(re.match(r"\\multicolumn\{(\d+)\}", str(c)).group(1)) if str(c).startswith("\\multicolumn")
                     else 1 for c in h)
        h = list(h) + [""] * (n - rong_h)
        out.append(" & ".join(boc(c) for c in h) + het)
    out += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}}", r"\end{center}"]
    return "\n".join(out)


def mu(e, bien="x"):
    return f"{bien}^{{{e}}}" if e > 1 else (bien if e == 1 else "1")


def cot_mu(n, bien="x"):
    return [mu(e, bien) for e in range(n, -1, -1)]


def bang_ngang(nhan_i, xs, ys):
    """Bang ngang cac moc: hang i (nhan_i), x_i, y_i (so lieu de cho)."""
    return bang(["i"] + [str(i) for i in nhan_i], [["x_i"] + [sl(t) for t in xs], ["y_i"] + [sl(t) for t in ys]])


def bang_ngang_goc(nhan_i, goc, xs, ys):
    """Bang ngang cac moc da trich (nhu dap an): hang i (danh so lai), chi so goc, x_i, y_i."""
    return bang(["i"] + [str(i) for i in nhan_i], [[r"\text{chỉ số gốc}"] + [str(j) for j in goc],
                                                  ["x_i"] + [sl(t) for t in xs], ["y_i"] + [sl(t) for t in ys]])


# --- cong thuc hien thi: 1 dong neu vua, khong thi it dong nhat va chia deu ---

LENH = {"cdot": 7.9, "quad": 11.0, "qquad": 22.0, ",": 1.8, ";": 3.1, " ": 3.7, "!": -1.8, "left": 0.0,
        "right": 0.0, "big": 0.5, "bigl": 0.5, "bigr": 0.5, "Big": 0.8, "biggl": 2.5, "biggr": 2.5, "dots": 13.0, "cdots": 13.0, "pi": 6.3, "omega": 7.2,
        "sigma": 6.3, "varphi": 6.6, "tfrac": 0.0, "dfrac": 0.0, "frac": 0.0, "text": 0.0, "sum": 12.0}
KT_RONG = {".": 3.1, ",": 3.1, ";": 3.1, ":": 3.1, "(": 4.3, ")": 4.3, "[": 3.1, "]": 3.1, "|": 3.1,
           "+": 13.4, "-": 13.4, "=": 14.7, " ": 0.0, "'": 3.0, "!": 3.1}


def dong_ngoac(t, i):
    sau = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            sau += 1
        elif t[j] == "}":
            sau -= 1
            if sau == 0:
                return j
    return len(t) - 1


def rong(t, k=1.0):
    """Uoc luong be ngang (pt) cua doan LaTeX toan hoc (Computer Modern 11pt); chi so tren/duoi x0.7."""
    w, i, truoc = 0.0, 0, ""
    while i < len(t):
        ch = t[i]
        if ch == "\\":
            m = re.match(r"\\([a-zA-Z]+|.)", t[i:])
            j = i + len(m.group(0))
            if m.group(1) in ("frac", "dfrac", "tfrac") and t[j:j + 1] == "{":   # phan so: rong = max(tu, mau)
                j1 = dong_ngoac(t, j)
                j2 = dong_ngoac(t, j1 + 1)
                kp = k * (0.7 if m.group(1) == "tfrac" else 1.0)
                w += max(rong(t[j + 1:j1], kp), rong(t[j1 + 2:j2], kp)) + 2.4 * k
                i, truoc = j2 + 1, ")"
                continue
            w += k * LENH.get(m.group(1), 7.0)
            i = j
            if m.group(1) in ("bigl", "biggl", "left"):
                truoc = "("
        elif ch in "+-" and truoc in ("", "(", ";", "{", "=", "[", ","):
            w += k * 8.6                               # dau mot ngoi (sau mo ngoac, dau ;, dau =)
            truoc = ch
            i += 1
        elif ch in "^_":
            i += 1
            if i < len(t) and t[i] == "{":
                j = dong_ngoac(t, i)
                w += rong(t[i + 1:j], k * 0.7)
                i = j + 1
            elif i < len(t):
                w += rong(t[i], k * 0.7)
                i += 1
        elif ch in "{}":
            i += 1
        else:
            w += k * KT_RONG.get(ch, 6.0 if ch.isalpha() else 5.5)
            if ch != " ":
                truoc = ch
            i += 1
    return w


def chia(ws, con):
    """Chia day so hang (do rong ws) thanh it dong nhat, moi dong <= con, can bang (cuc tieu dong dai nhat)."""
    n = len(ws)
    pre = [0.0]
    for w in ws:
        pre.append(pre[-1] + w)
    for L_ in range(1, n + 1):
        dp = [[(math.inf, -1)] * (n + 1) for _ in range(L_ + 1)]
        dp[0][0] = (0.0, -1)
        for l in range(1, L_ + 1):
            for i in range(1, n + 1):
                for j in range(l - 1, i):
                    m = max(dp[l - 1][j][0], pre[i] - pre[j])
                    if m < dp[l][i][0]:
                        dp[l][i] = (m, j)
        if dp[L_][n][0] <= con:
            cat, i = [], n
            for l in range(L_, 0, -1):
                j = dp[l][i][1]
                cat.append((j, i))
                i = j
            return cat[::-1]
    return [(i, i + 1) for i in range(n)]


def hien(ten, so_hang, rong_max=RONG, mo="", dong=""):
    """'ten = so_hang...' dang hien thi: 1 dong neu vua be ngang, khong thi align* it dong nhat, chia deu."""
    w0 = rong(ten) + 14.7 + rong(mo) + rong(dong)
    ws = [rong(s) + 0.5 for s in so_hang]
    if w0 + sum(ws) <= rong_max:
        return r"\[ " + ten + " = " + mo + " ".join(so_hang) + dong + r" \]"
    nhom = chia(ws, rong_max - w0 - 11.0)
    dong_tex = [" ".join(so_hang[a:b]) for a, b in nhom]
    dong_tex[0] = mo + dong_tex[0]
    dong_tex[-1] = dong_tex[-1] + dong
    return "\\begin{align*}\n" + ten + " &= " + " \\\\\n&\\quad ".join(dong_tex) + "\n\\end{align*}"


def hang_tu(he, bien="x"):
    """Cac so hang cua da thuc (he so bac cao -> thap), so hang dau khong co dau +."""
    n = len(he) - 1
    out = []
    for i, a in enumerate(he):
        if abs(a) < 1e-12:
            continue
        e = n - i
        s = so(abs(a))
        if e == 0:
            t = s
        elif s == "1":
            t = mu(e, bien)
        else:
            t = s + ("\\," if "cdot" in s else "") + mu(e, bien)
        out.append(("-" if a < 0 else "") + t if not out else ("- " if a < 0 else "+ ") + t)
    return out or ["0"]


def da_thuc(he, bien="x", ten="P(x)", rong_max=RONG):
    return hien(ten, hang_tu(he, bien), rong_max)


def muc_vec(phan):
    """Cac thanh phan vector (da la LaTeX) -> so hang cho hien(): ngan cach '; '."""
    return [p + r";\ " for p in phan[:-1]] + [phan[-1]]


def vec_hien(v, ten, rong_max=RONG):
    return hien(ten, muc_vec([so(t) for t in v]), rong_max, mo=r"\bigl(", dong=r"\bigr)")


def hien_nhieu(muc, rong_max=RONG):
    """Nhieu dang thuc (ten, so_hang, mo, dong) trong 1 align*, thang dau '='; dang thuc dai thi chia dong."""
    wt = max(rong(m[0]) for m in muc) + 14.7
    out = []
    for ten, so_hang, mo, dg in muc:
        ws = [rong(s) + 0.5 for s in so_hang]
        w_mo = rong(mo) + rong(dg)
        nhom = [(0, len(so_hang))] if wt + w_mo + sum(ws) <= rong_max else chia(ws, rong_max - wt - w_mo - 11.0)
        ds = [" ".join(so_hang[a:b]) for a, b in nhom]
        ds[0] = mo + ds[0]
        ds[-1] = ds[-1] + dg
        out.append(ten + " &= " + " \\\\\n&\\quad ".join(ds))
    return "\\begin{align*}\n" + " \\\\\n".join(out) + "\n\\end{align*}"


def vec_ct(ten, chi_, ct, gia):
    """2 dong cho hien_nhieu: ten = (cong thuc tung thanh phan) = (gia tri)."""
    lon = "bigg" if any("frac" in s for s in ct) else "big"   # ngoac cao theo phan so
    return [(ten, muc_vec(ct), rf"\{lon}l(", rf"\{lon}r)"),
            ("", muc_vec([so(v) for v in gia]), r"\bigl(", r"\bigr)")]


def L(_mau, **kw):
    """Thay @khoa@ trong doan LaTeX (tranh phai nhan doi ngoac nhon)."""
    for k, v in kw.items():
        _mau = _mau.replace("@" + k + "@", str(v))
    return _mau


def rut_lap(rows):
    """Hang bang lap: chi in lan 1, 2, ap chot, cuoi (giua in \\vdots); tong <= 4 hang thi in het."""
    if len(rows) <= 4:
        return rows
    return rows[:2] + [[r"\vdots"] * len(rows[0])] + rows[-2:]


def bang_horner_lap(a, c, k, bien="x"):
    """Bang Horner chia lap tai c (muc 2, horner.md), o r_j dong khung. Tra ve (bang, r, v)."""
    n = len(a) - 1
    r, v, hang = nw.horner_dao_ham(list(a), c, k)
    rows = [[r"\text{Hệ số}"] + [so(t) for t in a]]
    for j, sau in enumerate(hang):
        tich = [""] + [so(c * sau[l - 1]) for l in range(1, len(sau))]
        rows.append([f"c={so(c)}"] + tich)
        rows.append([f"j={j}"] + [so(t) for t in sau[:-1]] + [ob(so(sau[-1]))])
        rows.append(None)
    rows.pop()
    return bang([""] + cot_mu(n, bien), rows), r, v


def ds_chi_so(a, b):
    """Day chi so a..b viet gon: '1,2,3' (<= 4 so) hoac '1,\\dots,7'."""
    return ",".join(str(i) for i in range(a, b + 1)) if b - a <= 3 else f"{a},\\dots,{b}"


def doan_ts(x):
    """[x_0;x_n] viet gon (Ket luan)."""
    return f"[{sl(x[0])};{sl(x[-1])}]"


def mo_ta_luoi(x, h):
    """'N = 141 moc cach deu x_i = 1 + 0.1i (i = 0..140, x_i thuoc [1; 15], buoc luoi h = 0.1)' (nhu dap an giua ky)."""
    n = len(x) - 1
    x_i = (f"{sl(x[0])}+" if x[0] != 0 else "") + f"{sl(h)}\\,i"
    return (f"$N={n + 1}$ mốc cách đều $x_i={x_i}$ ($i=\\overline{{0,{n}}}$, $x_i\\in[{sl(x[0])};\\,{sl(x[-1])}]$, "
            f"bước lưới $h={sl(h)}$)")


# --- da thuc noi suy theo form dap an giua ky 20251: cong thuc -> thay so -> vector c -> bang nhan -> chinh tac ---

def phan_so(v):
    return Fraction(f"{float(v):.10g}")


def ghi_phan_so(p):
    """Fraction -> '=4.2' (thap phan huu han) / '=\\dfrac{9}{23}\\approx0.391304' / '\\approx...' (mau qua lon)."""
    q = p.denominator
    for f in (2, 5):
        while q % f == 0:
            q //= f
    if q == 1:
        return "=" + so(float(p))
    if p.denominator <= 1000:
        return f"={'-' if p < 0 else ''}\\dfrac{{{abs(p.numerator)}}}{{{p.denominator}}}\\approx{so(float(p))}"
    return "\\approx" + so(float(p))


def gia_tri_t(xbar, x0, h):
    """('\\bar t=\\dfrac{4.15-4.105}{0.115}=\\dfrac{9}{23}\\approx0.391304', Fraction)."""
    p = (phan_so(xbar) - phan_so(x0)) / phan_so(h)
    tu = f"{sl(xbar)}-{sl(x0)}" if x0 >= 0 else f"{sl(xbar)}+{sl(-x0)}"
    return f"\\bar t=\\dfrac{{{tu}}}{{{sl(h)}}}" + ghi_phan_so(p), p


def thua(bien, z):
    """Thua so (bien - z): 't', '(t-2)', '(t+1)', '(x-1.3)'."""
    if z == 0:
        return bien
    return f"({bien}-{sl(z)})" if z > 0 else f"({bien}+{sl(-z)})"


def tich_gon(ts_, gon):
    """Tich cac thua so; tu `gon` thua so tro len viet gon: dau, thu hai, \\cdots, cuoi."""
    if not ts_:
        return "1"
    if len(ts_) >= gon:
        return ts_[0] + ts_[1] + r"\cdots" + ts_[-1]
    return "".join(ts_)


def nhan_tich(z, bien, sap=False, gon=5):
    """Ten cac tich co so omega_k = prod_{i<k} (bien - z_i), k = 0..n (sap: thua so theo z tang, vd Gauss)."""
    out = []
    for k in range(len(z) + 1):
        zs = sorted(z[:k]) if sap else list(z[:k])
        out.append(tich_gon([thua(bien, v) for v in zs], gon))
    return out


def nhan_sb(n, ct, bien):
    """Ten cac tich co so Stirling (t, t^2, t(t^2-1), t^2(t^2-1), ...) / Bessel (u, (u^2-1/4), u(u^2-1/4), ...)."""
    out = []
    for k in range(n + 1):
        if ct == 3:                                # k = 2j+1: t(t^2-1)...(t^2-j^2); k = 2j: t^2(t^2-1)...(t^2-(j-1)^2)
            if k == 0:
                out.append("1")
                continue
            j = (k - 1) // 2 if k % 2 else k // 2 - 1
            out.append((bien if k % 2 else f"{bien}^2") + "".join(f"({bien}^2-{i * i})" for i in range(1, j + 1)))
        else:
            ts_ = "".join(f"({bien}^2-\\tfrac{{{(2 * i - 1) ** 2}}}{{4}})" for i in range(1, k // 2 + 1))
            out.append(((bien if k % 2 else "") + ts_) or "1")
    return out


def bang_nhan(nhan, pi, bien):
    """Bang nhan (nhu dap an): hang k = he so cua tich co so thu k theo luy thua cua bien (o trong ghi 0)."""
    n = len(pi) - 1
    rows = [[nhan[k]] + ["0"] * (n + 1 - len(p)) + [so(v) for v in p] for k, p in enumerate(pi)]
    return bang([""] + cot_mu(n, bien), rows, can="l" + "r" * (n + 1))


def nhan_vao(he, nhan):
    """'he' (LaTeX, da co dau) nhan voi tich co so: them '\\,' khi he la so dang a*10^k."""
    if nhan == "1":
        return he
    return he + ("\\," if "cdot10" in he else "") + nhan


def so_hang_tq(ct_he, nhan):
    """So hang cong thuc tong quat: c_k (cong thuc LaTeX) * tich co so."""
    out = []
    for k, (c_, nh) in enumerate(zip(ct_he, nhan)):
        s = c_ if nh == "1" else c_ + ("" if "frac" in c_ else "\\,") + nh
        out.append(s if k == 0 else "+" + s)
    return out


def so_hang_thay(o_k, nhan):
    """So hang cong thuc da thay so: o_k[k] = (cac o sai phan (chuoi), mau so LaTeX hoac '')."""
    out = []
    for k, ((tu, mau), nh) in enumerate(zip(o_k, nhan)):
        if mau:
            tu_s = tu[0] + "".join(("-" + s[1:]) if s.startswith("-") else ("+" + s) for s in tu[1:])
            s = nhan_vao(f"\\dfrac{{{tu_s}}}{{{mau}}}", nh)
            out.append(s if k == 0 else "+" + s)
        else:
            v = tu[0]
            s = nhan_vao(v if k == 0 or v.startswith("-") else "+" + v, nh)
            out.append(s)
    return out


def so_hang_gon(c, nhan):
    """So hang c_k * tich co so voi c_k da tinh (so tinh ra)."""
    out = []
    for k, (v, nh) in enumerate(zip(c, nhan)):
        s = so(v)
        out.append(nhan_vao(s if k == 0 or s.startswith("-") else "+" + s, nh))
    return out


def rut_so_hang(sh, tq=False):
    """Giu 5 so hang dau roi '+\\cdots' (nhu dap an); tq: cong thuc tong quat giu them so hang cuoi."""
    if len(sh) <= 6:
        return list(sh)
    return list(sh[:5]) + (["+\\cdots", sh[-1]] if tq else ["+\\cdots"])


def cong_thuc_thay(ten, thay, gon):
    """'P(t) = (thay so) = (gon)': 1 dang thuc neu hai dong trung nhau (vd ty sai phan: he so khong co phan so)."""
    thay, gon = rut_so_hang(thay), rut_so_hang(gon)
    if thay == gon:
        return hien(ten, thay)
    return hien_nhieu([(ten, thay, "", ""), ("", gon, "", "")], rong_max=RONG - 20)


def tinh_tai_bien(Pn, xbar, k, v, h, bien, dong_bien):
    """Doan tinh f(xbar), f^(k)(xbar) theo bien chuan hoa (t / u) nhu dap an. dong_bien: cau '... ta co \\bar t = ...'.
    v[j] = d^jP/dw^j tai diem tinh."""
    w = f"\\bar {bien}"
    xb = sl(xbar)
    dau = f"Tại $\\bar x={xb}$, ta có {dong_bien}. "
    if k == 0:
        return dau + f"Tính ${Pn}({w})$ bằng sơ đồ Horner chia (Câu 4a):\n\\[ f({xb})\\approx {Pn}({w})={so(v[0])}. \\]"
    dk = f"\\frac{{d{Pn}}}{{d{bien}}}" if k == 1 else f"\\frac{{d^{{{k}}}{Pn}}}{{d{bien}^{{{k}}}}}"
    tai = f"\\bigg|_{{{bien}={w}}}"
    ten_dh = f"{Pn}'({w})" if k == 1 else f"{dh(Pn, k)}({w})"
    mau = "h" if k == 1 else f"h^{{{k}}}"
    mau_so = sl(h) if k == 1 else f"{sl(h)}^{{{k}}}"
    return (dau + f"Tính ${Pn}({w})$ và ${ten_dh}$ bằng sơ đồ Horner chia lặp (Câu 4c):\n"
            f"\\[ f({xb})\\approx {Pn}({w})={so(v[0])},\\qquad {dk}{tai}={so(v[k])}. \\]\n"
            f"Đạo hàm theo biến gốc $x$:\n"
            f"\\[ {dh('f', k)}({xb})\\approx\\frac{{1}}{{{mau}}}\\,{dk}{tai}=\\frac{{{so(v[k])}}}{{{mau_so}}}"
            f"={so(v[k] / h ** k)}. \\]")


# ===== DOC DU LIEU (Buoc 0 theo loi giai) =====

CH = None                    # configparser cua data/loi_giai.ini (None: dung mac dinh)

MAC_DINH = {
    "cau3": {"file": "moc_cau3.txt"},
    "cau4": {"file": "horner_cau4.txt"},
    "cau5": {"file": "horner_cau5.txt"},
    "cau7": {"file": "lagrange_cau7.txt"},
    "cau8": {"file": "newton_cau8.txt"},
    "cau9": {"file": "newton_cau9.txt"},
    "cau11": {"file": "data Câu 11.xlsx", "sheet": "1", "xbar": "3.52", "m": "9", "chieu": "tien", "k": "1"},
    "cau12": {"file": "trung_tam_cau12.txt", "ghi_chu": ""},
    "cau13": {"file": "trung_tam_cau13.txt", "ghi_chu": ""},
    "cau14": {"file": "trung_tam_cau14.txt",
              "ghi_chu": r"Câu 14b ghi $\bar x=1.63$ (ngoài bảng $[5;5.7]$); sửa thành $\bar x=5.23$."},
    "cau16": {"file": "data Câu 11.xlsx", "sheet": "1", "xbar": "7.83", "m": "9", "k": "1"},
    "cau17": {"file": "data Câu 11.xlsx", "sheet": "1", "xbar": "7.83", "m": "8", "k": "1"},
    "cau19": {"file": "data Câu 19.xlsx", "sheet": "1", "ybar_a": "2.5", "ybar_b": "3.15", "m": "6",
              "eps": "1e-6", "n": "100"},
    "cau21": {"file_a": "spline_cau21a.txt", "file_b": "spline_cau21b.txt", "file_c": "spline_cau21c.txt",
              "ghi_chu_a": "", "ghi_chu_b": r"Đề ghi ``$S''(0)=-1,\ S''(0)=1$'' (lặp mốc 0); hiểu là "
                                         r"$S''(0)=-1$, $S''(3.1416)=1$.", "ghi_chu_c": ""},
    "cau23": {"file": "data Câu 23.xlsx"},
}


def ts(cau, khoa):
    """Tham so trong data/loi_giai.ini (thieu thi lay mac dinh)."""
    if CH is not None and CH.has_option(cau, khoa):
        return CH.get(cau, khoa).strip()
    return MAC_DINH.get(cau, {}).get(khoa, "")


def ts_so(cau, khoa, nguyen=False, nho_nhat=None):
    s = ts(cau, khoa)
    v, _, loi = nw.doc_o(s)
    if loi:
        raise LoiDuLieu(f"tham so {khoa} = {s!r} trong {TEN_CAU_HINH} khong phai so.")
    if nguyen:
        if v != int(v):
            raise LoiDuLieu(f"tham so {khoa} = {s!r} phai la so nguyen.")
        v = int(v)
    if nho_nhat is not None and v < nho_nhat:
        raise LoiDuLieu(f"tham so {khoa} = {s!r} phai >= {nho_nhat}.")
    return v


def duong_dan(ten):
    p = os.path.join(DATA, ten)
    if not os.path.isfile(p):
        raise LoiDuLieu(f"khong thay file '{p}'.")
    return p


def doc_tra_loi(ten):
    """File tra loi cua script (moi dong 1 cau tra loi, bo dong trong)."""
    with open(duong_dan(ten), encoding="utf-8-sig") as f:
        dong = [d for d in f.read().splitlines() if d.strip()]
    if not dong:
        raise LoiDuLieu(f"file '{ten}' rong.")
    return dong


def dong_thu(dong, i, ten, ten_file):
    if i >= len(dong):
        raise LoiDuLieu(f"file '{ten_file}' thieu dong {i + 1} ({ten}).")
    return dong[i]


def day_so(text, ten):
    """Day so trong 1 dong (tach bang khoang trang / ';'); o khong phai so -> loi."""
    out = []
    for o in nw.tach_o(text):
        v, _, loai = nw.doc_o(o)
        if loai:
            raise LoiDuLieu(f"{ten}: {o!r} khong phai so ({loai}).")
        out.append(v)
    if not out:
        raise LoiDuLieu(f"{ten}: khong co so nao.")
    return out


def mot_so(text, ten, nguyen=False, nho_nhat=None):
    v = day_so(text, ten)
    if len(v) != 1:
        raise LoiDuLieu(f"{ten}: can 1 so, doc duoc {len(v)}.")
    v = v[0]
    if nguyen:
        if v != int(v):
            raise LoiDuLieu(f"{ten} = {sl(v)} phai la so nguyen.")
        v = int(v)
    if nho_nhat is not None and v < nho_nhat:
        raise LoiDuLieu(f"{ten} = {v} phai >= {nho_nhat}.")
    return v


def muc_dich(text, hop_le):
    so_ = day_so(text, "muc dich")
    return {int(v) for v in so_ if v in hop_le}


def lam_sach(ox, oy, so=None, kieu="noi_suy"):
    """Buoc 0 cua loi giai: loai cap co o khong doc duoc; moc trung cung y giu 1, khac y bao loi
    (spline: moc trung la loi); sap tang theo x. kieu 'bptt': giu moi diem, giu thu tu.
    Tra ve (x, y, sk) voi sk = dict(loai, trung, sap, goc): loai = [(nhan, o_x, o_y, ly do x, ly do y)]."""
    if len(ox) != len(oy):
        raise LoiDuLieu(f"x co {len(ox)} o, y co {len(oy)} o -> khong ghep cap duoc.")
    so = so or [str(i) for i in range(1, len(ox) + 1)]
    loai, diem = [], []
    for j, a, b in zip(so, ox, oy):
        vx, _, lx = nw.doc_o(a)
        vy, _, ly = nw.doc_o(b)
        if lx or ly:
            loai.append((j, a, b, lx, ly))
        else:
            diem.append((vx, vy, j))
    if not diem:
        raise LoiDuLieu("khong con diem nao hop le.")
    sk = dict(loai=loai, trung=[], sap=False, goc=[(p[0], p[1]) for p in diem])
    if kieu == "bptt":
        dem = {}
        for xv, yv, _ in diem:
            dem.setdefault(xv, []).append(yv)
        sk["trung"] = [(xv, ys) for xv, ys in dem.items() if len(ys) > 1]
        return [p[0] for p in diem], [p[1] for p in diem], sk
    nhom = {}
    for xv, yv, j in diem:
        nhom.setdefault(xv, []).append((yv, j))
    gop = []
    for xv, cap in nhom.items():
        ys = [c[0] for c in cap]
        if len(ys) > 1:
            nguon = ", ".join(f"y = {yv:.10g} (o {j})" for yv, j in cap)
            if kieu == "spline":
                raise LoiDuLieu(f"moc trung x = {xv:.10g}: {nguon} -> spline khong cho moc trung.")
            if max(ys) != min(ys):
                raise LoiDuLieu(f"moc trung x = {xv:.10g} voi y khac nhau: {nguon} -> sua du lieu (loi giai: "
                                "khac y bao loi, dung).")
            sk["trung"].append((xv, len(ys)))
        gop.append((xv, ys[0]))
    x_cu = [p[0] for p in gop]
    gop.sort()
    sk["sap"] = [p[0] for p in gop] != x_cu
    return [p[0] for p in gop], [p[1] for p in gop], sk


LY_DO = {"o rong": "rỗng", "NaN": "là NaN", "vo cung": "là vô cùng", "khong doc duoc so": "không đọc được số"}


def ly_do_o(ten, o, loai):
    if loai == "o chu":
        return f"ô ${ten}$ là chữ ``{tex_chu(o.strip())}''"
    return f"ô ${ten}$ {LY_DO.get(loai, loai)}"


def cau_loai(sk, nhan_cap, cot_x=None, cot_y=None):
    """Cac cap bi loai -> cum tu. nhan_cap(j): 'dòng 1' / 'cặp thứ 3'; cot_x/cot_y: ten cot Excel (ghi o)."""
    out = []
    for j, a, b, lx, ly in sk["loai"]:
        if lx == "o rong" and not ly and cot_y:
            out.append(f"ô {cot_y}{j} $={sl(nw.doc_o(b)[0])}$ không có $x$ đi kèm nên bị loại ({nhan_cap(j)}, ô $x$ rỗng)")
        elif ly == "o rong" and not lx and cot_x:
            out.append(f"ô {cot_x}{j} $={sl(nw.doc_o(a)[0])}$ không có $y$ đi kèm nên bị loại ({nhan_cap(j)}, ô $y$ rỗng)")
        else:
            ly_do = ", ".join(ly_do_o(t, o, l) for t, o, l in (("x", a, lx), ("y", b, ly)) if l)
            out.append(f"{nhan_cap(j)} bị loại ({ly_do})")
    return out


def cau_trung_sap(sk):
    out = [f"mốc $x={sl(xv)}$ lặp lại {k} lần cùng giá trị $y$ nên giữ một" for xv, k in sk["trung"]]
    if sk["sap"]:
        out.append("sắp lại các mốc theo $x$ tăng dần")
    return out


def xu_ly_txt(sk):
    """'Xu ly du lieu' cho du lieu nhap tu file tra loi (.txt); rong neu du lieu sach."""
    cum = cau_loai(sk, lambda j: f"cặp thứ {j}") + cau_trung_sap(sk)
    if not cum:
        return ""
    s = "; ".join(cum)
    con = len(sk["goc"]) - sum(k - 1 for _, k in sk["trung"])
    return r"\pp{Xử lý dữ liệu.} " + s[0].upper() + s[1:] + f". Còn ${con}$ mốc.\n\n"


def doc_bang(ten, sheet=1):
    """Bang so lieu (xlsx / csv / txt bang) theo cach doc cua newton.py. Tra ve dict (x, y o goc, so dong...)."""
    p = duong_dan(ten)
    cac = []
    try:
        for ten_sheet, luoi in nw.doc_luoi_file(p):
            kq = nw.phan_tich_luoi(luoi)
            if kq:
                cac.append((ten_sheet, luoi, kq))
    except ValueError as e:
        raise LoiDuLieu(str(e))
    if not cac:
        raise LoiDuLieu(f"file '{ten}' khong co bang so lieu.")
    if not 1 <= sheet <= len(cac):
        raise LoiDuLieu(f"file '{ten}' co {len(cac)} sheet so lieu, khong co sheet thu {sheet}.")
    ten_sheet, luoi, kq = cac[sheet - 1]
    if not kq["co_x"]:
        raise LoiDuLieu(f"file '{ten}': chi co 1 day so (y), can 2 cot x, y.")
    if kq["vi_tri"] != "dong":
        raise LoiDuLieu(f"file '{ten}': can bang 2 cot x, y (moi cap 1 dong).")
    dau = int(kq["so"][0]) - 1                      # so dong truoc dong so lieu dau tien
    truoc = luoi[:dau]
    kq = dict(kq, file=ten, so_sheet=len(cac), sheet=sheet, ten_sheet=ten_sheet,
              dau=dau, dau_trong=all(not str(c).strip() for h in truoc for c in h))
    return kq


def doc_xy_bang(ten, sheet=1, kieu="noi_suy"):
    B = doc_bang(ten, sheet)
    x, y, sk = lam_sach(B["x"], B["y"], B["so"], kieu)
    return [round(v, 10) for v in x], y, sk, B


def mo_dau_bang(B):
    """'File `F` (sheet đầu)' / '`F` (dòng đầu trống, bỏ qua)'... cac phan mo dau mo ta file bang."""
    sheet = ""
    if B["so_sheet"] > 1:
        sheet = " (sheet đầu)" if B["sheet"] == 1 else f" (sheet thứ {B['sheet']}, ``{tex_chu(B['ten_sheet'])}'')"
    dau = ""
    if B["dau"]:
        dau = (" (dòng đầu trống, bỏ qua)" if B["dau"] == 1 else f" ({B['dau']} dòng đầu trống, bỏ qua)") \
            if B["dau_trong"] else f" ({B['dau']} dòng đầu không phải số liệu, bỏ qua)"
    trong = f"; bỏ qua dòng trống {', '.join(B['trong'])}" if B["trong"] else ""
    return sheet, dau, trong


def mo_ta_bang_11(B, sk, x, h):
    """Cau 11b: 'Xu ly du lieu. File `F` (sheet dau): cot A la x, cot B la y; ... Con N moc x = x0,...,xn, cach deu h.'"""
    sheet, dau, trong = mo_dau_bang(B)
    cum = cau_loai(sk, lambda j: f"dòng {j}", B["day_x"], B["day_y"]) + cau_trung_sap(sk)
    nhan = r"\pp{Xử lý dữ liệu.} " if cum or dau or trong else r"\pp{Dữ liệu.} "
    s = (f"File \\texttt{{{tex_chu(B['file'])}}}{sheet}{dau}: cột {B['day_x']} là $x$, cột {B['day_y']} là $y$"
         + trong + ("; " + "; ".join(cum) if cum else "") + ". ")
    s += "Ta có bảng dữ liệu gồm " + mo_ta_luoi(x, h) + "."
    return nhan + s


# ===== CAU 3 =====

def cau3():
    ten = ts("cau3", "file")
    khoi = []
    for d in doc_tra_loi(ten):
        bo = day_so(d, f"dong '{d}'")
        if len(bo) != 3:
            raise LoiDuLieu(f"dong '{d}': can 3 so n a b, doc duoc {len(bo)}.")
        n, a, b = bo
        if n != int(n) or n < 1:
            raise LoiDuLieu(f"dong '{d}': so moc n = {sl(n)} phai la so nguyen >= 1.")
        if a == b:
            raise LoiDuLieu(f"dong '{d}': a = b, doan noi suy suy bien.")
        doi = a > b
        if doi:
            a, b = b, a
        n = int(n)
        t, x, W = mt.moc_toi_uu(n, a, b, verbose=False)
        p, q = (a + b) / 2, (b - a) / 2
        ct = ("" if p == 0 else sl(p)) + "-" + ("" if q == 1 else sl(q)) + f"\\cos\\dfrac{{(2i+1)\\pi}}{{{2 * n}}}"
        nhan = f"$n={n}$, $[a,b]=[{sl(a)},{sl(b)}]$" + (" (đề cho $a>b$, đổi chỗ $a$, $b$)" if doi else "")
        khoi.append(f"\\pp{{{nhan}:}} $x_i={ct}$, $i=0,\\dots,{n - 1}$:\n"
                    + bang(["i"] + [str(i) for i in range(n)], [["x_i"] + [so(v) for v in x]]) + "\n"
                    + vec_hien(x, "x"))
        tc = np.sort(np.polynomial.chebyshev.chebroots([0] * n + [1]))
        KT[f"c3 n={n}: t vs chebroots"] = float(np.max(np.abs(np.array(t) - tc)))
    V["c3_cac_bo"] = "\n\n".join(khoi)


# ===== CAU 4, 5 =====

def doc_horner(ten):
    """File tra loi horner.py: muc dich / he so (muc 1,2,3,4,6) / c (muc 1-4) / k (muc 3, 6) / moc (muc 5)."""
    dong = doc_tra_loi(ten)
    muc = muc_dich(dong[0], (1, 2, 3, 4, 5, 6))
    kq, i = dict(muc=muc), 1
    if muc & {1, 2, 3, 4, 6}:
        kq["a"] = day_so(dong_thu(dong, i, "he so", ten), "he so")
        i += 1
        if muc & {1, 2, 3, 4}:
            kq["c"] = day_so(dong_thu(dong, i, "cac diem c", ten), "c")
            i += 1
        if muc & {3, 6}:
            kq["k"] = mot_so(dong_thu(dong, i, "cap dao ham k", ten), "k", nguyen=True, nho_nhat=0)
            i += 1
    if 5 in muc:
        kq["moc"] = day_so(dong_thu(dong, i, "cac moc x_k", ten), "cac moc")
    return kq


def cau4():
    H = doc_horner(ts("cau4", "file"))
    if "a" not in H or "c" not in H:
        raise LoiDuLieu("file can muc dich 1, 2, 3 (gia tri, phep chia, dao ham), he so va cac diem c.")
    a = list(H["a"])
    while a and a[0] == 0:                         # Buoc 0: bo he so 0 o dau
        a.pop(0)
    if len(a) < 2:
        raise LoiDuLieu("da thuc bac < 1: khong co phep chia cho (x - c).")
    n = len(a) - 1
    k = H.get("k", n)                              # de hoi dao ham cac cap -> mac dinh k = n
    K = min(k, n)
    V["c4_P"], V["c4_a"] = da_thuc_gon(a), r";\,".join(sl(v) for v in a)
    V["c4_n"], V["c4_ni"], V["c4_n1"], V["c4_K"], V["c4_n1p"] = str(n), chi(n), str(n - 1), str(K), str(n + 1)
    V["c4_thuong"] = "+".join(f"b^{{(0)}}_{chi(i)}" + mu_gon(i - 1) for i in range(n, 0, -1))
    khoi = []
    for c in H["c"]:
        B, r, v = bang_horner_lap(a, c, k)
        Q = nw.horner_dao_ham(list(a), c, 0)[2][0][:-1]
        s = (f"\\pp{{$c={sl(c)}$:}}\n{B}\n$P({sl(c)})=r_0={so(r[0])}$; thương ${' '.join(hang_tu(Q))}$, "
             f"dư ${so(r[0])}$")
        if k >= 1:
            ten = "(" + ",".join(dh("P", j) for j in range(k + 1)) + ")"
            ve = "(" + r";\ ".join(f"{j}!\\,r_{chi(j)}" if j <= n else "0" for j in range(k + 1)) + ")"
            s += f";\\\\\n${ten}({sl(c)})={ve}={vecl(v)}$."
        else:
            s += "."
        khoi.append(s)
        KT[f"c4 c={sl(c)}: Horner vs numpy"] = max(abs(np.polyval(np.polyder(a, j) if j else a, c) - v[j])
                                                   for j in range(K + 1))
    V["c4_cac_c"] = "\n\n".join(khoi)


def cau5():
    H = doc_horner(ts("cau5", "file"))
    if "moc" not in H:
        raise LoiDuLieu("file can muc dich 5 (tich w) va dong cac moc x_k.")
    xs = H["moc"]
    m = len(xs)
    p = [1.0]
    rows = [[""] + [""] * m + ["1"]]
    for i, z in enumerate(xs):
        p = nw.horner_nhan(p, z)
        hang = [so(t) for t in p]
        if i == m - 1:
            hang = [ob(t) for t in hang]
        rows.append([sl(z)] + [""] * (m - i - 1) + hang)
    V["c5_x"] = r";\ ".join(sl(v) for v in xs)
    V["c5_m"], V["c5_mi"] = str(m), chi(m)
    V["c5_tich"] = "".join(f"({x_tru(v)})" if v != 0 else "x" for v in xs)
    V["c5_bang"] = bang(["x_{k-1}"] + cot_mu(m), rows)
    V["c5_w"] = da_thuc(p, ten=f"w_{chi(m)}(x)", rong_max=RONG_KL)
    KT["c5: w vs numpy.poly"] = float(np.max(np.abs(np.array(p) - np.poly(xs))))


# ===== CAU 7 =====

def cau7():
    ten = ts("cau7", "file")
    dong = doc_tra_loi(ten)
    ox = nw.bo_nhan(nw.tach_o(dong_thu(dong, 1, "x", ten)))
    oy = nw.bo_nhan(nw.tach_o(dong_thu(dong, 2, "y", ten)))
    x, y, sk = lam_sach(ox, oy)
    n = len(x) - 1
    if n < 1:
        raise LoiDuLieu("can it nhat 2 moc.")
    a, D, bang_t, bang_c = lg.lagrange(x, y)
    V["c7_xl"] = xu_ly_txt(sk)
    V["c7_n"], V["c7_ni"], V["c7_n1"], V["c7_n1i"] = str(n), chi(n), str(n + 1), chi(n + 1)
    rows = [[""] + [""] * (n + 1) + ["1"]]
    for i, p in enumerate(bang_t):
        rows.append([sl(x[i])] + [""] * (n - i) + [so(t) for t in p])
    V["c7_bang_tich"] = bang(["x_{k-1}"] + cot_mu(n + 1), rows)
    V["c7_bang_thuong"] = bang(["i", "x_i"] + cot_mu(n) + [r"\text{dư}"],     # Q_{i,l}: thuong w / (x - x_i)
                               [[str(i), sl(x[i])] + [so(t) for t in q] + [so(du)] for i, (q, du) in enumerate(bang_c)])
    rows = [[str(i), sl(x[i])] + [r"\text{--}" if j == i else so(x[i] - x[j]) for j in range(n + 1)]
            + [so(D[i]), sl(y[i]), so(y[i] / D[i])] for i in range(n + 1)]
    V["c7_bang_he_so"] = bang(["i", "x_i", "j=0"] + [str(j) for j in range(1, n + 1)] + ["D_i", "y_i", "y_i/D_i"], rows)
    V["c7_YQ"] = vec_hien(a, rf"P_{chi(n)}=Y\cdot Q")
    V["c7_P"] = da_thuc(a, ten=f"P_{chi(n)}(x)", rong_max=RONG_KL)
    KT["c7: max |P(x_i) - y_i|"] = float(np.max(np.abs(np.polyval(a, x) - np.array(y))))


# ===== CAU 8, 9, 11: NEWTON =====

def bang_tsp(x, T, khung, ten_y="y_i", d=None):
    """Bang ty sai phan / sai phan tam giac duoi T[i][k]; khung = tap (i, k) dong khung."""
    n = len(x) - 1
    rows = []
    for i in range(n + 1):
        h = [str(i), sl(x[i])]
        for k in range(i + 1):
            s = sd(T[i][k], d) if d is not None else (sl(T[i][k]) if k == 0 else so(T[i][k]))
            h.append(ob(s) if (i, k) in khung else s)
        rows.append(h + [""] * (n - i))
    return bang(["i", "x_i", ten_y] + [f"\\text{{TSP{k}}}" if d is None else f"\\Delta^{{{k}}}" for k in range(1, n + 1)],
                rows)


def ngoai_suy(x, xbar):
    """Cau canh bao ngoai suy (rong neu xbar trong [x_0, x_n])."""
    if x[0] <= xbar <= x[-1]:
        return ""
    return (f"$\\bar x={sl(xbar)}$ nằm ngoài $[x_0;x_n]=[{sl(x[0])};{sl(x[-1])}]$ nên đây là ngoại suy, "
            "sai số có thể lớn. ")


def cong_thuc_dh(Pn, w, r, v, k, xbar, h=None):
    """Display: f(xbar) ~ P_n(w) = ..., f^(k)(xbar) ~ ... (h = None: theo x; h: theo t, chia h^k)."""
    xb = sl(xbar)
    f0 = f"f({xb})\\approx {Pn}({w})" + ("=r_0" if h is None else "") + f"={so(v[0])}"
    if k == 0:
        return f0
    if h is None:
        if k == 1:
            fk = f"{dh('f', 1)}({xb})\\approx {dh(Pn, 1)}({xb})=r_1={so(v[1])}"
        elif k <= len(r) - 1:
            fk = (f"{dh('f', k)}({xb})\\approx {dh(Pn, k)}({xb})={k}!\\,r_{chi(k)}={math.factorial(k)}\\cdot{sn(r[k])}"
                  f"={so(v[k])}")
        else:
            fk = f"{dh('f', k)}({xb})\\approx {dh(Pn, k)}({xb})=0"
    else:
        mau = "h" if k == 1 else f"h^{k}"
        mau_so = sl(h) if k == 1 else f"{sl(h)}^{k}"
        dP = so(r[1]) if k == 1 else so(v[k])
        fk = (f"{dh('f', k)}({xb})\\approx\\frac{{{dh(Pn, k)}({w})}}{{{mau}}}=\\frac{{{dP}}}{{{mau_so}}}"
              f"={so(v[k] / h ** k)}")
    return f0 + ",\\qquad " + fk


def ten_gia_tri(xbar, k):
    """'$f(1.8)$, $f'''(1.8)$' (tieu de cau b)."""
    xb = sl(xbar)
    return f"$f({xb})$" + (f", ${dh('f', k)}({xb})$" if k else "")


def newton_ty_sai_phan(x, y, chieu, xbar, k):
    """Than cau Newton tien / lui, moc bat ky (Cau 8, 9): cong thuc, bang ty sai phan, thay so, bang nhan, P_n(x),
    f(xbar)."""
    n = len(x) - 1
    ni = chi(n)
    tien = chieu == "tien"
    T = nw.bang_sai_phan(x, y)
    khung = {(i, i) for i in range(n + 1)} if tien else {(n, kk) for kk in range(n + 1)}
    R = nw.newton(x, T, chieu)
    c = R["c"]
    ct = []                                        # c_k = f[x_0..x_k] (tien) / f[x_{n-k}..x_n] (lui)
    for kk in range(n + 1):
        a_, b_ = (0, kk) if tien else (n - kk, n)
        ct.append(f"y_{{{a_}}}" if kk == 0 else f"f[x_{{{a_}}},x_{{{b_}}}]" if kk == 1
                  else f"f[x_{{{a_}}},\\dots,x_{{{b_}}}]")
    goc = list(range(n)) if tien else list(range(n, 0, -1))
    nhan_ky = [tich_gon([f"(x-x_{{{i}}})" for i in goc[:kk]], 4) for kk in range(n + 1)]
    nhan = nhan_tich(R["z"], "x", gon=4)
    o0 = sl(y[0] if tien else y[n])
    thay = so_hang_thay([([o0], "")] + [([so(c[kk])], "") for kk in range(1, n + 1)], nhan)
    r, v, _ = nw.horner_dao_ham(list(R["b"]), xbar, k)          # Horner chia lap (Cau 4c), khong in bang
    a_np = np.linalg.solve(np.vander(x), y)
    KT["newton: max |P(x_i) - y_i|"] = float(np.max(np.abs(np.polyval(R["b"], x) - np.array(y))))
    KT["newton: f^(j)(xbar) vs numpy"] = max(abs(np.polyval(np.polyder(a_np, j) if j else a_np, xbar) - v[j])
                                             for j in range(k + 1))
    ten_chieu = "tiến" if tien else "lùi"
    z_ = "x_{k-1}" if tien else f"x_{{{n + 1}-k}}"
    hc = "Horner chia lặp" if k else "Horner chia"
    cau4 = "Câu 4c" if k else "Câu 4a"
    ten_gt = f"${'P_' + ni}({sl(xbar)})$" + (f" và ${dh('P_' + ni, k)}({sl(xbar)})$" if k else "")
    return L(r"""\pp{Phương pháp.} Mốc không cách đều nên dùng tỷ sai phân@lui@. Công thức nội suy Newton @ten_chieu@ bậc $@n@$ có dạng:
@tq@

\subsection{a) Đa thức Newton @ten_chieu@}
\pp{Bảng tỷ sai phân} (hàng $i$, cột TSP$k$ là $f[x_{i-k},\dots,x_i]$; @o_khung@ $=c_k$):
\[ f[x_{i-k},\dots,x_i]=\frac{f[x_{i-k+1},\dots,x_i]-f[x_{i-k},\dots,x_{i-1}]}{x_i-x_{i-k}}. \]
@bang_tsp@
Thay các ô khung vào công thức:
@thay@
Vector hệ số theo thứ tự các cơ sở là
@vec_c@
Khai triển các tích cơ sở theo luỹ thừa của $x$ ta có bảng nhân (hàng $k$: $\omega_k(x)=\omega_{k-1}(x)\cdot(x-@z@)$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-@z@\,A_{k-1,l}$):
@bang_nhan@
Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:
@P@

\subsection{b) Tính gần đúng @ten_gt_f@}
@ns@Tại $\bar x=@xb@$, tính @ten_gt@ bằng sơ đồ @hc@ (@cau4@):
\[ @ct@. \]""", lui="" if tien else f"; Newton lùi xuất phát từ $x_{ni}={sl(x[n])}$", ten_chieu=ten_chieu, n=n,
             tq=hien(f"P_{{{n}}}(x)", rut_so_hang(so_hang_tq(ct, nhan_ky), tq=True)),
             o_khung="đường chéo khung" if tien else "hàng cuối khung", bang_tsp=bang_tsp(x, T, khung),
             thay=cong_thuc_thay(f"P_{{{n}}}(x)", thay, so_hang_gon(c, nhan)), vec_c=vec_hien(c, "c"), z=z_,
             bang_nhan=bang_nhan(nhan, R["bang_tich"], "x"), P=da_thuc(R["b"], ten=f"P_{{{n}}}(x)"),
             ten_gt_f=ten_gia_tri(xbar, k), ns=ngoai_suy(x, xbar), xb=sl(xbar), ten_gt=ten_gt, hc=hc, cau4=cau4,
             ct=cong_thuc_dh(f"P_{ni}", sl(xbar), r, v, k, xbar))


def newton_deu(xs, ys, h, chieu, xbar, k):
    """Newton tien / lui moc cach deu theo t (Cau 11c; Cau 8, 9 khi du lieu cach deu): cac khoi LaTeX."""
    n = len(xs) - 1
    tien = chieu == "tien"
    d = nw.so_le(ys)
    T = nw.bang_sai_phan(xs, ys, h)
    khung = {(i, i) for i in range(n + 1)} if tien else {(n, kk) for kk in range(n + 1)}

    def o_(i, kk):                                 # chuoi so trong bang sai phan
        return sd(T[i][kk], d) if d is not None else (sl(T[i][kk]) if kk == 0 else so(T[i][kk]))

    if d is None:                                  # du lieu khong co so chu so co dinh: in so tinh ra
        rows = []
        for i in range(n + 1):
            hh = [str(i), sl(xs[i])] + [ob(o_(i, kk)) if (i, kk) in khung else o_(i, kk) for kk in range(i + 1)]
            rows.append(hh + [""] * (n - i))
        bang_sp = bang(["i", "x_i", "y_i"] + [f"\\Delta^{{{kk}}}" for kk in range(1, n + 1)], rows)
    else:
        bang_sp = bang_tsp(xs, T, khung, d=d)
    R = nw.newton(xs, T, chieu, h)
    c = R["c"]
    g = "0" if tien else chi(n)
    ky = r"\Delta" if tien else r"\nabla"
    ct = [f"y_{g}", f"{ky} y_{g}"] + [f"\\dfrac{{{ky}^{{{kk}}}y_{g}}}{{{kk}!}}" for kk in range(2, n + 1)]
    nhan = nhan_tich(R["z"], "t")
    o_k = [([o_(kk if tien else n, kk)], "" if kk <= 1 else f"{kk}!") for kk in range(n + 1)]
    s0 = xs[0] if tien else xs[n]
    tb = (xbar - s0) / h
    r, v, _ = nw.horner_dao_ham(list(R["b"]), tb, k)
    a_np = np.linalg.solve(np.vander(np.arange(n + 1.0) - (0 if tien else n)), ys)
    KT["newton deu: f(xbar) vs numpy"] = abs(np.polyval(a_np, tb) - v[0])
    z_ = "(k-1)" if tien else "(-(k-1))"
    return dict(n=n, tien=tien, s0=s0, tb=tb, r=r, v=v, b=R["b"], c=c, bang_sp=bang_sp,
                tq=hien(f"P_{{{n}}}(t)", rut_so_hang(so_hang_tq(ct, nhan), tq=True)),
                thay=cong_thuc_thay(f"P_{{{n}}}(t)", so_hang_thay(o_k, nhan), so_hang_gon(c, nhan)),
                sh=(f"P_{{{n}}}(t)", so_hang_tq(ct, nhan), so_hang_thay(o_k, nhan), so_hang_gon(c, nhan)),
                ct_nhan=(f"hàng $k$: $\\omega_k(t)=\\omega_{{k-1}}(t)\\cdot(t-z_{{k-1}})$, $z_{{k-1}}={z_[1:-1]}$; "
                         f"$A_{{0,0}}=1$, $A_{{k,l}}=A_{{k-1,l-1}}{'-' if tien else '+'}(k-1)\\,A_{{k-1,l}}$"),
                bang_nhan=bang_nhan(nhan, R["bang_tich"], "t"), Pt=da_thuc(R["b"], "t", ten=rf"P_{chi(n)}(t)"),
                sp_ct=("(hàng $i$, cột $\\Delta^k$ là $\\Delta^ky_{i-k}$; đường chéo khung $=\\Delta^ky_0$)" if tien else
                       "(hàng $i$, cột $\\Delta^k$ là $\\Delta^ky_{i-k}=\\nabla^ky_i$; hàng cuối khung $=\\nabla^ky_n$)"))


def newton_deu_than(N, xbar, k, h, m_moc, cau8=False, ten_chieu=None):
    """Than Newton cach deu (sau bang moc). cau8: kieu Cau 8/9 (co cau a, b)."""
    n = N["n"]
    ni = chi(n)
    tien = N["tien"]
    t_ct = (f"$t=\\dfrac{{x-x_0}}{{h}}=\\dfrac{{{x_tru(N['s0'])}}}{{{sl(h)}}}$" if tien else
            f"$t=\\dfrac{{x-x_n}}{{h}}=\\dfrac{{{x_tru(N['s0'])}}}{{{sl(h)}}}$")
    ten = "tiến" if tien else "lùi"
    pp = (f"\\pp{{Phương pháp.}} {m_moc} mốc cách đều $h={sl(h)}$ nên dùng Newton {ten} mốc cách đều. Đặt biến "
          f"chuẩn hoá {t_ct}. Công thức nội suy Newton {ten} bậc ${n}$ có dạng:\n{N['tq']}")
    sp_ = L(r"""\pp{Bảng sai phân} @sp_ct@:
\[ \Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,@n@;\ i=0,\dots,@n@-k). \]
@bang_sp@
Thay các ô khung vào công thức:
@thay@
Vector hệ số theo thứ tự các cơ sở là
@vec_c@
Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân (@ct_nhan@):
@bang_nhan@
Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:
@Pt@""", sp_ct=N["sp_ct"], n=n, bang_sp=N["bang_sp"], thay=N["thay"], vec_c=vec_hien(N["c"], "c"),
             ct_nhan=N["ct_nhan"], bang_nhan=N["bang_nhan"], Pt=N["Pt"])
    gt = tinh_tai_bien(f"P_{ni}", xbar, k, N["v"], h, "t", "$" + gia_tri_t(xbar, N["s0"], h)[0] + "$")
    if not cau8:
        return pp + "\n\n" + sp_ + "\n\n" + gt
    return (pp + "\n\n" + f"\\subsection{{a) Đa thức Newton {ten_chieu}}}\n" + sp_ + "\n\n"
            + f"\\subsection{{b) Tính gần đúng {ten_gia_tri(xbar, k)}}}\n" + gt)


def doc_newton(ten, chieu_md):
    """File tra loi newton.py: muc dich / x / y / xbar / k [/ m]."""
    dong = doc_tra_loi(ten)
    muc = muc_dich(dong[0], (1, 2, 3, 4))
    if 1 in muc and 2 not in muc:
        chieu = "tien"
    elif 2 in muc and 1 not in muc:
        chieu = "lui"
    else:
        chieu = chieu_md
    ox = nw.bo_nhan(nw.tach_o(dong_thu(dong, 1, "x", ten)))
    oy = nw.bo_nhan(nw.tach_o(dong_thu(dong, 2, "y", ten)))
    if not muc & {3, 4}:
        raise LoiDuLieu("de hoi f(xbar): muc dich can co 3 va cac dong xbar, k.")
    xbar = day_so(dong_thu(dong, 3, "xbar", ten), "xbar")[0]
    k = mot_so(dong_thu(dong, 4, "k", ten), "k", nguyen=True, nho_nhat=0)
    return chieu, ox, oy, xbar, k


def newton_cau(cau, chieu_md):
    chieu, ox, oy, xbar, k = doc_newton(ts(cau, "file"), chieu_md)
    x, y, sk = lam_sach(ox, oy)
    n = len(x) - 1
    if n < 1:
        raise LoiDuLieu("can it nhat 2 moc.")
    h = nw.cach_deu(x)
    ten_chieu = "tiến" if chieu == "tien" else "lùi"
    so_cau = cau[3:]
    xl = xu_ly_txt(sk)
    if h is None:
        V["c" + cau[3:] + "_tieu_de"] = f"Câu {so_cau}. Đa thức nội suy Newton {ten_chieu} (mốc bất kỳ)"
        V["c" + cau[3:] + "_than"] = xl + newton_ty_sai_phan(x, y, chieu, xbar, k)
    else:
        V["c" + cau[3:] + "_tieu_de"] = f"Câu {so_cau}. Đa thức nội suy Newton {ten_chieu} (mốc cách đều)"
        N = newton_deu(x, y, h, chieu, xbar, k)
        V["c" + cau[3:] + "_than"] = xl + newton_deu_than(N, xbar, k, h, n + 1, cau8=True, ten_chieu=ten_chieu)


def cau8():
    newton_cau("cau8", "tien")


def cau9():
    newton_cau("cau9", "lui")


def trich_xuat(x, xbar, k, h):
    """Thuat toan Cau 11a: j = round((xbar - x_0)/h) (lam tron len khi bang .5), ket nap dan, hoa -> trai."""
    n = len(x) - 1
    u = (xbar - x[0]) / h
    j0 = math.floor(u + 0.5 + 1e-9)
    j = min(max(j0, 0), n)
    L_ = R_ = j
    thu_tu = [j]
    for _ in range(2, k + 1):
        if L_ == 0:
            R_ += 1
            thu_tu.append(R_)
        elif R_ == n:
            L_ -= 1
            thu_tu.append(L_)
        elif (xbar - x[L_ - 1]) - (x[R_ + 1] - xbar) <= 1e-9 * h:
            L_ -= 1
            thu_tu.append(L_)
        else:
            R_ += 1
            thu_tu.append(R_)
    L2, R2, _ = nw.trich_xuat(x, xbar, k)
    if (L2, R2) != (L_, R_):
        print(f"  Canh bao: trich xuat (xbar = {xbar:.10g}) khac newton.trich_xuat: [{L_}, {R_}] vs [{L2}, {R2}]")
    return L_, R_, thu_tu, j0


def cau_trich_xuat(x, xbar, h, thu_tu, j0, dem=False):
    """Qua trinh trich xuat (Cau 11a) trong 1 cau: moc gan nhat j = round((xbar - x_0)/h), thu tu them moc, L, R
    (dem: kem so moc trai / phai)."""
    tam = thu_tu[0]
    trai, phai = sum(j < tam for j in thu_tu), sum(j > tam for j in thu_tu)
    L_, R_ = min(thu_tu), max(thu_tu)
    them = ("; thêm lần lượt $" + ",".join(f"x_{{{j}}}" for j in thu_tu[1:]) + "$") if len(thu_tu) > 1 else ""
    dem_ = f"${trai}$ mốc trái, ${phai}$ mốc phải, " if dem else ""
    phan_so = f"\\operatorname{{round}}\\tfrac{{{sl(xbar)}-{sn(x[0])}}}{{{sl(h)}}}"
    j_ = f"$j={phan_so}={tam}$" if j0 == tam else f"${phan_so}={j0}$ ngoài $0..{len(x) - 1}$ nên $j={tam}$"
    return (f"mốc gần $\\bar x$ nhất là $x_{{{tam}}}={sl(x[tam])}$ "
            f"({j_}){them} $\\Rightarrow$ {dem_}$L={L_}$, $R={R_}$.")


# ===== CAU 11 =====

DL = {}                      # du lieu bang da doc (Cau 11 dung lai cho Cau 16, 17)


def doc_bang_cau(cau):
    ten, sheet = ts(cau, "file"), ts_so(cau, "sheet", nguyen=True, nho_nhat=1)
    khoa = (ten, sheet)
    if khoa not in DL:
        x, y, sk, B = doc_xy_bang(ten, sheet)
        h = nw.cach_deu(x)
        if h is None:
            raise LoiDuLieu(f"file '{ten}': moc khong cach deu (thuat toan 11a bao 'moc khong cach deu', dung).")
        DL[khoa] = (x, y, sk, B, h)
    return DL[khoa]


def kiem_m(m, N, ten="m"):
    """Buoc 0 (11a): m > so moc -> 'khong du moc', dung ca bang. Tra ve (m, cau ghi chu)."""
    if m > N:
        return N, f"Bảng chỉ có ${N}$ mốc nên không đủ ${m}$ mốc: dùng cả ${N}$ mốc. "
    return m, ""


def cau11():
    x, y, sk, B, h = doc_bang_cau("cau11")
    xbar = ts_so("cau11", "xbar")
    m = ts_so("cau11", "m", nguyen=True, nho_nhat=1)
    k = ts_so("cau11", "k", nguyen=True, nho_nhat=0)
    chieu = "lui" if ts("cau11", "chieu").lower().startswith("l") else "tien"
    m, ghi = kiem_m(m, len(x))
    L_, R_, thu_tu, j0 = trich_xuat(x, xbar, m, h)
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    V["c11_du_lieu"] = mo_ta_bang_11(B, sk, x, h)
    V["c11_m"], V["c11_xb"], V["c11_n"] = str(m), sl(xbar), str(m - 1)
    V["c11_ket_trich"] = ghi + ngoai_suy(x, xbar) + cau_trich_xuat(x, xbar, h, thu_tu, j0)
    V["c11_bang_xy"] = bang_ngang_goc(range(m), range(L_, R_ + 1), xs, ys)
    N = newton_deu(xs, ys, h, chieu, xbar, k)
    V["c11_c_tieu_de"] = (f"Đa thức Newton {'tiến' if chieu == 'tien' else 'lùi'}, $f(\\bar x)$"
                          + (f", ${dh('f', k)}(\\bar x)$" if k else ""))
    V["c11_c_than"] = newton_deu_than(N, xbar, k, h, m)


# ===== CAU 12 - 17: NOI SUY TRUNG TAM =====

TEN_CT = {1: "Gauss I", 2: "Gauss II", 3: "Stirling", 4: "Bessel"}
O_KHUNG = {1: r"(hàng $i$ chứa $y_i,\Delta y_i,\Delta^2y_i,\dots$; ô khung: $\Delta^ky_{-\lfloor k/2\rfloor}$)",
           2: r"(hàng $i$ chứa $y_i,\Delta y_i,\Delta^2y_i,\dots$; ô khung: $\Delta^ky_{-\lceil k/2\rceil}$)",
           3: r"(ô khung: cặp $\Delta^{2j-1}y_{-j},\Delta^{2j-1}y_{-j+1}$ và $\Delta^{2j}y_{-j}$)",
           4: r"(ô khung: cặp $\Delta^{2j}y_{-j},\Delta^{2j}y_{-j+1}$ và $\Delta^{2j+1}y_{-j}$)"}
CT_NHAN = {1: r"hàng $k$: $\omega_k(t)=\omega_{k-1}(t)\cdot(t-z_{k-1})$, $z=@z@$; $A_{0,0}=1$, "
              r"$A_{k,l}=A_{k-1,l-1}-z_{k-1}\,A_{k-1,l}$",
           3: r"$\Omega_0=1$, $\Omega_1=t$, $\Omega_{2j}=t\,\Omega_{2j-1}$, $\Omega_{2j+1}=\Omega_{2j-1}\cdot(t^2-j^2)$",
           4: r"$\Omega_0=1$, $\Omega_1=u$, $\Omega_{2j}=\Omega_{2j-2}\cdot\big(u^2-(j-\frac12)^2\big)$, "
              r"$\Omega_{2j+1}=u\,\Omega_{2j}$"}
CT_NHAN[2] = CT_NHAN[1]


def tt_tinh(xs, ys, h, ct, xbar, k):
    """Noi suy trung tam tren bo moc xs (cach deu): bang sai phan, cong thuc (tong quat / thay so), bang nhan, P,
    gia tri tai xbar."""
    n = len(xs) - 1
    q = tt.vi_tri_tam(n, ct)
    p = -q
    x0 = xs[q]
    tb = (xbar - x0) / h
    d = tt.so_le(ys)
    D = tt.bang_sai_phan(ys)
    c, chon = tt.he_so(D, p, ct)
    khung = {o for ds in chon for o in ds}
    o_str, rows = {}, []
    for s in range(n + 1):
        i = p + s
        h_ = [str(i), sl(xs[s])]
        for kk in range(n + 1 - s):
            v = sd(D[s][kk], d) if d is not None else (sl(D[s][kk]) if kk == 0 else so(D[s][kk]))
            o_str[(i, kk)] = v
            h_.append(ob(v) if (i, kk) in khung else v)
        rows.append(h_ + [""] * s)
    R = dict(n=n, q=q, p=p, x0=x0, x1=xs[q + 1] if q + 1 <= n else None, tb=tb, c=c)
    R["bang_sp"] = bang(["i", "x_i", "y_i"] + [dmu(kk) + "y_i" for kk in range(1, n + 1)], rows)
    ctk = []                                       # cong thuc c_k theo cac o khung
    for kk in range(n + 1):
        o = chon[kk]
        ten = " + ".join((dmu(kk) + f"y_{{{i}}}" if kk else f"y_{{{i}}}") for i, _ in o)
        if len(o) == 2:
            ten = f"\\dfrac{{{ten}}}{{2\\cdot{kk}!}}" if kk > 1 else f"\\dfrac{{{ten}}}{{2}}"
        elif kk > 1:
            ten = f"\\dfrac{{{ten}}}{{{kk}!}}"
        ctk.append(ten)
    P = tt.lap_P(c, n, ct)                         # muc 3, trung_tam.md: bang nhan cac tich co so
    b, bien, lech = P["b"], P["bien"], P["lech"]
    R["s0"], R["diem"], R["bien"] = x0 + lech * h, tb - lech, bien
    nhan = nhan_tich(P["z"], "t", sap=True) if ct in (1, 2) else nhan_sb(n, ct, bien)
    mau = [(("2" if kk <= 1 else f"2\\cdot{kk}!") if len(chon[kk]) == 2 else ("" if kk <= 1 else f"{kk}!"))
           for kk in range(n + 1)]
    ten_P = f"P_{{{n}}}({bien})"
    R["tq"] = hien(ten_P, rut_so_hang(so_hang_tq(ctk, nhan), tq=True))
    R["sh"] = (ten_P, so_hang_tq(ctk, nhan), so_hang_thay([([o_str[o] for o in chon[kk]], mau[kk])
                                                            for kk in range(n + 1)], nhan), so_hang_gon(c, nhan))
    R["thay"] = cong_thuc_thay(ten_P, so_hang_thay([([o_str[o] for o in chon[kk]], mau[kk]) for kk in range(n + 1)],
                                                    nhan), so_hang_gon(c, nhan))
    R["ct_nhan"] = L(CT_NHAN[ct], z=",".join(str(int(z)) for z in P.get("z", [])))
    R["bang_nhan"] = bang_nhan(nhan, P["pi"], bien)
    R["Pt"] = da_thuc(b, bien, ten=ten_P)
    R["r"], R["v"], _ = nw.horner_dao_ham(list(b), R["diem"], k)    # Horner chia lap (Cau 4c), khong in bang
    wi = np.arange(p, p + n + 1, dtype=float) - lech
    KT["trung tam: max |P(w_i) - y_i|"] = float(np.max(np.abs(np.polyval(b, wi) - np.array(ys))))
    KT["trung tam: f(xbar) vs Lagrange"] = abs(tt.lagrange_tai(xs, ys, xbar) - R["v"][0])
    return R


def tt_gia_tri(R, ct, xbar, k, h):
    """Doan tinh gia tri (va dao ham) tai xbar theo t (Bessel: u = t - 1/2), nhu dap an."""
    t_tex, t_ps = gia_tri_t(xbar, R["x0"], h)
    dong = f"${t_tex}$"
    if ct == 4:
        dong = f"${t_tex}\\ \\Longrightarrow\\ \\bar u=\\bar t-\\frac12{ghi_phan_so(t_ps - Fraction(1, 2))}$"
    return tinh_tai_bien(f"P_{chi(R['n'])}", xbar, k, R["v"], h, R["bien"], dong)


def ly_do_gauss(ct, tb):
    t = so(tb)
    if ct == 1 and tb >= 0:
        return f"$\\bar t={t}{'>' if tb > 0 else '='}0$ nên dùng Gauss I"
    if ct == 2 and tb <= 0:
        return f"$\\bar t={t}{'<' if tb < 0 else '='}0$ nên dùng Gauss II"
    khac = "Gauss II" if ct == 1 else "Gauss I"
    print(f"  Canh bao: chon {TEN_CT[ct]} nhung tbar = {tb:.6g} -> {khac} hop hon.")
    return f"$\\bar t={t}$, dùng {TEN_CT[ct]} theo yêu cầu ({khac} hợp với $\\bar t$ này hơn)"


def phuong_phap_tt(R, ct, m, h):
    """'Phuong phap. 9 moc cach deu ... Dat bien chuan hoa t = ... Cong thuc noi suy ... bac n co dang:' + cong thuc."""
    pi = f"($i={R['p']}..{R['p'] + R['n']}$)"
    t_ = f"$t=\\dfrac{{x-x_0}}{{h}}=\\dfrac{{{x_tru(R['x0'])}}}{{{sl(h)}}}$"
    if ct in (1, 2):
        dau = (f"{m} mốc cách đều, {ly_do_gauss(ct, R['tb'])}, mốc trung tâm $x_0={sl(R['x0'])}$ {pi}, "
               f"$h={sl(h)}$. Đặt biến chuẩn hoá {t_}.")
    elif ct == 3:
        dau = (f"{m} mốc cách đều (số lẻ) nên dùng Stirling, mốc trung tâm $x_0={sl(R['x0'])}$ {pi}, $h={sl(h)}$. "
               f"Đặt biến chuẩn hoá {t_}.")
    else:
        dau = (f"{m} mốc cách đều (số chẵn) nên dùng Bessel, hai mốc chính giữa $x_0={sl(R['x0'])}$, "
               f"$x_1={sl(R['x1'])}$ {pi}, $h={sl(h)}$. Đặt {t_} và biến đối xứng "
               f"$u=t-\\dfrac12=\\dfrac{{{x_tru(round(R['s0'], 10))}}}{{{sl(h)}}}$.")
    theo = " theo biến $u$" if ct == 4 else ""
    return (f"\\pp{{Phương pháp.}} {dau} Công thức nội suy {TEN_CT[ct]} bậc ${R['n']}${theo} có dạng:\n"
            + R["tq"])


KHOI_TT = r"""\pp{Bảng sai phân} @o_khung@:
\[ \Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,@n@;\ i=@p@,\dots,@pn@-k). \]
@bang_sp@
Thay các ô khung vào công thức:
@thay@
Vector hệ số theo thứ tự các cơ sở là
@vec_c@
Khai triển các tích cơ sở theo luỹ thừa của $@bien@$ ta có bảng nhân (@ct_nhan@):
@bang_nhan@
Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:
@Pt@"""


def khoi_tt(R, ct):
    return L(KHOI_TT, o_khung=O_KHUNG[ct], n=R["n"], p=R["p"], pn=R["p"] + R["n"], bang_sp=R["bang_sp"],
             thay=R["thay"], vec_c=vec_hien(R["c"], "c"), bien=R["bien"], ct_nhan=R["ct_nhan"],
             bang_nhan=R["bang_nhan"], Pt=R["Pt"])


def chinh_m(ct, m, N):
    """Buoc 0 (15): m > so moc -> m = so moc; Stirling can m le, Bessel m chan. Tra ve (m, ghi chu)."""
    ghi = ""
    if m > N:
        ghi += f"Bảng chỉ có ${N}$ mốc nên dùng ${N}$ mốc. "
        m = N
    if ct == 3 and m % 2 == 0:
        ghi += f"Stirling cần số mốc lẻ nên dùng ${m - 1}$ mốc. "
        m -= 1
    if ct == 4 and m % 2 == 1:
        ghi += f"Bessel cần số mốc chẵn nên dùng ${m - 1}$ mốc. "
        m -= 1
    if (ct == 3 and m < 3) or (ct == 4 and m < 2) or m < 1:
        raise LoiDuLieu(f"{TEN_CT[ct]}: khong du moc (m = {m}).")
    return m, ghi


def doc_trung_tam(cau):
    """File tra loi trung_tam.py: cong thuc / x / y / xbar / k / m."""
    ten = ts(cau, "file")
    dong = doc_tra_loi(ten)
    cts = muc_dich(dong[0], (1, 2, 3, 4))
    if len(cts) != 1:
        raise LoiDuLieu("dong cong thuc can dung 1 lua chon (1 Gauss I, 2 Gauss II, 3 Stirling, 4 Bessel).")
    ox = nw.bo_nhan(nw.tach_o(dong_thu(dong, 1, "x", ten)))
    oy = nw.bo_nhan(nw.tach_o(dong_thu(dong, 2, "y", ten)))
    xbar = day_so(dong_thu(dong, 3, "xbar", ten), "xbar")[0]
    k = mot_so(dong_thu(dong, 4, "k", ten), "k", nguyen=True, nho_nhat=0)
    m = mot_so(dong[5], "m", nguyen=True, nho_nhat=1) if len(dong) > 5 else None
    return cts.pop(), ox, oy, xbar, k, m


def tieu_de_gia_tri(xbar, k):
    if k == 0:
        return f"Tính gần đúng $f({sl(xbar)})$"
    if k == 1:
        return f"Giá trị và đạo hàm tại $\\bar x={sl(xbar)}$"
    return f"Giá trị và đạo hàm cấp ${k}$ tại $\\bar x={sl(xbar)}$"


def trung_tam_bang(cau):
    """Cau 12, 13, 14: bang du lieu cho san, lap da thuc trung tam, tinh tai xbar."""
    ct, ox, oy, xbar, k, m = doc_trung_tam(cau)
    x, y, sk = lam_sach(ox, oy)
    h = tt.cach_deu(x)
    if h is None:
        raise LoiDuLieu("moc khong cach deu (thuat toan 15 bao 'moc khong cach deu', dung).")
    m, ghi = chinh_m(ct, m or len(x), len(x))
    trich = ""
    if m < len(x):
        L_, R_, thu_tu, j0 = trich_xuat(x, xbar, m, h)
        xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    else:
        xs, ys = x, y
    R = tt_tinh(xs, ys, h, ct, xbar, k)
    if m < len(x):
        trich = (f"\\pp{{Trích xuất.}} {ghi}Thuật toán câu 11a ($\\bar x={sl(xbar)}$, $k={m}$): "
                 + cau_trich_xuat(x, xbar, h, thu_tu, j0, dem=True)
                 + f" Đánh số lại $i={R['p']}..{R['p'] + R['n']}$:\n"
                 + bang_ngang_goc(range(R["p"], R["p"] + m), range(L_, R_ + 1), xs, ys) + "\n\n")
    elif ghi:
        trich = ghi + "\n\n"
    ghi_chu = ts(cau, "ghi_chu")
    de = f"\\pp{{Đề (đã sửa).}} {ghi_chu}\n\n" if ghi_chu else ""
    V["c" + cau[3:] + "_tieu_de"] = f"Câu {cau[3:]}. Đa thức nội suy {TEN_CT[ct]}"
    V["c" + cau[3:] + "_than"] = L(r"""@de@@trich@@pp@

\subsection{a) Lập đa thức @ten@}
@khoi@

\subsection{b) @tieu_b@}
@ns@@gia_tri@""", de=de, trich=trich, pp=phuong_phap_tt(R, ct, m, h), ten=TEN_CT[ct], khoi=khoi_tt(R, ct),
                                   tieu_b=tieu_de_gia_tri(xbar, k), ns=ngoai_suy(x, xbar),
                                   gia_tri=tt_gia_tri(R, ct, xbar, k, h))


def cau12():
    trung_tam_bang("cau12")


def cau13():
    trung_tam_bang("cau13")


def cau14():
    trung_tam_bang("cau14")


def cau_tam(R, ct, xbar, L_, R_, m):
    """Cau chon moc tam sau khi trich xuat (nhu dap an): 'Chon tam x_0 = ... va trich xuat m moc doi xung ung voi
    chi so goc L..R, danh so lai i = ...:'."""
    goc = f"chỉ số gốc ${ds_chi_so(L_, R_)}$"
    so_lai = f"đánh số lại $i={R['p']}..{R['p'] + R['n']}$:"
    if ct == 3:
        return (f"Chọn tâm $x_0={sl(R['x0'])}$ (mốc chính giữa) và trích xuất ${m}$ mốc đối xứng ứng với {goc}, "
                + so_lai)
    j0_ = L_ + R["q"]
    giua = (f"$\\bar x={sl(xbar)}$ nằm trong khoảng trung tâm $[x_{{{j0_}}};x_{{{j0_ + 1}}}]="
            f"[{sl(R['x0'])};\\,{sl(R['x1'])}]$. " if R["x0"] <= xbar <= R["x1"] else "")
    return (giua + f"Chọn $x_0={sl(R['x0'])}$, $x_1={sl(R['x1'])}$ (hai mốc chính giữa) và trích xuất ${m}$ mốc ứng "
            f"với {goc}, " + so_lai)


def trung_tam_trich(cau, ct):
    """Cau 16 (Stirling), 17 (Bessel): trich xuat m moc tu bang dai (du lieu Cau 11) roi noi suy trung tam."""
    x, y, sk, B, h = doc_bang_cau(cau)
    xbar = ts_so(cau, "xbar")
    k = ts_so(cau, "k", nguyen=True, nho_nhat=0)
    m0 = ts_so(cau, "m", nguyen=True, nho_nhat=1)
    m, ghi = chinh_m(ct, m0, len(x))
    if m < len(x):
        L_, R_, thu_tu, j0 = trich_xuat(x, xbar, m, h)
    else:
        L_, R_, thu_tu, j0 = 0, len(x) - 1, None, None
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    R = tt_tinh(xs, ys, h, ct, xbar, k)
    n = R["n"]
    cung_11 = 11 in CAU_CO and (ts(cau, "file"), ts(cau, "sheet")) == (ts("cau11", "file"), ts("cau11", "sheet"))
    ten = TEN_CT[ct]
    V["c" + cau[3:] + "_tieu_de"] = f"Câu {cau[3:]}. Trích xuất {m0} điểm và nội suy {ten} tại $\\bar x={sl(xbar)}$"
    if ct == 3 and cung_11:
        du_lieu = f"Dữ liệu \\texttt{{{tex_chu(B['file'])}}} đã xử lý ở câu 11b (" + mo_ta_luoi(x, h) + "). "
        nguon = ""
    elif cung_11:
        du_lieu, nguon = "", ", dữ liệu câu 11b"
    else:
        du_lieu, nguon = mo_ta_bang_11(B, sk, x, h) + "\n\n", ""
    if thu_tu is None:
        trich_ = f"{ghi}Bảng có ${len(x)}$ mốc, dùng tất cả. "
    else:
        trich_ = (f"{ghi}{ngoai_suy(x, xbar)}Thuật toán câu 11a ($\\bar x={sl(xbar)}$, $k={m}${nguon}): "
                  + cau_trich_xuat(x, xbar, h, thu_tu, j0, dem=True) + " ")
    tam = cau_tam(R, ct, xbar, L_, R_, m)
    tieu_b = f"Đa thức {ten}, $f(\\bar x)$" + (f", ${dh('f', k)}(\\bar x)$" if k else "")
    V["c" + cau[3:] + "_than"] = L(r"""\subsection{a) Trích xuất}
@du_lieu@@trich@@tam@
@bang_xy@

\subsection{b) @tieu_b@}
@pp@

@khoi@

@gia_tri@""", du_lieu=du_lieu, trich=trich_, tam=tam,
                                   bang_xy=bang_ngang_goc(range(R["p"], R["p"] + n + 1), range(L_, R_ + 1), xs, ys),
                                   tieu_b=tieu_b, pp=phuong_phap_tt(R, ct, m, h), khoi=khoi_tt(R, ct),
                                   gia_tri=tt_gia_tri(R, ct, xbar, k, h))
    return R["v"]


def cau16():
    trung_tam_trich("cau16", 3)


def cau17():
    trung_tam_trich("cau17", 4)


# ===== CAU 19 =====

CHIEU = {1: "tăng", -1: "giảm", 0: "hằng"}


def tsp_x_theo_y(hn_):
    """Bang ty sai phan cua x theo y (ham nguoc), duong cheo khung."""
    u, vv, T = hn_["u"], hn_["v"], hn_["T"]
    r_ = len(u) - 1
    rows = []
    for s in range(r_ + 1):
        hh = [str(s), sl(u[s]), sl(vv[s])]
        for kk in range(1, s + 1):
            hh.append(ob(so(T[s][kk])) if kk == s else so(T[s][kk]))
        rows.append(hh + [""] * (r_ - s))
    rows[0][2] = ob(rows[0][2])
    return bang(["s", r"u_s=y", r"v_s=x"] + [f"\\text{{TSP{kk}}}" for kk in range(1, r_ + 1)], rows)


def khoi_ham_nguoc(x, y, yb, k, dd, m, dau_khoi, cong_thuc):
    """Phuong phap ham nguoc cho 1 khoang cach ly (x_k, x_{k+1}) trong doan don dieu dd = (a, b, chieu)."""
    a_, b_, s_ = dd
    hn_ = nsn.ham_nguoc(x, y, yb, k, a_, b_, m)
    so_moc = len(hn_["u"])
    chon = (f"\\pp{{Chọn {so_moc} mốc}} có $|y_j-\\bar y|$ nhỏ nhất trong đoạn đơn điệu"
            + (f" (đoạn chỉ có {so_moc} mốc)" if hn_["thieu"] else "") + ":\n")
    tong, rows = 0.0, []
    for j in range(so_moc):
        tong += hn_["so_hang"][j]
        rows.append([str(j), so(hn_["c"][j]), so(hn_["omega"][j]), so(hn_["so_hang"][j]), so(tong)])
    s = (dau_khoi + "\n\n" + chon
         + bang([r"\text{lần}", "j", "x_j", "y_j", r"|y_j-\bar y|"],
                [[str(t), str(j), sl(x[j]), sl(y[j]), so(abs(y[j] - yb))] for t, j in enumerate(hn_["thu_tu"], 1)])
         + "\n" + r"\pp{Bảng tỷ sai phân của $x$ theo $y$} ($u=y$, $v=x$; đường chéo khung $=c_j$):" + "\n")
    if cong_thuc:
        s += (r"\[ v[u_{s-k},\dots,u_s]=\frac{v[u_{s-k+1},\dots,u_s]-v[u_{s-k},\dots,u_{s-1}]}{u_s-u_{s-k}}. \]"
              + "\n")
    s += (tsp_x_theo_y(hn_) + "\n" + r"\pp{Giá trị tại $\bar y$:} $\bar x=\sum_jc_j\,\omega_j(\bar y)$, $\omega_0=1$, "
          r"$\omega_j=\omega_{j-1}\cdot(\bar y-u_{j-1})$:" + "\n"
          + bang(["j", "c_j", r"\omega_j(\bar y)", r"c_j\,\omega_j(\bar y)", r"\text{tổng}"], rows))
    xv = hn_["xbar"]
    dung = x[k] <= xv <= x[k + 1]
    if not dung:                                   # tu kiem tra: nghiem phai nam trong khoang cach ly
        s += (f"\n\\pp{{Nhận xét.}} $\\bar x={so(xv)}$ nằm ngoài khoảng cách ly $({sl(x[k])};{sl(x[k + 1])})$: các mốc "
              "chọn có $y$ gần như bằng nhau (gần điểm cực trị) nên tỷ sai phân của $x$ theo $y$ rất lớn, nội suy hàm "
              "ngược không tin cậy cho nghiệm này (dùng phương pháp lặp hoặc ít mốc hơn).")
        print(f"  Canh bao: ham nguoc ybar = {yb:.10g} trong ({x[k]:.10g}; {x[k + 1]:.10g}) cho xbar = {xv:.10g} "
              "nam ngoai khoang cach ly -> ghi 'khong tin cay'.")
    KT[f"c19 ham nguoc yb={yb} k={k}: |y(xbar) - ybar|"] = abs(nsn.y_tai(x, y, xv, m) - yb)
    idx = hn_["idx"]
    KQ_19.append([f"({sl(x[k])};\\ {sl(x[k + 1])})", f"[{sl(x[min(idx)])};\\ {sl(x[max(idx)])}]",
                  r"\text{hàm ngược (tỷ sai phân } x\text{ theo } y)", so(xv) if dung else r"\text{không tin cậy}"])
    return s, (xv, dung, k), abs(hn_["so_hang"][-1])


KQ_19 = []                   # hang bang ket qua (nhu dap an): khoang cach ly, moc su dung, phuong phap, ket qua


def bang_kq_19(x):
    """Bang tong hop nghiem (nhu dap an giua ky): Nghiem | Khoang cach ly | Moc su dung | Phuong phap | Ket qua."""
    if not KQ_19:
        return ""
    rows = [[f"\\bar x_{{{r}}}" if len(KQ_19) > 1 else r"\bar x"] + h for r, h in enumerate(KQ_19, 1)]
    KQ_19.clear()
    return ("\\pp{Tổng hợp.}\n" + bang([r"\text{Nghiệm}", r"\text{Khoảng cách ly}", r"\text{Mốc sử dụng}",
                                         r"\text{Phương pháp áp dụng}", r"\text{Kết quả}"], rows, can="ccccc"))


def bang_don_dieu(x, y, doan):
    if len(doan) <= 8:
        return bang([r"\text{đoạn}"] + [f"[{sl(x[a])};\\ {sl(x[b])}]" for a, b, _ in doan],
                    [[r"\text{chỉ số}"] + [f"{a}..{b}" for a, b, _ in doan],
                     ["y_a"] + [sl(y[a]) for a, _, _ in doan],
                     ["y_b"] + [sl(y[b]) for _, b, _ in doan],
                     [r"\text{chiều}"] + [f"\\text{{{CHIEU[s]}}}" for _, _, s in doan]])
    return bang([r"\text{đoạn}", r"\text{chỉ số}", "y_a", "y_b", r"\text{chiều}"],
                [[f"[{sl(x[a])};\\ {sl(x[b])}]", f"{a}..{b}", sl(y[a]), sl(y[b]), f"\\text{{{CHIEU[s]}}}"]
                 for a, b, s in doan])


def cong_thuc_lap(m, eps, cac):
    """Khoi cong thuc phuong phap lap (18d) cho cac huong dung (cac = tap {'tien', 'lui'})."""
    e = mu10(eps)
    out = []
    for huong in ("tien", "lui"):
        if huong not in cac:
            continue
        tien = huong == "tien"
        ky = r"\Delta" if tien else r"\nabla"
        y_g = "y_k" if tien else "y_{k+1}"
        dau = "-" if tien else "+"

        def tich(j):
            if j == 2:
                return f"t(t{dau}1)"
            if j == 3:
                return f"t(t{dau}1)(t{dau}2)"
            return f"t(t{dau}1)\\cdots(t{dau}{j - 1})"

        def hang(j, ve_phai):
            if ve_phai:
                return f"\\frac{{{ky}^{j}{y_g}}}{{{j}!\\,{ky} {y_g}}}{tich(j)}"
            return f"\\frac{{{ky}^{j}{y_g}}}{{{j}!}}{tich(j)}"

        if m <= 2:
            ve, phi = "", ""
        elif m == 3:
            ve, phi = "+" + hang(2, False), "-" + hang(2, True)
        elif m == 4:
            ve, phi = "+" + hang(2, False) + "+" + hang(3, False), "-" + hang(2, True) + "-" + hang(3, True)
        else:
            ve = "+" + hang(2, False) + "+\\dots+" + hang(m - 1, False)
            phi = "-" + hang(2, True) + "-\\dots-" + hang(m - 1, True)
        t_ten = r"\frac{x-x_k}{h}" if tien else r"\frac{x-x_{k+1}}{h}"
        moc = f"$x_k,\\dots,x_{{k+{m - 1}}}$ bên phải" if tien else f"$x_{{k-{m - 2}}},\\dots,x_{{k+1}}$ bên trái"
        if m == 2:
            moc = "$x_k,x_{k+1}$"
        dan = (f"Trên mốc cách đều, thay $f$ bằng đa thức nội suy Newton {'tiến' if tien else 'lùi'} {m} mốc theo "
               "$t$; phương trình $P=\\bar y$ viết lại thành $t=\\varphi(t)$ rồi lặp đơn, nghiệm hợp lệ khi "
               f"$t^*\\in{'[0;1]' if tien else '[-1;0]'}$")
        if len(cac) == 1:
            mo = (f"\\pp{{Phương pháp}} (18d; mỗi khoảng $(x_k;x_{{k+1}})$ đủ {m} mốc {moc} nên lặp Newton "
                  f"{'tiến' if tien else 'lùi'}, $t={t_ten}$, $\\varepsilon={e}$). {dan}:")
        else:
            mo = (f"\\pp{{Phương pháp lặp {'tiến' if tien else 'lùi'}}} (18d; khoảng đủ {m} mốc {moc}, $t={t_ten}$, "
                  f"$\\varepsilon={e}$). {dan}:")
        sp_ = (r"\Delta^0y_i=y_i,\qquad \Delta^jy_i=\Delta^{j-1}y_{i+1}-\Delta^{j-1}y_i\quad\text{(bảng sai phân, ô khung }"
               + (r"\Delta^jy_k" if tien else r"\nabla^jy_{k+1}") + r"\text{)};\\")
        x_tl = r"x_k+t_{l+1}h" if tien else r"x_{k+1}+t_{l+1}h"
        out.append(mo + "\n\\begin{gather*}\n" + sp_ + "\n"
                   + f"\\bar y={y_g}+{ky} {y_g}\\,t{ve}\\\\\n"
                   + f"\\Longrightarrow\\ t=\\varphi(t)=\\frac{{\\bar y-{y_g}}}{{{ky} {y_g}}}{phi},\\\\\n"
                   + f"t_0=\\frac{{\\bar y-{y_g}}}{{{ky} {y_g}}},\\qquad t_{{l+1}}=\\varphi(t_l),\\qquad\\text{{dừng khi }} "
                   f"h\\,|t_{{l+1}}-t_l|<\\varepsilon,\\qquad \\bar x={x_tl}.\n\\end{{gather*}}")
    return "\n".join(out)


def khoi_lap(x, y, yb, k, r, lp, h, d, hon_hop=False, m_yc=None, gon=False):
    """1 nghiem cua phuong phap lap: bang sai phan, phi(t), bang lap, ket qua. hon_hop: co ca nghiem lap tien va
    lui (ghi chu chieu o tung nghiem); m_yc: so moc yeu cau (khac so moc dung -> ghi chu);
    gon: ban thi giua ky (ghi chieu lap + t ngay dau, goi y ghi bang lap)."""
    idx, D = lp["idx"], lp["D"]
    m = len(idx)
    tien = lp["huong"] == "tien"
    rows = []
    for rr in range(m):
        hh = [str(idx[rr]), sl(x[idx[rr]])]
        for kk in range(rr + 1):
            s_ = sd(D[rr][kk], d) if d is not None else (sl(D[rr][kk]) if kk == 0 else so(D[rr][kk]))
            khung = kk == rr if tien else rr == m - 1
            hh.append(ob(s_) if khung else s_)
        rows.append(hh + [""] * (m - 1 - rr))
    b_sp = bang(["i", "x_i", "y_i"] + [dmu(kk) for kk in range(1, m)], rows)
    dau = "-" if tien else "+"
    phi = hien(r"\varphi(t)", [so(lp["A"])] + [
        ("- " if lp["B"][j] >= 0 else "+ ") + so(abs(lp["B"][j])) + "".join(f"(t{dau}{l})" if l else "t" for l in range(j))
        for j in range(2, m)])
    t = lp["t"]
    rows = [[str(j), so(t[j]), se(h * abs(t[j] - t[j - 1]))] for j in range(1, len(t))]
    if rows:
        rows[-1][1] = ob(rows[-1][1])
    b_it = bang(["l", "t_l", r"h|t_l-t_{l-1}|"], rut_lap(rows)) if rows else ""
    la = len(t) - 1
    s = lp["s"]
    ghi = (f"Không đủ ${m_yc}$ mốc về một phía của khoảng nên dùng ${m}$ mốc. "
           if m_yc is not None and m_yc != m else "")
    doan_t = "[0;1]" if tien else "[-1;0]"
    if lp["hoi_tu"]:
        ket = (f"Dừng sau ${la}$ lần, $t_{{{la}}}\\in{doan_t}$: $\\bar x_{{{r}}}=x_{{{s}}}+t_{{{la}}}h={sl(x[s])}+"
               f"{sn(t[-1])}\\cdot{sl(h)}={so(lp['xbar'])}$.")
    elif lp.get("ngoai"):
        ket = (f"Dừng sau ${la}$ lần nhưng $t_{{{la}}}={so(t[-1])}\\notin{doan_t}$: nghiệm lặp nằm ngoài khoảng cách ly, "
               "bỏ (đổi số mốc $m$).")
    else:
        ket = (f"Sau $N={la}$ lần chưa đạt $h\\,|t_{{l+1}}-t_l|<\\varepsilon$: \\textbf{{không hội tụ}} "
               f"($x_{{{s}}}+t_{{{la}}}h={so(lp['xbar'])}$ chỉ để tham khảo).")
    if hon_hop and not gon:
        ghi = ("Đủ mốc bên phải nên lặp Newton tiến. " if tien else
               "Không đủ mốc bên phải nên lặp Newton lùi từ $x_{k+1}$. ") + ghi
    if gon:
        ghi = ((f"Đủ ${m}$ mốc bên phải nên lặp Newton tiến" if tien else
                f"Không đủ ${m}$ mốc bên phải nên lặp Newton lùi")
               + f", $t=\\dfrac{{x-x_{{{s}}}}}{{h}}=\\dfrac{{{x_tru(x[s])}}}{{{sl(h)}}}$. " + ghi)
        if r == 1 and len(rows) > 4:
            b_it += "\n\\goiy{bảng lặp chỉ ghi lần 1, 2, $\\vdots$, 2 lần cuối.}"
    KQ_19.append([f"({sl(x[k])};\\ {sl(x[k + 1])})", f"[{sl(x[idx[0]])};\\ {sl(x[idx[-1]])}]",
                  f"\\text{{lặp Newton {'tiến' if tien else 'lùi'} (từ }} x_{{{s}}}={sl(x[s])})",
                  so(lp["xbar"]) if lp["hoi_tu"] else
                  (r"\text{ngoài khoảng}" if lp.get("ngoai") else r"\text{không hội tụ}")])
    return L(r"""
\paragraph{Nghiệm @r@: $(x_{@k@};x_{@k1@})=(@xk@;\ @xk1@)$.} @ghi@Bảng sai phân:
@b_sp@
Thay các ô khung vào $\varphi$:
@phi@
$t_0=@t0@$:
@b_it@
@ket@
""", r=r, k=k, k1=k + 1, xk=sl(x[k]), xk1=sl(x[k + 1]), ghi=ghi, b_sp=b_sp, phi=phi, t0=so(t[0]), b_it=b_it, ket=ket)


def ket_luan_nghiem(yb, x, nghiem, tai_moc, cuoi=None):
    """Ket luan: so nghiem va gia tri. nghiem = [(gia tri, dung, k)] (dung = False: ham nguoc khong tin cay /
    lap khong hoi tu); tai_moc = cac moc la nghiem (g_i = 0)."""
    tot = sorted([(v, False) for v, ok, _ in nghiem if ok] + [(x[i], True) for i in tai_moc])
    hong = [k for _, ok, k in nghiem if not ok]
    doan = doan_ts(x)
    tong = len(nghiem) + len(tai_moc)
    if tong == 0:
        return f"$f(x)={sl(yb)}$ không có nghiệm trong ${doan}$ (không có khoảng cách ly)."
    them = ("" if not hong else " Nghiệm trong " + ", ".join(f"$({sl(x[k])};{sl(x[k + 1])})$" for k in hong)
            + " chưa tính được bằng phương pháp này (xem nhận xét ở trên).")
    if tong == 1 and tot:
        v, la_moc = tot[0]
        if la_moc:
            return f"$f(x)={sl(yb)}$ có đúng một nghiệm trong ${doan}$: $\\bar x={sl(v)}$ (mốc có $y_i=\\bar y$)."
        return (f"$f(x)={sl(yb)}$ có đúng một nghiệm trong ${doan}$: $\\bar x\\approx{so(v)}$"
                + (f" (số hạng cuối ${cuoi}$ — ước lượng sai số)." if cuoi else "."))
    if tong == 1:
        return f"$f(x)={sl(yb)}$ có đúng một nghiệm trong ${doan}$." + them
    s = f"$f(x)={sl(yb)}$ có ${tong}$ nghiệm trong ${doan}$"
    if tot:
        s += (": $\\bar x=" + vecl([v for v, _ in tot]) + "$" + (" (có nghiệm tại mốc)" if tai_moc else ""))
    return s + "." + them


def cau19():
    ten, sheet = ts("cau19", "file"), ts_so("cau19", "sheet", nguyen=True, nho_nhat=1)
    yb_a, yb_b = ts_so("cau19", "ybar_a"), ts_so("cau19", "ybar_b")
    m = ts_so("cau19", "m", nguyen=True, nho_nhat=2)
    eps = ts_so("cau19", "eps")
    N_lap = ts_so("cau19", "n", nguyen=True, nho_nhat=1)
    if eps <= 0:
        raise LoiDuLieu("eps phai > 0.")
    x, y, sk, B = doc_xy_bang(ten, sheet)
    n = len(x) - 1
    if n < 1:
        raise LoiDuLieu("can it nhat 2 moc.")
    h = nsn.cach_deu(x)
    sheet_, dau, trong = mo_dau_bang(B)
    cum = cau_loai(sk, lambda j: f"dòng {j}", B["day_x"], B["day_y"]) + cau_trung_sap(sk)
    moc = (mo_ta_luoi(x, h) if h is not None and n >= 2 else
           f"${len(x)}$ mốc $x={sl(x[0])};\\dots;{sl(x[-1])}$" + (", không cách đều" if h is None else f", $h={sl(h)}$"))
    V["c19_du_lieu"] = (f"\\texttt{{{tex_chu(ten)}}}{sheet_}{dau}{trong}" + (": " + "; ".join(cum) if cum else "")
                        + ". Ta có bảng dữ liệu gồm " + moc + f" và các giá trị cho trước $\\bar y={sl(yb_a)}$ (câu a), "
                        f"$\\bar y={sl(yb_b)}$ (câu b).")
    KQ_19.clear()
    doan = nsn.khoang_don_dieu(y)
    doi = [b for _, b, _ in doan[:-1]]
    V["c19_doi"] = (r"$\Delta y_i=y_{i+1}-y_i$ đổi dấu tại $i=" + ",".join(str(b) for b in doi) + "$" if doi else
                    r"$\Delta y_i=y_{i+1}-y_i$ không đổi dấu (một đoạn đơn điệu)")
    V["c19_dd"] = bang_don_dieu(x, y, doan)
    dl = max([v for v in (nsn.so_le(y), nsn.so_le([yb_a]), nsn.so_le([yb_b])) if v is not None] or [0])
    rows, kh_, moc_ = [], {}, {}
    for yb in (yb_a, yb_b):
        tai_moc, kh = nsn.khoang_cach_ly(y, yb)
        kh_[yb], moc_[yb] = kh, tai_moc
        for k in kh:
            a_, b_, s_ = next(dd for dd in doan if dd[0] <= k < dd[1])
            rows.append([sl(yb), str(k), f"({sl(x[k])};\\ {sl(x[k + 1])})", sd(y[k] - yb, dl), sd(y[k + 1] - yb, dl),
                         f"[{sl(x[a_])};\\ {sl(x[b_])}]\\ \\text{{{CHIEU[s_]}}}"])
    tm = [(yb, i) for yb in (yb_a, yb_b) for i in moc_[yb]]
    V["c19_g0"] = (", không có $g_i=0$" if not tm else
                   "; $g_i=0$ (mốc là nghiệm) tại " + ", ".join(f"$x_{{{i}}}={sl(x[i])}$ ($\\bar y={sl(yb)}$)"
                                                             for yb, i in tm))
    V["c19_cl"] = (bang([r"\bar y", "k", r"(x_k;x_{k+1})", r"g_k=y_k-\bar y", "g_{k+1}", r"\text{nằm trong đoạn}"], rows)
                   if rows else "Không có khoảng cách ly nào.")
    # a) ham nguoc
    V["c19a_yb"] = sl(yb_a)
    khoi, nghiem, cuoi = [], [], []
    for r, k in enumerate(kh_[yb_a], 1):
        dd = next(dd for dd in doan if dd[0] <= k < dd[1])
        mo = (f"Nghiệm trong $(x_{{{k}}};x_{{{k + 1}}})=({sl(x[k])};\\ {sl(x[k + 1])})\\subset"
              f"[{sl(x[dd[0]])};\\ {sl(x[dd[1]])}]$, đoạn {CHIEU[dd[2]]} nên có hàm ngược.")
        if len(kh_[yb_a]) > 1:
            mo = f"\\paragraph{{Nghiệm {r}.}} " + mo
        s, xv, c_ = khoi_ham_nguoc(x, y, yb_a, k, dd, m, mo, r == 1)
        khoi.append(s)
        nghiem.append(xv)
        cuoi.append(c_)
    V["c19a_khoi"] = "\n\n".join(khoi) if khoi else "Không có khoảng cách ly nên không giải."
    V["c19a_bang_kq"] = bang_kq_19(x)
    V["c19a_kl"] = ket_luan_nghiem(yb_a, x, nghiem, moc_[yb_a], se(cuoi[0]) if len(cuoi) == 1 else None)
    # b) lap (moc cach deu; khong cach deu -> 18d Buoc 0: ham nguoc)
    V["c19b_yb"] = sl(yb_b)
    kh = kh_[yb_b]
    nghiem = []
    if h is None:
        khoi = ["Mốc không cách đều nên theo 18d (Bước 0) dùng phương pháp hàm ngược (18c):"]
        for r, k in enumerate(kh, 1):
            dd = next(dd for dd in doan if dd[0] <= k < dd[1])
            mo = (f"\\paragraph{{Nghiệm {r}.}} Nghiệm trong $(x_{{{k}}};x_{{{k + 1}}})=({sl(x[k])};\\ {sl(x[k + 1])})"
                  f"\\subset[{sl(x[dd[0]])};\\ {sl(x[dd[1]])}]$, đoạn {CHIEU[dd[2]]} nên có hàm ngược.")
            s, xv, _ = khoi_ham_nguoc(x, y, yb_b, k, dd, m, mo, r == 1)
            khoi.append(s)
            nghiem.append(xv)
        V["c19b_cong_thuc"], V["c19b_khoi"] = "", "\n\n".join(khoi)
    else:
        d = nsn.so_le(y)
        lps = [nsn.lap(x, y, yb_b, k, h, m, eps, N_lap) for k in kh]
        V["c19b_cong_thuc"] = cong_thuc_lap(lps[0]["m"] if lps else m, eps, {lp["huong"] for lp in lps}) if lps else ""
        khoi = []
        hon_hop = len({lp["huong"] for lp in lps}) > 1
        for r, (k, lp) in enumerate(zip(kh, lps), 1):
            khoi.append(khoi_lap(x, y, yb_b, k, r, lp, h, d, hon_hop, m))
            nghiem.append((lp["xbar"], lp["hoi_tu"], k))
            KT[f"c19 lap k={k}: |y(xbar) - ybar|"] = abs(nsn.y_tai(x, y, lp["xbar"], m) - yb_b)
        V["c19b_khoi"] = "\n".join(khoi) if khoi else "Không có khoảng cách ly nên không giải."
        if any(not lp["hoi_tu"] for lp in lps):
            print("  Canh bao: Cau 19b co nghiem lap khong hoi tu (tang N hoac doi m).")
    V["c19b_bang_kq"] = bang_kq_19(x)
    V["c19b_kl"] = ket_luan_nghiem(yb_b, x, nghiem, moc_[yb_b])


# ===== CAU 21 =====

def ten_dk(dk, x):
    """Dieu kien bien -> LaTeX: '$S'(0)=0$', '$S''(0)=-1$, $S''(3.1416)=1$', '$S'(0)=S'(3.1416)=0$'."""
    if len(dk) == 2 and dk[0][0] == dk[1][0] and dk[0][2] == dk[1][2] and dk[0][1] != dk[1][1]:
        r = dk[0][0]
        return f"${dh('S', r)}({sl(x[dk[0][1]])})={dh('S', r)}({sl(x[dk[1][1]])})={sl(dk[0][2])}$"
    return ", ".join(f"${dh('S', r)}({sl(x[k])})={sl(v)}$" for r, k, v in dk)


def he_so_bac3(x, y, sg):
    n = len(x) - 1
    he = []
    for k in range(n):
        hk = x[k + 1] - x[k]
        s = (y[k + 1] - y[k]) / hk
        a = (sg[k + 1] - sg[k]) / (6 * hk)
        b = (sg[k] * x[k + 1] - sg[k + 1] * x[k]) / (2 * hk)
        c = (-sg[k] * x[k + 1] ** 2 + sg[k + 1] * x[k] ** 2) / (2 * hk) + s - (sg[k + 1] - sg[k]) * hk / 6
        d = ((sg[k] * x[k + 1] ** 3 - sg[k + 1] * x[k] ** 3) / (6 * hk)
             + (y[k] * x[k + 1] - y[k + 1] * x[k]) / hk + (sg[k + 1] * x[k] - sg[k] * x[k + 1]) * hk / 6)
        he.append([a, b, c, d])
    return he


def hang_bien(r, k, v, x, n, kieu):
    """Mo ta hang bien cua he sigma (spline cap 3). kieu 'gon' (trong 'hang bien: ...') / 'muc' (1 dong itemize)."""
    ni = chi(n)
    if r == 2:
        mo = (f"$\\sigma_0={sl(v)}$ ($d_0=1$, $u_0=0$, $r_0={sl(v)}$)" if k == 0 else
              f"$\\sigma_{ni}={sl(v)}$ ($\\ell_{ni}=0$, $d_{ni}=1$, $r_{ni}={sl(v)}$)")
        return (f"${dh('S', 2)}({sl(x[k])})={sl(v)}$: " + mo) if kieu == "muc" else mo
    n1 = chi(n - 1)
    if k == 0:
        vp = f"s_0-{sl(v)}" if v >= 0 else f"s_0-({sl(v)})"
        rr = "s_0" if v == 0 else (f"s_0-{sl(v)}" if v > 0 else f"s_0+{sl(-v)}")
        mo = (f"${dh('S', 1)}({sl(x[0])})={sl(v)}$: $\\dfrac{{h_0}}{{3}}\\sigma_0+\\dfrac{{h_0}}{{6}}\\sigma_1={vp}$ \\ "
              f"($d_0=\\frac{{h_0}}{{3}}$, $u_0=\\frac{{h_0}}{{6}}$, $r_0={rr}$)")
    else:
        vp = f"{sl(v)}-s_{n1}"
        rr = f"-s_{n1}" if v == 0 else f"{sl(v)}-s_{n1}"
        mo = (f"${dh('S', 1)}({sl(x[n])})={sl(v)}$: $\\dfrac{{h_{n1}}}{{6}}\\sigma_{n1}+\\dfrac{{h_{n1}}}{{3}}\\sigma_{ni}"
              f"={vp}$ \\ ($\\ell_{ni}=\\frac{{h_{n1}}}{{6}}$, $d_{ni}=\\frac{{h_{n1}}}{{3}}$, $r_{ni}={rr}$)")
    return mo


def spline_cau(nhan, p, x, y, dk, dau_bac3):
    """Than 1 y cua Cau 21. dau_bac3: None neu day la spline cap 3 dau tien (viet du cong thuc), nguoc lai nhan
    y cap 3 dau tien (vd 'b') de dan chieu."""
    n = len(x) - 1
    ni = chi(n)

    def bang_he(he, bac):
        ten = "abcd"[:bac + 1]
        return bang(["k", r"[x_k;x_{k+1}]"] + [f"{t}_k" for t in ten],
                    [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]"] + [so(v) for v in he[k]] for k in range(n)])

    def ham(he):
        dong = [f"S_{{{k}}}(x) &= " + " ".join(hang_tu(he[k])) + f",\\quad x\\in[{sl(x[k])};\\ {sl(x[k + 1])}]"
                for k in range(n)]
        return "\\begin{align*}\n" + " \\\\\n".join(dong) + "\n\\end{align*}"

    if p == 2:
        r0, k0, v0 = dk[0]
        g, m_, he = sp.spline2(x, y, dk)
        if k0 == 0:
            ct = (f"$m_0=S'({sl(x[0])})={sl(v0)}$, $m_{{k+1}}=\\gamma_k-m_k$, "
                  r"$\gamma_k=\dfrac{2(y_{k+1}-y_k)}{h_k}$;")
            bm = bang(["k", r"\gamma_k=\frac{2(y_{k+1}-y_k)}{h_k}", r"m_{k+1}=\gamma_k-m_k"],
                      [[str(k), so(g[k]), so(m_[k + 1])] for k in range(n)])
        else:
            ct = (f"$m_{ni}=S'({sl(x[n])})={sl(v0)}$, $m_k=\\gamma_k-m_{{k+1}}$, "
                  r"$\gamma_k=\dfrac{2(y_{k+1}-y_k)}{h_k}$;")
            bm = bang(["k", r"\gamma_k=\frac{2(y_{k+1}-y_k)}{h_k}", r"m_k=\gamma_k-m_{k+1}"],
                      [[str(k), so(g[k]), so(m_[k])] for k in range(n - 1, -1, -1)])
        KT[f"c21{nhan} bac 2: noi suy"] = max(abs(np.polyval(he[k], x[k + 1]) - y[k + 1]) for k in range(n))
        return L(r"""\pp{Phương pháp} (spline cấp 2, Câu 20b). Trên $[x_k;x_{k+1}]$, $S_k$ bậc 2 qua $(x_k,y_k)$, $(x_{k+1},y_{k+1})$ và $S'$ liên tục nên $m_k+m_{k+1}=\gamma_k$, $m_k=S'(x_k)$; điều kiện biên cho $m$ đầu tiên: @ct@
\[ a_k=\frac{m_{k+1}-m_k}{2h_k},\qquad b_k=\frac{m_kx_{k+1}-m_{k+1}x_k}{h_k},\qquad c_k=\frac{m_{k+1}x_k^2-m_kx_{k+1}^2}{2h_k}+y_k+\frac{m_kh_k}{2}. \]
@bm@
\pp{Hệ số} $S_k(x)=a_kx^2+b_kx+c_k$:
@he@
\begin{ketluan}
@S@
\end{ketluan}""", ct=ct, bm=bm, he=bang_he(he, 2), S=ham(he))
    # p = 3
    cung_dau = dk[0][1] == dk[1][1]
    trong = (f"hàng $i={ds_chi_so(1, n - 1)}$ (trơn tại $x_i$): $\\ell_i=\\dfrac{{h_{{i-1}}}}{{6}}$, "
             r"$d_i=\dfrac{h_{i-1}+h_i}{3}$, $u_i=\dfrac{h_i}{6}$, $r_i=s_i-s_{i-1}$;") if n >= 2 else ""
    if cung_dau:
        M, rhs, _, Dn, _ = sp.spline_tq(x, y, 3, dk)
        sg = [Dn[k][2] for k in range(n + 1)]
        he = he_so_bac3(x, y, sg)
        ve = "\n".join(f"\\item {hang_bien(r, k, v, x, n, 'muc')};" for r, k, v in dk)
        than = (f"\\pp{{Lập hệ}} theo $\\sigma_k=S''(x_k)$: hai điều kiện biên cùng ở $x_{{{0 if dk[0][1] == 0 else n}}}$ "
                "nên hệ không có dạng ba đường chéo; giải bằng khử Gauss chọn trụ (20b, Bước 4):\n\\begin{itemize}\n"
                + (f"\\item {trong}\n" if trong else "") + ve + "\n\\end{itemize}\n"
                + bang(["i", r"\sigma_i"], [[str(i), ob(so(sg[i]))] for i in range(n + 1)]))
        duoi = ""
    else:
        hh, s, (Lr, Dg, U, R), P, Q, sg, he = sp.spline3(x, y, dk)
        duoi = bang(["i", r"\ell_i", "d_i", "u_i", "r_i", "P_i", "Q_i", r"\sigma_i"],
                    [[str(i), so(Lr[i]), so(Dg[i]), so(U[i]), so(R[i]), so(P[i]), so(Q[i]), ob(so(sg[i]))]
                     for i in range(n + 1)])
        if dau_bac3 is None:
            bien = r"; \ ".join(hang_bien(r, k, v, x, n, "gon") for r, k, v in dk)
            than = L(r"""\pp{Phương pháp} (spline cấp 3, Câu 20a). Ẩn $\sigma_k=S''(x_k)$; trơn cấp 1 tại các mốc trong (phương trình khung, Câu 20a) và 2 điều kiện biên cho hệ ba đường chéo, giải bằng truy đuổi; có $\sigma_k$ thì tính hệ số chính tắc của từng $S_k$.

\pp{Lập hệ} theo $\sigma_k=S''(x_k)$: $\ell_i\sigma_{i-1}+d_i\sigma_i+u_i\sigma_{i+1}=r_i$, $i=0,\dots,@n@$:
\begin{itemize}
@trong@\item hàng biên: @bien@.
\end{itemize}
\pp{Giải hệ bằng truy đuổi:}
\begin{gather*}
P_0=-\frac{u_0}{d_0},\quad Q_0=\frac{r_0}{d_0};\qquad P_i=\frac{-u_i}{d_i+\ell_iP_{i-1}},\quad Q_i=\frac{r_i-\ell_iQ_{i-1}}{d_i+\ell_iP_{i-1}}\ \ (i=1,\dots,@n@);\\
\sigma_@ni@=Q_@ni@,\qquad \sigma_i=P_i\sigma_{i+1}+Q_i\ \ (i=@n1@,\dots,0).
\end{gather*}
@duoi@
\pp{Hệ số chính tắc} $S_k(x)=a_kx^3+b_kx^2+c_kx+d_k$ trên $[x_k;x_{k+1}]$:
\begin{gather*}
a_k=\frac{\sigma_{k+1}-\sigma_k}{6h_k},\qquad b_k=\frac{\sigma_kx_{k+1}-\sigma_{k+1}x_k}{2h_k},\qquad c_k=\frac{\sigma_{k+1}x_k^2-\sigma_kx_{k+1}^2}{2h_k}+s_k-\frac{(\sigma_{k+1}-\sigma_k)h_k}{6},\\
d_k=\frac{\sigma_kx_{k+1}^3-\sigma_{k+1}x_k^3}{6h_k}+\frac{y_kx_{k+1}-y_{k+1}x_k}{h_k}+\frac{(\sigma_{k+1}x_k-\sigma_kx_{k+1})h_k}{6}.
\end{gather*}""", n=n, ni=ni, n1=n - 1, trong=(f"\\item {trong}\n" if trong else ""), bien=bien, duoi=duoi)
            duoi = ""
        else:
            loai_r = {r for r, _, _ in dk}
            theo = "$S'$" if loai_r == {1} else "$S''$" if loai_r == {2} else "điều kiện biên"
            muc = [hang_bien(r, k, v, x, n, "muc") for r, k, v in dk]
            than = ((f"\\pp{{Lập hệ:}} hàng $i={ds_chi_so(1, n - 1)}$ giữ nguyên ($\\ell_i$, $d_i$, $u_i$, $r_i$ ở câu "
                     f"{dau_bac3}); hàng biên đổi theo {theo}:\n" if n >= 2 else
                     f"\\pp{{Lập hệ:}} hàng biên đổi theo {theo}:\n")
                    + "\\begin{itemize}\n" + "\n".join(f"\\item {t}" + (";" if i < len(muc) - 1 else ".")
                                                       for i, t in enumerate(muc))
                    + f"\n\\end{{itemize}}\nTruy đuổi và hệ số chính tắc theo công thức ở câu {dau_bac3}:")
    from scipy.interpolate import CubicSpline
    if not cung_dau:
        cs = CubicSpline(x, y, bc_type=((dk[0][0], dk[0][2]), (dk[1][0], dk[1][2])))
        KT[f"c21{nhan}: sigma vs scipy"] = float(np.max(np.abs(cs(x, 2) - np.array(sg))))
    return than + "\n" + (duoi + "\n" if duoi else "") + bang_he(he, 3) + "\n\\begin{ketluan}\n" + ham(he) \
        + "\n\\end{ketluan}"


def cau21():
    du = {}
    for nhan in "abc":
        ten = ts("cau21", "file_" + nhan)
        dong = doc_tra_loi(ten)
        p = mot_so(dong[0], "bac p", nguyen=True)
        if p not in (2, 3):
            raise LoiDuLieu(f"{ten}: loi giai Cau 21 trinh bay spline cap 2 hoac 3 (file cho p = {p}).")
        ox = nw.bo_nhan(nw.tach_o(dong_thu(dong, 1, "x", ten)))
        oy = nw.bo_nhan(nw.tach_o(dong_thu(dong, 2, "y", ten)))
        x, y, sk = lam_sach(ox, oy, kieu="spline")
        if len(x) < 2:
            raise LoiDuLieu(f"{ten}: can it nhat 2 moc.")
        bao = []
        try:
            dk = sp.doc_bien(dong_thu(dong, 3, "dieu kien bien", ten), x, p, bao)
        except ValueError as e:
            raise LoiDuLieu(f"{ten}: {e}")
        du[nhan] = (ten, p, x, y, sk, dk)
    ten, _, x, y, sk, _ = du["a"]
    for nhan in "bc":
        if du[nhan][2] != x or du[nhan][3] != y:
            raise LoiDuLieu(f"x, y trong {du[nhan][0]} khac {ten}: 3 file Cau 21 phai cung 1 bang du lieu.")
    n = len(x) - 1
    hk = [x[k + 1] - x[k] for k in range(n)]
    nguoc = [(sk["goc"][i], sk["goc"][i - 1]) for i in range(1, len(sk["goc"])) if sk["goc"][i][0] < sk["goc"][i - 1][0]]
    cum = cau_loai(sk, lambda j: f"cặp thứ {j}")
    if nguoc:
        cum.append("bảng đề cho $x$ \\textbf{không tăng dần} (" + ", ".join(
            f"cặp $({sl(a[0])};{sl(a[1])})$ đứng sau $({sl(b[0])};{sl(b[1])})$" for a, b in nguoc) + "), sắp lại theo $x$")
    ct = r"$h_k=x_{k+1}-x_k$, $s_k=\frac{y_{k+1}-y_k}{h_k}$:"
    if cum:
        V["c21_du_lieu"] = r"\pp{Xử lý dữ liệu.} " + "; ".join(c[0].upper() + c[1:] if i == 0 else c
                                                             for i, c in enumerate(cum)) + "; " + ct
    else:
        V["c21_du_lieu"] = r"\pp{Dữ liệu.} " + ct
    V["c21_xy"] = bang(["i"] + [str(i) for i in range(n + 1)], [["x_i"] + [sl(t) for t in x], ["y_i"] + [sl(t) for t in y]])
    V["c21_h"] = bang(["k", r"[x_k;x_{k+1}]", "h_k", r"s_k=\frac{y_{k+1}-y_k}{h_k}"],
                      [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]", so(hk[k]), so((y[k + 1] - y[k]) / hk[k])]
                       for k in range(n)])
    dau_bac3 = None
    for nhan in "abc":
        _, p, _, _, _, dk = du[nhan]
        V[f"c21{nhan}_tieu_de"] = f"Spline cấp {p} với {ten_dk(dk, x)}"
        ghi_chu = ts("cau21", "ghi_chu_" + nhan)
        de = f"\\pp{{Đề.}} {ghi_chu}\n\n" if ghi_chu else ""
        V[f"c21{nhan}_than"] = de + spline_cau(nhan, p, x, y, dk, dau_bac3)
        if p == 3 and dau_bac3 is None:
            dau_bac3 = nhan


# ===== CAU 23: BINH PHUONG TOI THIEU THEO FORM DAP AN GIUA KY 20251 =====
# Ham co so viet dang (p, f): x^p nhan cac ham trong f ('cos', 'ln'); vd (1, ()) = x, (-1, ()) = 1/x, (0, ('cos',)) = cos x.

def gia_tri_co_so(p, f, x):
    v = np.asarray(x, dtype=float) ** p
    for q in f:
        v = v * (np.cos(x) if q == "cos" else np.log(x))
    return v


def ten_ham(p, f, bien="x"):
    """Ten LaTeX ham co so: 1, x, x^2, \\frac{1}{x}, \\cos x, \\ln x (bien = 'x_i' khi viet tai moc)."""
    phu = "".join(rf"\{q} {bien}" for q in f)
    if p < 0:
        return rf"\frac{{1}}{{{bien}}}" if p == -1 else rf"\frac{{1}}{{{bien}^{{{-p}}}}}"
    xp = "" if p == 0 else (bien if p == 1 else f"{bien}^{{{p}}}")
    return (xp + phu) or "1"


def ten_tong(p, f, w=None):
    """Ten tong sum_i x_i^p * f(x_i) * w_i ('n' neu la tong cua 1): \\sum x_i^2, \\sum\\frac{Y_i}{x_i}, ..."""
    dem = {}
    for q in f:
        dem[q] = dem.get(q, 0) + 1
    phu = "".join((rf"\{q} x_i" if k == 1 else (rf"\cos^{k}x_i" if q == "cos" else rf"(\ln x_i)^{k}"))
                  for q, k in sorted(dem.items()))
    wi = f"{w}_i" if w else ""
    if p < 0:
        mau = "x_i" if p == -1 else f"x_i^{{{-p}}}"
        return rf"\sum\frac{{{(wi + phu) or '1'}}}{{{mau}}}"
    xp = "" if p == 0 else ("x_i" if p == 1 else f"x_i^{{{p}}}")
    return "n" if not (xp + wi + phu) else r"\sum " + xp + wi + phu


def hang_S(an, p, f):
    """So hang 'tham so * co so tai x_i' trong S: a x_i, \\frac{b}{x_i}, c\\cos x_i, A."""
    if p == 0 and not f:
        return an
    if p < 0:
        return rf"\frac{{{an}}}{{{'x_i' if p == -1 else f'x_i^{{{-p}}}'}}}"
    return an + ten_ham(p, f, "x_i")


def ma_tran(o):
    return r"\begin{bmatrix}" + r"\\".join("&".join(h) for h in o) + r"\end{bmatrix}"


def tong_hop_so(he, cs, bien="x", nhan_a=""):
    """'1.998874x-\\frac{3.004924}{x}', '2.000101x^{2}-2.999001\\cos x+1.004497' (he so * co so, bo he so 1)."""
    s = ""
    for v, (p, f) in zip(he, cs):
        a = so(abs(v))
        if p < 0:
            t = rf"\frac{{{a}}}{{{ten_ham(-p, (), bien)}}}"
        elif p == 0 and not f:
            t = a
        else:
            t = ("" if a == "1" else a + ("\\," if "cdot" in a or f else "")) + ten_ham(p, f, bien)
        s += ("-" if v < 0 else ("+" if s else "")) + t
    return s


def bptt_y(x, y, cs, an, dang="tt", nhan=True, chi_so=None):
    """1 y BPTT theo form dap an. cs: co so [(p, f)]; an: ten tham so.
    dang 'tt': y = sum an_j phi_j (tuyen tinh theo tham so); 'mu': y = a e^{sum b_j phi_j} (cs khong ke ham 1, an = [b, c]);
    'luy': y = a x^b (cs = [(0, ('ln',))], an = ['b']). nhan: co nhan 'Phuong phap.' / 'Tinh toan.';
    chi_so: None -> diem bi loai ghi theo x; so -> ghi y_i voi chi so bat dau tu chi_so (nhu dap an: y_102 = 0.0169).
    Tra ve (than LaTeX, he so, sigma)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    N0 = len(y)
    idx0 = np.arange(N0)
    pp, tinh = [], []
    loai_y = []
    s, Sy, Sx = 1.0, 0.0, 0.0
    if dang in ("mu", "luy"):
        if dang == "luy":
            _, giu, Sx = bp.xu_ly_dau(x, 1.0)
            if not giu.all():
                loai_y.append(("x", x[~giu], y[~giu], idx0[~giu]))
                x, y, idx0 = x[giu], y[giu], idx0[giu]
        s, giu, Sy = bp.xu_ly_dau(y)
        if not giu.all():
            loai_y.append(("y", x[~giu], y[~giu], idx0[~giu]))
            x, y, idx0 = x[giu], y[giu], idx0[giu]
    n = len(y)
    lon = ">" if s > 0 else "<"
    if dang == "tt":
        cs_d, an_d, w = list(cs), list(an), "y"
        off = 0 if cs[0] == (0, ()) else 1           # chi so phi bat dau tu 0 khi co so dau la ham 1 (nhu dap an)
        pp.append("Hàm cần tìm tuyến tính theo các tham số " + ", ".join(f"${a}$" for a in an) + " với hệ hàm cơ sở "
                  + ", ".join(f"$\\varphi_{{{j + off}}}(x)={ten_ham(p, f)}$" for j, (p, f) in enumerate(cs))
                  + ":\n\\[ y=" + "+".join(f"{a}\\varphi_{{{j + off}}}(x)" for j, a in enumerate(an)) + ". \\]")
    else:
        off = 0
        bx = (f"(x+{sl(Sx)})" if Sx else "x")
        E = ("+".join(hang_S(a, p, f).replace("x_i", "x") for a, (p, f) in zip(an, cs)) if dang == "mu" else None)
        mo_hinh = f"a\\,e^{{{E}}}" if dang == "mu" else f"a\\,{bx}^{{b}}"
        mo_hinh_dau = f"(-a)\\,e^{{{E}}}" if dang == "mu" else f"(-a)\\,{bx}^{{b}}"
        ln_mh = f"\\ln\\Big(e^{{{E}}}\\Big)" if dang == "mu" else f"\\ln\\big({bx}^{{b}}\\big)"
        mu_ = E if dang == "mu" else f"b\\ln {bx}"
        S_ = sl(abs(Sy))
        lhs = "y" if not Sy else (f"y+{S_}" if Sy > 0 else f"y-{S_}")
        ve = ("y" if s > 0 else "-y") if not Sy else (f"y+{S_}" if s > 0 else f"{S_}-y")
        a_s = "a" if s > 0 else "-a"
        so_dau = int(np.sum(s * y > 0))
        lay_ln = "lấy logarit tự nhiên hai vế:" if s > 0 else "ta nhân hai vế với $-1$ rồi lấy logarit:"
        if Sy:
            q = int(np.sum(s * y <= 0))
            sai_dau = r"y_i\le0" if s > 0 else r"y_i\ge0"
            cuc = f"nhỏ nhất bằng ${sl(y.min())}$" if s > 0 else f"lớn nhất bằng ${sl(y.max())}$"
            mo = (f"Dữ liệu có ${q}$ mốc ${sai_dau}$ ({cuc}) nên chưa lấy logarit được. Ta tịnh tiến dữ liệu "
                  f"{'lên' if s > 0 else 'xuống'} ${S_}$ đơn vị, tức tìm ${lhs}={mo_hinh}$ (khi đó "
                  f"${lhs.replace('y', 'y_i')}{lon}0$ với mọi $i$ và $a{lon}0$), "
                  + ("rồi lấy logarit tự nhiên hai vế:" if s > 0 else "nhân hai vế với $-1$ rồi lấy logarit:"))
        elif any(t[0] == "y" for t in loai_y):
            mo = (f"Do ${so_dau}$ mốc mang dấu {'dương' if s > 0 else 'âm'} ($y_i{lon}0\\Longrightarrow a{lon}0$), "
                  + lay_ln)
        else:
            mo = f"Mọi $y_i{lon}0$ nên $a{lon}0$, " + lay_ln
        if dang == "luy":
            if Sx:
                mo = (f"Có mốc $x_i\\le0$ (nhỏ nhất bằng ${sl(x.min())}$) nên tịnh tiến $x$ lên ${sl(Sx)}$ đơn vị, "
                      f"tìm $y=a{bx}^b$. ") + mo
            elif not any(t[0] == "x" for t in loai_y):
                mo = "Mọi $x_i>0$. " + mo
        dong = [f"{lhs}&={mo_hinh}"]
        if s < 0:
            dong.append(f"\\iff {ve}&={mo_hinh_dau}")
        ln_ve = f"\\ln {ve}" if ve == "y" else f"\\ln({ve})"
        ln_a = f"\\ln {a_s}" if a_s == "a" else f"\\ln({a_s})"
        dong += [f"\\iff {ln_ve}&={ln_a}+{ln_mh}", f"\\iff {ln_ve}&={ln_a}+{mu_}."]
        cs_d = [(0, ())] + ([(0, ("ln",))] if dang == "luy" else list(cs))
        an_d = ["A"] + list(an)
        w = "Y"
        phi = ", ".join(f"$\\varphi_{{{j}}}(x)={ten_ham(p, f).replace('x', bx) if dang == 'luy' and j else ten_ham(p, f)}$"
                        for j, (p, f) in enumerate(cs_d))
        pp.append(mo + "\n\\begin{align*}\n" + "\\\\\n".join(dong) + "\n\\end{align*}\n"
                  + f"Đặt $Y={ln_ve}$, $A={ln_a}$ ($\\Longrightarrow a={'' if s > 0 else '-'}e^A$) và hệ hàm "
                  f"cơ sở {phi}. Ta đưa được về dạng tuyến tính theo các tham số $({','.join(an_d)})$:\n"
                  "\\[ Y=" + "+".join(f"{a}\\varphi_{{{j}}}(x)" for j, a in enumerate(an_d)) + ". \\]")
    # S, he chuan dang ky hieu
    so_hang = "+".join(hang_S(a, p, f) for a, (p, f) in zip(an_d, cs_d)).replace("+-", "-")
    if dang == "luy" and Sx:
        so_hang = so_hang.replace("x_i", f"(x_i+{sl(Sx)})")
    pp.append(f"Đặt hàm tổng bình phương sai lệch:\n\\[ S({','.join(an_d)})=\\sum_{{i=1}}^{{n}}\\Big({so_hang}-{w}_i\\Big)^2"
              f"\\to\\min. \\]")
    m = len(cs_d)
    M_ky = [[ten_tong(cs_d[j][0] + cs_d[k][0], cs_d[j][1] + cs_d[k][1]) for k in range(m)] for j in range(m)]
    d_ky = [ten_tong(p, f, w) for p, f in cs_d]
    if dang == "luy" and Sx:
        M_ky = [[t.replace("x_i", f"(x_i+{sl(Sx)})") for t in h] for h in M_ky]
        d_ky = [t.replace("x_i", f"(x_i+{sl(Sx)})") for t in d_ky]
    dk = ", ".join(f"$\\dfrac{{\\partial S}}{{\\partial {a}}}=0$" for a in an_d)
    luu_y = []                                     # tich hai co so rut gon (vd x * 1/x = 1) nhu dap an
    for j in range(m):
        for k in range(j + 1, m):
            (pj, fj), (pk, fk) = cs_d[j], cs_d[k]
            if pj * pk < 0 and not fj and not fk:
                luu_y.append(f"$\\varphi_{{{j + off}}}(x_i)\\varphi_{{{k + off}}}(x_i)={ten_ham(pj, (), 'x_i')}\\cdot"
                             f"{ten_ham(pk, (), 'x_i')}={ten_ham(pj + pk, (), 'x_i')}$")
    pp.append(f"Từ điều kiện cực trị {dk}, ta thu được hệ phương trình $(\\Phi^T\\Phi)\\theta=\\Phi^T{w}$:\n"
              f"\\[ {ma_tran(M_ky)}{ma_tran([[a] for a in an_d])}={ma_tran([[t] for t in d_ky])} \\]"
              + (f"\n(lưu ý {', '.join(luu_y)})." if luu_y else ""))
    # Tinh toan
    if dang == "tt":
        Phi = np.column_stack([gia_tri_co_so(p, f, x) for p, f in cs_d])
        he, M, d, _, g, sigma = bp.bptt(Phi, y)
        z = y
    else:
        X = x + Sx
        Phi = np.column_stack([gia_tri_co_so(p, f, X) for p, f in cs_d])
        he, M, d, _, z, gY, _, _ = bp.tuyen_tinh_hoa(Phi, y + Sy, s)
        g = gY - Sy
        sigma = float(np.sqrt(np.mean((g - y) ** 2)))
    KT[f"bptt {dang}: he so vs lstsq"] = float(np.max(np.abs(np.array(he) - np.linalg.lstsq(Phi, z, rcond=None)[0])))
    for t, xv, yv, iv in loai_y:
        if chi_so is None:
            ds_ = "; ".join(f"$x={sl(a)}$: $y={sl(b)}$" for a, b in list(zip(xv, yv))[:6]) + ("; …" if len(xv) > 6 else "")
            ly = "$x_i\\le0$" if t == "x" else ("$y_i\\le0$" if s > 0 else "$y_i\\ge0$")
            tinh.append(f"Trong ${N0}$ mốc dữ liệu có ${len(xv)}$ mốc {ly} ({ds_}) nên không lấy logarit được, loại bỏ.")
            continue
        q = len(iv)                                # nhu dap an: '2 moc cuoi duong y_102 = 0.0169, y_103 = 0.0091'
        vt = " cuối" if list(iv) == list(range(N0 - q, N0)) else " đầu" if list(iv) == list(range(q)) else ""
        v_ = xv if t == "x" else yv
        if t == "x":
            loai = "có $x\\le0$"
        elif s < 0:
            loai = "dương" if np.all(yv > 0) else "không âm"
        else:
            loai = "âm" if np.all(yv < 0) else "không dương"
        ds_ = ", ".join(f"${t}_{{{i + chi_so}}}={sl(v)}$" for i, v in list(zip(iv, v_))[:6]) + (", …" if q > 6 else "")
        tinh.append(f"Trong ${N0}$ mốc dữ liệu có ${q}$ mốc{vt} {loai} {ds_} nên không lấy logarit, loại bỏ.")
    tong = {}
    for j in range(m):
        for k in range(j, m):
            tong.setdefault(M_ky[j][k], M[j][k])
    for j in range(m):
        tong.setdefault(d_ky[j], d[j])
    tong.pop("n", None)
    muc = [f"{t}&={so(v)}" for t, v in tong.items()]
    hang3 = [", & ".join(muc[i:i + 3]) for i in range(0, len(muc), 3)]
    tinh.append(f"Trên $n={n}$ mốc ta có các tính toán:\n\\begin{{align*}}\n" + ",\\\\\n".join(hang3)
                + ".\n\\end{align*}")
    so_M = [[so(v) for v in h] for h in M]
    tinh.append("Thay vào hệ phương trình chuẩn:\n"
                f"\\[ {ma_tran(so_M)}{ma_tran([[a] for a in an_d])}={ma_tran([[so(v)] for v in d])}. \\]")
    if dang == "tt":
        nghiem = ",\\qquad ".join(f"{a}={so(v)}" for a, v in zip(an_d, he))
        g_tex = tong_hop_so(he, cs_d)
        a_v = None
    else:
        a_v = s * math.exp(he[0])
        nghiem = (f"A={so(he[0])}\\ \\Longrightarrow\\ a={'' if s > 0 else '-'}e^A={so(a_v)},\\qquad "
                  + ",\\qquad ".join(f"{a}={so(v)}" for a, v in zip(an_d[1:], he[1:])))
        if dang == "mu":
            g_tex = f"{so(a_v)}\\,e^{{{tong_hop_so(he[1:], cs)}}}"
        else:
            g_tex = f"{so(a_v)}\\,{'x' if not Sx else f'(x+{sl(Sx)})'}^{{{so(he[1])}}}"
        if Sy:
            g_tex += f"{'-' if Sy > 0 else '+'}{sl(abs(Sy))}"
    tinh.append(f"Giải hệ phương trình trên ta được:\n\\[ {nghiem}. \\]")
    tinh.append(f"Vậy hàm thực nghiệm cần tìm là:\n\\[ y=g(x)={g_tex}. \\]")
    ban_dau = " (tính trên $y_i$ ban đầu)" if dang != "tt" and (nhan or Sy or Sx) else ""
    tinh.append(f"Sai số trung bình phương của hàm thực nghiệm{ban_dau}:\n"
                f"\\[ \\sigma=\\sqrt{{\\frac1n\\sum_{{i=1}}^{{n}}\\big(y_i-g(x_i)\\big)^2}}={so(sigma)}. \\]")
    if dang != "tt":                               # sigma lon: ly do (ln khuech dai sai so cua cac y nho)
        Y = np.abs(y + Sy)
        bien_do = float(np.max(y) - np.min(y))
        if sigma > 0.05 * bien_do > 0:
            nguong = 10.0 ** math.floor(math.log10(0.01 * float(np.max(Y))))
            nho = Y < nguong
            if np.any(nho):
                tinh[-1] += (f"\n$\\sigma$ lớn vì ${int(np.sum(nho))}$ điểm có $|y|<{sl(nguong)}$ "
                             f"($x\\ge{sl(float(np.min(x[nho])))}$): ở đó sai lệch nhỏ của $y$ làm $\\ln|y|$ lệch "
                             "nhiều và chi phối hệ chuẩn.")
    if nhan:
        than = r"\pp{Phương pháp.} " + "\n".join(pp) + "\n\n" + r"\pp{Tính toán.} " + "\n".join(tinh)
    else:                                          # ban thi (nhu dap an): khong nhan, 2 phan noi lien
        than = "\n".join(pp) + "\n" + "\n".join(tinh)
    return than, (he, a_v), sigma


def doc_khoi(ten):
    """Cac bo du lieu (cap cot lien ke co >= 3 dong so) trong sheet dau, giu nhan goc (Cau a ...) va so dong."""
    try:
        luoi = bp.doc_luoi(duong_dan(ten))
    except ValueError as e:
        raise LoiDuLieu(str(e))
    R_ = len(luoi)
    C = max((len(h) for h in luoi), default=0)
    luoi = [list(h) + [""] * (C - len(h)) for h in luoi]
    la_so = [[nw.doc_o(c)[0] is not None for c in h] for h in luoi]
    khoi, j = [], 0
    while j < C - 1:
        dong = [i for i in range(R_) if la_so[i][j] and la_so[i][j + 1]]
        if len(dong) >= 3:
            i0, i1 = dong[0], dong[-1]
            chu = [luoi[i][c].strip() for i in range(i0) for c in (j - 1, j, j + 1)
                   if 0 <= c < C and luoi[i][c].strip() and nw.doc_o(luoi[i][c])[0] is None]
            cap = [(luoi[i][j], luoi[i][j + 1], str(i + 1)) for i in range(i0, i1 + 1)
                   if luoi[i][j].strip() or luoi[i][j + 1].strip()]
            khoi.append(dict(nhan=" ".join(chu), ox=[c[0] for c in cap], oy=[c[1] for c in cap],
                             so=[c[2] for c in cap], cot_x=nw.ten_cot(j), cot_y=nw.ten_cot(j + 1)))
            j += 2
        else:
            j += 1
    return khoi


def cau23():
    ten = ts("cau23", "file")
    khoi = doc_khoi(ten)
    if len(khoi) < 4:
        raise LoiDuLieu(f"file '{ten}' can 4 bo du lieu (a, b, c, d) dat canh nhau, tim thay {len(khoi)}.")
    du = {}
    for nhan, kh in zip("abcd", khoi):
        x, y, sk = lam_sach(kh["ox"], kh["oy"], kh["so"], kieu="bptt")
        du[nhan] = (np.array(x), np.array(y), sk, kh)
    co = [len(du[nh][0]) for nh in "abcd"]
    nhan_ = [kh["nhan"] for kh in khoi[:4]]
    s = f"\\texttt{{{tex_chu(ten)}}} có {len(khoi)} bộ dữ liệu đặt cạnh nhau"
    if all(nhan_):
        s += f" (``{tex_chu(nhan_[0])}'' … ``{tex_chu(nhan_[-1])}'')"
    s += (f", mỗi bộ {co[0]} cặp $(x_i,y_i)$" if len(set(co)) == 1 else
          f", lần lượt có {', '.join(map(str, co))} cặp $(x_i,y_i)$")
    ghi = []
    for nh in "abcd":
        x, y, sk, kh = du[nh]
        for xv, ys in sk["trung"]:
            if len(ys) == 2 and ys[0] != ys[1]:
                ghi.append(f"bộ {nh} có mốc $x={sl(xv)}$ lặp lại với hai giá trị $y$ — giữ cả hai")
            else:
                ghi.append(f"bộ {nh} có mốc $x={sl(xv)}$ lặp lại {len(ys)} lần — giữ tất cả")
        for c in cau_loai(sk, lambda j: f"dòng {j}", kh["cot_x"], kh["cot_y"]):
            ghi.append(f"bộ {nh}: {c}")
    V["c23_du_lieu"] = s + ("; " + "; ".join(ghi) if ghi else "") + "."
    cac = {"a": ([(1, ()), (-1, ())], ["a", "b"], "tt"),
           "b": ([(2, ()), (0, ("cos",)), (0, ())], ["a", "b", "c"], "tt"),
           "c": ([(1, ()), (2, ())], ["b", "c"], "mu"),
           "d": ([(0, ("ln",))], ["b"], "luy")}
    for nh, (cs, an, dang) in cac.items():
        x, y, _, _ = du[nh]
        if dang == "tt" or dang == "mu":
            with np.errstate(all="ignore"):
                Phi = np.column_stack([gia_tri_co_so(p, f, x) for p, f in cs])
            tot = np.all(np.isfinite(Phi), axis=1)
            if not np.all(tot):
                raise LoiDuLieu(f"bo {nh}: co so khong xac dinh tai x = {', '.join(sl(v) for v in x[~tot])}.")
        try:
            V[f"c23{nh}_than"], _, _ = bptt_y(x, y, cs, an, dang)
        except ValueError as e:
            raise LoiDuLieu(f"bo {nh}: {e}")


# ===== DE GIUA KY (form dap an giua ky 20251): chon file de, chon tung cau theo menu, sinh loi giai =====

CO_SO_GK = {"1": (0, ()), "x": (1, ()), "x^2": (2, ()), "x^3": (3, ()), "x^4": (4, ()), "1/x": (-1, ()),
            "1/x^2": (-2, ()), "cosx": (0, ("cos",)), "lnx": (0, ("ln",))}
# tham chieu cheo trong thuat toan lay tu mau (de giua ky khong co Cau 4, 5, 11, 18, 22) -> ten thuat toan
THAY_GK = [("theo thuật toán Câu 5a", "bằng sơ đồ Horner nhân"), ("theo thuật toán Câu 5b", "bằng bảng tích (Horner nhân lặp)"),
           ("theo thuật toán Câu 4a", "bằng sơ đồ Horner chia"), ("Gọi thuật toán Câu 11a với", "Gọi thuật toán trích xuất với"),
           ("(câu a, b)", "(thuật toán khoảng cách ly, khoảng đơn điệu)"),
           ("theo câu a", "theo thuật toán bình phương tối thiểu tuyến tính"),
           (r"thì tìm đoạn đơn điệu $[x_a,x_b]$ chứa $(x_k,x_{k+1})$ theo thuật toán câu b, gọi thuật toán câu c "
            r"với $x$, $y$, $\bar y$, $k$, $a$, $b$, $m$ được $\bar x$, dừng thuật toán, trả về $\bar x$.",
            r"thì báo ``mốc không cách đều'', dừng thuật toán."),
           (" (Câu 4c)", ""), (" (Câu 4a)", ""), ("(18d; ", "(thuật toán lặp; "), ("(18c)", "(thuật toán hàm ngược)"),
           ("thuật toán câu 11a", "thuật toán trích xuất")]


def doc_co_so_gk(s):
    """'x; 1/x' -> [(1, ()), (-1, ())] (cac ham: 1, x, x^2, x^3, x^4, 1/x, 1/x^2, cos x, ln x)."""
    out = []
    for t in re.split(r"[;,]", s):
        k = re.sub(r"\s+", "", t.lower())
        if not k:
            continue
        if k not in CO_SO_GK:
            raise LoiDuLieu(f"co so: ham '{t.strip()}' chua ho tro (dung: 1, x, x^2, x^3, x^4, 1/x, 1/x^2, cos x, ln x).")
        out.append(CO_SO_GK[k])
    if not out:
        raise LoiDuLieu("co so rong.")
    return out


def bo_tham_chieu(s):
    for cu, moi in THAY_GK:
        s = s.replace(cu, moi)
    return s


class Hoi:
    """Hoi tung cau (Enter / EOF = mac dinh); co file tra loi thi doc tung dong (bo dong '#'); ghi lai cac tra loi."""

    def __init__(self, tra_loi=None):
        self.tl, self.ghi = tra_loi, []

    def __call__(self, cau, mac_dinh="", menu=None):
        if menu and self.tl is None:
            for k, v in menu.items():
                print(f"  {k}. {v}")
        if self.tl is not None:
            s = self.tl.pop(0).strip() if self.tl else ""
            print(f"{cau} (VD [{mac_dinh}]): {s}")
        else:
            try:
                s = input(f"{cau} (VD [{mac_dinh}]): ").strip()
            except EOFError:
                s = ""
        self.ghi.append((cau, s))
        return s or str(mac_dinh)

    def so(self, cau, mac_dinh, nguyen=False, nho_nhat=None):
        while True:
            s = self(cau, mac_dinh)
            v, _, loi = nw.doc_o(s)
            if not loi and (not nguyen or v == int(v)) and (nho_nhat is None or v >= nho_nhat):
                return int(v) if nguyen else v
            print(f"  -> '{s}' khong hop le" + (f" (can so nguyen >= {nho_nhat})" if nguyen else "") + ", nhap lai.")
            if self.tl is not None:
                raise LoiDuLieu(f"file tra loi: '{cau}' = '{s}' khong hop le.")


def tim_file_de():
    """Cac file de cua hoc ky moi nhat trong data/ (ten '...GKtest...'), moi de 1 file: .xlsx > .csv > .txt > .rar
    (.rar chi tinh khi chua giai nen). Tra ve danh sach duong dan tuong doi voi data/, sap theo ten (test1, test2...)."""
    uu_tien = {".xlsx": 0, ".csv": 1, ".txt": 2, ".rar": 3, ".zip": 3, ".7z": 3}
    tot = {}                                       # ten de -> (uu tien, duong dan)
    for goc, _, ds in os.walk(DATA):
        for t in ds:
            ten, duoi = os.path.splitext(t)
            if re.search(r"gk\s*test", t, re.I) and duoi.lower() in uu_tien:
                p = os.path.relpath(os.path.join(goc, t), DATA).replace("\\", "/")
                k = ten.lower()
                if k not in tot or uu_tien[duoi.lower()] < tot[k][0]:
                    tot[k] = (uu_tien[duoi.lower()], p)
    if not tot:
        return []
    nam = max((re.findall(r"\d{5}", k)[:1] or ["0"])[0] for k in tot)
    return [tot[k][1] for k in sorted(tot) if (re.findall(r"\d{5}", k)[:1] or ["0"])[0] == nam]


def giai_nen(p, hoi):
    """File .rar / .zip / .7z cua de: hoi mat khau, giai nen bang 7-Zip vao data/de_<ten>/, tra ve file so lieu ben trong."""
    z = shutil.which("7z") or next((c for c in (r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe")
                                    if os.path.isfile(c)), None)
    if not z:
        raise LoiDuLieu("khong thay 7-Zip (7z.exe): tu giai nen file de vao data/ roi chay lai.")
    ten = os.path.splitext(os.path.basename(p))[0]
    dich = os.path.join(DATA, "de_" + re.sub(r"\D", "", ten)[:5] if re.search(r"\d{5}", ten) else "de_" + ten)
    co_san = set(os.listdir(dich)) if os.path.isdir(dich) else set()
    for lan in range(3):                           # sai mat khau: don file hong (0 byte) roi cho nhap lai
        mk = hoi("Mat khau file nen (ghi tren de; Enter = khong co)", "")
        kq = subprocess.run([z, "x", p, f"-o{dich}", "-y", f"-p{mk}"], capture_output=True, text=True, errors="replace")
        if kq.returncode == 0:
            break
        for t in set(os.listdir(dich)) - co_san if os.path.isdir(dich) else []:
            os.remove(os.path.join(dich, t))
        if os.path.isdir(dich) and not os.listdir(dich):
            os.rmdir(dich)
        print(f"  -> giai nen loi (sai mat khau?): {kq.stderr.strip()[:120]}")
        if hoi.tl is not None or lan == 2:
            raise LoiDuLieu(f"khong giai nen duoc '{os.path.basename(p)}' (sai mat khau).")
    cac = [os.path.join(g, t) for g, _, ds in os.walk(dich) for t in ds
           if os.path.splitext(t)[0].lower() == ten.lower() and t.lower().endswith((".xlsx", ".csv", ".txt"))]
    if not cac:
        cac = [os.path.join(g, t) for g, _, ds in os.walk(dich) for t in ds if t.lower().endswith((".xlsx", ".csv", ".txt"))]
    if not cac:
        raise LoiDuLieu(f"trong '{os.path.basename(p)}' khong co file .xlsx / .csv / .txt.")
    cac.sort(key=lambda q: (not q.lower().endswith(".xlsx"), q))
    print(f"  Da giai nen vao {dich}: {', '.join(os.path.basename(q) for q in cac)} -> dung {os.path.basename(cac[0])}")
    return cac[0]


def doc_de(hoi):
    """Chon file, sheet; doc bang, xbar / ybar trong file. Tra ve dict du lieu de."""
    cac_de = tim_file_de()
    menu = {str(i): f for i, f in enumerate(cac_de, 1)}
    if menu:
        print("Cac file de tim thay trong data/ (de 1 -> test1, de 2 -> test2):")
    ten = hoi("File du lieu de: so thu tu, hoac duong dan (tuong doi voi data/)", "1" if menu else "", menu=menu)
    ten = menu.get(ten, ten)
    p = ten if os.path.isabs(ten) else (ten if os.path.isfile(ten) else os.path.join(DATA, ten))
    if not os.path.isfile(p):
        raise LoiDuLieu(f"khong thay file '{ten}'.")
    if p.lower().endswith((".rar", ".zip", ".7z")):
        p = giai_nen(p, hoi)
    try:
        cac = [(ts_, l, kq) for ts_, l in nw.doc_luoi_file(p) for kq in [nw.phan_tich_luoi(l)] if kq]
    except ValueError as e:
        raise LoiDuLieu(str(e))
    if not cac:
        raise LoiDuLieu(f"file '{ten}' khong co bang so lieu.")
    sheet = 1
    if len(cac) > 1:
        print("Cac sheet co so lieu:")
        for i, (ts_, _, kq) in enumerate(cac, 1):
            print(f"  {i}. {ts_}: {len(kq['y'])} dong, tham so {', '.join(f'{k} = {v[0]:.10g}' for k, v in kq['ts'].items())}")
        sheet = hoi.so("Chon sheet", 1, nguyen=True, nho_nhat=1)
        if sheet > len(cac):
            raise LoiDuLieu(f"chi co {len(cac)} sheet so lieu.")
    ten_sheet, luoi, kq = cac[sheet - 1]
    if not kq["co_x"]:                            # file chi co y: sinh x cach deu
        print(f"  File chi co 1 day so ({len(kq['y'])} gia tri) -> sinh x cach deu x_i = x_0 + i*h.")
        x0 = hoi.so("x_0", 1)
        hh = hoi.so("h", 1)
        kq["x"] = [f"{x0 + i * hh:.12g}" for i in range(len(kq["y"]))]
        kq["co_x"], kq["vi_tri"], kq["day_x"] = True, "dong", "(sinh)"
    dau = int(kq["so"][0]) - 1 if kq["vi_tri"] == "dong" else 0
    B = dict(kq, file=os.path.relpath(p, DATA).replace("\\", "/") if p.startswith(DATA) else os.path.basename(p),
             so_sheet=len(cac), sheet=sheet, ten_sheet=ten_sheet, dau=dau,
             dau_trong=all(not str(c).strip() for h in luoi[:dau] for c in h))
    x, y, sk = lam_sach(B["x"], B["y"], B["so"])
    x = [round(v, 10) for v in x]
    xb, yb = B["ts"].get("xbar"), B["ts"].get("ybar")
    h = nw.cach_deu(x) if len(x) > 1 else None
    print(f"\nDOC FILE: {B['file']}" + (f" (sheet {ten_sheet})" if len(cac) > 1 else ""))
    print(f"  cot x = {B['day_x']}, cot y = {B['day_y']}; {len(x)} moc [{x[0]:.10g}; {x[-1]:.10g}]"
          + (f", cach deu h = {h:.10g}" if h else ", KHONG cach deu"))
    for j, a, b, lx, ly in sk["loai"]:
        print(f"  bo dong {j}: x = {a!r}, y = {b!r} ({lx or ly})")
    print(f"  xbar = {xb[0]:.10g} (o {xb[1]})" if xb else "  khong thay xbar trong file")
    print(f"  ybar = {yb[0]:.10g} (o {yb[1]})" if yb else "  khong thay ybar trong file")
    ngoai = []                                     # moi o ngoai 2 cot so lieu: tham so khac cua de (xbar 2, ybar 2...)
    cot_xy = {B["day_x"], B["day_y"]}
    for i, hang in enumerate(luoi):
        for j, o in enumerate(hang):
            if str(o).strip() and nw.ten_cot(j) not in cot_xy and kq["vi_tri"] == "dong":
                ngoai.append(f"{nw.ten_cot(j)}{i + 1} = {str(o).strip()!r}")
    if ngoai:
        print("  O ngoai bang x, y: " + "; ".join(ngoai[:30]) + (" ..." if len(ngoai) > 30 else ""))
    return dict(B=B, x=x, y=y, sk=sk, h=h, xbar=xb, ybar=yb, ten=os.path.splitext(os.path.basename(p))[0])


def mo_ta_de(D, cac_gt):
    """Cau mo dau (nhu dap an): 'Ta co bang du lieu gom ... va cac gia tri cho truoc ...'; dong bi bo ghi o goi y."""
    x, h = D["x"], D["h"]
    s = ("Ta có bảng dữ liệu gồm "
         + (mo_ta_luoi(x, h) if h else f"$N={len(x)}$ mốc $x\\in[{sl(x[0])};\\,{sl(x[-1])}]$ (không cách đều)"))
    if cac_gt:
        s += " và các giá trị cho trước " + ", ".join(cac_gt)
    bo = [str(j) for j, *_ in D["sk"]["loai"]]
    trung = cau_trung_sap(D["sk"])
    goi = "không chép bảng số liệu"
    if bo:
        goi = f"file có dòng {', '.join(bo)} thiếu $x$ hoặc $y$ (đã bỏ, không cần ghi); " + goi
    if trung:
        goi = "; ".join(trung) + "; " + goi
    return s + ".\n\\goiy{" + goi + ".}"


def can_cach_deu(D, ten):
    if D["h"] is None:
        raise LoiDuLieu(f"{ten} can moc cach deu, du lieu khong cach deu.")


def ct_gop(sh):
    """Cong thuc 1 khoi nhu dap an: P = (tong quat) = (thay so) = (rut gon), moi dong 5 so hang dau roi \\cdots."""
    ten, tq, thay, gon = sh
    muc = [(ten, rut_so_hang(tq), "", ""), ("", rut_so_hang(thay), "", "")]
    if rut_so_hang(gon) != rut_so_hang(thay):
        muc.append(("", rut_so_hang(gon), "", ""))
    return hien_nhieu(muc, rong_max=RONG - 20)


def gk_bptt(hoi, D, mau, tt_):
    dg = hoi("Dang ham (1 tuyen tinh theo tham so, 2 mu y = a e^(...), 3 luy thua y = a x^b)", "2")
    dang = {"1": "tt", "2": "mu", "3": "luy"}.get(dg)
    if dang is None:
        raise LoiDuLieu("dang ham phai la 1, 2 hoac 3.")
    if dang == "luy":
        cs, an, mo_hinh = [(0, ("ln",))], ["b"], "a\\,x^b"
    else:
        cs = doc_co_so_gk(hoi("Cac ham co so cach nhau ';' (1, x, x^2, x^3, 1/x, 1/x^2, cos x, ln x)",
                              "x; 1/x" if dang == "mu" else "x; 1"))
        an = list(("abcdefg" if dang == "tt" else "bcdefg")[:len(cs)])
        hang = "+".join(hang_S(a, p, f).replace("x_i", "x") for a, (p, f) in zip(an, cs))
        mo_hinh = hang if dang == "tt" else "a\\,e^{" + hang + "}"
    xa, ya, _ = lam_sach(D["B"]["x"], D["B"]["y"], D["B"]["so"], kieu="bptt")[:3]
    try:
        than, (he, a_v), sigma = bptt_y(xa, ya, cs, an, dang, nhan=False, chi_so=0)
    except ValueError as e:
        raise LoiDuLieu(str(e))
    than = than.replace("Thay vào hệ phương trình chuẩn:", r"\goiy{ghi đủ các tổng (đều dùng trong hệ chuẩn), không "
                        r"lập bảng từng điểm.}" + "\nThay vào hệ phương trình chuẩn:", 1)
    gt_ = re.search(r"y=g\(x\)=(.*?)\. \\\]", than)
    return (f"Hàm thực nghiệm dạng $y={mo_hinh}$ và sai số", than,
            f"g(x) = {gt_.group(1) if gt_ else '?'}, sigma = {so(sigma)}")


def gk_ybar(hoi, D):
    yb = D["ybar"][0] if D["ybar"] else ""
    return hoi.so("ybar", yb if yb != "" else 0)


TT_LAP_GON = r"""\begin{thuattoan}{Lặp giải $f(x)=\bar y$ trên lưới mốc cách đều}
\item[Input:] mốc cách đều $x_i$, $y_i$ ($i=0,\dots,n$), bước $h$; $\bar y$; số mốc nội suy $m$; sai số $\varepsilon$; số lần lặp tối đa $N$.
\item[Output:] các nghiệm gần đúng $\bar x$ của $f(x)=\bar y$.
\item[B1:] \textbf{Tìm khoảng cách ly:} lặp $i=0,\dots,n-1$:\thut nếu $y_i=\bar y$ thì $x_i$ là nghiệm;\thut nếu $(y_i-\bar y)(y_{i+1}-\bar y)<0$ thì $(x_i,x_{i+1})$ là khoảng cách ly.
\item[B2:] \textbf{Lặp trên từng khoảng} $(x_k,x_{k+1})$:
  \begin{con}
  \item[a)] \textbf{Chọn hướng, mốc gốc:} nếu $k+m-1\le n$ thì Newton tiến, $s:=k$, mốc $x_k,\dots,x_{k+m-1}$; ngược lại Newton lùi, $s:=k+1$, mốc $x_{k+2-m},\dots,x_{k+1}$.
  \item[b)] \textbf{Sai phân:} lập bảng sai phân của $m$ mốc; $d_j:=\Delta^jy_k$ (tiến) hoặc $d_j:=\nabla^jy_{k+1}$ (lùi), $j=0,\dots,m-1$.
  \item[c)] \textbf{Hàm lặp:} với $t=\frac{x-x_s}{h}$, $\varphi(t):=\dfrac{\bar y-d_0}{d_1}-\sum_{j=2}^{m-1}\dfrac{d_j}{j!\,d_1}\,t(t\mp1)\cdots\big(t\mp(j-1)\big)$ (dấu $-$ khi tiến, $+$ khi lùi).
  \item[d)] \textbf{Lặp:} $t_0:=\dfrac{\bar y-d_0}{d_1}$, $t_{l+1}:=\varphi(t_l)$ đến khi $h\,|t_{l+1}-t_l|<\varepsilon$; quá $N$ lần thì báo ``không hội tụ''.
  \item[e)] \textbf{Nghiệm:} nếu $t^*\in[0;1]$ (tiến) hoặc $t^*\in[-1;0]$ (lùi) thì $\bar x:=x_s+t^*h$; ngược lại bỏ khoảng này.
  \end{con}
\item[B3:] \textbf{Trả về} các nghiệm.
\end{thuattoan}"""

TT_HAM_NGUOC_GON = r"""\begin{thuattoan}{Hàm ngược giải $f(x)=\bar y$}
\item[Input:] mốc $x_i$, $y_i$ ($i=0,\dots,n$); $\bar y$; số mốc nội suy $m$.
\item[Output:] các nghiệm gần đúng $\bar x$ của $f(x)=\bar y$.
\item[B1:] \textbf{Khoảng cách ly:} các $(x_k,x_{k+1})$ có $(y_k-\bar y)(y_{k+1}-\bar y)<0$.
\item[B2:] \textbf{Đoạn đơn điệu:} tách bảng tại các $i$ mà $\Delta y_i=y_{i+1}-y_i$ đổi dấu; lấy đoạn $[x_a,x_b]$ chứa $(x_k,x_{k+1})$.
\item[B3:] \textbf{Chọn mốc:} trong $[x_a,x_b]$ chọn $m$ mốc liên tiếp quanh khoảng cách ly có $|y_j-\bar y|$ nhỏ nhất; đặt $u_s:=y$, $v_s:=x$ (sắp $u$ tăng).
\item[B4:] \textbf{Tỷ sai phân:} lập bảng tỷ sai phân của $v$ theo $u$, $c_j:=v[u_0,\dots,u_j]$.
\item[B5:] \textbf{Giá trị:} $\bar x:=\sum_jc_j\prod_{i<j}(\bar y-u_i)$; số hạng cuối là ước lượng sai số. Trả về các $\bar x$.
\end{thuattoan}"""


def cau_kcl(x, y, ybar, kh, tai_moc):
    """Cau khoang cach ly (nhu dap an)."""
    moc = ("; mốc là nghiệm: " + ", ".join(f"$x_{{{i}}}={sl(x[i])}$" for i in tai_moc)) if tai_moc else ""
    if not kh:
        return f"Với $\\bar y={sl(ybar)}$, phương trình $f(x)={sl(ybar)}$ không có khoảng cách ly nghiệm{moc}."
    ds = "; ".join(f"$[x_{{{k}}},x_{{{k + 1}}}]=[{sl(x[k])};\\,{sl(x[k + 1])}]$ (vì $y_{{{k}}}={sl(y[k])}"
                   f"{'<' if y[k] < ybar else '>'}{sl(ybar)}{'<' if y[k] < ybar else '>'}y_{{{k + 1}}}={sl(y[k + 1])}$)"
                   for k in kh)
    so_kh = "duy nhất $1$ khoảng cách ly nghiệm là" if len(kh) == 1 else f"${len(kh)}$ khoảng cách ly nghiệm:"
    return (f"Từ dữ liệu đã cho là mốc cách đều tăng dần, với $\\bar y={sl(ybar)}$, phương trình $f(x)={sl(ybar)}$ có "
            f"{so_kh} {ds}{moc}.")


def bang_kq():
    """Bang ket qua (nhu dap an): Nghiem | Khoang cach ly | Moc su dung | Phuong phap ap dung | Ket qua x*."""
    rows = [[f"x^*_{{{r}}}" if len(KQ_19) > 1 else "x^*"] + h for r, h in enumerate(KQ_19, 1)]
    KQ_19.clear()
    return bang([r"\text{Nghiệm}", r"\text{Khoảng cách ly}", r"\text{Mốc sử dụng}", r"\text{Phương pháp áp dụng}",
                 r"\text{Kết quả }x^*"], rows, can="ccccc")


def lap_gon(x, k, lp, h, dl, nhieu):
    """1 khoang cach ly cua phuong phap lap, ghi gon: moc, cac sai phan, phi(t), day lap, nghiem."""
    idx, d = lp["idx"], lp["d"]
    m = len(idx)
    tien = lp["huong"] == "tien"
    s = lp["s"]
    ky, g = (r"\Delta", f"{k}") if tien else (r"\nabla", f"{k + 1}")
    nh = [f"y_{{{g}}}", f"{ky} y_{{{g}}}"] + [f"{ky}^{{{j}}}y_{{{g}}}" for j in range(2, m)]
    gt = [sl(d[0])] + [sd(v, dl) if dl is not None else so(v) for v in d[1:]]
    dau = "-" if tien else "+"
    phi = [so(lp["A"])] + [("- " if lp["B"][j] >= 0 else "+ ") + so(abs(lp["B"][j]))
                           + "".join(f"(t{dau}{l})" if l else "t" for l in range(j)) for j in range(2, m)]
    t = lp["t"]
    la = len(t) - 1
    chon = list(range(la + 1)) if la <= 4 else [0, 1, 2, None, la]
    day = r",\ ".join(r"\dots" if j is None else f"t_{{{j}}}={so(t[j])}" for j in chon)
    doan_t = "[0;1]" if tien else "[-1;0]"
    if lp["hoi_tu"]:
        kq = (f"\\Longrightarrow\\ t^*=t_{{{la}}}\\in{doan_t},\\quad \\bar x=x_{{{s}}}+t^*h={sl(x[s])}+{sn(t[-1])}"
              f"\\cdot{sl(h)}={so(lp['xbar'])}")
        kq_bang = so(lp["xbar"])
    elif lp.get("ngoai"):
        kq = f"\\Longrightarrow\\ t^*=t_{{{la}}}={so(t[-1])}\\notin{doan_t}:\\ \\text{{bỏ (đổi }}m\\text{{)}}"
        kq_bang = r"\text{ngoài khoảng}"
    else:
        kq = f"\\text{{sau }}N={la}\\text{{ lần chưa hội tụ}}"
        kq_bang = r"\text{không hội tụ}"
    KQ_19.append([f"[{sl(x[k])};\\ {sl(x[k + 1])}]", f"[{sl(x[idx[0]])};\\ {sl(x[idx[-1]])}]",
                  f"\\text{{Newton {'tiến' if tien else 'lùi'} (từ }}x_{{{s}}}={sl(x[s])})", kq_bang])
    mo = (f"Khoảng $[x_{{{k}}},x_{{{k + 1}}}]$: " if nhieu else "") + (
        f"Newton {'tiến' if tien else 'lùi'} với ${m}$ mốc $x_{{{idx[0]}}},\\dots,x_{{{idx[-1]}}}$, "
        f"$t=\\dfrac{{{x_tru(x[s])}}}{{{sl(h)}}}$; " + ", ".join(f"${a}={b}$" for a, b in zip(nh, gt)) + ":")
    return (mo + "\n" + hien(r"\varphi(t)", phi) + "\n\\begin{gather*}\n" + day + r",\\" + "\n" + kq
            + ".\n\\end{gather*}")


def gk_lap(hoi, D, mau, tt_):
    can_cach_deu(D, "phuong phap lap")
    x, y, h = D["x"], D["y"], D["h"]
    ybar = gk_ybar(hoi, D)
    m_b = hoi.so("So moc noi suy m (dap an dung 6; du lieu nhieu dung 3-4)", 4, nguyen=True, nho_nhat=2)
    eps = hoi.so("Sai so eps", 1e-6)
    N_lap = hoi.so("So lan lap toi da N", 100, nguyen=True, nho_nhat=1)
    co_tt = hoi("Ghi thuat toan lap (c/k)", "c").lower().startswith("c")
    ghi = hoi("Ghi chu ly do chon so moc (LaTeX; Enter = khong)", "")
    tai_moc, kh = nsn.khoang_cach_ly(y, ybar)
    lps = [nsn.lap(x, y, ybar, k, h, m_b, eps, N_lap) for k in kh]
    dl = nsn.so_le(y)
    KQ_19.clear()
    khoi = [lap_gon(x, k, lp, h, dl, len(kh) > 1) for k, lp in zip(kh, lps)]
    for k, lp in zip(kh, lps):
        KT[f"lap k={k}: |y(xbar) - ybar|"] = abs(nsn.y_tai(x, y, lp["xbar"], m_b) - ybar)
    than = ((TT_LAP_GON + "\n\\goiy{đề yêu cầu viết thuật toán: ghi đủ B1--B3.}\n\n" if co_tt else "")
            + cau_kcl(x, y, ybar, kh, tai_moc)
            + (f" Áp dụng thuật toán với $m={m_b}$ mốc, $\\varepsilon={mu10(eps)}$" + (f" ({ghi})" if ghi else "")
               + ":\n" if kh else "\n")
            + "\n\n".join(khoi)
            + ("\n\\goiy{dãy lặp chỉ cần ghi $t_0,t_1,t_2,\\dots,t$ cuối.}\nKết quả như sau:\n" + bang_kq() if kh else ""))
    tom = ", ".join(so(lp["xbar"]) if lp["hoi_tu"] else "khong hoi tu/ngoai khoang" for lp in lps) or "khong co nghiem"
    return f"Phương pháp lặp giải $f(x)=\\bar y$, $\\bar y={sl(ybar)}$", bo_tham_chieu(than), f"xbar = {tom}"


def gk_ham_nguoc(hoi, D, mau, tt_):
    x, y = D["x"], D["y"]
    ybar = gk_ybar(hoi, D)
    m = hoi.so("So moc noi suy m", 6, nguyen=True, nho_nhat=2)
    co_tt = hoi("Ghi thuat toan ham nguoc (c/k)", "k").lower().startswith("c")
    tai_moc, kh = nsn.khoang_cach_ly(y, ybar)
    doan = nsn.khoang_don_dieu(y)
    KQ_19.clear()
    khoi, tom = [], []
    for k in kh:
        a_, b_, s_ = next(dd for dd in doan if dd[0] <= k < dd[1])
        hn_ = nsn.ham_nguoc(x, y, ybar, k, a_, b_, m)
        idx = hn_["idx"]
        xv = hn_["xbar"]
        dung = x[k] <= xv <= x[k + 1]
        sh = [so(v) for v in hn_["so_hang"]]
        tong = [sh[0]] + [v if v.startswith("-") else "+" + v for v in sh[1:]] + [f"={so(hn_['xbar'])}"]
        mo = (f"Khoảng $[x_{{{k}}},x_{{{k + 1}}}]\\subset[{sl(x[a_])};\\,{sl(x[b_])}]$ (đoạn {CHIEU[s_]}), chọn ${len(idx)}$ "
              f"mốc $x_{{{min(idx)}}},\\dots,x_{{{max(idx)}}}$; bảng tỷ sai phân của $v=x$ theo $u=y$:")
        khoi.append(mo + "\n" + tsp_x_theo_y(hn_) + "\n"
                    + hien(r"\bar x\approx\sum_jc_j\prod_{i<j}(\bar y-u_i)", tong)
                    + ("" if dung else "\n$\\bar x$ nằm ngoài khoảng cách ly: không tin cậy (đổi $m$)."))
        KQ_19.append([f"[{sl(x[k])};\\ {sl(x[k + 1])}]", f"[{sl(x[min(idx)])};\\ {sl(x[max(idx)])}]",
                      r"\text{hàm ngược (tỷ sai phân)}", so(xv) if dung else r"\text{không tin cậy}"])
        tom.append(so(xv) if dung else "khong tin cay")
        KT[f"ham nguoc k={k}: |y(xbar) - ybar|"] = abs(nsn.y_tai(x, y, xv, m) - ybar)
    pp = (TT_HAM_NGUOC_GON + "\n\n" if co_tt else
          r"Trên đoạn đơn điệu chứa khoảng cách ly, $y=f(x)$ có hàm ngược $x=f^{-1}(y)$. Đổi vai trò $x$, $y$ "
          r"($u=y$, $v=x$), nội suy Newton $v$ theo $u$ bằng tỷ sai phân rồi thay $u=\bar y$: "
          r"$\bar x\approx\sum_jc_j\,\omega_j(\bar y)$, $c_j=v[u_0,\dots,u_j]$, $\omega_j(\bar y)=\prod_{i<j}(\bar y-u_i)$."
          + "\n\n")
    than = (pp + cau_kcl(x, y, ybar, kh, tai_moc) + (f" Áp dụng với $m={m}$ mốc:\n" if kh else "\n")
            + "\n\n".join(khoi) + ("\nKết quả như sau:\n" + bang_kq() if kh else ""))
    return (f"Phương pháp hàm ngược giải $f(x)=\\bar y$, $\\bar y={sl(ybar)}$", bo_tham_chieu(than),
            "xbar = " + (", ".join(tom) or "khong co nghiem"))


def gk_xbar_m_k(hoi, D, m_md):
    xb = D["xbar"][0] if D["xbar"] else ""
    xbar = hoi.so("xbar", xb if xb != "" else D["x"][len(D["x"]) // 2])
    m = hoi.so("So moc m", m_md, nguyen=True, nho_nhat=1)
    k = hoi.so("Cap dao ham k (0 = chi gia tri)", 1, nguyen=True, nho_nhat=0)
    return xbar, m, k


def trich_gon(D, xbar, m):
    """Trich xuat m moc (thuat toan trich xuat) viet nhu dap an. Tra ve (L, R, cau, (so moc trai, phai))."""
    x, h = D["x"], D["h"]
    L_, R_, thu_tu, j0 = trich_xuat(x, xbar, m, h)
    j = thu_tu[0]
    s = ngoai_suy(x, xbar) + f"Mốc gần $\\bar x={sl(xbar)}$ nhất là $x_{{{j}}}={sl(x[j])}$ (với bước $h={sl(h)}$). "
    return L_, R_, s, (j - L_, R_ - j)


def cau_trich_tt(xbar, m, R, ct, L_, R_, lech):
    """Cau chon tam + trich xuat cho Gauss / Stirling / Bessel (sau trich_gon)."""
    goc = f"chỉ số gốc $i\\in\\{{{ds_chi_so(L_, R_)}\\}}$ (đánh số lại ${R['p']}..{R['p'] + R['n']}$)"
    trai, phai = lech
    bien = f" (gần biên: ${trai}$ mốc trái, ${phai}$ mốc phải)" if abs(trai - phai) > 1 else ""
    if ct == 4:
        j0_ = L_ + R["q"]
        giua = (f"Điểm $\\bar x$ nằm trong khoảng trung tâm $[x_{{{j0_}}},x_{{{j0_ + 1}}}]="
                f"[{sl(R['x0'])};\\,{sl(R['x1'])}]$. " if R["x0"] <= xbar <= R["x1"] else "")
        return (giua + f"Chọn $x_0={sl(R['x0'])}$, $x_1={sl(R['x1'])}$ và trích xuất ${m}$ mốc đối xứng ứng với "
                f"{goc}{bien}:")
    return f"Chọn tâm $x_0={sl(R['x0'])}$ và trích xuất ${m}$ mốc đối xứng ứng với {goc}{bien}:"


def phan_tinh_gk(sp_ten, bang_sp, mo_ct, sh, c, bien, bang_nhan_, Pt, gia_tri):
    """Phan da thuc noi suy (nhu dap an): bang sai phan -> cong thuc 1 khoi -> vector c -> bang nhan -> chinh tac -> gia tri."""
    return L(r"""@sp_ten@
@bang_sp@
\goiy{ghi đủ bảng, khoanh các ô dùng trong công thức.}
@mo_ct@
@ct@
Vector hệ số theo thứ tự các cơ sở là
@vec_c@
Khai triển các tích cơ sở theo luỹ thừa của $@bien@$ ta có bảng nhân:
@bang_nhan@
\goiy{các ô $0$ phía trên có thể để trống.}
Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:
@Pt@
@gia_tri@""", sp_ten=sp_ten, bang_sp=bang_sp, mo_ct=mo_ct, ct=ct_gop(sh), vec_c=vec_hien(c, "c"), bien=bien,
             bang_nhan=bang_nhan_, Pt=Pt, gia_tri=gia_tri)


def gk_trung_tam(hoi, D, mau, ct):
    can_cach_deu(D, TEN_CT.get(ct, "Gauss"))
    x, y, h = D["x"], D["y"], D["h"]
    xbar, m0, k = gk_xbar_m_k(hoi, D, {3: 7, 4: 8}.get(ct, 7))
    m, ghi = chinh_m(3 if ct == 3 else 4 if ct == 4 else 1, min(m0, len(x)), len(x))
    L_, R_, trich, lech = trich_gon(D, xbar, m)
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    if ct == 0:                                    # Gauss: I neu tbar >= 0 (voi x_0 cua Gauss I), nguoc lai II
        q1 = tt.vi_tri_tam(m - 1, 1)
        ct = 1 if (xbar - xs[q1]) / h >= 0 else 2
    R = tt_tinh(xs, ys, h, ct, xbar, k)
    n, p = R["n"], R["p"]
    t_ = f"$t=\\dfrac{{{x_tru(R['x0'])}}}{{{sl(h)}}}$"
    if ct in (1, 2):
        mo_ct = (f"Vì {ly_do_gauss(ct, R['tb'])}. Đặt biến chuẩn hoá {t_}. Công thức nội suy {TEN_CT[ct]} bậc ${n}$ "
                 "có dạng:")
    elif ct == 3:
        mo_ct = f"Đặt biến chuẩn hoá {t_}. Công thức nội suy Stirling bậc ${n}$ có dạng:"
    else:
        mo_ct = (f"Đặt {t_} và biến đối xứng $u=t-\\dfrac12=\\dfrac{{{x_tru(round(R['s0'], 10))}}}{{{sl(h)}}}$. "
                 f"Công thức nội suy Bessel bậc ${n}$ theo biến $u$ là:")
    than = (ghi + trich + cau_trich_tt(xbar, m, R, ct, L_, R_, lech) + "\n"
            + bang_ngang_goc(range(p, p + n + 1), range(L_, R_ + 1), xs, ys) + "\n"
            + phan_tinh_gk("Bảng sai phân trung tâm:", R["bang_sp"], mo_ct, R["sh"], R["c"], R["bien"],
                           R["bang_nhan"], R["Pt"], tt_gia_tri(R, ct, xbar, k, h)))
    gtc = "$f(\\bar x)$" + (f", ${dh('f', k)}(\\bar x)$" if k else "")
    v = R["v"]
    tom = f"f({sl(xbar)}) ~ {so(v[0])}" + (f", f^({k})({sl(xbar)}) ~ {so(v[k] / h ** k)}" if k else "")
    return (f"Đa thức nội suy {TEN_CT[ct]} {m} mốc, {gtc} với $\\bar x={sl(xbar)}$", bo_tham_chieu(than), tom)


def chon_moc(hoi, D, m_md, can_y=True, xbar=None):
    """Chon bo moc cho 1 cau: 1 trich m moc gan xbar, 2 theo chi so goc 'a-b', 3 ca bang, 4 nhap tay.
    Tra ve (xs, ys, doan LaTeX mo dau + bang moc, xbar)."""
    x, y, h = D["x"], D["y"], D["h"]
    N = len(x)
    cach = hoi("Lay moc: 1 trich m moc gan xbar, 2 theo chi so goc (vd 10-17), 3 ca bang, 4 nhap tay",
               "3" if N <= 12 else "1")
    goc = None
    if cach == "1":
        if xbar is None:
            xb = D["xbar"][0] if D["xbar"] else x[N // 2]
            xbar = hoi.so("xbar (diem can tinh / de trich moc)", xb)
        m = min(hoi.so("So moc m", m_md, nguyen=True, nho_nhat=1), N)
        if h is not None:
            L_, R_, mo, _ = trich_gon(D, xbar, m)
        else:
            L_, R_, _ = nw.trich_xuat(x, xbar, m)
            mo = ""
        mo += f"Trích xuất ${m}$ mốc gần $\\bar x$ nhất ứng với chỉ số gốc $i\\in\\{{{ds_chi_so(L_, R_)}\\}}$"
        xs, ys, goc = x[L_:R_ + 1], y[L_:R_ + 1], range(L_, R_ + 1)
    elif cach == "2":
        s = hoi("Chi so goc dau-cuoi (vd 10-17)", f"0-{min(N, 6) - 1}")
        so_ = [int(v) for v in re.findall(r"\d+", s)]
        if len(so_) != 2 or not 0 <= so_[0] < so_[1] < N:
            raise LoiDuLieu(f"chi so goc '{s}' khong hop le (0..{N - 1}).")
        L_, R_ = so_
        xs, ys, goc = x[L_:R_ + 1], y[L_:R_ + 1], range(L_, R_ + 1)
        mo = f"Lấy các mốc ứng với chỉ số gốc $i\\in\\{{{ds_chi_so(L_, R_)}\\}}$"
    elif cach == "3":
        xs, ys = list(x), list(y)
        mo = f"Dùng cả bảng ${N}$ mốc"
    else:
        ox = nw.bo_nhan(nw.tach_o(hoi("Cac moc x_i (cach nhau khoang trang)", "1 1.5 2 2.5")))
        if can_y:
            oy = nw.bo_nhan(nw.tach_o(hoi("Cac gia tri y_i", "1 2 3 4")))
            xs, ys, sk = lam_sach(ox, oy)
        else:
            xs = sorted(day_so(" ".join(ox), "x_i"))
            ys = [0.0] * len(xs)
        mo = "Các mốc đề cho"
    if goc is not None:
        bang_m = bang_ngang_goc(range(len(xs)), goc, xs, ys) if can_y else \
            bang(["i"] + [str(i) for i in range(len(xs))], [[r"\text{chỉ số gốc}"] + [str(j) for j in goc],
                                                           ["x_i"] + [sl(t) for t in xs]])
    else:
        bang_m = bang_ngang(range(len(xs)), xs, ys) if can_y else \
            bang(["i"] + [str(i) for i in range(len(xs))], [["x_i"] + [sl(t) for t in xs]])
    return xs, ys, mo + f" (đánh số lại $i=0..{len(xs) - 1}$):\n" + bang_m + "\n", xbar


def gk_vandermonde(hoi, D, mau, tt_):
    xs, _, mo, _ = chon_moc(hoi, D, 5, can_y=False)
    n = len(xs) - 1
    if n < 1:
        raise LoiDuLieu("Vandermonde can it nhat 2 moc.")
    Vm = np.vander(np.array(xs, dtype=float), increasing=True)
    hieu, tich = [], 1.0
    rows = []
    for i in range(n):
        hang_ = [str(i), sl(xs[i])]
        for j in range(1, n + 1):
            if j > i:
                v = xs[j] - xs[i]
                hieu.append(v)
                tich *= v
                hang_.append(so(v))
            else:
                hang_.append("")
        rows.append(hang_)
    KT["vandermonde: det vs numpy"] = abs(tich - float(np.linalg.det(Vm))) / max(1.0, abs(tich))
    ma = r"\begin{bmatrix}" + r"\\".join("&".join(so(v) for v in h_) for h_ in Vm) + r"\end{bmatrix}"
    h = nw.cach_deu(xs)
    deu = ""
    if h is not None:
        e = n * (n + 1) // 2
        sieu = 1
        for k in range(1, n + 1):
            sieu *= math.factorial(k)
        deu = (f"\nMốc cách đều $h={sl(h)}$ nên $x_j-x_i=(j-i)h$ và $\\det V=h^{{{e}}}\\prod_{{k=1}}^{{{n}}}k!="
               f"{sl(h)}^{{{e}}}\\cdot{sieu}={so(tich)}$.")
    than = L(r"""@mo@Với $n+1=@n1@$ mốc, ma trận Vandermonde $V=(x_i^{\,j})_{i,j=0}^{@n@}$ (hàng $i$: $1,x_i,\dots,x_i^{@n@}$):
\[ V=@ma@,\qquad \det V=\prod_{0\le i<j\le @n@}(x_j-x_i). \]
Các mốc đôi một phân biệt nên $\det V\ne0$, hệ $Va=y$ có nghiệm duy nhất: đa thức nội suy bậc $\le @n@$ qua $@n1@$ mốc tồn tại và duy nhất.

Bảng hiệu $x_j-x_i$ ($i<j$; hàng $i$, cột $j$):
@bang@
\goiy{nhân tất cả các ô của bảng hiệu được $\det V$.}
\[ \det V=@tich@. \]@deu@""", mo=mo, n1=n + 1, n=n, ma=ma,
             bang=bang(["i", "x_i"] + [f"j={j}" for j in range(1, n + 1)], rows), tich=so(tich), deu=deu)
    return "Định thức Vandermonde", than, f"det V = {so(tich)}"


def gk_chebyshev(hoi, D, mau, tt_):
    n = hoi.so("Bac n cua T_n", 5, nguyen=True, nho_nhat=1)
    T = [[1.0], [1.0, 0.0]]
    for k in range(1, n):
        a = T[k] + [0.0]                           # x*T_k (he so bac cao -> thap)
        b = [0.0, 0.0] + T[k - 1]
        T.append([2 * u - v for u, v in zip(a, b)])
    rows = [[f"T_{{{k}}}"] + ["0"] * (n - k) + [so(v) for v in T[k]] for k in range(n + 1)]
    ng = [math.cos((2 * i + 1) * math.pi / (2 * n)) for i in range(n)]
    KT["chebyshev: max |T_n(nghiem)|"] = max(abs(np.polyval(T[n], v)) for v in ng)
    than = L(r"""Đa thức Chebyshev $T_n(x)=\cos(n\arccos x)$, $x\in[-1,1]$. Đặt $x=\cos\theta$: từ $\cos(k+1)\theta+\cos(k-1)\theta=2\cos\theta\cos k\theta$ ta có truy hồi
\[ T_0(x)=1,\qquad T_1(x)=x,\qquad T_{k+1}(x)=2x\,T_k(x)-T_{k-1}(x). \]
Quy nạp theo $k$: $T_k$ là đa thức bậc $k$ với hệ số đầu $2^{k-1}$ ($k\ge1$); $|T_k(x)|\le1$ trên $[-1,1]$; nghiệm $x_i=\cos\frac{(2i+1)\pi}{2k}$, $i=0,\dots,k-1$.

Bảng truy hồi (hàng $k$: hệ số của $T_k$; hàng $k+1$ $=2\times$ hàng $k$ dịch trái $-$ hàng $k-1$):
@bang@
\goiy{các ô $0$ phía trên có thể để trống.}
@Tn@
Bậc $@n@$, hệ số đầu $2^{@n1@}=@dau@$. Nghiệm của $T_@ni@$:
@bang_ng@
Đa thức monic $\tilde T_@ni@=2^{1-@n@}T_@ni@$ có $\max_{[-1,1]}|\tilde T_@ni@|=2^{1-@n@}=@m@$ nhỏ nhất trong các đa thức bậc $@n@$ hệ số đầu $1$.""",
             bang=bang([""] + cot_mu(n), rows, can="l" + "r" * (n + 1)),
             Tn=da_thuc(T[n], ten=f"T_{chi(n)}(x)"), n=n, n1=n - 1, ni=chi(n), dau=sl(2 ** (n - 1)),
             bang_ng=bang(["i"] + [str(i) for i in range(n)],
                          [[r"x_i=\cos\frac{(2i+1)\pi}{" + str(2 * n) + "}"] + [so(v) for v in ng]]),
             m=so(2.0 ** (1 - n)))
    return f"Đa thức Chebyshev $T_{chi(n)}$", than, f"T_{n}: he so dau {2 ** (n - 1)}"


def gk_moc_toi_uu(hoi, D, mau, tt_):
    n = hoi.so("So moc n", 5, nguyen=True, nho_nhat=1)
    a = hoi.so("a", D["x"][0])
    b = hoi.so("b", D["x"][-1])
    if a == b:
        raise LoiDuLieu("a = b.")
    if a > b:
        a, b = b, a
    _, xm, _ = mt.moc_toi_uu(n, a, b, verbose=False)
    p, q = (a + b) / 2, (b - a) / 2
    ct = ("" if p == 0 else sl(p)) + "-" + ("" if q == 1 else sl(q)) + f"\\cos\\dfrac{{(2i+1)\\pi}}{{{2 * n}}}"
    than = L(r"""Sai số nội suy với $n$ mốc: $f(x)-P(x)=\dfrac{f^{(n)}(\xi)}{n!}\,w_n(x)$, $w_n(x)=\prod_{i=0}^{n-1}(x-x_i)$. Mốc tối ưu làm $\max_{[a,b]}|w_n|$ nhỏ nhất: chọn $w_n$ là đa thức Chebyshev monic đổi biến $x=\frac{a+b}2+\frac{b-a}2t$, tức các mốc là nghiệm của $T_n$ (sắp tăng):
\[ x_i=\frac{a+b}{2}-\frac{b-a}{2}\cos\frac{(2i+1)\pi}{2n},\quad i=0,\dots,n-1,\qquad \min\max_{[a,b]}|w_n|=\frac{(b-a)^n}{2^{2n-1}}. \]
Với $n=@n@$, $[a,b]=[@a@;\,@b@]$: $x_i=@ct@$:
@bang@
\[ x=@vec@,\qquad \max_{[a,b]}|w_@n@|=\frac{(@ba@)^{@n@}}{2^{@e@}}=@w@. \]""",
             n=n, a=sl(a), b=sl(b), ct=ct, bang=bang(["i"] + [str(i) for i in range(n)], [["x_i"] + [so(v) for v in xm]]),
             vec=vecl(xm), ba=sl(b - a), e=2 * n - 1, w=so((b - a) ** n / 2 ** (2 * n - 1)))
    return f"{n} mốc nội suy tối ưu trên $[{sl(a)};{sl(b)}]$", than, "x = " + ", ".join(so(v) for v in xm)


def gk_horner(hoi, D, mau, tt_):
    a = day_so(hoi("He so P tu bac cao xuong bac thap (vd 3 0 -2 -1)", "3 0 -2 -1"), "he so")
    while a and a[0] == 0:
        a.pop(0)
    if len(a) < 2:
        raise LoiDuLieu("da thuc bac < 1.")
    n = len(a) - 1
    cs = day_so(hoi("Diem c (co the nhieu, cach nhau khoang trang)", "2"), "c")
    k = hoi.so("Cap dao ham k (0 = chi P(c) va phep chia)", n, nguyen=True, nho_nhat=0)
    khoi, tom = [], []
    for c in cs:
        B, r, v = bang_horner_lap(a, c, k)
        Q = nw.horner_dao_ham(list(a), c, 0)[2][0][:-1]
        s = (f"Tại $c={sl(c)}$:\n{B}\n$P({sl(c)})=r_0={so(r[0])}$; thương ${' '.join(hang_tu(Q))}$, dư ${so(r[0])}$")
        if k >= 1:
            ten = "(" + ",".join(dh("P", j) for j in range(k + 1)) + ")"
            ve = "(" + r";\ ".join(f"{j}!\\,r_{chi(j)}" if j <= n else "0" for j in range(k + 1)) + ")"
            s += f";\\\\\n${ten}({sl(c)})={ve}={vecl(v)}$."
        else:
            s += "."
        khoi.append(s)
        tom.append(f"P({sl(c)}) = {so(r[0])}")
        KT[f"horner c={sl(c)}"] = max(abs(np.polyval(np.polyder(a, j) if j else a, c) - v[j]) for j in range(min(k, n) + 1))
    than = (f"Với $P(x)={da_thuc_gon(a)}$, $a=({';'.join(sl(v) for v in a)})$. Sơ đồ Horner chia $P$ cho $(x-c)$: "
            r"$b_{n-1}=a_n$, $b_{i-1}=a_i+c\,b_i$, số dư $r_0=a_0+c\,b_0=P(c)$; chia lặp thương cho $(x-c)$, "
            r"số dư lần chia thứ $j$ là $r_j=\dfrac{P^{(j)}(c)}{j!}$ nên $P^{(j)}(c)=j!\,r_j$. Bảng: hàng ``Hệ số'' là $a_i$, "
            r"hàng $c$ ghi $c\,b_{i+1}$, hàng $j$ ghi các $b_i$ sau lần chia thứ $j$ (ô khung là $r_j$)."
            + "\n\n" + "\n\n".join(khoi))
    return "Sơ đồ Horner", than, "; ".join(tom)


def gk_nhan(hoi, D, mau, tt_):
    che_do = hoi("1 nhan P(x) voi (x - c), 2 tich w(x) = (x - x_0)...(x - x_n)", "2")
    if che_do == "1":
        a = day_so(hoi("He so P tu bac cao xuong (vd 3 0 -2 -1)", "3 0 -2 -1"), "he so")
        c = day_so(hoi("c", "2"), "c")[0]
        d = nw.horner_nhan(list(a), c)
        n = len(a) - 1
        rows = [[r"\text{Hệ số }a"] + [so(v) for v in a] + [""], [f"-c\\,a\\ (c={sl(c)})", ""] + [so(-c * v) for v in a],
                [r"d=P\cdot(x-c)"] + [so(v) for v in d]]
        than = (f"Với $P(x)={da_thuc_gon(a)}$. Sơ đồ Horner nhân với $(x-c)$: "
                r"$d_{n+1}=a_n$, $d_i=a_{i-1}-c\,a_i$ ($i=n,\dots,1$), $d_0=-c\,a_0$:" + "\n"
                + bang([""] + cot_mu(n + 1), rows, can="l" + "r" * (n + 2)) + "\n"
                + da_thuc(d, ten=f"P(x)({x_tru(c)})"))
        KT["nhan (x-c) vs numpy"] = float(np.max(np.abs(np.array(d) - np.polymul(a, [1, -c]))))
        return "Nhân đa thức với $(x-c)$", than, "d = " + ", ".join(so(v) for v in d)
    xs, _, mo, _ = chon_moc(hoi, D, 6, can_y=False)
    m = len(xs)
    p = [1.0]
    rows = [[""] + [""] * m + ["1"]]
    for i, z in enumerate(xs):
        p = nw.horner_nhan(p, z)
        hang_ = [so(t) for t in p]
        if i == m - 1:
            hang_ = [ob(t) for t in hang_]
        rows.append([sl(z)] + [""] * (m - i - 1) + hang_)
    KT["tich w vs numpy.poly"] = float(np.max(np.abs(np.array(p) - np.poly(xs))))
    than = (mo + r"Bảng tích: hàng đầu là đa thức $1$, mỗi hàng sau nhân hàng trên với $(x-x_{k-1})$ (mốc ở cột đầu) bằng "
            r"Horner nhân: $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-x_{k-1}A_{k-1,l}$; hàng cuối là hệ số của $w$:" + "\n"
            + bang(["x_{k-1}"] + cot_mu(m), rows) + "\n\\goiy{các ô trống phía trên không cần ghi.}\n"
            + da_thuc(p, ten=f"w_{chi(m)}(x)"))
    return f"Tích $w_{chi(m)}(x)$", than, "w = " + ", ".join(so(v) for v in p)


def gk_lagrange(hoi, D, mau, tt_):
    xs, ys, mo, xbar = chon_moc(hoi, D, 6)
    if xbar is None:
        xb = D["xbar"][0] if D["xbar"] else xs[len(xs) // 2]
        xbar = hoi.so("xbar (diem can tinh)", xb)
    k = hoi.so("Cap dao ham k (0 = chi gia tri)", 1, nguyen=True, nho_nhat=0)
    n = len(xs) - 1
    a, Dd, bang_t, bang_c = lg.lagrange(xs, ys)
    rows = [[""] + [""] * (n + 1) + ["1"]]
    for i, p in enumerate(bang_t):
        rows.append([sl(xs[i])] + [""] * (n - i) + [so(t) for t in p])
    r, v, _ = nw.horner_dao_ham(list(a), xbar, k)
    KT["lagrange: max |P(x_i) - y_i|"] = float(np.max(np.abs(np.polyval(a, xs) - np.array(ys))))
    ni = chi(n)
    than = L(r"""@mo@Đa thức nội suy Lagrange viết qua $w_{@n1@}(x)=\prod_{j=0}^{@n@}(x-x_j)$:
\[ P_@ni@(x)=\sum_{i=0}^{@n@}\frac{y_i}{D_i}\,q^{(i)}(x),\qquad q^{(i)}(x)=\frac{w_{@n1@}(x)}{x-x_i},\qquad D_i=\prod_{j\ne i}(x_i-x_j). \]
Bảng tích (hàng cuối là hệ số của $w_{@n1@}$):
@bang_tich@
Bảng thương (hàng $i$: chia $w_{@n1@}$ cho $(x-x_i)$ bằng Horner):
@bang_thuong@
Bảng hệ số ($D_i$ là tích các ô $x_i-x_j$, $j\ne i$):
@bang_he_so@
\goiy{bảng hệ số chỉ cần ghi cột $D_i$ và $y_i/D_i$.}
Vector hệ số của $P_@ni@$ với $Y=\bigl(\frac{y_0}{D_0},\dots,\frac{y_@ni@}{D_@ni@}\bigr)$ và ma trận thương $Q$:
@YQ@
@P@
Tại $\bar x=@xb@$, tính bằng sơ đồ Horner chia@lap@:
\[ @ct@. \]""", mo=mo, n=n, n1=n + 1, ni=ni,
              bang_tich=bang(["x_{k-1}"] + cot_mu(n + 1), rows),
              bang_thuong=bang(["i", "x_i"] + cot_mu(n) + [r"\text{dư}"],
                               [[str(i), sl(xs[i])] + [so(t) for t in q] + [so(du)] for i, (q, du) in enumerate(bang_c)]),
              bang_he_so=bang(["i", "x_i", "j=0"] + [str(j) for j in range(1, n + 1)] + ["D_i", "y_i", "y_i/D_i"],
                              [[str(i), sl(xs[i])] + [r"\text{--}" if j == i else so(xs[i] - xs[j]) for j in range(n + 1)]
                               + [so(Dd[i]), sl(ys[i]), so(ys[i] / Dd[i])] for i in range(n + 1)]),
              YQ=vec_hien(a, rf"P_{ni}=Y\cdot Q"), P=da_thuc(a, ten=f"P_{ni}(x)"), xb=sl(xbar),
              lap=" lặp" if k else "", ct=cong_thuc_dh(f"P_{ni}", sl(xbar), r, v, k, xbar))
    tom = f"f({sl(xbar)}) ~ {so(v[0])}" + (f", f^({k})({sl(xbar)}) ~ {so(v[k])}" if k else "")
    return f"Đa thức nội suy Lagrange, $\\bar x={sl(xbar)}$", bo_tham_chieu(than), tom


def gk_newton(hoi, D, mau, tt_):
    xs, ys, mo, xbar = chon_moc(hoi, D, 9)
    if xbar is None:
        xb = D["xbar"][0] if D["xbar"] else xs[len(xs) // 2]
        xbar = hoi.so("xbar (diem can tinh)", xb)
    k = hoi.so("Cap dao ham k (0 = chi gia tri)", 1, nguyen=True, nho_nhat=0)
    chieu = "lui" if hoi("Chieu (t = tien, l = lui)", "t").lower().startswith("l") else "tien"
    h = nw.cach_deu(xs) if len(xs) > 1 else None
    ten = "tiến" if chieu == "tien" else "lùi"
    if h is None:                                  # moc bat ky: ty sai phan theo x
        s = newton_ty_sai_phan(list(xs), list(ys), chieu, xbar, k)
        s = re.sub(r"\\subsection\{[^\n]*\}\n", "", s).replace(r"\pp{Phương pháp.} ", "")
        r, v, _ = nw.horner_dao_ham(list(nw.newton(list(xs), nw.bang_sai_phan(list(xs), list(ys)), chieu)["b"]), xbar, k)
        tom = f"f({sl(xbar)}) ~ {so(v[0])}" + (f", f^({k})({sl(xbar)}) ~ {so(v[k])}" if k else "")
        return f"Newton {ten} (mốc bất kỳ), $\\bar x={sl(xbar)}$", bo_tham_chieu(mo + s), tom
    N = newton_deu(list(xs), list(ys), h, chieu, xbar, k)
    n = N["n"]
    tien = N["tien"]
    mo_ct = (f"Mốc cách đều $h={sl(h)}$. Đặt biến chuẩn hoá $t=\\dfrac{{x-x_{'0' if tien else 'n'}}}{{h}}="
             f"\\dfrac{{{x_tru(N['s0'])}}}{{{sl(h)}}}$. Công thức nội suy Newton {ten} bậc ${n}$ có dạng:")
    than = (mo + phan_tinh_gk("Bảng sai phân:", N["bang_sp"], mo_ct, N["sh"], N["c"], "t", N["bang_nhan"], N["Pt"],
                              tinh_tai_bien(f"P_{chi(n)}", xbar, k, N["v"], h, "t",
                                            "$" + gia_tri_t(xbar, N["s0"], h)[0] + "$")))
    v = N["v"]
    tom = f"f({sl(xbar)}) ~ {so(v[0])}" + (f", f^({k})({sl(xbar)}) ~ {so(v[k] / h ** k)}" if k else "")
    return f"Newton {ten}, $\\bar x={sl(xbar)}$", bo_tham_chieu(than), tom


def gk_khoang(hoi, D, mau, tt_):
    x, y = D["x"], D["y"]
    ybar = gk_ybar(hoi, D)
    doan = nsn.khoang_don_dieu(y)
    doi = [b for _, b, _ in doan[:-1]]
    tai_moc, kh = nsn.khoang_cach_ly(y, ybar)
    dl = max([v for v in (nsn.so_le(y), nsn.so_le([ybar])) if v is not None] or [0])
    rows = []
    for k in kh:
        a_, b_, s_ = next(dd for dd in doan if dd[0] <= k < dd[1])
        rows.append([str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]", sd(y[k] - ybar, dl), sd(y[k + 1] - ybar, dl),
                     f"[{sl(x[a_])};\\ {sl(x[b_])}]\\ \\text{{{CHIEU[s_]}}}"])
    than = ((r"Khoảng đơn điệu: xét dấu $\Delta y_i=y_{i+1}-y_i$; " + (
        f"$\\Delta y_i$ đổi dấu tại $i={','.join(map(str, doi))}$:" if doi else "$\\Delta y_i$ không đổi dấu:")) + "\n"
            + bang_don_dieu(x, y, doan) + "\n"
            + ("\\goiy{nhiều đoạn (dữ liệu nhiễu): chỉ ghi các đoạn chứa khoảng cách ly.}\n" if len(doan) > 6 else "")
            + r"Khoảng cách ly: $g_i=y_i-\bar y$ đổi dấu giữa $x_k$ và $x_{k+1}$ ($g_kg_{k+1}<0$)"
            + (", có mốc $g_i=0$ tại " + ", ".join(f"$x_{{{i}}}={sl(x[i])}$" for i in tai_moc) if tai_moc else "") + ":\n"
            + (bang(["k", r"[x_k;x_{k+1}]", r"g_k=y_k-\bar y", "g_{k+1}", r"\text{nằm trong đoạn}"], rows) if rows else
               "Không có khoảng cách ly.") + "\n" + cau_kcl(x, y, ybar, kh, tai_moc))
    return (f"Khoảng đơn điệu, khoảng cách ly của $f(x)={sl(ybar)}$", than,
            f"{len(doan)} doan don dieu, {len(kh)} khoang cach ly")


def he_spline(p, x, y, dk):
    """He so S_k (bac cao -> thap) de tinh S(xbar)."""
    n = len(x) - 1
    if p == 1:
        return [[(y[k + 1] - y[k]) / (x[k + 1] - x[k]), y[k] - (y[k + 1] - y[k]) / (x[k + 1] - x[k]) * x[k]]
                for k in range(n)]
    if p == 2:
        return sp.spline2(x, y, dk)[2]
    if dk[0][1] == dk[1][1]:
        _, _, _, Dn, _ = sp.spline_tq(x, y, 3, dk)
        return he_so_bac3(x, y, [Dn[k][2] for k in range(n + 1)])
    return sp.spline3(x, y, dk)[-1]


def gk_spline(hoi, D, mau, tt_):
    p = hoi.so("Bac spline p (1, 2, 3)", 3, nguyen=True, nho_nhat=1)
    if p > 3:
        raise LoiDuLieu("chi ho tro spline bac 1, 2, 3 (bac 4: chay interpolation/spline.py).")
    xs, ys, mo, xbar = chon_moc(hoi, D, 5)
    x, y = list(xs), list(ys)
    n = len(x) - 1
    if n < 1:
        raise LoiDuLieu("spline can it nhat 2 moc.")
    hk = [x[k + 1] - x[k] for k in range(n)]
    sk_ = [(y[k + 1] - y[k]) / hk[k] for k in range(n)]
    bang_h = bang(["k", r"[x_k;x_{k+1}]", "h_k", r"s_k=\frac{y_{k+1}-y_k}{h_k}"],
                  [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]", so(hk[k]), so(sk_[k])] for k in range(n)])
    if p == 1:
        he = he_spline(1, x, y, [])
        than = (mo + r"Spline bậc 1: trên $[x_k;x_{k+1}]$, $S_k(x)=y_k+s_k(x-x_k)=a_kx+b_k$ với $a_k=s_k$, "
                r"$b_k=y_k-s_kx_k$:" + "\n" + bang(["k", r"[x_k;x_{k+1}]", "a_k=s_k", "b_k"],
                                                   [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]", so(he[k][0]),
                                                     so(he[k][1])] for k in range(n)]))
        dk = []
    else:
        md = "S'(x0) = 0" if p == 2 else "S''(x0) = 0; S''(xn) = 0"
        bao = []
        try:
            dk = sp.doc_bien(hoi(f"Dieu kien bien ({p - 1} dieu kien, vd {md})", md), x, p, bao)
        except ValueError as e:
            raise LoiDuLieu(str(e))
        if len(dk) != p - 1:
            raise LoiDuLieu(f"spline bac {p} can {p - 1} dieu kien bien.")
        than = (mo + f"Điều kiện biên: {ten_dk(dk, x)}; $h_k=x_{{k+1}}-x_k$, $s_k=\\frac{{y_{{k+1}}-y_k}}{{h_k}}$:\n"
                + bang_h + "\n" + spline_cau("gk", p, x, y, dk, None))
        he = he_spline(p, x, y, dk)
    if xbar is not None and x[0] <= xbar <= x[-1]:
        kk = min(max(i for i in range(n) if x[i] <= xbar), n - 1)
        than += (f"\n\nTại $\\bar x={sl(xbar)}\\in[x_{{{kk}}};x_{{{kk + 1}}}]$: "
                 f"$S(\\bar x)=S_{{{kk}}}({sl(xbar)})={so(float(np.polyval(he[kk], xbar)))}$.")
    for c_, v_ in ((", Câu 20a", ""), (", Câu 20b", ""), (" (20b, Bước 4)", "")):
        than = than.replace(c_, v_)
    return f"Spline bậc {p}", bo_tham_chieu(than), f"spline bac {p}, {n} doan"


DANG_GK = {"1": "Dinh thuc Vandermonde, tinh duy nhat noi suy", "2": "Da thuc Chebyshev T_n (truy hoi, bac, he so dau)",
           "3": "n moc noi suy toi uu tren [a, b]", "4": "Horner: P(c), chia cho (x - c), dao ham cap k tai c",
           "5": "Nhan da thuc: P(x)(x - c) hoac tich w(x) = (x - x_0)...(x - x_n)",
           "6": "Lagrange (bang diem / trich m moc), f(xbar)",
           "7": "Newton tien / lui (bang diem / trich m moc), f(xbar), dao ham",
           "8": "Stirling (trich m moc le), f(xbar), f'(xbar)", "9": "Bessel (trich m moc chan), f(xbar), f'(xbar)",
           "10": "Khoang don dieu + khoang cach ly cua f(x) = ybar",
           "11": "Giai f(x) = ybar: phuong phap ham nguoc", "12": "Giai f(x) = ybar: phuong phap lap",
           "13": "Spline (ham ghep tron) bac 1, 2, 3 + dieu kien bien",
           "14": "Binh phuong toi thieu (ham thuc nghiem, sai so)"}


HAM_GK = {"1": gk_vandermonde, "2": gk_chebyshev, "3": gk_moc_toi_uu, "4": gk_horner, "5": gk_nhan,
          "6": gk_lagrange, "7": gk_newton, "8": lambda h_, D, m, t: gk_trung_tam(h_, D, m, 3),
          "9": lambda h_, D, m, t: gk_trung_tam(h_, D, m, 4), "10": gk_khoang, "11": gk_ham_nguoc,
          "12": gk_lap, "13": gk_spline, "14": gk_bptt}   # Gauss I/II bo khoi menu (nguoi dung yeu cau)


def giai_giua_ky(hoi, mau):
    """Hoi file de va tung cau, sinh than LaTeX. Tra ve (ma, tieu de, than, tom tat)."""
    D = doc_de(hoi)
    ma = re.sub(r"[^0-9A-Za-z]+", "_", hoi("Ten file loi giai giua_ky_<ten>", D["ten"])).strip("_") or "de"
    phan, tom, gt = [], [], {}
    print("\nCHON CAC CAU (Enter o 'Dang cau' = ket thuc):")
    for so_cau in "abcdefgh":
        while True:
            dang = hoi(f"Dang cau {so_cau} (Enter = het cau)", "", menu=DANG_GK)
            if not dang or dang in HAM_GK:
                break
            print(f"  -> '{dang}' khong co trong menu, chon 1..{len(DANG_GK)}.")
            if hoi.tl is not None:
                raise LoiDuLieu(f"file tra loi: dang cau '{dang}' khong co trong menu.")
        if not dang:
            break
        KT.clear()
        tieu, than, kq = HAM_GK[dang](hoi, D, mau, None)
        for k_, v in KT.items():
            print(f"  kiem tra {k_} = {v:.3g}")
        phan.append(f"\\pp{{{so_cau}.}} {than}")      # nhu dap an: 'a.' roi vao bai ngay, khong tieu de
        tom.append(f"{so_cau}) {kq}")
        print(f"  => {so_cau}) {kq}")
        for k_ in ("xbar", "ybar"):
            m_ = re.search(r"\\bar " + k_[0] + r"=([-0-9.e]+)", tieu)
            if m_:
                gt.setdefault(k_, m_.group(1))
    cac_gt = [f"$\\bar {k[0]}={gt[k]}$" for k in ("xbar", "ybar") if k in gt]
    than = mo_ta_de(D, cac_gt) + "\n\n" + "\n\n".join(phan) + "\n"
    return ma, f"LỜI GIẢI ĐỀ GIỮA KỲ MI3042 — {tex_chu(D['ten'])}", than, tom


def xuat_giua_ky(mau, tra_loi=None):
    """Che do 'gk': hoi (hoac doc file tra loi) roi ghi docs/loi_giai/giua_ky_<ten>.md (+ .tex/.pdf neu chon).
    Lan giai dau o dang Markdown; chon PDF thi giai lai (im lang) bang chinh cac tra loi da nhap."""
    global FMT
    FMT = "md"
    BANG_MD.clear()
    hoi = Hoi(tra_loi)
    try:
        ma, tieu, than, tom = giai_giua_ky(hoi, mau)
        dd = hoi("Dinh dang file loi giai (1 Markdown, 2 PDF, 3 ca hai)", "1")
    except LoiDuLieu as e:
        print(f"\nLOI DU LIEU (chua ghi file): {e}")
        sys.exit(1)
    dich = os.path.join(THU_MUC, f"giua_ky_{ma}")
    if dd in ("1", "3"):
        with open(dich + ".md", "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {tieu}\n\n" + tex_sang_md(than))
        print(f"Da ghi {dich}.md")
    if dd in ("2", "3"):
        FMT = "tex"
        with contextlib.redirect_stdout(io.StringIO()):
            _, _, than_tex, _ = giai_giua_ky(Hoi([s for _, s in hoi.ghi]), mau)
        dau = mau.split("\\begin{document}", 1)[0]
        with open(dich + ".tex", "w", encoding="utf-8", newline="\n") as f:
            f.write(dau + "\\begin{document}\n\n\\begin{center}\n{\\Large\\bfseries " + tieu + "}\n\\end{center}\n\n"
                    + than_tex + "\n\\end{document}\n")
        print(f"Da ghi {dich}.tex")
        pdf = dich_pdf(dich + ".tex")
        if pdf:
            print(f"Da dich {pdf}")
    p_tl = os.path.join(DATA, f"giua_ky_{ma}_tra_loi.txt")
    with open(p_tl, "w", encoding="utf-8", newline="\n") as f:
        f.write("# File tra loi de giua ky. Chay lai: python docs/loi_giai/sinh_loi_giai.py gk "
                f"data/giua_ky_{ma}_tra_loi.txt\n# Moi cau hoi 2 dong: dong '#' la cau hoi, dong sau la tra loi "
                "(de trong = mac dinh).\n")
        for cau, s in hoi.ghi:
            f.write(f"# {cau}\n{s}\n")
    print(f"Da luu cac tra loi vao {p_tl}")
    print("\nKET QUA:")
    for d in tom:
        print("  " + d)


# ===== MARKDOWN =====

def thay_lenh(s, ten, ham):
    """Thay moi \\ten{...} (ngoac can bang) bang ham(noi dung)."""
    out, i, mau = [], 0, "\\" + ten + "{"
    while True:
        k = s.find(mau, i)
        if k < 0:
            out.append(s[i:])
            return "".join(out)
        out.append(s[i:k])
        j = dong_ngoac(s, k + len(mau) - 1)
        out.append(ham(s[k + len(mau):j]))
        i = j + 1


def tex_sang_md(than):
    """Than tai lieu LaTeX (giua \\begin{document} va \\end{document}) -> Markdown + toan KaTeX ($...$, $$...$$).
    Bang da la token @@BANGi@@ (bang() voi FMT = 'md')."""
    than = "\n".join(d for d in than.split("\n") if not re.match(r"\s*%", d))
    than = re.sub(r"\\begin\{center\}.*?\\end\{center\}", "", than, count=1, flags=re.S)
    HT, IM, MD = [], [], []

    def giu_ht(noi, mt_=None):
        s = noi.strip().replace("\\ob{", "\\boxed{").replace("\\mbox{", "\\text{")
        if mt_:
            s = "\\begin{" + mt_ + "}\n" + s + "\n\\end{" + mt_ + "}"
        HT.append(s)
        return f"@@HT{len(HT) - 1}@@"

    than = re.sub(r"\\begin\{align\*\}(.*?)\\end\{align\*\}", lambda m: giu_ht(m.group(1), "aligned"), than, flags=re.S)
    than = re.sub(r"\\begin\{gather\*\}(.*?)\\end\{gather\*\}", lambda m: giu_ht(m.group(1), "gathered"), than,
                  flags=re.S)
    than = re.sub(r"(?<!\\)\\\[(.*?)\\\]", lambda m: giu_ht(m.group(1)), than, flags=re.S)

    def giu_im(m):
        IM.append(m.group(1).replace("\\ob{", "\\boxed{").replace("\\mbox{", "\\text{").strip())
        return f"@@IM{len(IM) - 1}@@"

    than = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", giu_im, than, flags=re.S)

    def van_ban(s, mot_dong=False):
        s = thay_lenh(s, "goiy", lambda t: f"\n\n> *▹ Gợi ý ghi: {t.strip()}*\n\n")
        s = thay_lenh(s, "section", lambda t: f"\n\n## {t.strip()}\n\n")
        s = thay_lenh(s, "subsection", lambda t: f"\n\n### {t.strip()}\n\n")
        s = thay_lenh(s, "pp", lambda t: f"\n\n**{t.strip()}** ")
        s = thay_lenh(s, "paragraph", lambda t: f"\n\n**{t.strip()}** ")
        s = thay_lenh(s, "textbf", lambda t: f"**{t}**")
        s = thay_lenh(s, "texttt", lambda t: "`" + t.replace("\\_", "_") + "`")
        s = thay_lenh(s, "emph", lambda t: f"*{t}*")
        s = thay_lenh(s, "mbox", lambda t: t)
        s = thay_lenh(s, "ob", lambda t: f"$\\boxed{{{t}}}$")
        s = s.replace("\\newline", "<br>").replace("\\thut", "<br>&emsp;&emsp;")
        s = re.sub(r"\\\\(\[[^\]]*\])?\s*", "<br>\n", s)
        s = s.replace("``", "“").replace("''", "”").replace("--", "–")
        s = re.sub(r"\\q?quad(?![a-zA-Z])", " ", s)
        s = s.replace("\\ ", " ").replace("~", " ")
        s = re.sub(r"\\(noindent|par|smallskip|medskip|bigskip)(?![a-zA-Z])", "", s)
        for a, b in ((r"\%", "%"), (r"\&", "&"), (r"\#", "#"), (r"\{", "{"), (r"\}", "}"), (r"\textbackslash{}", "\\"),
                     (r"\_", "\\_"), (r"\$", "\\$")):
            s = s.replace(a, b)
        if mot_dong:
            s = re.sub(r"\s*\n\s*", " ", s).strip()

        def ht(m):
            noi = HT[int(m.group(1))]
            if mot_dong:
                return "<br>$\\displaystyle " + " ".join(noi.split()) + "$<br>"
            return "\n\n$$\n" + noi + "\n$$\n\n"

        s = re.sub(r"@@HT(\d+)@@", ht, s)
        return re.sub(r"@@IM(\d+)@@", lambda m: "$" + IM[int(m.group(1))] + "$", s)

    def giu_md(s):
        MD.append(s)
        return f"\n\n@@MD{len(MD) - 1}@@\n\n"

    def thuat_toan(m):
        tieu, noi = m.group(1), m.group(2)
        con = []

        def giu_con(mm):
            con.append(mm.group(1))
            return f"@@CON{len(con) - 1}@@"

        noi = re.sub(r"\\begin\{con\}(.*?)\\end\{con\}", giu_con, noi, flags=re.S)
        out = [f"**Thuật toán: {van_ban(tieu, True)}**", ""]
        for muc in re.split(r"\\item\[", noi)[1:]:
            nhan, _, nd = muc.partition("]")
            phan = re.split(r"@@CON(\d+)@@", nd)
            out.append(f"- **{nhan.strip()}** " + van_ban(phan[0], True))
            for i in range(1, len(phan), 2):
                for muc2 in re.split(r"\\item\[", con[int(phan[i])])[1:]:
                    nhan2, _, nd2 = muc2.partition("]")
                    out.append(f"  - **{nhan2.strip()}** " + van_ban(nd2, True))
                if phan[i + 1].strip():
                    out.append("  " + van_ban(phan[i + 1], True))
        return giu_md("\n".join(out))

    def ket_luan(m):
        nd = re.sub(r"\n{3,}", "\n\n", van_ban(m.group(1)).strip())
        dong = ("**Kết luận.**" + ("\n\n" if nd.startswith("$$") else " ") + nd).split("\n")
        return giu_md("\n".join("> " + d if d.strip() else ">" for d in dong))

    def liet_ke(m):
        muc = re.split(r"\\item(?![a-zA-Z])\s*", m.group(1))[1:]
        return giu_md("\n".join("- " + van_ban(t, True) for t in muc))

    than = re.sub(r"\\begin\{thuattoan\}\{(.*?)\}(.*?)\\end\{thuattoan\}", thuat_toan, than, flags=re.S)
    than = re.sub(r"\\begin\{ketluan\}(.*?)\\end\{ketluan\}", ket_luan, than, flags=re.S)
    than = re.sub(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", liet_ke, than, flags=re.S)
    than = van_ban(than)
    than = re.sub(r"@@MD(\d+)@@", lambda m: MD[int(m.group(1))], than)
    than = re.sub(r"[ \t]*@@BANG(\d+)@@[ \t]*", lambda m: "\n\n" + BANG_MD[int(m.group(1))] + "\n\n", than)
    than = "\n".join(re.sub(r"(?<=\S) {2,}(?=\S)", " ", d.rstrip()) for d in than.split("\n"))
    than = re.sub(r"\n{3,}", "\n\n", than).strip() + "\n"
    con_lai = sorted(set(re.findall(r"\\[a-zA-Z]+", re.sub(r"\$\$.*?\$\$|\$.*?\$", "", than, flags=re.S))))
    if con_lai:
        print("  Canh bao (Markdown): lenh LaTeX chua chuyen ngoai cong thuc:", ", ".join(con_lai))
    return than


# ===== GHEP =====

HAM_CAU = {3: cau3, 4: cau4, 5: cau5, 7: cau7, 8: cau8, 9: cau9, 11: cau11, 12: cau12, 13: cau13, 14: cau14,
           16: cau16, 17: cau17, 19: cau19, 21: cau21, 23: cau23}
TAT_CA = list(range(3, 24))


def tach_mau(mau):
    """Mau -> (dau: preamble + tieu de + quy uoc, {so cau: khoi}, duoi: \\end{document})."""
    phan = re.split(r"(?m)^%=+ cau (\d+)\s*\n", mau)
    dau = phan[0]
    khoi = {int(phan[i]): phan[i + 1] for i in range(1, len(phan), 2)}
    cuoi = max(khoi)
    khoi[cuoi], _, duoi = khoi[cuoi].partition("\\end{document}")
    return dau, khoi, "\\end{document}" + duoi


def pham_vi(cac):
    return "Câu 3 -- Câu 23" if cac == TAT_CA else "Câu " + ", ".join(map(str, cac))


def dich_pdf(tex):
    """Dich bang xelatex (2 lan) trong thu muc docs/loi_giai. Tra ve duong dan PDF hoac None."""
    xl = shutil.which("xelatex")
    if not xl:
        print("  Khong thay xelatex: tu dich bang 'xelatex loi_giai_bai_tap.tex' (2 lan) trong docs/loi_giai.")
        return None
    pdf = os.path.splitext(tex)[0] + ".pdf"
    lenh = [xl, "-interaction=nonstopmode", "-halt-on-error", os.path.basename(tex)]
    lan_ok = 0
    for _ in range(4):                             # xelatex (TinyTeX) doi khi crash o lan dau: chay lai
        kq = subprocess.run(lenh, cwd=os.path.dirname(tex), capture_output=True, text=True, errors="replace")
        if kq.returncode == 0:
            lan_ok += 1
            if lan_ok == 2:
                return pdf
    log = os.path.splitext(tex)[0] + ".log"
    print(f"  Loi dich PDF (xem {log}). Neu file PDF dang mo trong trinh xem khac thi dong lai roi chay lai.")
    return None


def main():
    global FMT, DATA, CH
    sys.stdout.reconfigure(errors="backslashreplace")
    args = sys.argv[1:]
    if "--data" in args:
        i = args.index("--data")
        if i + 1 >= len(args):
            print("Loi: --data can ten thu muc.")
            sys.exit(2)
        DATA = os.path.abspath(args[i + 1])
        del args[i:i + 2]
    dinh_dang = None
    cau = []
    if "gk" in [a.lower() for a in args]:          # che do de giua ky: hoi file de, tung cau -> giua_ky_<ten>.md
        args = [a for a in args if a.lower() != "gk"]
        tra_loi = None
        if args:                                   # file tra loi (luu tu lan chay truoc): moi dong 1 tra loi
            try:
                with open(args[0], encoding="utf-8-sig") as f:
                    tra_loi = [d for d in f.read().splitlines() if not d.startswith("#")]
            except OSError:
                print(f"Loi: khong mo duoc file tra loi '{args[0]}'.")
                sys.exit(2)
        print(f"SINH LOI GIAI DE GIUA KY (du lieu trong {DATA})")
        xuat_giua_ky(open(os.path.join(THU_MUC, "mau_loi_giai.tex"), encoding="utf-8").read(), tra_loi)
        return
    for a in args:
        if a.lower() in ("md", "markdown", "1"):
            dinh_dang = "md"
        elif a.lower() in ("tex", "latex", "pdf", "2"):
            dinh_dang = "tex"
        elif a.isdigit():
            cau.append(int(a))
        else:
            print(f"Loi: doi so {a!r} khong hieu (dung: md | tex, so cau, --data <thu muc>).")
            sys.exit(2)
    print(f"SINH LOI GIAI CAU 3-23 TU DU LIEU TRONG {DATA}")
    if dinh_dang is None:
        print("Dinh dang:")
        print("  1. Markdown (docs/loi_giai/loi_giai_bai_tap.md)")
        print("  2. TeX (docs/loi_giai/loi_giai_bai_tap.tex) + dich PDF bang xelatex")
        try:
            s = input("Chon dinh dang (VD [1]): ").strip()
        except EOFError:
            s = ""
        dinh_dang = "tex" if s == "2" or s.lower() in ("tex", "pdf") else "md"
        if not cau:
            try:
                s = input("Cac cau can sinh, cach nhau boi khoang trang (VD [tat ca]): ").strip()
            except EOFError:
                s = ""
            cau = [int(t) for t in re.findall(r"\d+", s)]
    sai = [c for c in cau if c not in TAT_CA]
    if sai:
        print(f"Loi: chi co Cau 3..23 (khong co {sai}).")
        sys.exit(2)
    cac = sorted(set(cau)) or TAT_CA
    FMT = dinh_dang
    CAU_CO.update(cac)
    p_ch = os.path.join(DATA, TEN_CAU_HINH)
    if os.path.isfile(p_ch):
        CH = configparser.ConfigParser(interpolation=None, comment_prefixes=(";", "#"), inline_comment_prefixes=None)
        with open(p_ch, encoding="utf-8-sig") as f:
            CH.read_file(f)
    else:
        print(f"  (khong co {p_ch}: dung file / tham so mac dinh)")
    loi, kt = [], {}
    for c in cac:
        if c not in HAM_CAU:
            continue
        KT.clear()
        try:
            HAM_CAU[c]()
        except LoiDuLieu as e:
            loi.append(f"Cau {c}: {e}")
        kt.update({f"Cau {c}: {k}": v for k, v in KT.items()})
    KT.clear()
    KT.update(kt)
    if loi:
        print("\nLOI DU LIEU (chua ghi file loi giai):")
        for d in loi:
            print("  " + d)
        sys.exit(1)
    mau = open(os.path.join(THU_MUC, "mau_loi_giai.tex"), encoding="utf-8").read()
    dau, khoi, duoi = tach_mau(mau)
    V["pham_vi"] = pham_vi(cac)
    tex = dau + "".join(f"%{'=' * 69} cau {c}\n" + khoi[c] for c in cac) + duoi
    dung = set()

    def thay(m):
        k = m.group(1)
        if k not in V:
            sys.exit(f"Loi: mau can khoa <<{k}>> nhung chua sinh.")
        dung.add(k)
        return V[k]

    tex = re.sub(r"<<([A-Za-z0-9_]+)>>", thay, tex)
    thua = sorted(set(V) - dung)
    if thua:
        print("  Canh bao: khoa sinh ra nhung khong dung:", ", ".join(thua))
    if KT:
        print("KIEM TRA (khong dua vao loi giai): max sai lech so voi numpy / scipy")
        for k, v in KT.items():
            print(f"  {k} = {v:.3g}")
    if FMT == "tex":
        dich = os.path.join(THU_MUC, "loi_giai_bai_tap.tex")
        with open(dich, "w", encoding="utf-8", newline="\n") as f:
            f.write(tex)
        print(f"Da ghi {dich}")
        pdf = dich_pdf(dich)
        if pdf:
            print(f"Da dich {pdf}")
    else:
        than = tex.split("\\begin{document}", 1)[1].split("\\end{document}", 1)[0]
        md = ("# LỜI GIẢI BÀI TẬP PHƯƠNG PHÁP SỐ (MI3042)\n\n"
              f"*{V['pham_vi'].replace('--', '–')} (Chương 1: Xấp xỉ hàm số)*\n\n" + tex_sang_md(than))
        dich = os.path.join(THU_MUC, "loi_giai_bai_tap.md")
        with open(dich, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        print(f"Da ghi {dich}")


if __name__ == "__main__":
    main()
