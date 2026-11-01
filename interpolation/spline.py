"""
HAM GHEP TRON (SPLINE) BAC p <= 4
Thuat toan: docs/thuat_toan/spline.md

Bo diem (x_i, y_i), i = 0..n, x tang dan; S(x) = S_k(x) tren [x_k, x_(k+1)], S_k bac p, S tron cap p-1.
Can p-1 dieu kien bien S^(r)(x_0) / S^(r)(x_n) = v (1 <= r <= p-1). He so S_k in tu BAC CAO xuong BAC THAP.
Bien the (tu chon theo p va dieu kien bien):
  p = 1                                  -> muc 1 (cong thuc truc tiep)
  p = 2, cho S'(x_0) hoac S'(x_n)        -> muc 2 (truy hoi m_k = S'(x_k))
  p = 3, moi dau 1 dieu kien S' hoac S'' -> muc 3 (he 3 duong cheo sigma_k = S''(x_k), truy duoi)
  con lai (p = 4, dieu kien don 1 dau)   -> muc 4 (dang Taylor dia phuong, khu Gauss)
Muc 4 luon chay them de kiem tra muc 1/2/3.

Cach chay:
  python interpolation/spline.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/spline.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi:
                                                    p / x / y / dieu kien bien
  python interpolation/spline.py data/<file>.csv -> file chi chua bang: 2 hang hoac 2 cot x, y (.xlsx: sheet dau);
                                                    cac cau con lai nhap tu ban phim
Dieu kien bien: "S'(0) = 0", "S''(0) = -1; S''(3.1416) = 1" (dau " = '', nhay Unicode -> ') hoac bo ba "r x v".
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


def nhan_tu(bien, z):
    """Chuoi thua so (bien - z)."""
    if z == 0:
        return bien
    return f"{bien} - {z:.10g}" if z > 0 else f"{bien} + {-z:.10g}"


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


def ten_dh(r):
    """S', S'', S''' hoac S^(r)."""
    return "S" + "'" * r if r <= 3 else f"S^({r})"


def doc_bien(text, x, p, bao):
    """Buoc 0: chuoi dieu kien bien -> [(r, k, v)] voi k = 0 (x_0) hoac n (x_n)."""
    n = len(x) - 1
    s = re.sub("[’′‘`´]", "'", text).replace('"', "''")
    s = re.sub("[−–—]", "-", s)
    phan = []
    for t in (t.strip() for t in re.split(r";|\n", s) if t.strip()):
        ve = [v.strip() for v in t.split("=")]
        if len(ve) > 2:                                           # "S'(a) = S'(b) = v" -> 2 dieu kien
            phan += [f"{v} = {ve[-1]}" for v in ve[:-1]]
        else:
            phan.append(t)
    if len(phan) == 1 and not re.search(r"[Ss]", phan[0]):       # cho phep "r x v, r x v" -> tach theo bo 3
        so = tach_o(phan[0])
        if len(so) % 3 == 0 and len(so) > 3:
            phan = [" ".join(so[i:i + 3]) for i in range(0, len(so), 3)]
    dk = []
    tol = 1e-6 * (x[-1] - x[0])
    for t in phan:
        m = re.match(r"^[Ss]\s*('+|\^\s*\(?\s*(\d+)\s*\)?)\s*\(\s*([^)]*)\)\s*=\s*(.+)$", t)
        if m:
            r = len(m.group(1)) if m.group(1).startswith("'") else int(m.group(2))
            o_x, o_v = m.group(3), m.group(4)
        else:
            o = tach_o(t)
            if len(o) != 3:
                raise ValueError(f"dieu kien bien {t!r} khong dung dang S'(x) = v hoac 'r x v'.")
            vr, _, lr = doc_o(o[0])
            if lr or vr != int(vr):
                raise ValueError(f"dieu kien bien {t!r}: cap r phai la so nguyen.")
            r, o_x, o_v = int(vr), o[1], o[2]
        o_x = o_x.strip()
        if re.fullmatch(r"x_?0|a", o_x):
            vx = x[0]
        elif re.fullmatch(r"x_?n|b", o_x):
            vx = x[-1]
        else:
            vx, sua, lx = doc_o(o_x)
            if lx:
                raise ValueError(f"dieu kien bien {t!r}: diem {o_x!r} khong doc duoc ({lx}).")
        vv, sua, lv = doc_o(o_v)
        if lv:
            raise ValueError(f"dieu kien bien {t!r}: gia tri {o_v!r} khong doc duoc ({lv}).")
        if sua:
            bao.append(f"dieu kien bien {t!r}: " + ", ".join(sua))
        if abs(vx - x[0]) <= tol:
            k = 0
        elif abs(vx - x[-1]) <= tol:
            k = n
        else:
            raise ValueError(f"dieu kien bien {t!r}: diem {vx:.10g} khong phai x_0 = {x[0]:.10g} hay x_n = {x[-1]:.10g}.")
        if not 1 <= r <= p - 1:
            raise ValueError(f"dieu kien bien {t!r}: cap r = {r} phai trong 1..p-1 = 1..{p - 1}.")
        if any(d[0] == r and d[1] == k for d in dk):
            raise ValueError(f"dieu kien {ten_dh(r)}({x[k]:.10g}) bi cho 2 lan "
                             "(neu de ghi S''(0) hai lan thi dieu kien thu hai thuong la tai x_n).")
        dk.append((r, k, vv))
    if len(dk) != p - 1:
        raise ValueError(f"spline bac {p} can dung {p - 1} dieu kien bien, nhan duoc {len(dk)}.")
    return sorted(dk, key=lambda d: (d[1], d[0]))


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


def doi_bien(b, s, h):
    """Muc 5: P theo t = (x - s)/h -> P theo x. Tra ve (a bac cao -> thap, vector a sau moi buoc j)."""
    a = [b[0]]                                     # Buoc 1 - Khoi tao: a = (b_n)
    hang = []
    for j in range(1, len(b)):                     # Buoc 2: b[j] = b_(n-j), j chay n-1..0 theo chi so .md
        a = horner_nhan(a, s)                      # Buoc 2.1 - Nhan (x - s)
        a = [v / h for v in a]                     # Buoc 2.2 - Chia h
        a[-1] += b[j]                              # Buoc 2.3 - Cong vao he so tu do
        hang.append(a)
    return a, hang                                 # Buoc 3 - Ket thuc


def spline1(x, y):
    """Muc 1: [(a_k, b_k)]."""
    kq = []
    for k in range(len(x) - 1):
        h = x[k + 1] - x[k]
        kq.append([(y[k + 1] - y[k]) / h, (y[k] * x[k + 1] - y[k + 1] * x[k]) / h])
    return kq


def spline2(x, y, dk):
    """Muc 2: (gamma, m, [(a_k, b_k, c_k)])."""
    n = len(x) - 1
    h = [x[k + 1] - x[k] for k in range(n)]
    g = [2 * (y[k + 1] - y[k]) / h[k] for k in range(n)]          # Buoc 1
    m = [0.0] * (n + 1)
    r, k0, v = dk[0]
    if k0 == 0:                                                   # Buoc 2 - TH1 xuoi
        m[0] = v
        for k in range(n):
            m[k + 1] = g[k] - m[k]
    else:                                                         # TH2 nguoc
        m[n] = v
        for k in range(n - 1, -1, -1):
            m[k] = g[k] - m[k + 1]
    he = []
    for k in range(n):                                            # Buoc 3 - He so
        a = (m[k + 1] - m[k]) / (2 * h[k])
        b = (m[k] * x[k + 1] - m[k + 1] * x[k]) / h[k]
        c = (-m[k] * x[k + 1] ** 2 + m[k + 1] * x[k] ** 2) / (2 * h[k]) + y[k] + m[k] * h[k] / 2
        he.append([a, b, c])
    return g, m, he


def spline3(x, y, dk):
    """Muc 3: (h, s, he (l, d, u, r), P, Q, sigma, [(a_k, b_k, c_k, d_k)])."""
    n = len(x) - 1
    h = [x[k + 1] - x[k] for k in range(n)]                       # Buoc 1
    s = [(y[k + 1] - y[k]) / h[k] for k in range(n)]
    L, Dg, U, R = [0.0] * (n + 1), [0.0] * (n + 1), [0.0] * (n + 1), [0.0] * (n + 1)
    (r0, _, A), (rn, _, B) = dk
    if r0 == 2:                                                   # Buoc 2.1 - Hang 0
        Dg[0], U[0], R[0] = 1.0, 0.0, A
    else:
        Dg[0], U[0], R[0] = h[0] / 3, h[0] / 6, s[0] - A
    for i in range(1, n):                                         # Buoc 2.2 - Hang trong
        L[i], Dg[i], U[i], R[i] = h[i - 1] / 6, (h[i - 1] + h[i]) / 3, h[i] / 6, s[i] - s[i - 1]
    if rn == 2:                                                   # Buoc 2.3 - Hang n
        L[n], Dg[n], R[n] = 0.0, 1.0, B
    else:
        L[n], Dg[n], R[n] = h[n - 1] / 6, h[n - 1] / 3, B - s[n - 1]
    P, Q = [0.0] * (n + 1), [0.0] * (n + 1)
    P[0], Q[0] = -U[0] / Dg[0], R[0] / Dg[0]                      # Buoc 3 - Truy duoi xuoi
    for i in range(1, n + 1):
        mu = Dg[i] + L[i] * P[i - 1]
        if abs(mu) < 1e-14:
            raise ValueError("he sigma suy bien (mu = 0) -> dung muc 4.")
        P[i], Q[i] = -U[i] / mu, (R[i] - L[i] * Q[i - 1]) / mu
    sg = [0.0] * (n + 1)                                          # Buoc 4 - Truy duoi nguoc
    sg[n] = Q[n]
    for i in range(n - 1, -1, -1):
        sg[i] = P[i] * sg[i + 1] + Q[i]
    he = []
    for k in range(n):                                            # Buoc 5 - He so
        a = (sg[k + 1] - sg[k]) / (6 * h[k])
        b = (sg[k] * x[k + 1] - sg[k + 1] * x[k]) / (2 * h[k])
        c = (-sg[k] * x[k + 1] ** 2 + sg[k + 1] * x[k] ** 2) / (2 * h[k]) + s[k] - (sg[k + 1] - sg[k]) * h[k] / 6
        d = ((sg[k] * x[k + 1] ** 3 - sg[k + 1] * x[k] ** 3) / (6 * h[k])
             + (y[k] * x[k + 1] - y[k + 1] * x[k]) / h[k] + (sg[k + 1] * x[k] - sg[k] * x[k + 1]) * h[k] / 6)
        he.append([a, b, c, d])
    return h, s, (L, Dg, U, R), P, Q, sg, he


def gauss(M, b):
    """Khu Gauss chon tru theo cot (muc 4, Buoc 3)."""
    A = [list(map(float, h)) + [float(v)] for h, v in zip(M, b)]
    N = len(A)
    for c in range(N):
        tru = max(range(c, N), key=lambda i: abs(A[i][c]))
        if abs(A[tru][c]) < 1e-12 * max(1.0, max(abs(v) for v in A[tru][:N])):
            raise ValueError("he suy bien -> dieu kien bien khong xac dinh duy nhat spline.")
        A[c], A[tru] = A[tru], A[c]
        for i in range(c + 1, N):
            f = A[i][c] / A[c][c]
            if f:
                A[i] = [a - f * bb for a, bb in zip(A[i], A[c])]
    z = [0.0] * N
    for i in range(N - 1, -1, -1):
        z[i] = (A[i][N] - sum(A[i][j] * z[j] for j in range(i + 1, N))) / A[i][i]
    return z


def spline_tq(x, y, p, dk):
    """Muc 4: (M, rhs, ten_an, D (n+1) x p voi D[k][r] = S^(r)(x_k), e[k] = he so dia phuong bac cao -> thap)."""
    n = len(x) - 1
    h = [x[k + 1] - x[k] for k in range(n)]
    so_an = (p - 1) * (n + 1)                                     # Buoc 1 - An D_(k,r), r = 1..p-1

    def cot(k, r):
        return k * (p - 1) + (r - 1)

    M, rhs = [], []
    for k in range(n):                                            # Buoc 2.1 - Tron + noi suy tai x_(k+1)
        for r in range(p - 1):
            hang = [0.0] * so_an
            for j in range(max(r, 1), p):
                hang[cot(k, j)] += h[k] ** (j - r) / math.factorial(j - r)
            if p >= 2:
                he = h[k] ** (p - r - 1) / math.factorial(p - r)
                hang[cot(k + 1, p - 1)] += he
                hang[cot(k, p - 1)] -= he
            if r >= 1:
                hang[cot(k + 1, r)] -= 1.0
            M.append(hang)
            rhs.append(y[k + 1] - y[k] if r == 0 else 0.0)
    for r, k, v in dk:                                            # Buoc 2.2 - Bien
        hang = [0.0] * so_an
        hang[cot(k, r)] = 1.0
        M.append(hang)
        rhs.append(v)
    z = gauss(M, rhs) if so_an else []                            # Buoc 3 - Giai
    D = [[y[k]] + [z[cot(k, r)] for r in range(1, p)] for k in range(n + 1)]
    e = []
    for k in range(n):                                            # Buoc 4 - He so dia phuong
        ek = [D[k][j] / math.factorial(j) for j in range(p)]
        ek.append((D[k + 1][p - 1] - D[k][p - 1]) / (math.factorial(p) * h[k]))
        e.append(ek[::-1])
    ten = [f"{ten_dh(r)}(x_{k})" for k in range(n + 1) for r in range(1, p)]
    return M, rhs, ten, D, e                                      # Buoc 5 - Ket thuc


# ===== GIAI =====

def dao_ham_da_thuc(a, r):
    """He so dao ham cap r (bac cao -> thap)."""
    return list(np.polyder(np.array(a, dtype=float), r)) if r else list(a)


def in_ngang(hang, le="  ", rong_max=110):
    """In bang ngang: hang = [(ten, [o, ...]), ...]; qua rong -> ngat thanh nhieu khoi cot."""
    S = [(ten, [v if isinstance(v, str) else fmt(v) for v in o]) for ten, o in hang]
    w0 = max(len(t) for t, _ in S) + 1
    so = len(S[0][1])
    rong = [max(len(o[j]) for _, o in S) + 2 for j in range(so)]
    dau = 0
    while dau < so:
        cuoi, tong = dau, w0
        while cuoi < so and (cuoi == dau or tong + rong[cuoi] <= rong_max):
            tong += rong[cuoi]
            cuoi += 1
        for ten, o in S:
            print(le + f"{ten:<{w0}}" + "".join(f"{o[j]:>{rong[j]}}" for j in range(dau, cuoi)))
        dau = cuoi


def giai(x, y, p, dk):
    n = len(x) - 1
    if p == 1:
        bien_the = 1
    elif p == 2:
        bien_the = 2
    elif p == 3 and dk[0][1] == 0 and dk[1][1] == n and n >= 1:
        bien_the = 3
    else:
        bien_the = 4
    ten_bt = {1: "muc 1 (cong thuc truc tiep)", 2: "muc 2 (truy hoi m_k)", 3: "muc 3 (he 3 duong cheo sigma_k)",
              4: "muc 4 (dang Taylor dia phuong, khu Gauss)"}[bien_the]
    print(f"\nHam ghep tron bac p = {p}: {n + 1} moc, {n} khoang -> {ten_bt}")
    print(f"  x = {vec(x, '.10g')}")
    print(f"  y = {vec(y, '.10g')}")
    if dk:
        print("  Dieu kien bien: " + ",  ".join(f"{ten_dh(r)}({x[k]:.10g}) = {v:.10g}" for r, k, v in dk))

    print("\nTINH TOAN:")
    in_ngang([("i", [str(i) for i in range(n + 1)]), ("x_i", [f"{v:.10g}" for v in x]),
              ("y_i", [f"{v:.10g}" for v in y])])
    h = [x[k + 1] - x[k] for k in range(n)]
    print("\nKhoang cach va ty sai phan:")
    print("  h_k = x_(k+1) - x_k,  s_k = (y_(k+1) - y_k)/h_k")
    in_bang(["k", "[x_k, x_(k+1)]", "h_k", "s_k"],
            [[str(k), f"[{x[k]:.10g}, {x[k + 1]:.10g}]", h[k], (y[k + 1] - y[k]) / h[k]] for k in range(n)])
    kq = {}
    if bien_the == 1:
        he = spline1(x, y)
    elif bien_the == 2:
        g, m, he = spline2(x, y, dk)
        kq["m"] = m
        tu_dau = dk[0][1] == 0
        print(f"\nTruy hoi m_k ({'xuoi tu m_0' if tu_dau else 'nguoc tu m_n'} = {dk[0][2]:.10g}):")
        print("  m_k = S'(x_k):  m_k + m_(k+1) = gamma_k = 2(y_(k+1) - y_k)/h_k")
        if tu_dau:
            in_bang(["k", "gamma_k", "m_(k+1) = gamma_k - m_k"], [[str(k), g[k], m[k + 1]] for k in range(n)])
        else:
            in_bang(["k", "gamma_k", "m_k = gamma_k - m_(k+1)"],
                    [[str(k), g[k], m[k]] for k in range(n - 1, -1, -1)])
        print(f"  m = (m_0, ..., m_{n}) = {vec(m)}")
    elif bien_the == 3:
        hh, s, (L, Dg, U, R), P, Q, sg, he = spline3(x, y, dk)
        kq["sigma"] = sg
        print("\nHe phuong trinh theo sigma (ma tran bo sung, hang i: l_i sigma_(i-1) + d_i sigma_i + u_i sigma_(i+1) = r_i):")
        print("  sigma_k = S''(x_k),  s_k = (y_(k+1) - y_k)/h_k")
        print("  hang trong: h_(i-1)/6 sigma_(i-1) + (h_(i-1) + h_i)/3 sigma_i + h_i/6 sigma_(i+1) = s_i - s_(i-1)")
        print("  bien: S''(x_0) = A -> sigma_0 = A;  S'(x_0) = A -> h_0/3 sigma_0 + h_0/6 sigma_1 = s_0 - A")
        print("        S''(x_n) = B -> sigma_n = B;  S'(x_n) = B -> h_(n-1)/6 sigma_(n-1) + h_(n-1)/3 sigma_n = B - s_(n-1)")
        Mfull = [[0.0] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            Mfull[i][i] = Dg[i]
            if i:
                Mfull[i][i - 1] = L[i]
            if i < n:
                Mfull[i][i + 1] = U[i]
        in_bang([""] + [f"sigma_{j}" for j in range(n + 1)] + ["| r_i"],
                [[f"i = {i}"] + Mfull[i] + [R[i]] for i in range(n + 1)])
        print("\nTruy duoi xuoi / nguoc:")
        print("  P_0 = -u_0/d_0, Q_0 = r_0/d_0;  mu = d_i + l_i P_(i-1), P_i = -u_i/mu,"
              " Q_i = (r_i - l_i Q_(i-1))/mu;  sigma_n = Q_n, sigma_i = P_i sigma_(i+1) + Q_i")
        in_bang(["i", "l_i", "d_i", "u_i", "r_i", "P_i", "Q_i", "sigma_i"],
                [[str(i), L[i], Dg[i], U[i], R[i], P[i], Q[i], sg[i]] for i in range(n + 1)])
        print(f"  sigma = (sigma_0, ..., sigma_{n}) = {vec(sg)}")
    M, rhs, ten, D, e = spline_tq(x, y, p, dk)                   # muc 4: ket qua chinh hoac kiem tra
    if bien_the == 4:
        if M:
            print(f"\nHe {len(M)} phuong trinh, an = ({', '.join(ten)}):")
            print(f"  D_(k,r) = S^(r)(x_k), r = 1..{p - 1};  S_k(x) = sum_(j<p) D_(k,j)/j! (x - x_k)^j"
                  f" + (D_(k+1,{p - 1}) - D_(k,{p - 1}))/({p}! h_k) (x - x_k)^{p}")
            print("  tai x_(k+1), r = 0..p-2: sum_(j=max(r,1)..p-1) h_k^(j-r)/(j-r)! D_(k,j)"
                  " + h_k^(p-r-1)/(p-r)! (D_(k+1,p-1) - D_(k,p-1)) - [r>=1] D_(k+1,r) = [r=0](y_(k+1) - y_k)")
            print("  bien: D_(0 hoac n, r) = v;  giai bang khu Gauss chon tru")
            in_bang(["pt"] + ten + ["| ve phai"], [[str(i)] + M[i] + [rhs[i]] for i in range(len(M))])
        print("\nNghiem D_(k,r) = S^(r)(x_k):")
        in_bang(["k", "x_k"] + [ten_dh(r) if r else "y_k" for r in range(p)],
                [[str(k), f"{x[k]:.10g}"] + D[k] for k in range(n + 1)])
        print(f"\nHe so dia phuong S_k(x) = sum e_(k,j) (x - x_k)^j (bac cao -> thap) va dang chinh tac (muc 5):")
        print("  dang chinh tac: doi bien u = x - x_k")
        in_bang(["k", "bien"] + [f"u^{j}" if j > 1 else ("u" if j else "1") for j in range(p, -1, -1)],
                [[str(k), f"u = {nhan_tu('x', x[k])}"] + e[k] for k in range(n)])
        he = [doi_bien(e[k], x[k], 1.0)[0] for k in range(n)]
        kq["D"] = D
    print(f"\nHe so chinh tac S_k(x) = " + " + ".join(f"{'abcde'[j]}_k x^{p - j}" if p - j > 1 else
                                                    (f"{'abcde'[j]}_k x" if p - j else f"{'abcde'[j]}_k")
                                                    for j in range(p + 1)) + ":")
    if bien_the == 1:
        print("  S_k(x) = a_k x + b_k,  a_k = (y_(k+1) - y_k)/h_k,  b_k = (y_k x_(k+1) - y_(k+1) x_k)/h_k")
    elif bien_the == 2:
        print("  S_k(x) = [-m_k (x - x_(k+1))^2 + m_(k+1) (x - x_k)^2]/(2h_k) + y_k + m_k h_k/2 = a_k x^2 + b_k x + c_k")
        print("  a_k = (m_(k+1) - m_k)/(2h_k),  b_k = (m_k x_(k+1) - m_(k+1) x_k)/h_k,")
        print("  c_k = (-m_k x_(k+1)^2 + m_(k+1) x_k^2)/(2h_k) + y_k + m_k h_k/2")
    elif bien_the == 3:
        print("  S_k(x) = [-sigma_k (x - x_(k+1))^3 + sigma_(k+1) (x - x_k)^3]/(6h_k) + alpha_k (x - x_k) - beta_k (x - x_(k+1))")
        print("  alpha_k = y_(k+1)/h_k - sigma_(k+1) h_k/6,  beta_k = y_k/h_k - sigma_k h_k/6")
        print("  a_k = (sigma_(k+1) - sigma_k)/(6h_k),  b_k = (sigma_k x_(k+1) - sigma_(k+1) x_k)/(2h_k),")
        print("  c_k = (-sigma_k x_(k+1)^2 + sigma_(k+1) x_k^2)/(2h_k) + s_k - (sigma_(k+1) - sigma_k) h_k/6,")
        print("  d_k = (sigma_k x_(k+1)^3 - sigma_(k+1) x_k^3)/(6h_k) + (y_k x_(k+1) - y_(k+1) x_k)/h_k"
              " + (sigma_(k+1) x_k - sigma_k x_(k+1)) h_k/6")
    in_bang(["k", "[x_k, x_(k+1)]"] + [f"{'abcde'[j]}_k" for j in range(p + 1)],
            [[str(k), f"[{x[k]:.10g}, {x[k + 1]:.10g}]"] + he[k] for k in range(n)])
    print("\nKET QUA (vector he so bac cao -> thap):")
    for k in range(n):
        print(f"  S_{k}(x) = {vec(he[k])} = {da_thuc_str(he[k])},  x in [{x[k]:.10g}, {x[k + 1]:.10g}]")

    print("\nKIEM TRA:")
    kiem("noi suy: max |S_k(x_k) - y_k|, |S_k(x_(k+1)) - y_(k+1)|",
         max(max(abs(np.polyval(he[k], x[k]) - y[k]), abs(np.polyval(he[k], x[k + 1]) - y[k + 1])) for k in range(n)))
    for r in range(1, p):
        if n >= 2:
            kiem(f"tron: max |{ten_dh(r)}_k(x_(k+1)) - {ten_dh(r)}_(k+1)(x_(k+1))|",
                 max(abs(np.polyval(dao_ham_da_thuc(he[k], r), x[k + 1])
                         - np.polyval(dao_ham_da_thuc(he[k + 1], r), x[k + 1])) for k in range(n - 1)))
    for r, k, v in dk:
        kk = 0 if k == 0 else n - 1
        kiem(f"bien: |{ten_dh(r)}({x[k]:.10g}) - ({v:.10g})|", abs(np.polyval(dao_ham_da_thuc(he[kk], r), x[k]) - v))
    if bien_the != 4:
        he4 = [doi_bien(e[k], x[k], 1.0)[0] for k in range(n)]
        kiem("so voi muc 4 (he tong quat): max |he so|, tuong doi",
             max(np.max(np.abs(np.array(he[k]) - np.array(he4[k]))) / max(1.0, np.max(np.abs(he4[k])))
                 for k in range(n)))
    kq.update(he=he, D=D, e=e, bien_the=bien_the)
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
        goc["p"] = nhap("Bac spline p (1..4)", "3")
        ps = doc_day_so(goc["p"], "p", bao)
        if len(ps) != 1 or ps[0] != int(ps[0]) or not 1 <= ps[0] <= 4:
            raise ValueError("p phai la 1 so nguyen trong 1..4.")
        p = int(ps[0])
        so_dong, ts = None, {}
        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "0 0.5236 1.5708 1.0472 3.1416")
            goc["y"] = nhap("Cac gia tri y_i", "1 0.866 0 -0.866 -1")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            B = doc_bang_file(bang, nhap, bao)
            ox, oy, vi_tri, so_dong, ts = B["x"], B["y"], B["vi_tri"], B["so"], B["ts"]
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao, so_dong, None if tra_loi is not None else hoi_moc_trung)
        if len(x) < 2:
            raise ValueError("can it nhat 2 moc.")
        dk = []
        if p > 1:
            vd = {2: f"S'({x[0]:.10g}) = 0", 3: f"S''({x[0]:.10g}) = -1; S''({x[-1]:.10g}) = 1",
                  4: f"S'({x[0]:.10g}) = 0; S''({x[0]:.10g}) = -1; S'({x[-1]:.10g}) = 0"}[p]
            goc["dieu kien bien"] = nhap(f"{p - 1} dieu kien bien", vd)
            dk = doc_bien(goc["dieu kien bien"], x, p, bao)
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

    try:
        giai(x, y, p, dk)
    except ValueError as e:
        print(f"\nLoi: {e}")


if __name__ == "__main__":
    main()
