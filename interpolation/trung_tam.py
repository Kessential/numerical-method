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
(sai -> m - 1, co bao). Moi cong thuc: bang sai phan (o duoc chon dat trong [ ]), bang tich, P(t),
Horner chia lap tai t = (xbar - x_0)/h -> f(xbar), f^(j)(xbar) = P^(j)(t)/h^j.

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

import numpy as np

# ===== CAC HAM CONG CU =====

def fmt(v, spec=".6f"):
    """Dinh dang so, |v| < 1e-12 in thanh 0."""
    if abs(v) < 1e-12:
        v = 0.0
    return format(v, spec)


def fmt_bang(v):
    """So trong bang: .6f; |v| qua nho / qua lon -> .6e de khong mat chu so."""
    if abs(v) >= 1e-12 and (abs(v) < 1e-3 or abs(v) >= 1e9):
        return format(v, ".6e")
    return fmt(v)


def vec(v, spec=".10g"):
    """In vector dang [v0, v1, ...]."""
    return "[" + ", ".join(fmt(x, spec) for x in v) + "]"


def ngan(s, toi_da=240):
    """Rut gon chuoi qua dai (bang du lieu lon) khi in XU LY DU LIEU."""
    return s if len(s) <= toi_da else s[:toi_da // 2] + " ... " + s[-toi_da // 4:]


def da_thuc_str(he_so, bien="x"):
    """Chuoi da thuc tu he so bac cao -> thap."""
    n = len(he_so) - 1
    parts = []
    for i, a in enumerate(he_so):
        if abs(a) < 1e-12:
            continue
        k = n - i
        mag = f"{abs(a):.10g}"
        if k == 0:
            term = mag
        elif k == 1:
            term = bien if mag == "1" else f"{mag}{bien}"
        else:
            term = f"{bien}^{k}" if mag == "1" else f"{mag}{bien}^{k}"
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


def in_bang(cot, hang, le="  "):
    """In bang; o la so / chuoi / None (trong); hang = None -> ke ngang. Do rong tung cot tu dong."""
    S = [None if h is None else ["" if v is None else v if isinstance(v, str) else fmt_bang(v) for v in h]
         for h in hang]
    so_cot = max([len(cot)] + [len(h) for h in S if h])
    rong = [len(cot[j]) if j < len(cot) else 0 for j in range(so_cot)]
    for h in S:
        for j, s in enumerate(h or []):
            rong[j] = max(rong[j], len(s))
    rong = [r + 2 for r in rong]
    ke = le + "-" * sum(rong)
    print(le + "".join(f"{c:>{r}}" for c, r in zip(cot, rong)))
    print(ke)
    for h in S:
        print(ke if h is None else le + "".join(f"{s:>{r}}" for s, r in zip(h, rong)))


def so_ngoac(v):
    """So .10g; so am dat trong ngoac."""
    s = fmt(v, ".10g")
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


def doc_bang_file(duong_dan):
    """Doc bang tu .csv / .xlsx: 2 hang (x, y) hoac 2 cot (x, y). Tra ve (o_x, o_y, ten vi tri)."""
    if duong_dan.lower().endswith((".xlsx", ".xls")):
        try:
            import pandas as pd
            df = pd.read_excel(duong_dan, header=None, dtype=str)
        except ImportError as e:
            raise ValueError(f"doc file Excel can pandas + openpyxl ({e}); hay luu bang thanh .csv.")
        luoi = [["" if not isinstance(v, str) else v for v in h] for h in df.values.tolist()]
    else:
        with open(duong_dan, encoding="utf-8-sig") as f:
            dong = f.read().splitlines()
        if any(re.search(r"[;\t]", d) for d in dong):
            luoi = [tach_o(d) for d in dong]
        else:
            luoi = [list(h) for h in csv.reader(dong)]    # csv chuan: ',' la dau phan tach
    luoi = [h for h in luoi if any(c.strip() for c in h)]
    if not luoi:
        raise ValueError(f"file '{duong_dan}' khong co du lieu.")
    so_cot = max(len(h) for h in luoi)
    luoi = [h + [""] * (so_cot - len(h)) for h in luoi]
    giu = [j for j in range(so_cot) if any(h[j].strip() for h in luoi)]   # bo cot rong
    luoi = [[h[j] for j in giu] for h in luoi]
    if len(luoi) == 2 and len(luoi[0]) > 2:                               # 2 hang: x / y
        return bo_nhan(luoi[0]), bo_nhan(luoi[1]), "o thu"
    if len(luoi[0]) < 2:
        raise ValueError("bang can 2 hang hoac 2 cot (x, y).")
    if doc_o(luoi[0][0])[0] is None and doc_o(luoi[0][1])[0] is None:     # hang tieu de
        luoi = luoi[1:]
    return [h[0] for h in luoi], [h[1] for h in luoi], "dong"


def lam_sach(ox, oy, vi_tri, bao):
    """Buoc 0: cap o (x, y) -> x, y sach, phan biet, sap tang. Ghi bao cao vao bao; loi -> ValueError."""
    if len(ox) != len(oy):
        raise ValueError(f"hang x co {len(ox)} o, hang y co {len(oy)} o -> khong ghep cap duoc.")
    sua, diem = {}, []
    for j, (a, b) in enumerate(zip(ox, oy), 1):
        vx, sx, lx = doc_o(a)
        vy, sy, ly = doc_o(b)
        for ten, ds in (("x", sx), ("y", sy)):
            for g in ds:
                sua.setdefault(f"{ten}: {g}", []).append(j)
        if lx or ly:
            ly_do = ", ".join(f"{t} = {o!r}: {l}" for t, o, l in (("x", a, lx), ("y", b, ly)) if l)
            bao.append(f"loai cap {vi_tri} {j} ({ly_do})")
        else:
            diem.append((vx, vy))
    thu_tu = sorted(sua.items(), key=lambda m: m[0][0])            # gom ghi chu cua x truoc, y sau
    bao[:0] = [f"{g} ({vi_tri} {', '.join(map(str, ds))})" for g, ds in thu_tu]
    if not diem:
        raise ValueError("khong con diem nao hop le.")

    eps_y = 1e-3 * max(1.0, max(abs(p[1]) for p in diem))
    nhom = {}
    for xv, yv in diem:
        nhom.setdefault(xv, []).append(yv)
    gop = []
    for xv, ys in nhom.items():
        if len(ys) == 1:
            gop.append((xv, ys[0]))
        elif max(ys) == min(ys):
            bao.append(f"moc trung x = {xv:.10g} ({len(ys)} lan, cung y = {ys[0]:.10g}) -> giu 1")
            gop.append((xv, ys[0]))
        elif max(ys) - min(ys) <= eps_y:
            tb = sum(ys) / len(ys)
            bao.append(f"moc trung x = {xv:.10g}, y = {vec(ys)} chenh {max(ys) - min(ys):.3g} <= eps_y = "
                       f"{eps_y:.3g} -> lay trung binh y = {tb:.10g}")
            gop.append((xv, tb))
        else:
            raise ValueError(f"moc trung x = {xv:.10g} co y = {vec(ys)} chenh {max(ys) - min(ys):.3g} > eps_y = "
                             f"{eps_y:.3g} -> khong co da thuc noi suy.")
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
    """O bang sai phan: d chu so thap phan neu biet, nguoc lai .10g."""
    return fmt(round(v, d), f".{d}f") if d is not None else fmt(v, ".10g")


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
    """Muc 3, Buoc 2: pi_0..pi_n (he so bac cao -> thap) va chuoi thua so nhan them."""
    pi, nhan = [[1.0]], ["1"]
    for k in range(1, n + 1):
        if ct in (1, 2):                           # Gauss: pi_k = pi_(k-1) (t - z_(k-1))
            z = k // 2 if k % 2 == 0 else -(k // 2)
            z = z if ct == 1 else -z
            pi.append(horner_nhan(pi[k - 1], z))
            nhan.append(f"pi_{k - 1} * ({nhan_tu('t', z)})")
        elif ct == 3:                              # Stirling
            if k == 1:
                pi.append([1.0, 0.0])
                nhan.append("t")
            elif k % 2 == 0:
                pi.append(horner_nhan(pi[k - 1], 0.0))
                nhan.append(f"pi_{k - 1} * t")
            else:
                j = k // 2
                pi.append(horner_nhan(horner_nhan(pi[k - 2], j), -j))
                nhan.append(f"pi_{k - 2} * (t^2 - {j * j})")
        else:                                      # Bessel
            if k % 2 == 0:
                j = k // 2
                pi.append(horner_nhan(horner_nhan(pi[k - 2], -(j - 1)), j))
                nhan.append(f"pi_{k - 2} * ({nhan_tu('t', -(j - 1))})({nhan_tu('t', j)})")
            else:
                pi.append(horner_nhan(pi[k - 1], 0.5))
                nhan.append(f"pi_{k - 1} * (t - 0.5)")
    return pi, nhan


def to_hop(c, pi):
    """Muc 3, Buoc 3: b = sum c_k * pi_k (he so bac cao -> thap)."""
    n = len(c) - 1
    B = [0.0] * (n + 1)                            # B[l] = he so cua t^l
    for ck, p_k in zip(c, pi):
        for l, v in enumerate(reversed(p_k)):
            B[l] += ck * v
    return B[::-1]


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

CONG_THUC = {
    1: ["Gauss I : P = y_0 + t Dy_0 + t(t-1)/2! D2y_-1 + (t+1)t(t-1)/3! D3y_-1 + (t+1)t(t-1)(t-2)/4! D4y_-2 + ...",
        "          c_k = D^k y_(-floor(k/2)) / k!,  pi_k = pi_(k-1) (t - z_(k-1)),  z = 0, 1, -1, 2, -2, ..."],
    2: ["Gauss II: P = y_0 + t Dy_-1 + (t+1)t/2! D2y_-1 + (t+1)t(t-1)/3! D3y_-2 + (t+2)(t+1)t(t-1)/4! D4y_-2 + ...",
        "          c_k = D^k y_(-ceil(k/2)) / k!,  pi_k = pi_(k-1) (t - z_(k-1)),  z = 0, -1, 1, -2, 2, ..."],
    3: ["Stirling: P = y_0 + t (Dy_-1 + Dy_0)/2 + t^2/2! D2y_-1 + t(t^2-1)/3! (D3y_-2 + D3y_-1)/2"
        " + t^2(t^2-1)/4! D4y_-2 + ...",
        "          c_(2j-1) = (D^(2j-1)y_(-j) + D^(2j-1)y_(-j+1)) / (2 (2j-1)!),  c_(2j) = D^(2j)y_(-j) / (2j)!",
        "          pi_1 = t,  pi_(2j+1) = pi_(2j-1) (t^2 - j^2),  pi_(2j) = t pi_(2j-1)"],
    4: ["Bessel  : P = (y_0 + y_1)/2 + (t - 1/2) Dy_0 + t(t-1)/2! (D2y_-1 + D2y_0)/2 + (t - 1/2)t(t-1)/3! D3y_-1 + ...",
        "          c_(2j) = (D^(2j)y_(-j) + D^(2j)y_(-j+1)) / (2 (2j)!),  c_(2j+1) = D^(2j+1)y_(-j) / (2j+1)!",
        "          pi_(2j) = pi_(2j-2) (t + j - 1)(t - j),  pi_(2j+1) = (t - 1/2) pi_(2j)"],
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
    print(f"  x = {vec(xs)}")
    print(f"  y = {vec(ys)}")

    print("\nCONG THUC:")
    if trich:
        print("  Trich xuat: j_1 = argmin |xbar - x_i|;  ket nap dan x_(L-1) neu xbar - x_(L-1) <= x_(R+1) - xbar,"
              " nguoc lai x_(R+1)")
    print("  t = (x - x_0)/h;  sai phan: D^0 y_i = y_i,  D^k y_i = D^(k-1) y_(i+1) - D^(k-1) y_i   (D = Delta)")
    for dong in CONG_THUC[ct]:
        print("  " + dong)
    print("  P(t) = sum_k c_k pi_k(t)  (bang tich: Horner nhan);  f^(j)(xbar) ~ P^(j)(t)/h^j = j! r_j / h^j")
    print("  Sai so: |f(xbar) - P(xbar)| <= M_(n+1) h^(n+1)/(n+1)! * |prod_i (t - i)|")

    print("\nTINH TOAN:")
    if trich:
        print(f"Trich xuat (muc 1): thu tu ket nap moc gan xbar = {xbar:.10g} nhat:")
        in_bang(["lan", "chi so goc", "x_j", "|xbar - x_j|", "y_j"],
                [[str(s), str(j), f"{x[j]:.10g}", f"{abs(xbar - x[j]):.10g}", f"{y[j]:.10g}"]
                 for s, j in enumerate(thu_tu, 1)])
        print(f"  => bo moc con x_{L}..x_{R} = [{xs[0]:.10g}, {xs[-1]:.10g}]")
    print(f"Moc trung tam x_0 = {x0:.10g} (vi tri {q + 1}/{m}), chi so tuong doi i = {p}..{p + n}")
    print(f"  t = (xbar - x_0)/h = ({xbar:.10g} - {x0:.10g}) / {h:.10g} = {tb:.10g}")

    D = bang_sai_phan(ys)                                               # Muc 2, Buoc 3-4
    c, chon = he_so(D, p, ct)                                           # Muc 3, Buoc 1
    duoc_chon = {o for ds in chon for o in ds}
    print(f"\nBang sai phan (hang i: y_i, D y_i, D^2 y_i, ...; o [ ] duoc chon cho {TEN[ct]}):")
    hang = []
    for s in range(n + 1):
        i = p + s
        o = []
        for kk in range(n + 1 - s):
            v = o_bang(D[s][kk], d)
            o.append(f"[{v}]" if (i, kk) in duoc_chon else v)
        hang.append([str(i), f"{xs[s]:.10g}"] + o + [None] * s)
    in_bang(["i", "x_i", "y_i"] + [f"D{kk}" for kk in range(1, n + 1)], hang)

    print("\nHe so c_k:")
    hang = []
    for kk in range(n + 1):
        ten_o = " + ".join(f"D{kk}y_{i}" if kk else f"y_{i}" for i, _ in chon[kk])
        if len(chon[kk]) == 2:
            ten_o = f"({ten_o}) / 2"
        hang.append([str(kk), ten_o + (f" / {kk}!" if kk > 1 else ""), c[kk]])
    in_bang(["k", "c_k =", "c_k"], hang)

    pi, nhan = bang_tich(n, ct)                                         # Muc 3, Buoc 2
    b = to_hop(c, pi)                                                   # Muc 3, Buoc 3
    print(f"\nBang tich (hang k: he so pi_k(t) bac cao -> thap); P(t) = sum c_k * hang k:")
    in_bang(["k", "pi_k =", "c_k"] + cot_mu(n, "t"),
            [[str(kk), nhan[kk], c[kk]] + [None] * (n - kk) + pk for kk, pk in enumerate(pi)]
            + [None] + [["P(t)", "", ""] + b])

    a, bang_db = doi_bien(b, x0, h)                                     # P theo x (muc 5, newton.md)
    print(f"\nDoi bien t = ({nhan_tu('x', x0)}) / {h:.10g} -> x (hang j: vector a sau khi cong b_j):")
    in_bang(["j", "b_j"] + cot_mu(n),
            [[str(n), b[0]] + [None] * n + [b[0]]] +
            [[str(n - j), b[j]] + [None] * (n - j) + aa for j, aa in enumerate(bang_db, 1)])

    r, dd, v, hang_h = tai_xbar(b, tb, h, k)                            # Muc 4
    print(f"\nHorner chia lap tai t = {tb:.10g} (hang j: he so sau lan chia thu j+1, o cuoi r_j):")
    in_bang([""] + cot_mu(n, "t"), [["P(t)"] + b] + [[f"j = {j}"] + hh for j, hh in enumerate(hang_h)])
    for j in range(len(r)):
        dong = f"  P^({j})(t) = {j}! * {so_ngoac(r[j])} = {fmt(dd[j], '.10g')}"
        if j:
            dong += f"  ->  f^({j})(xbar) ~ {so_ngoac(dd[j])} / {h:.10g}^{j} = {fmt(v[j], '.10g')}"
        print(dong)
    lE = log_E(p, n, tb, h)
    E = math.exp(lE) if lE < 709 else math.inf

    print("\nKET QUA (vector he so bac cao -> thap):")
    print(f"  {TEN[ct]}, x_0 = {x0:.10g}, h = {h:.10g}, t = ({nhan_tu('x', x0)}) / {h:.10g}:")
    print(f"    P_{n}(t) = b = (b_{n}, ..., b_0) = {vec(b)}")
    print(f"    P_{n}(t) = {da_thuc_str(b, 't')}")
    print(f"    P_{n}(x) = a = (a_{n}, ..., a_0) = {vec(a)}")
    print(f"    P_{n}(x) = {da_thuc_str(a)}")
    ten = "(f(xbar))" if k == 0 else f"(f(xbar), ..., f^({k})(xbar))"
    print(f"  xbar = {xbar:.10g} (t = {tb:.10g}): v = {ten} ~ {vec(v)}")
    print(f"    f({xbar:.10g}) ~ {fmt(v[0], '.10g')}" + (f",  f'({xbar:.10g}) ~ {fmt(v[1], '.10g')}" if k else ""))
    print(f"    sai so: |f(xbar) - P_{n}(xbar)| <= M_{n + 1} * {h:.10g}^{n + 1} / {n + 1}! * |prod (t - i)|"
          f" = M_{n + 1} * {E:.6e}")

    print("\nKIEM TRA:")
    ti = np.arange(p, p + n + 1, dtype=float)
    kiem("max |P(t_i) - y_i|, t_i = i", np.max(np.abs(np.polyval(b, ti) - ys)))
    b_np = np.linalg.solve(np.vander(ti, n + 1), ys) if n else np.array(ys)
    kiem("he so P(t) vs numpy.linalg.solve(vander(t_i)), tuong doi",
         np.max(np.abs(np.array(b) - b_np)) / max(1.0, np.max(np.abs(b_np))))
    kiem("f(xbar) vs cong thuc Lagrange truc tiep", abs(lagrange_tai(xs, ys, xbar) - v[0]))
    kiem(f"f^(j)(xbar) vs numpy.polyder, j = 0..{min(k, n)}",
         max(abs(np.polyval(np.polyder(b_np, j) if j else b_np, tb) / h ** j - v[j]) for j in range(min(k, n) + 1)))
    kiem("P(x) (doi bien) tai x_i vs y_i", np.max(np.abs(np.polyval(a, xs) - ys)))
    return dict(b=b, a=a, c=c, v=v, t=tb, x0=x0, xs=xs, ys=ys, p=p, D=D, chon=chon, pi=pi, E=E)


# ===== CHUONG TRINH CHINH =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")   # in du lieu goc co ky tu la khong bi crash
    tra_loi, bang = None, None
    if len(sys.argv) > 1:
        p = sys.argv[1]
        try:
            if p.lower().endswith((".csv", ".xlsx", ".xls")):
                bang = doc_bang_file(p)
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

        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "1.4 1.5 1.6 1.7 1.8 1.9 2 2.1 2.2")
            goc["y"] = nhap("Cac gia tri y_i",
                            "2.4347052 2.5473627 2.6495552 2.741261 2.8225627 2.8936474 2.9548 3.0064203 3.0489801")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            ox, oy, vi_tri = bang
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao)
        if len(x) < 2:
            raise ValueError("can it nhat 2 moc.")
        h = cach_deu(x)
        if h is None:
            raise ValueError("moc khong cach deu -> khong dung duoc noi suy trung tam (dung newton.py, moc bat ky).")

        vd = "1.63" if bang is None else f"{(x[0] + x[-1]) / 2:.10g}"
        goc["xbar"] = nhap("Cac diem xbar", vd)
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
        print(f"    x = {ngan(vec(x))}")
        print(f"    y = {ngan(vec(y))}")
        print(f"    xbar = {vec(xbars)},  k = {k},  m = {m}")

    for ct, xb, mc in viec:
        giai(x, y, ct, xb, k, mc, h)


if __name__ == "__main__":
    main()
