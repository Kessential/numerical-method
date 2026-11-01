"""
DA THUC NOI SUY LAGRANGE
Thuat toan: docs/thuat_toan/lagrange.md

Bo diem (x_i, y_i), i = 0..n;  P_n(x) = a_n*x^n + ... + a_1*x + a_0  (a_i la he so cua x^i)
Vector he so in tu BAC CAO xuong BAC THAP: a = (a_n, ..., a_0).
Muc dich -> bien the duoc chon:
  1. He so P_n(x) dang chinh tac -> bang tich + bang chia (muc 1)
  2. Gia tri P_n(xbar)           -> chi chon 2: cong thuc truc tiep (muc 2);
                                    co chon 1 hoac 3: lay tu Horner, muc 2 dung de kiem tra
  3. Dao ham cap 0..k tai xbar   -> muc 1 + Horner chia lap (muc 3)

Cach chay:
  python interpolation/lagrange.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/lagrange.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi:
                                                      muc dich / x / y / xbar / k (dong x, y duoc co nhan 'x', 'y')
  python interpolation/lagrange.py data/<file>.csv -> file chi chua bang: 2 hang hoac 2 cot x, y
                                                      (.xlsx can pandas + openpyxl); cac cau con lai nhap tu ban phim
O tach bang khoang trang, ';' hoac tab. Dau ',' giua hai chu so = dau thap phan.
"""

import csv
import math
import re
import sys
import unicodedata

import numpy as np

# ===== CAC HAM CONG CU =====

def fmt(v, spec=None, nho=1e-12):
    """So tinh ra: toi da 6 chu so thap phan, bo so 0 thua; |v| < 1e-4 -> dang e (9.14e-04); |v| < nho -> 0
    (danh gia sai so: nho = 0 de khong mat so rat nho).
    spec (vd '.10g') -> in theo spec (so lieu de cho giu nguyen)."""
    if v == 0 or abs(v) < nho:
        return "0"
    if spec:
        return format(v, spec)
    if abs(v) < 1e-4:
        m, e = format(v, ".6e").split("e")
        return m.rstrip("0").rstrip(".") + "e" + e
    s = format(v, ".6f").rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def fmt_bang(v):
    """So trong bang: nhu fmt."""
    return fmt(v)


def vec(v, spec=None):
    """In vector dang [v0, v1, ...] (so theo fmt; so lieu de cho: spec = '.10g')."""
    return "[" + ", ".join(fmt(x, spec) for x in v) + "]"


def da_thuc_str(he_so, bien="x"):
    """Chuoi da thuc tu he so bac cao -> thap (he so theo fmt; he so dang e -> them '*')."""
    n = len(he_so) - 1
    parts = []
    for i, a in enumerate(he_so):
        if abs(a) < 1e-12:
            continue
        k = n - i
        mag = fmt(abs(a))
        if k == 0:
            term = mag
        else:
            mu = bien if k == 1 else f"{bien}^{k}"
            term = mu if mag == "1" else (f"{mag}*{mu}" if "e" in mag else f"{mag}{mu}")
        parts.append(("-" if a < 0 else "+", term))
    if not parts:
        return "0"
    s = ("-" if parts[0][0] == "-" else "") + parts[0][1]
    for sign, term in parts[1:]:
        s += f" {sign} {term}"
    return s


def in_bang(cot, hang, le="  ", khung=None, nhan_khung=""):
    """In bang; o la so / chuoi / None (trong); hang = None -> ke ngang. Do rong tung cot tu dong.
    khung = j: ke '|' truoc cot j (phan ben phai la ma tran duoc khoanh), nhan_khung in phia tren phan do."""
    S = [None if h is None else ["" if v is None else v if isinstance(v, str) else fmt_bang(v) for v in h]
         for h in hang]
    so_cot = max([len(cot)] + [len(h) for h in S if h])
    rong = [len(cot[j]) if j < len(cot) else 0 for j in range(so_cot)]
    for h in S:
        for j, s in enumerate(h or []):
            rong[j] = max(rong[j], len(s))
    rong = [r + 2 for r in rong]

    def dong(o):
        o = list(o) + [""] * (so_cot - len(o))
        if khung is None:
            return le + "".join(f"{s:>{r}}" for s, r in zip(o, rong))
        return (le + "".join(f"{s:>{r}}" for s, r in zip(o[:khung], rong[:khung])) + " |"
                + "".join(f"{s:>{r}}" for s, r in zip(o[khung:], rong[khung:])))

    if khung is not None and nhan_khung:
        print(le + " " * (sum(rong[:khung]) + 2) + f"{nhan_khung:^{sum(rong[khung:])}}".rstrip())
    print(dong(cot))
    ke = le + "-" * sum(rong) if khung is None else le + "-" * sum(rong[:khung]) + "-+" + "-" * sum(rong[khung:])
    print(ke)
    for h in S:
        print(ke if h is None else dong(h))


def so_ngoac(v):
    """So theo fmt; so am dat trong ngoac."""
    s = fmt(v)
    return f"({s})" if s.startswith("-") else s


def kiem(nhan, sai):
    """1 dong KIEM TRA, can thang dau '='."""
    print(f"  {nhan:<62} = {sai:.2e}")


def cot_mu(bac, bien="x"):
    """Ten cot bac cao -> thap: x^bac, ..., x, 1."""
    return [f"{bien}^{e}" if e > 1 else (bien if e == 1 else "1") for e in range(bac, -1, -1)]


def doc_o(o):
    """Buoc 0: 1 o -> (so | None, ghi chu sua, ly do loai | None)."""
    s = o.strip()
    if not s:
        return None, [], "o rong"
    sua = []
    t = re.sub("[−–—]", "-", s)                       # dau tru Unicode (copy tu PDF) -> '-'
    if t != s:
        sua.append("doi dau tru Unicode thanh '-'")
    t2 = re.sub(r"(?<=\d),(?=\d)", ".", t)            # ',' thap phan -> '.'
    if t2 != t:
        sua.append("doi dau ',' thap phan thanh '.'")
    t = t2
    try:
        v = float(t)
    except ValueError:
        la = re.sub(r"[0-9eE+\-.]", "", t)
        if any(ch.isalpha() for ch in la) or not re.search(r"\d", t):
            return None, sua, "o chu"
        try:
            v = float(re.sub(r"[^0-9eE+\-.]", "", t))   # bo ky tu la khong phai chu (*, khoang trang dac biet...)
        except ValueError:
            return None, sua, "khong doc duoc so"
        sua.append(f"bo ky tu la {la!r}")
    if not math.isfinite(v):
        return None, sua, "NaN" if v != v else "vo cung"
    return v, sua, None


def tach_o(dong):
    """Tach 1 dong thanh cac o. Co ';' hoac tab -> giu o rong; nguoc lai tach theo khoang trang."""
    dong = re.sub(r",(?!\d)|(?<!\d),", " ", dong).strip()   # ',' khong nam giua 2 chu so -> phan tach
    if not re.search(r"[;\t]", dong):
        return dong.split()
    o = []
    for phan in re.split(r"[;\t]", dong):
        o += phan.split() or [""]
    while o and o[0] == "":                            # ';' thua o hai dau
        o.pop(0)
    while o and o[-1] == "":
        o.pop()
    return o


NHAN = re.compile(r"^[xy](_?i)?\s*[:=]?$", re.I)


def bo_nhan(o):
    """Bo nhan dau hang ('x', 'y', 'x_i:', 'y =' ...)."""
    if o and NHAN.match(o[0].strip()):
        o = o[1:]
        if o and o[0].strip() in (":", "="):
            o = o[1:]
    return o


def doc_day_so(text, ten, bao):
    """Day so (xbar, k): bo o loi va ghi vao bao."""
    so = []
    for o in tach_o(text):
        v, sua, loai = doc_o(o)
        bao += [f"{ten}: {g}" for g in sua]
        if loai:
            bao.append(f"{ten}: loai {o!r} ({loai})")
        else:
            so.append(v)
    return so


def ten_cot(j):
    """Chi so cot 0, 1, ... -> ten cot Excel A, B, ..., Z, AA, ..."""
    s, j = "", j + 1
    while j:
        j, r = divmod(j - 1, 26)
        s = chr(65 + r) + s
    return s


def tach_o_giu(dong):
    """Tach 1 dong file bang thanh o, giu dung vi tri cot: tab / ';' / ',' (csv) / khoang trang."""
    if "\t" in dong:
        return [o.strip() for o in dong.split("\t")]
    if ";" in dong:
        return [o.strip() for o in dong.split(";")]
    if re.search(r",(?!\d)|(?<!\d),", dong):
        return [o.strip() for o in next(csv.reader([dong]))]
    return dong.split()


def la_file_bang(duong_dan):
    """File la bang so lieu (.csv/.xlsx/.xls, hoac .txt co >= 5 dong bat dau bang 2 o so)? Nguoc lai: file tra loi."""
    if duong_dan.lower().endswith((".csv", ".xlsx", ".xls")):
        return True
    with open(duong_dan, encoding="utf-8-sig") as f:
        dong = [d for d in f.read().splitlines() if d.strip()]
    dem = 0
    for d in dong:
        o = tach_o_giu(d)
        dem += len(o) >= 2 and doc_o(o[0])[0] is not None and doc_o(o[1])[0] is not None
    return dem >= 5 and 2 * dem >= len(dong)


def doc_luoi_file(duong_dan):
    """Doc file thanh luoi o (chuoi), giu nguyen dong / cot. Tra ve [(ten sheet | None, luoi)]."""
    if duong_dan.lower().endswith((".xlsx", ".xls")):
        try:
            import pandas as pd
            sheets = pd.read_excel(duong_dan, header=None, dtype=str, sheet_name=None)
        except ImportError as e:
            raise ValueError(f"doc file Excel can pandas + openpyxl ({e}); hay luu bang thanh .csv.")
        return [(ten, [["" if not isinstance(v, str) else v for v in h] for h in df.values.tolist()])
                for ten, df in sheets.items()]
    with open(duong_dan, encoding="utf-8-sig") as f:
        return [(None, [tach_o_giu(d) for d in f.read().splitlines()])]


TEN_TS = {"x": "xbar", "xbar": "xbar", "y": "ybar", "ybar": "ybar"}


def phan_tich_luoi(luoi):
    """Tim cot so lieu x, y (hoac chi 1 day y), dong tieu de, tham so xbar / ybar ghi trong file.
    Bang 2 hang (x / y) duoc xoay thanh 2 cot. Tra ve dict, hoac None neu khong co bang so."""
    so_cot = max((len(h) for h in luoi), default=0)
    # o = (noi dung, ten dong / cot cua o theo chieu doc so lieu, ten o Excel)
    O = [[(h[j] if j < len(h) else "", str(i + 1), ten_cot(j), f"{ten_cot(j)}{i + 1}") for j in range(so_cot)]
         for i, h in enumerate(luoi)]
    la_so = lambda o: doc_o(o[0])[0] is not None
    cot = [j for j in range(so_cot) if sum(la_so(h[j]) for h in O) >= 3]
    vi_tri, ten_day = "dong", 2                    # moi cap nam tren 1 dong; ten cot so lieu = phan chu
    if not cot:                                    # bang 2 hang x / y -> xoay
        O = [[(o[0], o[2], o[1], o[3]) for o in c] for c in zip(*O)] if O else []
        cot = [j for j in range(len(O[0]) if O else 0) if sum(la_so(h[j]) for h in O) >= 3]
        vi_tri = "cot"
        if not cot:
            return None
    cx, cy = (cot[0], cot[1]) if len(cot) >= 2 else (None, cot[0])
    dau = min(i for i, h in enumerate(O) if la_so(h[cy]) or (cx is not None and la_so(h[cx])))
    ox, oy, so, trong, cho = [], [], [], [], []
    for i in range(dau, len(O)):
        a = O[i][cx][0] if cx is not None else ""
        b = O[i][cy][0]
        if not a.strip() and not b.strip():
            cho.append(O[i][cy][1])                # dong trong: chi bao neu con so lieu phia sau
            continue
        trong += cho
        cho = []
        ox.append(a)
        oy.append(b)
        so.append(O[i][cy][1])
    tieu_de = lambda j: O[dau - 1][j][0].strip() if dau > 0 and j is not None else ""
    ts = {}
    for i, h in enumerate(O):                      # tham so: nhan x / x_bar / y / y_bar ngoai cac cot so lieu
        for j, o in enumerate(h):
            if j in cot:
                continue
            k = TEN_TS.get(re.sub(r"[\s_\-:=̄̅¯]", "", unicodedata.normalize("NFD", o[0]).lower()))
            if not k or k in ts:
                continue
            ke = ([h[j + 1]] if j + 1 < len(h) else []) + ([O[i + 1][j]] if i + 1 < len(O) else [])
            for gt in ke:
                v = doc_o(gt[0])[0]
                if v is not None:
                    ts[k] = (v, gt[3], o[0].strip())
                    break
    return dict(x=ox, y=oy, so=so, vi_tri=vi_tri, trong=trong, ts=ts, so_day=len(cot), co_x=cx is not None,
                ten_x=tieu_de(cx), ten_y=tieu_de(cy),
                day_x=None if cx is None else O[dau][cx][ten_day], day_y=O[dau][cy][ten_day])


def sinh_x(n_moc, nhap, bao):
    """File chi co day y: sinh n_moc moc x cach deu / moc toi uu tren [a, b]."""
    print("  File chi co 1 day so (y) -> sinh moc x:")
    print("    1. Cach deu tren [a, b]: x_i = a + i(b - a)/n")
    print("    2. Moc toi uu tren [a, b], thu tu theo cong thuc (giam dan): "
          "x_i = (a+b)/2 + (b-a)/2 cos((2i+1)pi/(2N))")
    print("    3. Moc toi uu tren [a, b], sap tang dan")
    cach = doc_day_so(nhap("  Cach sinh x", "1"), "cach sinh x", bao)
    if len(cach) != 1 or cach[0] not in (1, 2, 3):
        raise ValueError("cach sinh x phai la 1, 2 hoac 3.")
    ab = doc_day_so(nhap("  Doan [a, b]", "0 1"), "doan [a, b]", bao)
    if len(ab) != 2 or ab[0] == ab[1]:
        raise ValueError("doan [a, b] can 2 so khac nhau.")
    a, b = sorted(ab)
    if cach[0] == 1:
        if n_moc < 2:
            raise ValueError("can it nhat 2 gia tri y.")
        return [a + i * (b - a) / (n_moc - 1) for i in range(n_moc)], f"cach deu tren [{a:.10g}, {b:.10g}]"
    x = [(a + b) / 2 + (b - a) / 2 * math.cos((2 * i + 1) * math.pi / (2 * n_moc)) for i in range(n_moc)]
    if cach[0] == 3:
        return x[::-1], f"moc toi uu tren [{a:.10g}, {b:.10g}], tang dan (y_0 ghep voi moc nho nhat)"
    return x, f"moc toi uu tren [{a:.10g}, {b:.10g}], giam dan theo cong thuc (y_0 ghep voi moc lon nhat)"


def doc_bang_file(duong_dan, nhap, bao):
    """Doc bang so lieu tu file va in khoi DOC FILE de nguoi dung xac nhan; nhieu sheet -> chon sheet.
    Tra ve dict: x, y (o goc), so (so dong / ten cot tung cap), vi_tri, ts = {xbar | ybar: (gia tri, o, nhan)}."""
    bang = []
    for ten, luoi in doc_luoi_file(duong_dan):
        kq = phan_tich_luoi(luoi)
        if kq:
            bang.append((ten, kq))
    if not bang:
        raise ValueError(f"file '{duong_dan}' khong co bang so lieu (can it nhat 3 o so tren 1 cot / hang).")
    print(f"\nDOC FILE: {duong_dan}")
    if len(bang) > 1:
        print(f"  File co {len(bang)} sheet co so lieu:")
        for s, (ten, kq) in enumerate(bang, 1):
            ts = ", ".join(f"{k} = {v[0]:.10g}" for k, v in kq["ts"].items()) or "khong co tham so"
            print(f"    {s}. sheet '{ten}': {len(kq['y'])} {kq['vi_tri']} so lieu, {ts}")
        chon = doc_day_so(nhap("  Chon sheet", "1"), "sheet", bao)
        if len(chon) != 1 or chon[0] != int(chon[0]) or not 1 <= chon[0] <= len(bang):
            raise ValueError(f"sheet phai la 1 so nguyen trong 1..{len(bang)}.")
        ten, kq = bang[int(chon[0]) - 1]
    else:
        ten, kq = bang[0]
    if ten is not None:
        print(f"  sheet '{ten}'")
    vt, so = kq["vi_tri"], kq["so"]
    day = "cot" if vt == "dong" else "hang"
    ten_y = f"{day} y = {kq['day_y']}" + (f" ('{kq['ten_y']}')" if kq["ten_y"] else "")
    if kq["co_x"]:
        print(f"  {day} x = {kq['day_x']}" + (f" ('{kq['ten_x']}')" if kq["ten_x"] else "")
              + f", {ten_y}, {vt} {so[0]}..{so[-1]}: {len(so)} cap so")
    else:
        print(f"  {ten_y}, {vt} {so[0]}..{so[-1]}: {len(so)} gia tri")
    if kq["so_day"] > 2:
        print(f"  (file co {kq['so_day']} {day} so, dung 2 {day} dau)")
    if kq["trong"]:
        print(f"  bo qua {vt} trong: {', '.join(kq['trong'])}")
    if kq["ts"]:
        print("  tham so trong file: " + ", ".join(f"{k} = {v[0]:.10g} (o {v[1]}, nhan '{v[2]}')"
                                                    for k, v in kq["ts"].items()))
    else:
        print("  khong thay tham so xbar / ybar trong file")
    if not kq["co_x"]:
        x, mo_ta = sinh_x(len(kq["y"]), nhap, bao)
        kq["x"] = [f"{v:.12g}" for v in x]
        print(f"  x: {mo_ta}")
    return kq


def hoi_moc_trung(xv, cap, tb, vi_tri):
    """Moc trung chenh lon (nhap tu ban phim): hoi 1 = giu dau, 2 = giu sau, 3 = trung binh, 0 = dung; Enter = 1."""
    print(f"Moc trung x = {xv:.10g}: " + ", ".join(f"y = {yv:.10g} ({vi_tri} {j})" for yv, j in cap)
          + f", trung binh {tb:.10g}")
    for so, ten in ((1, "giu gia tri dau"), (2, "giu gia tri sau"), (3, "lay trung binh"), (0, "dung")):
        print(f"  {so}. {ten}")
    try:
        s = input("Chon (VD [1]): ").strip()
    except EOFError:
        s = ""
    return int(s) if s in ("0", "1", "2", "3") else 1


def lam_sach(ox, oy, vi_tri, bao, so=None, chon=None):
    """Buoc 0: cap o (x, y) -> x, y sach, phan biet, sap tang. Ghi bao cao vao bao; loi -> ValueError."""
    if len(ox) != len(oy):
        raise ValueError(f"hang x co {len(ox)} o, hang y co {len(oy)} o -> khong ghep cap duoc.")
    sua, diem = {}, []
    for j, a, b in zip(so or range(1, len(ox) + 1), ox, oy):   # so: so dong / cot goc trong file
        vx, sx, lx = doc_o(a)
        vy, sy, ly = doc_o(b)
        for ten, ds in (("x", sx), ("y", sy)):
            for g in ds:
                sua.setdefault(f"{ten}: {g}", []).append(j)
        if lx or ly:
            ly_do = ", ".join(f"{t} = {o!r}: {l}" for t, o, l in (("x", a, lx), ("y", b, ly)) if l)
            bao.append(f"loai cap {vi_tri} {j} ({ly_do})")
        else:
            diem.append((vx, vy, j))
    thu_tu = sorted(sua.items(), key=lambda m: m[0][0])            # gom ghi chu cua x truoc, y sau
    bao[:0] = [f"{g} ({vi_tri} {', '.join(map(str, ds))})" for g, ds in thu_tu]
    if not diem:
        raise ValueError("khong con diem nao hop le.")

    eps_y = 1e-3 * max(1.0, max(abs(p[1]) for p in diem))
    nhom = {}
    for xv, yv, j in diem:
        nhom.setdefault(xv, []).append((yv, j))
    gop = []
    for xv, cap in nhom.items():
        ys = [c[0] for c in cap]
        if len(ys) == 1:
            gop.append((xv, ys[0]))
        elif max(ys) == min(ys):
            bao.append(f"moc trung x = {xv:.10g} ({len(ys)} lan, cung y = {ys[0]:.10g}) -> giu 1")
            gop.append((xv, ys[0]))
        elif max(ys) - min(ys) <= eps_y:
            tb = sum(ys) / len(ys)
            bao.append(f"moc trung x = {xv:.10g}, y = {vec(ys, '.10g')} chenh {max(ys) - min(ys):.3g} <= eps_y = "
                       f"{eps_y:.3g} -> lay trung binh y = {tb:.10g}")
            gop.append((xv, tb))
        else:
            tb = sum(ys) / len(ys)
            k = chon(xv, cap, tb, vi_tri) if chon else 1   # file / khong co ban phim -> giu gia tri dau
            nguon = ", ".join(f"y = {yv:.10g} ({vi_tri} {j})" for yv, j in cap)
            if k == 0:
                raise ValueError(f"moc trung x = {xv:.10g}: {nguon} chenh {max(ys) - min(ys):.3g} > eps_y = "
                                 f"{eps_y:.3g} -> dung theo lua chon.")
            yv = ys[0] if k == 1 else ys[-1] if k == 2 else tb
            ten = {1: "giu gia tri dau", 2: "giu gia tri sau", 3: "lay trung binh"}[k]
            bao.append(f"moc trung x = {xv:.10g}: {nguon} chenh {max(ys) - min(ys):.3g} > eps_y = {eps_y:.3g}"
                       f" -> {ten} y = {yv:.10g}")
            gop.append((xv, yv))
    x_cu = [p[0] for p in gop]
    gop.sort()
    if [p[0] for p in gop] != x_cu:
        bao.append("sap lai cac moc theo x tang dan")
    return [p[0] for p in gop], [p[1] for p in gop]


def log_E(x, xbar):
    """log(|w_(n+1)(xbar)| / (n+1)!) tinh qua log de khong tran so; -inf neu xbar trung moc."""
    if any(xbar == xi for xi in x):
        return -math.inf
    return sum(math.log(abs(xbar - xi)) for xi in x) - math.lgamma(len(x) + 1)


# ===== THUAT TOAN =====
# Vector trong code luu tu bac cao -> thap (giong luc in); dao nguoc thanh A voi A[i] = a_i
# (he so cua x^i) de viet dung chi so nhu trong .md.

def horner_chia(a, c):
    """Muc 1, horner.md: P(x) = (x - c)Q(x) + r. Tra ve (Q bac cao -> thap, r)."""
    n = len(a) - 1
    A = a[::-1]
    if n == 0:
        return [], A[0]
    B = [0.0] * n
    B[n - 1] = A[n]
    for i in range(n - 1, 0, -1):
        B[i - 1] = A[i] + c * B[i]
    return B[::-1], A[0] + c * B[0]


def horner_nhan(a, c):
    """Muc 3, horner.md: P(x)(x - c). Tra ve he so bac cao -> thap."""
    n = len(a) - 1
    A = a[::-1]
    D = [0.0] * (n + 2)
    D[n + 1] = A[n]
    for i in range(n, 0, -1):
        D[i] = A[i - 1] - c * A[i]
    D[0] = -c * A[0]
    return D[::-1]


def horner_dao_ham(a, c, k):
    """Muc 2, horner.md: chia lap cho (x - c). Tra ve (r, v, hang); v_j = P^(j)(c), hang j = (b_n..b_j)."""
    n = len(a) - 1
    K = min(k, n)
    b = a[::-1]                                    # b_i = a_i
    r, v, hang = [], [], []
    gt = 1.0
    for j in range(K + 1):
        for i in range(n - 1, j - 1, -1):          # chia cho (x - c)
            b[i] = b[i] + c * b[i + 1]
        r.append(b[j])                             # r_j = b_j = P^(j)(c) / j!
        gt *= max(j, 1)
        v.append(gt * b[j])
        hang.append([b[i] for i in range(n, j - 1, -1)])
    v += [0.0] * (k - K)                           # cap > n: dao ham bang 0
    return r, v, hang


def lagrange(x, y):
    """Muc 1: P_n(x) = sum (y_i/D_i) * w_(n+1)(x)/(x - x_i). Tra ve (a, D, bang_tich, bang_chia)."""
    n = len(x) - 1
    p = [1.0]                                      # Buoc 1 - Bang tich: w_(n+1)(x) (muc 4, horner.md)
    bang_tich = []
    for xi in x:
        p = horner_nhan(p, xi)
        bang_tich.append(p)
    A = [0.0] * (n + 1)                            # Buoc 2 - Khoi tao: a_l = 0
    D, bang_chia = [], []
    for i in range(n + 1):                         # Buoc 3
        q, du = horner_chia(p, x[i])               # Buoc 3.1 - Bang chia: w_(n+1)(x) / (x - x_i)
        D.append(math.prod(x[i] - x[j] for j in range(n + 1) if j != i))   # Buoc 3.2 - He so D_i
        Q = q[::-1]                                # Q[l] = q_l^(i)
        for l in range(n + 1):                     # Buoc 3.3 - Cong don
            A[l] += y[i] / D[i] * Q[l]
        bang_chia.append((q, du))
    return A[::-1], D, bang_tich, bang_chia        # Buoc 4 - Ket thuc


def gia_tri_truc_tiep(x, y, xbar, D):
    """Muc 2: P_n(xbar) = w_(n+1)(xbar) * sum y_i / (D_i (xbar - x_i)). Tra ve (P(xbar), w, cac so hang)."""
    for m, xm in enumerate(x):                     # Buoc 1 - Trung moc
        if xbar == xm:
            return y[m], 0.0, None
    w = math.prod(xbar - xi for xi in x)           # Buoc 2 - Tich
    # Buoc 3 - He so D_i: dung lai D da tinh
    so_hang = [y[i] / (D[i] * (xbar - x[i])) for i in range(len(x))]   # Buoc 4 - Tong
    return w * sum(so_hang), w, so_hang            # Buoc 5 - Ket thuc


# ===== GIAI =====

def in_horner_lap(a, c, k):
    """Muc 3, Buoc 1: in bang Horner chia lap tai c, tra ve (r, v)."""
    n = len(a) - 1
    r, v, hang = horner_dao_ham(a, c, k)
    print(f"  Horner chia lap tai c = {c:.10g} (hang j: (b_n, ..., b_j) sau lan chia thu j+1, o cuoi r_j):")
    print("  P^(j)(xbar) = j! * r_j,  r_j = du lan chia thu j+1 cho (x - xbar)")
    in_bang([""] + cot_mu(n), [["P(x)"] + list(a)] + [[f"j = {j}"] + h for j, h in enumerate(hang)])
    for j in range(len(r)):
        print(f"  P^({j})(c) = {j}! * {so_ngoac(r[j])} = {fmt(v[j])}")
    return r, v


def giai(x, y, muc, xbars, k):
    n = len(x) - 1
    print(f"\nNoi suy Lagrange: n = {n} ({n + 1} moc)")
    print(f"  x = {vec(x, '.10g')}")
    print(f"  y = {vec(y, '.10g')}")
    lap_he_so = bool(muc & {1, 3})

    print("\nTINH TOAN:")
    if lap_he_so:
        a, D, bang_tich, bang_chia = lagrange(x, y)
        print(f"Bang tich w_{n + 1}(x) (hang x_i: he so sau khi nhan them (x - x_i)):")
        print("  w_(n+1)(x) = (x - x_0)(x - x_1)...(x - x_n)")
        in_bang(["x_i"] + cot_mu(n + 1), [["bat dau"] + [None] * (n + 1) + [1.0]] +
                [[f"{x[i]:.10g}"] + [None] * (n - i) + h for i, h in enumerate(bang_tich)])
        print(f"\nBang thuong w_{n + 1}(x) / (x - x_i) (Horner chia, du = 0; hang i la ma tran Q):")
        in_bang(["x_i"] + cot_mu(n) + ["du"],
                [[f"{x[i]:.10g}"] + q + [du] for i, (q, du) in enumerate(bang_chia)])
        print("\nBang he so (o hang i, cot j: x_i - x_j; D_i la tich cac o j != i cua hang i):")
        print("  D_i = (x_i - x_0)...(x_i - x_(i-1))(x_i - x_(i+1))...(x_i - x_n)")
        in_bang(["i", "x_i"] + [f"j = {j}" if j == 0 else str(j) for j in range(n + 1)] + ["D_i", "y_i", "y_i/D_i"],
                [[str(i), f"{x[i]:.10g}"] + ["-" if j == i else x[i] - x[j] for j in range(n + 1)]
                 + [D[i], f"{y[i]:.10g}", y[i] / D[i]] for i in range(n + 1)])
        print(f"\nHe so cua P_{n}: Y = (y_0/D_0, ..., y_{n}/D_{n}) (vector hang), Q = bang thuong:")
        print("  P_n(x) = sum_(i=0..n) (y_i / D_i) * w_(n+1)(x) / (x - x_i)")
        print(f"  P_{n} = Y.Q = {vec(a)}")
    else:
        D = [math.prod(x[i] - x[j] for j in range(n + 1) if j != i) for i in range(n + 1)]

    gia_tri = {}                                   # xbar -> (P(xbar) theo muc 2, v theo muc 3 | None)
    for xbar in xbars:
        print(f"\nxbar = {xbar:.10g}:")
        P_tt, w, so_hang = gia_tri_truc_tiep(x, y, xbar, D)
        if 2 in muc:
            if so_hang is None:
                print(f"  xbar trung moc -> P(xbar) = y = {P_tt:.10g}")
            else:
                print("  Gia tri truc tiep (muc 2):")
                print("  P_n(xbar) = w_(n+1)(xbar) * sum_(i=0..n) y_i / (D_i (xbar - x_i))")
                in_bang(["i", "x_i", "y_i", "D_i", "y_i/(D_i(xbar-x_i))"],
                        [[str(i), f"{x[i]:.10g}", f"{y[i]:.10g}", D[i], so_hang[i]] for i in range(n + 1)])
                print(f"  w_{n + 1}(xbar) = {fmt(w)},  S = {fmt(sum(so_hang))},  P(xbar) = w * S = {fmt(P_tt)}")
        v = in_horner_lap(a, xbar, k)[1] if 3 in muc else None
        gia_tri[xbar] = (P_tt, v)

    print("\nKET QUA (vector he so bac cao -> thap):" if lap_he_so else "\nKET QUA:")
    ket_qua = {}
    if lap_he_so:
        print(f"  a = (a_{n}, ..., a_0) = {vec(a)}" if n else f"  a = (a_0) = {vec(a)}")
        print(f"  P_{n}(x) = {da_thuc_str(a)}")
        ket_qua["a"] = np.array(a)
    for xbar, (P_tt, v) in gia_tri.items():
        if 2 in muc:
            print(f"  P_{n}({xbar:.10g}) = {fmt(P_tt)}")
        if 3 in muc:
            ten = "(P(xbar))" if k == 0 else f"(P(xbar), ..., P^({k})(xbar))"
            print(f"  xbar = {xbar:.10g}: v = {ten} = {vec(v)}")
        lE = log_E(x, xbar)
        E = math.exp(lE) if lE < 709 else math.inf
        print(f"    sai so: |f({xbar:.10g}) - P_{n}({xbar:.10g})| <= M_{n + 1} / {n + 1}! * |w_{n + 1}(xbar)|"
              f" = M_{n + 1} * {fmt(E, nho=0)}")
        ket_qua[xbar] = np.array(v) if v is not None else P_tt
    print("\nKIEM TRA:")
    a_np = np.linalg.solve(np.vander(x, n + 1), y) if n else np.array(y)
    if lap_he_so:
        kiem("max |P(x_i) - y_i|", np.max(np.abs(np.polyval(a, x) - y)))
        kiem("he so vs numpy.linalg.solve(vander), tuong doi",
             np.max(np.abs(np.array(a) - a_np)) / max(1.0, np.max(np.abs(a_np))))
    for xbar, (P_tt, v) in gia_tri.items():
        if lap_he_so:
            kiem(f"xbar = {xbar:.10g}: Horner tren he so chinh tac vs muc 2", abs(np.polyval(a, xbar) - P_tt))
        else:
            kiem(f"xbar = {xbar:.10g}: P(xbar) vs numpy.polyval", abs(np.polyval(a_np, xbar) - P_tt))
        if 3 in muc:
            kiem(f"xbar = {xbar:.10g}: dao ham vs numpy.polyder",
                 max(abs(np.polyval(np.polyder(a_np, j) if j else a_np, xbar) - v[j]) for j in range(min(k, n) + 1)))
    return ket_qua


# ===== CHUONG TRINH CHINH =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")   # in du lieu goc co ky tu la khong bi crash
    tra_loi, bang = None, None
    if len(sys.argv) > 1:
        p = sys.argv[1]
        try:
            if la_file_bang(p):
                bang = p                                   # bang so lieu: doc (va xac nhan) sau khi hoi muc dich
            else:
                with open(p, encoding="utf-8-sig") as f:
                    tra_loi = [d for d in f.read().splitlines() if d.strip()]
                if not tra_loi:
                    raise ValueError(f"file '{p}' rong.")
        except OSError:
            print(f"Loi: khong mo duoc file '{p}'.")
            return
        except ValueError as e:
            print(f"Loi: {e}")
            return

    thieu = []        # file thieu dong -> dung VD, bao trong XU LY DU LIEU

    def nhap(prompt, mac_dinh):
        if tra_loi is not None:
            if tra_loi:
                return tra_loi.pop(0)
            thieu.append(f"file thieu dong cho '{prompt}' -> dung VD [{mac_dinh}]")
            return mac_dinh
        try:
            s = input(f"{prompt} (VD [{mac_dinh}]): ").strip()
        except EOFError:
            s = ""
        return s or mac_dinh

    bao = []          # Buoc 0: chi in khi du lieu ban / loi
    goc = {}
    loi = False
    try:
        if tra_loi is None:
            print("Muc dich (chon 1 hoac nhieu, cach nhau boi khoang trang):")
            print("  1. Da thuc noi suy Lagrange P_n(x) (he so)")
            print("  2. Gia tri P_n(xbar)")
            print("  3. Dao ham cap 0..k tai xbar")
        goc["muc dich"] = nhap("Chon muc dich", "1")
        so_muc = doc_day_so(goc["muc dich"], "muc dich", bao)
        muc = {int(v) for v in so_muc if v in (1, 2, 3)}
        if len(muc) != len(set(so_muc)):
            bao.append("muc dich: loai cac gia tri ngoai 1..3")
        if not muc:
            raise ValueError("Khong co muc dich hop le (1..3).")

        so_dong, ts = None, {}
        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "1.2 1.5 1.7 1.8 2.1 2.3")
            goc["y"] = nhap("Cac gia tri y_i", "0.892 1.179 1.358 1.445 1.688 1.839")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            B = doc_bang_file(bang, nhap, bao)
            ox, oy, vi_tri, so_dong, ts = B["x"], B["y"], B["vi_tri"], B["so"], B["ts"]
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao, so_dong, None if tra_loi is not None else hoi_moc_trung)

        xbars, k = [], 0
        if muc & {2, 3}:
            vd = "1.6" if bang is None else f"{(x[0] + x[-1]) / 2:.10g}"   # bang tu file: trung diem
            nhan = "Cac diem xbar"
            if "xbar" in ts:                             # xbar ghi trong file: Enter = dung
                vd, nhan = f"{ts['xbar'][0]:.10g}", f"Cac diem xbar (file: o {ts['xbar'][1]})"
            goc["xbar"] = nhap(nhan, vd)
            xbars = doc_day_so(goc["xbar"], "xbar", bao)
            if not xbars:
                raise ValueError("Khong co diem xbar hop le.")
            for xb in xbars:
                if not x[0] <= xb <= x[-1]:
                    bao.append(f"xbar = {xb:.10g} ngoai [x_0, x_n] = [{x[0]:.10g}, {x[-1]:.10g}]"
                               " -> ngoai suy, sai so co the lon")
        if 3 in muc:
            goc["k"] = nhap("Cap dao ham k", "2")
            ks = doc_day_so(goc["k"], "k", bao)
            if len(ks) != 1 or ks[0] < 0 or ks[0] != int(ks[0]):
                raise ValueError("k phai la 1 so nguyen >= 0.")
            k = int(ks[0])
    except ValueError as e:
        bao.append(f"Loi: {e}")
        loi = True
    bao += thieu

    if bao:
        print("\nXU LY DU LIEU")
        print("-" * 78)
        for ten, s in goc.items():
            print(f"  {ten} (goc): {s!r}")
        for m in bao:
            print("  " + m)
        if loi:
            return
        print("  Du lieu sach:")
        print(f"    x = {vec(x)}")
        print(f"    y = {vec(y)}")
        if xbars:
            print(f"    xbar = {vec(xbars, '.10g')}" + (f",  k = {k}" if 3 in muc else ""))

    giai(x, y, muc, xbars, k)


if __name__ == "__main__":
    main()
