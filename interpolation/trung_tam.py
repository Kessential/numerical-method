"""
NOI SUY TRUNG TAM: GAUSS I, GAUSS II, STIRLING, BESSEL (MOC CACH DEU)
Thuat toan: docs/thuat_toan/trung_tam.md

Bo diem cach deu (x_i, y_i); chi so tuong doi voi moc trung tam x_0 (co chi so am), t = (x - x_0)/h.
P(x_0 + th) = sum_k c_k * pi_k(t);  vector he so in tu BAC CAO xuong BAC THAP.
Cong thuc (chon 1 hoac nhieu, cach nhau boi khoang trang):
  1. Gauss I   -> ket nap phai truoc: x_0, x_1, x_-1, x_2, ...  (hop 0 < t < 1/2)
  2. Gauss II  -> ket nap trai truoc: x_0, x_-1, x_1, x_-2, ... (hop -1/2 < t < 0)
  3. Stirling  -> so moc le, x_0 chinh giua                     (hop |t| <= 1/4)
  4. Bessel    -> so moc chan, x_0 va x_1 chinh giua            (hop 1/4 <= t <= 3/4)
Bang dai hon m moc -> trich xuat m moc gan xbar nhat (muc 1); Stirling can m le, Bessel can m chan
(sai -> m - 1, co bao). Moi cong thuc: bang sai phan (o duoc chon dat trong [ ]), bang tich, P,
Horner chia lap tai xbar -> f(xbar), f^(j)(xbar) = P^(j)/h^j.
Gauss I/II: bang tich theo t. Stirling/Bessel: tach he so le / chan nhu file Excel mau
(slide_example/VD noi suy moc cach deu.xlsx): bang tich theo u = t^2 (Bessel: u = v^2, v = t - 1/2),
ghep xen ke P(t) = y_0 + t P_le(t^2) + t^2 P_chan(t^2)  /  P(v) = P_chan(v^2) + v P_le(v^2).

Cach chay:
  python interpolation/trung_tam.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/trung_tam.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi:
                                                       cong thuc / x / y / xbar / k / m
  python interpolation/trung_tam.py data/<file>.csv -> file chi chua bang: 2 hang hoac 2 cot x, y (lay 2 cot dau,
                                                       .xlsx: sheet dau, can pandas + openpyxl); cau con lai nhap tay
  VD cau 16: python interpolation/trung_tam.py "slide_example/data Câu 11.xlsx"  roi nhap: 3 / 7.83 / 1 / 9
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


def so_le(y):
    """So chu so thap phan d cua du lieu (y_i = so nguyen * 10^-d); sai phan lam tron ve d chu so la dung."""
    for d in range(11):
        if all(abs(v * 10 ** d - round(v * 10 ** d)) < 1e-6 for v in y):
            return d
    return None


def o_bang(v, d):
    """O bang sai phan: d chu so thap phan cua du lieu (giu so 0 cuoi, vd 0.0000000); d = None -> fmt."""
    if d is None:
        return fmt(v)
    s = format(round(v, d), f".{d}f")
    return s[1:] if s.startswith("-") and float(s) == 0 else s


# ===== THUAT TOAN =====
# Vector he so luu tu bac cao -> thap (giong luc in).

TEN = {1: "Gauss I", 2: "Gauss II", 3: "Stirling", 4: "Bessel"}


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


def trich_xuat(x, xbar, m):
    """Muc 1 (= muc 7, newton.md): m moc gan xbar nhat. Tra ve (L, R, thu tu ket nap j_1..j_m)."""
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


def bang_sai_phan(y):
    """Muc 2, Buoc 3-4: D[s][k] = Delta^k y_(p+s) (hang s cua bo moc con), s = 0..n-k.
    y co d chu so thap phan -> sai phan dung d chu so, lam tron de khu sai so dau phay dong."""
    n = len(y) - 1
    dl = so_le(y)
    D = [[None] * (n + 1) for _ in range(n + 1)]
    for s in range(n + 1):                         # Buoc 3 - Cot 0
        D[s][0] = y[s]
    for k in range(1, n + 1):                      # Buoc 4
        for s in range(n - k + 1):
            d = D[s + 1][k - 1] - D[s][k - 1]
            D[s][k] = round(d, dl) if dl is not None else d
    return D


def vi_tri_tam(n, ct):
    """Muc 2, Buoc 1: vi tri q cua x_0 trong bo moc con 0..n (p = -q)."""
    return n // 2 if ct in (1, 4) else (n + 1) // 2


def he_so(D, p, ct):
    """Muc 3, Buoc 1: c_k va cac o (i, k) duoc chon trong bang (i = chi so tuong doi)."""
    n = len(D) - 1
    c, chon, gt = [], [], 1.0
    for k in range(n + 1):
        gt *= max(k, 1)                            # k! tinh dan
        j = k // 2
        if ct == 1:                                # Gauss I: Delta^k y_(-floor(k/2))
            o = [-j]
        elif ct == 2:                              # Gauss II: Delta^k y_(-ceil(k/2))
            o = [-((k + 1) // 2)]
        elif ct == 3:                              # Stirling: k chan 1 o, k le trung binh 2 o
            o = [-j] if k % 2 == 0 else [-(j + 1), -j]
        else:                                      # Bessel: k chan trung binh 2 o, k le 1 o
            o = [-j, -j + 1] if k % 2 == 0 else [-j]
        c.append(sum(D[i - p][k] for i in o) / len(o) / gt)
        chon.append([(i, k) for i in o])
    return c, chon


def bang_tich(n, ct):
    """Muc 3, Buoc 2.1 (Gauss I/II): pi_0..pi_n theo t (he so bac cao -> thap) va nut z_0..z_(n-1)."""
    pi, z = [[1.0]], []
    for k in range(1, n + 1):                      # pi_k = pi_(k-1) (t - z_(k-1))
        zk = k // 2 if k % 2 == 0 else -(k // 2)   # Gauss I: z = 0, 1, -1, 2, -2, ...
        zk = zk if ct == 1 else -zk                # Gauss II: z = 0, -1, 1, -2, 2, ...
        pi.append(horner_nhan(pi[k - 1], zk))
        z.append(zk)
    return pi, z


def bang_tich_u(s, ct):
    """Muc 3, Buoc 3.2 (Stirling/Bessel): Pi_0..Pi_(s-1) theo u va nut zeta_j = j^2 hoac (j - 1/2)^2."""
    Pi, zeta = [[1.0]], []
    for j in range(1, s):                          # Pi_j = Pi_(j-1) (u - zeta_j)
        zj = float(j * j) if ct == 3 else (j - 0.5) ** 2
        Pi.append(horner_nhan(Pi[j - 1], zj))
        zeta.append(zj)
    return Pi, zeta


def to_hop(c, pi):
    """Muc 3, Buoc 2.2 / 3.3: sum c_k * pi_k (he so bac cao -> thap, bac = len(c) - 1)."""
    n = len(c) - 1
    B = [0.0] * (n + 1)                            # B[l] = he so cua bien^l
    for ck, p_k in zip(c, pi):
        for l, v in enumerate(reversed(p_k)):
            B[l] += ck * v
    return B[::-1]


def lap_P(c, n, ct):
    """Muc 3, Buoc 2-4: P theo bien w (t; Bessel: v = t - 1/2). Tra ve dict(b, bien, lech = t - w, bang tich...)."""
    if ct in (1, 2):                               # Buoc 2 - TH1 Gauss I / II: bang tich theo t
        pi, z = bang_tich(n, ct)
        return dict(b=to_hop(c, pi), bien="t", lech=0.0, pi=pi, z=z)
    s = n // 2 if ct == 3 else (n + 1) // 2        # Buoc 3 - TH2 Stirling / Bessel
    if ct == 3:                                    # Buoc 3.1 - Tach he so le / chan
        cl, cc = [c[2 * j + 1] for j in range(s)], [c[2 * j + 2] for j in range(s)]
    else:
        cc, cl = [c[2 * j] for j in range(s)], [c[2 * j + 1] for j in range(s)]
    Pi, zeta = bang_tich_u(s, ct)                  # Buoc 3.2 - Bang tich theo u
    Pl, Pc = to_hop(cl, Pi), to_hop(cc, Pi)        # Buoc 3.3 - Cong don
    b = []
    for l in range(s):                             # Buoc 3.4 - Ghep xen ke
        b += [Pc[l], Pl[l]] if ct == 3 else [Pl[l], Pc[l]]
    if ct == 3:
        b.append(c[0])
    return dict(b=b, bien="t" if ct == 3 else "v", lech=0.0 if ct == 3 else 0.5,
                Pi=Pi, zeta=zeta, cl=cl, cc=cc, Pl=Pl, Pc=Pc)


def tai_xbar(b, tb, h, k):
    """Muc 4, Buoc 1-2: (r, d, v, hang Horner); d_j = P^(j)(t), v_j = d_j / h^j."""
    r, d, hang = horner_dao_ham(b, tb, k)
    v, hj = [], 1.0
    for dj in d:
        v.append(dj / hj)
        hj *= h
    return r, d, v, hang


def log_E(p, n, tb, h):
    """Muc 4, Buoc 3: log(h^(n+1)/(n+1)! * prod |t - i|), -inf neu t trung moc."""
    if any(abs(tb - i) < 1e-12 for i in range(p, p + n + 1)):
        return -math.inf
    return ((n + 1) * math.log(h) + sum(math.log(abs(tb - i)) for i in range(p, p + n + 1))
            - math.lgamma(n + 2))


# ===== GIAI =====

CHUOI = {                                          # chuoi cong thuc cua phuong phap
    1: ["P(x_0 + th) = y_0 + t Dy_0 + t(t-1)/2! D2y_-1 + (t+1)t(t-1)/3! D3y_-1 + (t+1)t(t-1)(t-2)/4! D4y_-2 + ..."],
    2: ["P(x_0 + th) = y_0 + t Dy_-1 + (t+1)t/2! D2y_-1 + (t+1)t(t-1)/3! D3y_-2 + (t+2)(t+1)t(t-1)/4! D4y_-2 + ..."],
    3: ["P(x_0 + th) = y_0 + t (Dy_-1 + Dy_0)/2 + t^2/2! D2y_-1 + t(t^2-1)/3! (D3y_-2 + D3y_-1)/2"
        " + t^2(t^2-1)/4! D4y_-2 + ..."],
    4: ["P(x_0 + th) = (y_0 + y_1)/2 + (t - 1/2) Dy_0 + t(t-1)/2! (D2y_-1 + D2y_0)/2 + (t - 1/2)t(t-1)/3! D3y_-1 + ..."],
}
HE_SO = {
    1: "c_k = D^k y_(-floor(k/2)) / k!",
    2: "c_k = D^k y_(-ceil(k/2)) / k!",
    3: "c_(2j-1) = (D^(2j-1)y_(-j) + D^(2j-1)y_(-j+1)) / (2 (2j-1)!),  c_(2j) = D^(2j)y_(-j) / (2j)!",
    4: "c_(2j) = (D^(2j)y_(-j) + D^(2j)y_(-j+1)) / (2 (2j)!),  c_(2j+1) = D^(2j+1)y_(-j) / (2j+1)!",
}
TICH = {
    1: "pi_0 = 1,  pi_k = pi_(k-1) (t - z_(k-1)),  z = 0, 1, -1, 2, -2, ...  (Horner nhan)",
    2: "pi_0 = 1,  pi_k = pi_(k-1) (t - z_(k-1)),  z = 0, -1, 1, -2, 2, ...  (Horner nhan)",
    3: "u = t^2,  Pi_0 = 1,  Pi_j = Pi_(j-1) (u - j^2)  (Horner nhan);"
       "  P_le(u) = sum_j c_(2j+1) Pi_j,  P_chan(u) = sum_j c_(2j+2) Pi_j",
    4: "v = t - 1/2,  u = v^2,  Pi_0 = 1,  Pi_j = Pi_(j-1) (u - (j - 1/2)^2)  (Horner nhan);"
       "  P_chan(u) = sum_j c_(2j) Pi_j,  P_le(u) = sum_j c_(2j+1) Pi_j",
}


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


def ten_he_so(k, o):
    """Ten c_k theo cac o duoc chon: y_0, Dy_0, D2y_-1/2!, (D3y_-2 + D3y_-1)/(2*3!), ..."""
    ten = [(f"D{k}y_{i}" if k > 1 else "Dy_" + str(i) if k else f"y_{i}") for i, _ in o]
    if len(ten) == 1:
        return ten[0] + (f"/{k}!" if k > 1 else "")
    return f"({ten[0]} + {ten[1]})/" + (f"(2*{k}!)" if k > 1 else "2")


def in_vec_ten(ten, ten_o, gia_tri):
    """In 'ten = (ten_0; ten_1; ...)' roi dong duoi '= (gia tri; ...)'."""
    print(f"  {ten} = ({'; '.join(ten_o)})")
    print(f"  {' ' * len(ten)} = ({'; '.join(fmt(v) for v in gia_tri)})")


def giai(x, y, ct, xbar, k, m, h):
    """1 cong thuc, 1 xbar: x, y la ca bang (da sach, cach deu); dung m moc gan xbar nhat."""
    N = len(x) - 1
    trich = m < N + 1
    L, R, thu_tu = trich_xuat(x, xbar, m) if trich else (0, N, None)   # Muc 1
    xs, ys = x[L:R + 1], y[L:R + 1]
    n = m - 1
    q = vi_tri_tam(n, ct)                                               # Muc 2, Buoc 1
    p = -q
    x0 = xs[q]
    tb = (xbar - x0) / h                                                # Muc 2, Buoc 2
    d = so_le(ys)

    print(f"\nNoi suy {TEN[ct]}: {m} moc, moc cach deu h = {h:.10g}, xbar = {xbar:.10g}")
    if trich:
        print(f"  (trich xuat {m} moc gan xbar nhat tu bang {N + 1} moc [{x[0]:.10g}, {x[-1]:.10g}])")
    print(f"  x = {vec(xs, '.10g')}")
    print(f"  y = {vec(ys, '.10g')}")

    print("\nTINH TOAN:")
    chi_so = f"(i = {p}..{p + n})"
    if trich:
        print(f"Trich xuat (muc 1): thu tu ket nap moc gan xbar = {xbar:.10g} nhat:")
        print("  j_1 = argmin |xbar - x_i|;  ket nap dan x_(L-1) neu xbar - x_(L-1) <= x_(R+1) - xbar,"
              " nguoc lai x_(R+1)")
        in_bang(["lan", "chi so goc", "x_j", "|xbar - x_j|", "y_j"],
                [[str(s), str(j), f"{x[j]:.10g}", abs(xbar - x[j]), f"{y[j]:.10g}"]
                 for s, j in enumerate(thu_tu, 1)])
        print(f"  => bo moc con x_{L}..x_{R} = [{xs[0]:.10g}, {xs[-1]:.10g}], danh so lai {chi_so}"
              f" quanh moc trung tam x_0 = {x0:.10g}:")
        in_ngang([("i", [str(p + s) for s in range(m)]), ("x_i", [f"{v:.10g}" for v in xs]),
                  ("y_i", [f"{v:.10g}" for v in ys])])
        print()
    print(f"t = (xbar - x_0)/h = ({xbar:.10g} - {x0:.10g}) / {h:.10g} = {tb:.10g}")
    if ct in (1, 2):
        hop = (tb >= 0) == (ct == 1)
        dau = (">" if tb > 0 else "=" if tb == 0 else "<") + " 0"
        ly_do = f"t = {tb:.10g} {dau} nen dung {TEN[ct]}" if hop else f"dung {TEN[ct]} (t = {tb:.10g} {dau})"
        print(f"Phuong phap: {ly_do}, x_0 = {x0:.10g} {chi_so}")
    elif ct == 3:
        print(f"Phuong phap: {m} moc cach deu (so le) nen dung Stirling, x_0 = {x0:.10g} {chi_so}")
    else:
        print(f"Phuong phap: {m} moc cach deu (so chan) nen dung Bessel, x_0 = {x0:.10g},"
              f" x_1 = {xs[q + 1]:.10g} {chi_so}")
        print(f"  v = t - 1/2 = {tb - 0.5:.10g}")
    for dong in CHUOI[ct]:
        print("  " + dong)

    D = bang_sai_phan(ys)                                               # Muc 2, Buoc 3-4
    c, chon = he_so(D, p, ct)                                           # Muc 3, Buoc 1
    duoc_chon = {o for ds in chon for o in ds}
    print(f"\nBang sai phan (hang i: y_i, D y_i, D^2 y_i, ...; o [ ] duoc chon cho {TEN[ct]}):")
    print("  D^0 y_i = y_i,  D^k y_i = D^(k-1) y_(i+1) - D^(k-1) y_i   (D = Delta)")
    hang = []
    for s in range(n + 1):
        i = p + s
        o = []
        for kk in range(n + 1 - s):
            v = o_bang(D[s][kk], d)
            o.append(f"[{v}]" if (i, kk) in duoc_chon else v)
        hang.append([str(i), f"{xs[s]:.10g}"] + o + [None] * s)
    in_bang(["i", "x_i", "y_i"] + [f"D{kk}" for kk in range(1, n + 1)], hang)

    P = lap_P(c, n, ct)                                                 # Muc 3, Buoc 2-4
    b, w, lech = P["b"], P["bien"], P["lech"]
    print("\nHe so:")
    print("  " + HE_SO[ct])
    if ct in (1, 2):
        in_vec_ten("C", [ten_he_so(kk, chon[kk]) for kk in range(n + 1)], c)
    else:
        if ct == 3:
            print(f"  c_0 = y_0 = {ys[q]:.10g}")
            k_chan, k_le = range(2, n + 1, 2), range(1, n + 1, 2)
        else:
            k_chan, k_le = range(0, n + 1, 2), range(1, n + 1, 2)
        for ten, ks, he in (("C_chan", k_chan, P["cc"]), ("C_le", k_le, P["cl"])):
            if he:
                in_vec_ten(ten, [ten_he_so(kk, chon[kk]) for kk in ks], he)

    s0 = x0 + lech * h                                                  # Bessel: v = (x - (x_0 + h/2))/h
    voi = "  voi " + (f"t = ({nhan_tu('x', x0)}) / {h:.10g}" if ct != 4 else
                      f"v = t - 1/2 = ({nhan_tu('x', s0)}) / {h:.10g}")
    if ct in (1, 2):
        print("\nBang tich theo t (hang k: pi_k = pi_(k-1) (t - z_(k-1)), he so bac cao -> thap); "
              "P(t) = sum c_k * hang k:")
        print("  " + TICH[ct])
        in_bang(["k", "z_(k-1)", "c_k"] + cot_mu(n, "t"),
                [[str(kk), "" if kk == 0 else f"{P['z'][kk - 1]:.10g}", c[kk]] + [None] * (n - kk) + pk
                 for kk, pk in enumerate(P["pi"])] + [None] + [["P(t)", "", ""] + b],
                khung=3, nhan_khung="ma tran A (hang k: he so cua pi_k(t))")
        print(f"  P_{n} = C.A = {vec(b)}")
        print(f"  P_{n}(t) = {da_thuc_str(b, 't')}")
        print(voi)
    elif not P["cl"]:
        print("\n1 moc: P(t) = y_0")
    else:
        s = len(P["cl"])
        nut = "j^2" if ct == 3 else "(j-1/2)^2"
        ten_c, cot_c = ((("c_(2j+1)", "c_(2j+2)"), (P["cl"], P["cc"])) if ct == 3 else
                        (("c_(2j)", "c_(2j+1)"), (P["cc"], P["cl"])))
        tong = ((("P_le(u)", P["Pl"]), ("P_chan(u)", P["Pc"])) if ct == 3 else
                (("P_chan(u)", P["Pc"]), ("P_le(u)", P["Pl"])))
        print(f"\nBang tich theo {'u = t^2' if ct == 3 else 'u = v^2, v = t - 1/2'} "
              f"(hang j: Pi_j = Pi_(j-1) (u - {nut}), he so bac cao -> thap):")
        print("  " + TICH[ct])
        in_bang(["j", nut, ten_c[0], ten_c[1]] + cot_mu(s - 1, "u"),
                [[str(j), "" if j == 0 else f"{P['zeta'][j - 1]:.10g}", cot_c[0][j], cot_c[1][j]]
                 + [None] * (s - 1 - j) + P["Pi"][j] for j in range(s)]
                + [None] + [[ten, "", "", ""] + list(he) for ten, he in tong],
                khung=4, nhan_khung="ma tran A (hang j: he so cua Pi_j(u))")
        print(f"  P_chan = C_chan.A = {vec(P['Pc'])}")
        print(f"  P_le   = C_le.A   = {vec(P['Pl'])}")
        print("  Ghep xen ke he so chan / le: " + ("P(t) = y_0 + t P_le(t^2) + t^2 P_chan(t^2)" if ct == 3 else
                                                  "P(v) = P_chan(v^2) + v P_le(v^2)"))
        print(f"  b = {vec(b)}")
        print(f"  P_{n}({w}) = {da_thuc_str(b, w)}")
        print(voi)

    a, _ = doi_bien(b, s0, h)                                           # P theo x (muc 5, newton.md)

    wb = tb - lech
    r, dd, v, hang_h = tai_xbar(b, wb, h, k)                            # Muc 4
    print(f"\nHorner chia lap tai {w} = {wb:.10g} (hang j: he so sau lan chia thu j+1, o cuoi r_j):")
    print(f"  f^(j)(xbar) ~ P^(j)({w}) / h^j = j! r_j / h^j")
    in_bang([""] + cot_mu(n, w), [[f"P({w})"] + b] + [[f"j = {j}"] + hh for j, hh in enumerate(hang_h)])
    for j in range(len(r)):
        dong = f"  P^({j})({w}) = {j}! * {so_ngoac(r[j])} = {fmt(dd[j])}"
        if j:
            dong += f"  ->  f^({j})(xbar) ~ {so_ngoac(dd[j])} / {h:.10g}^{j} = {fmt(v[j])}"
        print(dong)
    lE = log_E(p, n, tb, h)
    E = math.exp(lE) if lE < 709 else math.inf

    print("\nKET QUA (vector he so bac cao -> thap):")
    print(f"  {TEN[ct]}, x_0 = {x0:.10g}, h = {h:.10g}, {w} = ({nhan_tu('x', s0)}) / {h:.10g}:")
    print(f"    P_{n}({w}) = b = (b_{n}, ..., b_0) = {vec(b)}")
    print(f"    P_{n}({w}) = {da_thuc_str(b, w)}")
    print(f"    P_{n}(x) = a = (a_{n}, ..., a_0) = {vec(a)}")
    print(f"    P_{n}(x) = {da_thuc_str(a)}")
    ten = "(f(xbar))" if k == 0 else f"(f(xbar), ..., f^({k})(xbar))"
    print(f"  xbar = {xbar:.10g} ({w} = {wb:.10g}): {ten} ~ {vec(v)}")
    print(f"    f({xbar:.10g}) ~ {fmt(v[0])}" + (f",  f'({xbar:.10g}) ~ {fmt(v[1])}" if k else ""))
    print(f"    sai so: |f(xbar) - P_{n}(xbar)| <= M_{n + 1} * {h:.10g}^{n + 1} / {n + 1}! * |prod (t - i)|"
          f" = M_{n + 1} * {fmt(E, nho=0)}")
    print("\nKIEM TRA:")
    wi = np.arange(p, p + n + 1, dtype=float) - lech                   # moc theo bien w
    kiem(f"max |P({w}_i) - y_i|, {w}_i = i" + (" - 1/2" if lech else ""), np.max(np.abs(np.polyval(b, wi) - ys)))
    b_np = np.linalg.solve(np.vander(wi, n + 1), ys) if n else np.array(ys)
    kiem(f"he so P({w}) vs numpy.linalg.solve(vander({w}_i)), tuong doi",
         np.max(np.abs(np.array(b) - b_np)) / max(1.0, np.max(np.abs(b_np))))
    kiem("f(xbar) vs cong thuc Lagrange truc tiep", abs(lagrange_tai(xs, ys, xbar) - v[0]))
    kiem(f"f^(j)(xbar) vs numpy.polyder, j = 0..{min(k, n)}",
         max(abs(np.polyval(np.polyder(b_np, j) if j else b_np, wb) / h ** j - v[j]) for j in range(min(k, n) + 1)))
    kiem("P(x) (doi bien) tai x_i vs y_i", np.max(np.abs(np.polyval(a, xs) - ys)))
    return dict(b=b, a=a, c=c, v=v, t=tb, w=wb, bien=w, lech=lech, x0=x0, xs=xs, ys=ys, p=p, D=D, chon=chon,
                P=P, E=E)


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
    viec = []         # (cong thuc, xbar, m)
    try:
        if tra_loi is None:
            print("Cong thuc (chon 1 hoac nhieu, cach nhau boi khoang trang):")
            for so, ten in TEN.items():
                print(f"  {so}. {ten}")
        goc["cong thuc"] = nhap("Chon cong thuc", "3")
        so_ct = doc_day_so(goc["cong thuc"], "cong thuc", bao)
        cts = sorted({int(v) for v in so_ct if v in (1, 2, 3, 4)})
        if len(cts) != len(set(so_ct)):
            bao.append("cong thuc: loai cac gia tri ngoai 1..4")
        if not cts:
            raise ValueError("Khong co cong thuc hop le (1..4).")

        so_dong, ts = None, {}
        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "1.4 1.5 1.6 1.7 1.8 1.9 2 2.1 2.2")
            goc["y"] = nhap("Cac gia tri y_i",
                            "2.4347052 2.5473627 2.6495552 2.741261 2.8225627 2.8936474 2.9548 3.0064203 3.0489801")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            B = doc_bang_file(bang, nhap, bao)
            ox, oy, vi_tri, so_dong, ts = B["x"], B["y"], B["vi_tri"], B["so"], B["ts"]
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao, so_dong, None if tra_loi is not None else hoi_moc_trung)
        if len(x) < 2:
            raise ValueError("can it nhat 2 moc.")
        h = cach_deu(x)
        if h is None:
            raise ValueError("moc khong cach deu -> khong dung duoc noi suy trung tam (dung newton.py, moc bat ky).")

        vd = "1.63" if bang is None else f"{(x[0] + x[-1]) / 2:.10g}"   # bang tu file: trung diem
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
        goc["k"] = nhap("Cap dao ham k", "1")
        ks = doc_day_so(goc["k"], "k", bao)
        if len(ks) != 1 or ks[0] < 0 or ks[0] != int(ks[0]):
            raise ValueError("k phai la 1 so nguyen >= 0.")
        k = int(ks[0])
        goc["m"] = nhap("So moc dung m", str(len(x)))
        ms = doc_day_so(goc["m"], "m", bao)
        if len(ms) != 1 or ms[0] < 2 or ms[0] != int(ms[0]):
            raise ValueError("m phai la 1 so nguyen >= 2.")
        m = int(ms[0])
        if m > len(x):
            bao.append(f"m = {m} > so moc {len(x)} -> dung ca {len(x)} moc")
            m = len(x)
        for ct in cts:                             # dieu kien rieng: Stirling m le, Bessel m chan
            mc = m
            if ct == 3 and mc % 2 == 0:
                mc -= 1
                bao.append(f"Stirling can so moc le: m = {m} -> {mc} (bo moc bien xa xbar nhat)")
            if ct == 4 and mc % 2 == 1:
                mc -= 1
                bao.append(f"Bessel can so moc chan: m = {m} -> {mc} (bo moc bien xa xbar nhat)")
            viec += [(ct, xb, mc) for xb in xbars]
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
        print(f"  Du lieu sach ({len(x)} moc, cach deu h = {h:.10g}):")
        print(f"    x = {ngan(vec(x, '.10g'))}")
        print(f"    y = {ngan(vec(y, '.10g'))}")
        print(f"    xbar = {vec(xbars, '.10g')},  k = {k},  m = {m}")

    for ct, xb, mc in viec:
        giai(x, y, ct, xb, k, mc, h)


if __name__ == "__main__":
    main()
