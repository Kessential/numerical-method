"""
NOI SUY NGUOC: GIAI f(x) = ybar TU BANG DU LIEU (PHUONG PHAP HAM NGUOC / PHUONG PHAP LAP)
Thuat toan: docs/thuat_toan/noi_suy_nguoc.md

Bang (x_i, y_i), y_i = f(x_i). Voi moi ybar:
  muc 1. khoang cach ly: (x_i, x_(i+1)) voi (y_i - ybar)(y_(i+1) - ybar) < 0;  y_i = ybar -> x_i la nghiem
  muc 2. khoang don dieu: doi dau cua y_(i+1) - y_i
Phuong phap (chon 1 hoac nhieu):
  1. Ham nguoc -> noi suy Newton x theo y qua m moc |y_j - ybar| nho nhat trong doan don dieu (muc 3)
  2. Lap       -> moc cach deu; Newton tien tu x_k (du m moc ben phai) hoac lui tu x_(k+1) (muc 4)
                  t = phi(t), dung khi h |t_(j+1) - t_j| < eps, toi da N lan

Cach chay:
  python interpolation/noi_suy_nguoc.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/noi_suy_nguoc.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi:
                                                           phuong phap / x / y / ybar / m / eps / N
  python interpolation/noi_suy_nguoc.py data/<file>.csv -> file chi chua bang: 2 hang hoac 2 cot x, y (lay 2 cot dau,
                                                           .xlsx: sheet dau, can pandas + openpyxl); cau con lai nhap tay
  VD cau 19a: python interpolation/noi_suy_nguoc.py "slide_example/data Câu 19.xlsx"  roi nhap: 1 / 2.5 / 6 / 1e-6 / 100
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


def ngan(s, toi_da=240):
    """Rut gon chuoi qua dai (bang du lieu lon) khi in XU LY DU LIEU."""
    return s if len(s) <= toi_da else s[:toi_da // 2] + " ... " + s[-toi_da // 4:]


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


def chon_in(n):
    """Chi so lan lap can in khi biet tong N lan: 1, 2, ap chot, cuoi (<= 4 lan -> in het)."""
    return [j for j in range(1, n + 1) if j <= 2 or j >= n - 1]


# ===== THUAT TOAN =====

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


def cach_deu(x, delta=1e-6):
    """Buoc 0: h neu moc cach deu (|x_(i+1) - x_i - h| <= delta*h moi i), nguoc lai None."""
    n = len(x) - 1
    if n < 1:
        return None
    h = (x[-1] - x[0]) / n
    return h if all(abs(x[i + 1] - x[i] - h) <= delta * h for i in range(n)) else None


def so_le(y):
    """So chu so thap phan d cua du lieu (y_i = so nguyen * 10^-d); None neu khong co d <= 10."""
    for d in range(11):
        if all(abs(v * 10 ** d - round(v * 10 ** d)) < 1e-6 for v in y):
            return d
    return None


def bang_sai_phan(x, y, h=None):
    """Muc 1: bang tam giac duoi T[i][k]. TH1 (h = None): ty sai phan; TH2: sai phan
    (y co d chu so thap phan -> sai phan dung d chu so, lam tron de khu sai so dau phay dong)."""
    n = len(x) - 1
    dl = so_le(y) if h is not None else None
    T = [[None] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):                         # Buoc 1 - Cot 0
        T[i][0] = y[i]
    for k in range(1, n + 1):                      # Buoc 2
        for i in range(k, n + 1):
            d = T[i][k - 1] - T[i - 1][k - 1]
            if h is None:
                T[i][k] = d / (x[i] - x[i - k])
            else:
                T[i][k] = round(d, dl) if dl is not None else d
    return T                                       # Buoc 3 - Ket thuc


def trich_xuat(x, xbar, m):
    """Muc 7: m moc gan xbar nhat. Tra ve (L, R, thu tu ket nap j_1..j_m)."""
    n = len(x) - 1
    j = min(range(n + 1), key=lambda i: (abs(xbar - x[i]), i))   # Buoc 1 - Moc gan nhat
    L = R = j
    thu_tu = [j]
    for _ in range(2, m + 1):                      # Buoc 2 - Ket nap dan
        if L == 0:                                 # TH1: cham bien trai
            R += 1
            thu_tu.append(R)
        elif R == n:                               # TH2: cham bien phai
            L -= 1
            thu_tu.append(L)
        elif xbar - x[L - 1] <= x[R + 1] - xbar:   # TH3: ben nao gan hon
            L -= 1
            thu_tu.append(L)
        else:
            R += 1
            thu_tu.append(R)
    return L, R, thu_tu                            # Buoc 3 - Ket thuc


def khoang_cach_ly(y, yb):
    """Muc 1: (chi so nghiem tai moc, chi so k cua khoang cach ly (x_k, x_(k+1)))."""
    g = [v - yb for v in y]                        # Buoc 1 - Do lech
    tai_moc, khoang = [], []
    for i in range(len(y)):                        # Buoc 2
        if g[i] == 0:                              # 2.1 - Nghiem tai moc
            tai_moc.append(i)
        if i < len(y) - 1 and g[i] * g[i + 1] < 0: # 2.2 - Doi dau
            khoang.append(i)
    return tai_moc, khoang                         # Buoc 3


def khoang_don_dieu(y):
    """Muc 2: danh sach (a, b, chieu) voi chieu = 1 tang, -1 giam, 0 hang."""
    n = len(y) - 1
    s = [int(np.sign(y[i + 1] - y[i])) for i in range(n)]   # Buoc 1 - Dau sai phan
    doan, a = [], 0                                          # Buoc 2 - Khoi tao
    for i in range(1, n):                                    # Buoc 3
        if s[i] != s[i - 1]:
            doan.append((a, i, s[i - 1]))
            a = i
    doan.append((a, n, s[n - 1]))                            # Buoc 4 - Doan cuoi
    return doan


def ham_nguoc(x, y, yb, k, a, b, m):
    """Muc 3: tra ve dict (thu_tu, L, R, u, v, T, c, omega, so_hang, xbar, thieu)."""
    L, R = k, k + 1                                # Buoc 1.1 - Khoi tao
    thu_tu = [k, k + 1] if abs(y[k] - yb) <= abs(y[k + 1] - yb) else [k + 1, k]
    thieu = False
    while R - L + 1 < m:                           # Buoc 1.2 - Ket nap dan
        if L == a and R == b:                      # TH1: het doan don dieu
            thieu = True
            break
        if L == a or (R < b and abs(y[R + 1] - yb) < abs(y[L - 1] - yb)):
            R += 1                                 # TH2 / TH4 ben phai
            thu_tu.append(R)
        else:
            L -= 1                                 # TH3 / TH4 ben trai
            thu_tu.append(L)
    idx = list(range(L, R + 1))                    # Buoc 2 - Doi vai, u tang dan
    if y[R] < y[L]:
        idx.reverse()
    u = [y[i] for i in idx]
    v = [x[i] for i in idx]
    T = bang_sai_phan(u, v)                        # Buoc 3 - Bang ty sai phan (muc 1, newton.md)
    c = [T[j][j] for j in range(len(u))]
    omega, so_hang, S = [1.0], [c[0]], c[0]        # Buoc 4 - Gia tri tai ybar
    for j in range(1, len(u)):
        omega.append(omega[-1] * (yb - u[j - 1]))
        so_hang.append(c[j] * omega[-1])
        S += so_hang[-1]
    return dict(thu_tu=thu_tu, L=L, R=R, idx=idx, u=u, v=v, T=T, c=c, omega=omega, so_hang=so_hang,
                xbar=S, thieu=thieu)               # Buoc 5 - Ket thuc


def da_thuc_w(m, sigma):
    """Bang tich w_j(t) = t(t + sigma)(t + 2 sigma)... (j thua so), j = 0..m-1 (he so bac cao -> thap)."""
    w = [[1.0]]
    for j in range(1, m):
        w.append(horner_nhan(w[-1], -sigma * (j - 1)))
    return w


def lap(x, y, yb, k, h, m, eps, N):
    """Muc 4: tra ve dict (huong, s, idx, d, A, B, t, xbar, hoi_tu, q, bao)."""
    n = len(x) - 1
    bao = []
    m = min(m, n + 1)                              # Buoc 1 - Chon huong
    if k + m - 1 > n and k + 2 - m < 0:
        m2 = max(n - k + 1, k + 2)
        bao.append(f"khong du {m} moc ve mot phia cua (x_{k}, x_{k + 1}) -> m = {m2}")
        m = m2
    if k + m - 1 <= n:                             # TH1 tien
        huong, s, sigma = "tien", k, -1
        idx = list(range(k, k + m))
        D = bang_sai_phan(x[k:k + m], y[k:k + m], h)
        d = [D[j][j] for j in range(m)]            # Delta^j y_k (duong cheo)
    else:                                          # TH2 lui
        huong, s, sigma = "lui", k + 1, 1
        idx = list(range(k + 2 - m, k + 2))
        D = bang_sai_phan(x[k + 2 - m:k + 2], y[k + 2 - m:k + 2], h)
        d = [D[m - 1][j] for j in range(m)]        # Nabla^j y_(k+1) (hang cuoi)
    A = (yb - d[0]) / d[1]                         # Buoc 3 - phi(t) = A - sum B_j w_j(t)
    B, gt = [0.0, 0.0], 1.0
    for j in range(2, m):
        gt *= j
        B.append(d[j] / gt / d[1])
    w = da_thuc_w(m, sigma)
    Q = [0.0] * m                                  # Q(t) = sum B_j w_j(t), he so bac cao -> thap
    for j in range(2, m):
        for l, val in enumerate(reversed(w[j])):
            Q[m - 1 - l] += B[j] * val

    def phi(t):
        return A - float(np.polyval(Q, t))

    t = [A]                                        # Buoc 4 - Khoi tao t_0
    hoi_tu = False
    for _ in range(N):                             # Buoc 5 - Lap
        t.append(phi(t[-1]))                       # 5.1
        if h * abs(t[-1] - t[-2]) < eps:           # 5.2 - Dung
            hoi_tu = True
            break
    xbar = x[s] + t[-1] * h                        # Buoc 5.2 / Buoc 6 (khong hoi tu -> tham khao)
    q = abs(horner_dao_ham(Q, t[-1], 1)[1][1]) if m > 2 else 0.0   # |phi'(t*)|
    return dict(huong=huong, s=s, sigma=sigma, idx=idx, D=D, d=d, A=A, B=B, w=w, Q=Q, t=t, xbar=xbar,
                hoi_tu=hoi_tu, q=q, bao=bao, m=m)


# ===== GIAI =====

def lagrange_tai(xs, ys, xb):
    """Kiem tra: gia tri da thuc noi suy tai xb theo cong thuc Lagrange truc tiep."""
    s = 0.0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        L = 1.0
        for j, xj in enumerate(xs):
            if j != i:
                L *= (xb - xj) / (xi - xj)
        s += yi * L
    return s


def y_tai(x, y, xb, m):
    """Kiem tra: y(xb) noi suy truc tiep qua m moc gan xb nhat."""
    L, R, _ = trich_xuat(x, xb, min(m, len(x)))
    return lagrange_tai(x[L:R + 1], y[L:R + 1], xb)


CHIEU = {1: "tang", -1: "giam", 0: "hang"}


def in_ham_nguoc(x, y, yb, kq):
    print(f"  Phuong phap ham nguoc (muc 3): chon moc co |y_j - ybar| nho nhat trong doan don dieu:")
    in_bang(["lan", "j", "x_j", "y_j", "|y_j - ybar|"],
            [[str(s), str(j), f"{x[j]:.10g}", f"{y[j]:.10g}", f"{abs(y[j] - yb):.10g}"]
             for s, j in enumerate(kq["thu_tu"], 1)], le="    ")
    if kq["thieu"]:
        print(f"    (doan don dieu chi co {kq['R'] - kq['L'] + 1} moc -> dung het)")
    r = len(kq["u"]) - 1
    print(f"    Bang ty sai phan cua x theo y (u_s = y, v_s = x, u tang dan; duong cheo = c_j):")
    in_bang(["s", "u_s = y", "v_s = x"] + [f"TSP{j}" for j in range(1, r + 1)],
            [[str(s), f"{kq['u'][s]:.10g}"] + kq["T"][s][:s + 1] + [None] * (r - s) for s in range(r + 1)],
            le="    ")
    print(f"    xbar = sum c_j w_j(ybar),  w_0 = 1,  w_j = w_(j-1) (ybar - u_(j-1)):")
    tong, hang = 0.0, []
    for j in range(r + 1):
        tong += kq["so_hang"][j]
        hang.append([str(j), kq["c"][j], kq["omega"][j], kq["so_hang"][j], fmt(tong, ".10f")])
    in_bang(["j", "c_j", "w_j(ybar)", "c_j * w_j", "tong"], hang, le="    ")
    print(f"    => xbar ~ {kq['xbar']:.10g}   (so hang cuoi: {abs(kq['so_hang'][-1]):.2e})")


def in_lap(x, y, yb, h, eps, kq):
    k = kq["idx"]
    s, m = kq["s"], kq["m"]
    if kq["huong"] == "tien":
        print(f"  Phuong phap lap (muc 4), TH1 Newton tien tu x_{s} = {x[s]:.10g}, {m} moc x_{k[0]}..x_{k[-1]}:")
        ten_d = [f"D^{j}y_{s}" for j in range(m)]
    else:
        print(f"  Phuong phap lap (muc 4), TH2 Newton lui tu x_{s} = {x[s]:.10g}, {m} moc x_{k[0]}..x_{k[-1]}:")
        ten_d = [f"N^{j}y_{s}" for j in range(m)]
    for b in kq["bao"]:
        print("    " + b)
    print("    Bang sai phan (hang i: T_(i,j); " + ("duong cheo" if kq["huong"] == "tien" else "hang cuoi")
          + " = d_j):")
    D = kq["D"]
    in_bang(["i", "x_i", "y_i"] + [f"SP{j}" for j in range(1, m)],
            [[str(k[r]), f"{x[k[r]]:.10g}"] + D[r][:r + 1] + [None] * (m - 1 - r) for r in range(m)], le="    ")
    w = "t(t-1)...(t-j+1)" if kq["huong"] == "tien" else "t(t+1)...(t+j-1)"
    print(f"    phi(t) = A - sum_(j=2..{m - 1}) B_j w_j(t),  A = (ybar - d_0)/d_1,  B_j = d_j / (j! d_1),  w_j = {w}")
    in_bang(["j", "d_j", "", "B_j"],
            [[str(j), kq["d"][j], ten_d[j], "" if j < 2 else kq["B"][j]] for j in range(m)], le="    ")
    print(f"    A = ({yb:.10g} - {kq['d'][0]:.10g}) / {so_ngoac(kq['d'][1])} = {kq['A']:.10g} = t_0")
    t = kq["t"]
    L = len(t) - 1
    hang = []
    for l in chon_in(L):
        if l > 3 and l == L - 1 and L > 4:
            hang.append(["...", "...", "..."])
        hang.append([str(l), t[l], h * abs(t[l] - t[l - 1])])
    print(f"    Lap t_(l+1) = phi(t_l), dung khi h|t_(l+1) - t_l| < eps = {eps:g}, xbar = x_{s} + t_(l+1) h:")
    in_bang(["l", "t_l", "h|t_l - t_(l-1)|"], hang, le="    ")
    if kq["hoi_tu"]:
        print(f"    Dung sau {L} lan: xbar = x_{s} + t_{L} h = {x[s]:.10g} + {so_ngoac(t[L])} * {h:.10g}"
              f" = {fmt(kq['xbar'])}")
    else:
        print(f"    => KHONG HOI TU sau {L} lan lap (t_N = {t[-1]:.10g}, x = {kq['xbar']:.10g} chi de tham khao)")


def giai(x, y, yb, pp, m, eps, N, h):
    n = len(x) - 1
    print(f"\nGiai f(x) = ybar = {yb:.10g} tu bang {n + 1} moc [{x[0]:.10g}, {x[-1]:.10g}]"
          + (f", moc cach deu h = {h:.10g}" if h else ", moc bat ky"))

    print("\nCONG THUC:")
    print("  Khoang cach ly : g_i = y_i - ybar;  g_i * g_(i+1) < 0 -> (x_i, x_(i+1)) chua nghiem;  g_i = 0 -> x_i la nghiem")
    print("  Khoang don dieu: dau cua y_(i+1) - y_i khong doi")
    if 1 in pp:
        print("  Ham nguoc: x = P(y) = sum c_j w_j(y), c_j = x[u_0..u_j] (ty sai phan x theo y),"
              " w_j = (y - u_0)...(y - u_(j-1));  xbar = P(ybar)")
    if 2 in pp:
        print("  Lap tien : t = phi(t) = (ybar - y_k)/Dy_k - 1/Dy_k * sum_(j>=2) D^j y_k / j! * t(t-1)...(t-j+1),"
              "  x = x_k + t h")
        print("  Lap lui  : t = phi(t) = (ybar - y_(k+1))/Ny_(k+1) - 1/Ny_(k+1) * sum_(j>=2) N^j y_(k+1) / j!"
              " * t(t+1)...(t+j-1),  x = x_(k+1) + t h")
        print("  t_0 = (ybar - d_0)/d_1,  t_(j+1) = phi(t_j);  dung khi h |t_(j+1) - t_j| < eps")

    print("\nTINH TOAN:")
    doan = khoang_don_dieu(y)                      # Muc 2
    print("Khoang don dieu (muc 2):")
    in_bang(["doan", "[x_a, x_b]", "chi so", "chieu"],
            [[str(r), f"[{x[a]:.10g}, {x[b]:.10g}]", f"{a}..{b}", CHIEU[s]] for r, (a, b, s) in enumerate(doan, 1)])
    tai_moc, khoang = khoang_cach_ly(y, yb)        # Muc 1
    print(f"\nKhoang cach ly cua f(x) = {yb:.10g} (muc 1):")
    if khoang:
        in_bang(["k", "x_k", "x_(k+1)", "g_k = y_k - ybar", "g_(k+1)"],
                [[str(k), f"{x[k]:.10g}", f"{x[k + 1]:.10g}", fmt(y[k] - yb, ".7f"), fmt(y[k + 1] - yb, ".7f")]
                 for k in khoang])
    else:
        print("  (khong co khoang doi dau)")
    for i in tai_moc:
        print(f"  y_{i} = ybar -> x_{i} = {x[i]:.10g} la nghiem dung tai moc")
    hang = [(a, b) for a, b, s in doan if s == 0 and y[a] == yb]
    for a, b in hang:
        print(f"  CHU Y: y hang = ybar tren [{x[a]:.10g}, {x[b]:.10g}] -> theo bang, moi x trong doan deu la nghiem")

    kq = []
    for r, k in enumerate(khoang, 1):
        a, b, s = next(dd for dd in doan if dd[0] <= k < dd[1])
        print(f"\nNghiem {r}: khoang cach ly (x_{k}, x_{k + 1}) = ({x[k]:.10g}, {x[k + 1]:.10g}),"
              f" thuoc doan don dieu [{x[a]:.10g}, {x[b]:.10g}] ({CHIEU[s]})")
        mot = dict(k=k, a=a, b=b)
        if 1 in pp:
            mot["hn"] = ham_nguoc(x, y, yb, k, a, b, m)
            in_ham_nguoc(x, y, yb, mot["hn"])
        if 2 in pp and h:
            mot["lap"] = lap(x, y, yb, k, h, m, eps, N)
            in_lap(x, y, yb, h, eps, mot["lap"])
        kq.append(mot)

    print("\nKET QUA:")
    if not khoang and not tai_moc:
        print(f"  f(x) = {yb:.10g} khong co nghiem trong [{x[0]:.10g}, {x[-1]:.10g}]")
    for i in tai_moc:
        print(f"  x = {x[i]:.10g} (nghiem dung tai moc)")
    for a, b in hang:
        print(f"  moi x trong [{x[a]:.10g}, {x[b]:.10g}] (y hang = ybar, vo so nghiem)")
    for r, mot in enumerate(kq, 1):
        k = mot["k"]
        dong = f"  Nghiem {r} trong ({x[k]:.10g}, {x[k + 1]:.10g}):"
        if "hn" in mot:
            dong += f"  ham nguoc x ~ {mot['hn']['xbar']:.10g}"
        if "lap" in mot:
            L = mot["lap"]
            dong += (f"  |  lap x ~ {L['xbar']:.10g} ({len(L['t']) - 1} lan, eps = {eps:g})" if L["hoi_tu"]
                     else f"  |  lap: KHONG HOI TU sau {N} lan")
        print(dong)
    nghiem = [("hn", "ham nguoc"), ("lap", "lap")]
    vec_kq = {ten: [mot[kk]["xbar"] for mot in kq if kk in mot] for kk, ten in nghiem}
    for ten, v in vec_kq.items():
        if v:
            print(f"  vector nghiem ({ten}) = {vec(v)}")

    print("\nKIEM TRA (thay nghiem vao da thuc noi suy truc tiep y(x) qua m moc gan x nhat):")
    for r, mot in enumerate(kq, 1):
        for kk, ten in nghiem:
            if kk in mot:
                xb = mot[kk]["xbar"]
                kiem(f"nghiem {r} ({ten}): |y(xbar) - ybar|, xbar = {xb:.10g}", abs(y_tai(x, y, xb, m) - yb))
        if "lap" in mot:
            q = mot["lap"]["q"]
            nhan = f"nghiem {r}: dieu kien hoi tu |phi'(t*)| < 1"
            print(f"  {nhan:<62} = {q:.4g}" + ("  -> dung" if q < 1 else "  -> SAI"))
        if "hn" in mot and "lap" in mot:
            kiem(f"nghiem {r}: |ham nguoc - lap|", abs(mot["hn"]["xbar"] - mot["lap"]["xbar"]))
    return kq


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
            print("Phuong phap (chon 1 hoac nhieu, cach nhau boi khoang trang):")
            print("  1. Phuong phap ham nguoc")
            print("  2. Phuong phap lap (moc cach deu)")
        goc["phuong phap"] = nhap("Chon phuong phap", "1 2")
        so_pp = doc_day_so(goc["phuong phap"], "phuong phap", bao)
        pp = {int(v) for v in so_pp if v in (1, 2)}
        if len(pp) != len(set(so_pp)):
            bao.append("phuong phap: loai cac gia tri ngoai 1..2")
        if not pp:
            raise ValueError("Khong co phuong phap hop le (1..2).")

        so_dong, ts = None, {}
        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "1.2 1.4 1.6 1.8 2 2.2 2.4 2.6 2.8")
            goc["y"] = nhap("Cac gia tri y_i", "4.02 3.98 4.23 3.67 2.99 1.24 0.87 2.08 4.54")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            B = doc_bang_file(bang, nhap, bao)
            ox, oy, vi_tri, so_dong, ts = B["x"], B["y"], B["vi_tri"], B["so"], B["ts"]
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao, so_dong, None if tra_loi is not None else hoi_moc_trung)
        if len(x) < 2:
            raise ValueError("can it nhat 2 moc.")
        h = cach_deu(x)
        if 2 in pp and h is None:
            bao.append("moc khong cach deu -> bo phuong phap lap (chi dung ham nguoc)")
            pp.discard(2)
            pp.add(1)

        vd = "2.5" if bang is None else f"{(min(y) + max(y)) / 2:.10g}"
        nhan = "Cac gia tri ybar"
        if "ybar" in ts:                             # ybar ghi trong file: Enter = dung
            vd, nhan = f"{ts['ybar'][0]:.10g}", f"Cac gia tri ybar (file: o {ts['ybar'][1]})"
        goc["ybar"] = nhap(nhan, vd)
        ybars = doc_day_so(goc["ybar"], "ybar", bao)
        if not ybars:
            raise ValueError("Khong co ybar hop le.")
        for yb in ybars:
            if not min(y) <= yb <= max(y):
                bao.append(f"ybar = {yb:.10g} ngoai [min y, max y] = [{min(y):.10g}, {max(y):.10g}]"
                           " -> khong co nghiem trong bang")
        goc["m"] = nhap("So moc noi suy m", "6")
        ms = doc_day_so(goc["m"], "m", bao)
        if len(ms) != 1 or ms[0] < 2 or ms[0] != int(ms[0]):
            raise ValueError("m phai la 1 so nguyen >= 2.")
        m = int(ms[0])
        eps, N = 1e-6, 100
        if 2 in pp:
            goc["eps"] = nhap("Sai so eps", "1e-6")
            es = doc_day_so(goc["eps"], "eps", bao)
            if len(es) != 1 or es[0] <= 0:
                raise ValueError("eps phai la 1 so > 0.")
            eps = es[0]
            goc["N"] = nhap("So lan lap toi da N", "100")
            Ns = doc_day_so(goc["N"], "N", bao)
            if len(Ns) != 1 or Ns[0] < 1 or Ns[0] != int(Ns[0]):
                raise ValueError("N phai la 1 so nguyen >= 1.")
            N = int(Ns[0])
    except ValueError as e:
        bao.append(f"Loi: {e}")
        loi = True
    bao += thieu

    if bao:
        print("\nXU LY DU LIEU")
        print("-" * 78)
        for ten, s in goc.items():
            print(f"  {ten} (goc): {ngan(repr(s))}")
        for dong in bao:
            print("  " + dong)
        if loi:
            return
        print(f"  Du lieu sach ({len(x)} moc):")
        print(f"    x = {ngan(vec(x, '.10g'))}")
        print(f"    y = {ngan(vec(y, '.10g'))}")
        print(f"    ybar = {vec(ybars)},  m = {m}" + (f",  eps = {eps:g},  N = {N}" if 2 in pp else ""))

    for yb in ybars:
        if min(y) <= yb <= max(y):
            giai(x, y, yb, pp, m, eps, N, h)


if __name__ == "__main__":
    main()
