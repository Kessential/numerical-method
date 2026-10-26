"""
DA THUC NOI SUY NEWTON TIEN / LUI (MOC BAT KY / MOC CACH DEU)
Thuat toan: docs/thuat_toan/newton.md

Bo diem (x_i, y_i), i = 0..n;  P_n(x) = a_n*x^n + ... + a_1*x + a_0  (a_i la he so cua x^i)
Vector he so in tu BAC CAO xuong BAC THAP: a = (a_n, ..., a_0).
Muc dich -> bien the duoc chon (loai moc tu kiem tra o Buoc 0):
  1. Da thuc Newton tien         -> moc bat ky: ty sai phan (muc 3, TH1); cach deu: sai phan, bien t (muc 3, TH2)
  2. Da thuc Newton lui          -> nhu tren (muc 4); bang (ty) sai phan lap 1 lan dung chung cho tien va lui
  3. f(xbar), f^(j)(xbar), j<=k  -> Horner chia lap tren da thuc da chon o 1/2 (muc 6);
                                    khong chon hoac chon ca 1, 2: tien neu xbar gan x_0, lui neu gan x_n
  4. Bang dai: trich xuat m moc   -> ket nap dan moc gan xbar nhat (muc 7), roi lam 1/2/3 tren bo moc con
     gan xbar nhat                   (moi xbar 1 bo moc rieng)

Cach chay:
  python interpolation/newton.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/newton.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi:
                                                    muc dich / x / y / xbar / k / m (m chi khi chon muc 4;
                                                    dong x, y duoc co nhan 'x', 'y')
  python interpolation/newton.py data/<file>.csv -> file chi chua bang: 2 hang hoac 2 cot x, y (lay 2 cot dau,
                                                    .xlsx: sheet dau, can pandas + openpyxl); cau con lai nhap tu ban phim
  VD cau 11: python interpolation/newton.py "slide_example/data Câu 11.xlsx"  roi nhap: 1 3 4 / 3.52 / 1 / 9
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


def log_E(x, xbar):
    """log(|w_(n+1)(xbar)| / (n+1)!) tinh qua log de khong tran so; -inf neu xbar trung moc."""
    if any(xbar == xi for xi in x):
        return -math.inf
    return sum(math.log(abs(xbar - xi)) for xi in x) - math.lgamma(len(x) + 1)


# ===== THUAT TOAN =====
# Vector trong code luu tu bac cao -> thap (giong luc in); dao nguoc thanh A voi A[i] = a_i
# (he so cua x^i) de viet dung chi so nhu trong .md.

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


def to_hop_newton(c, z):
    """Muc 2: sum c_k (u - z_0)...(u - z_(k-1)). Tra ve (b bac cao -> thap, bang tich omega_0..omega_n)."""
    n = len(c) - 1
    omega = [1.0]                                  # Buoc 1 - Khoi tao: omega_0 = 1, b_0 = c_0
    B = [0.0] * (n + 1)                            # B[l] = b_l
    B[0] = c[0]
    bang = [omega]
    for k in range(1, n + 1):                      # Buoc 2
        omega = horner_nhan(omega, z[k - 1])       # Buoc 2.1 - Bang tich (muc 3, horner.md)
        W = omega[::-1]                            # W[l] = he so cua u^l trong omega_k
        for l in range(k + 1):                     # Buoc 2.2 - Cong don
            B[l] += c[k] * W[l]
        bang.append(omega)
    return B[::-1], bang                           # Buoc 3 - Ket thuc


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


def newton(x, T, chieu, h=None):
    """Muc 3 (chieu = 'tien') / muc 4 ('lui'). Tra ve dict: c, z, b, bang_tich, a, bang_doi_bien, s."""
    n = len(x) - 1
    # Buoc 1 - Bang: T lap 1 lan (muc 1), dung chung cho tien va lui
    c = [T[k][k] if chieu == "tien" else T[n][k] for k in range(n + 1)]   # Buoc 2 - He so
    if h is not None:                              # TH2: c_k = T / k!, chia dan de khong tran so
        for k in range(2, n + 1):
            for m in range(2, k + 1):
                c[k] /= m
    if h is None:                                  # Buoc 3 - Nut tich
        z = [x[i] if chieu == "tien" else x[n - i] for i in range(n)]
    else:
        z = [float(i if chieu == "tien" else -i) for i in range(n)]
    b, bang_tich = to_hop_newton(c, z)             # Buoc 4 - Da thuc theo u (TH1 u = x, TH2 u = t)
    kq = dict(c=c, z=z, b=b, bang_tich=bang_tich, a=b, bang_doi_bien=None, s=None)
    if h is not None:                              # Buoc 5 - Doi bien t -> x (muc 5)
        kq["s"] = x[0] if chieu == "tien" else x[n]
        kq["a"], kq["bang_doi_bien"] = doi_bien(b, kq["s"], h)
    return kq                                      # Buoc 6 - Ket thuc


def tai_xbar(kq, xbar, k, h=None):
    """Muc 6, Buoc 1-3: v_j ~ f^(j)(xbar). Tra ve (u, r, d, v, hang Horner); d_j = P^(j)(u)."""
    if h is None:                                  # Buoc 1 - Bien
        u, g = xbar, 1.0
    else:
        u, g = (xbar - kq["s"]) / h, h
    r, d, hang = horner_dao_ham(kq["b"], u, k)     # Buoc 2 - Horner chia lap (muc 2, horner.md)
    v, gj = [], 1.0
    for dj in d:                                   # Buoc 3 - v_j = d_j / g^j
        v.append(dj / gj)
        gj *= g
    return u, r, d, v, hang                        # Buoc 4 - sai so: log_E(); Buoc 5 - Ket thuc


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


# ===== GIAI =====

TEN = {"tien": "Newton tien", "lui": "Newton lui"}


def newton_long_nhau(c, z, u):
    """Kiem tra: P(u) = c_0 + (u - z_0)(c_1 + (u - z_1)(... + (u - z_(n-1)) c_n)), khong qua he so chinh tac."""
    p = c[-1]
    for kk in range(len(c) - 2, -1, -1):
        p = c[kk] + (u - z[kk]) * p
    return p


def giai(x, y, muc, xbars, k, trich=None):
    """trich = (x_goc, y_goc, m, L, R, thu_tu): x, y la bo moc con trich xuat (muc 7) quanh xbars[0]."""
    n = len(x) - 1
    h = cach_deu(x)                                # Buoc 0 - kiem tra cach deu -> TH1 / TH2
    u = "x" if h is None else "t"
    if trich:
        xg, yg, m, L, R, thu_tu = trich
        print(f"\nTrich xuat m = {m} moc gan xbar = {xbars[0]:.10g} nhat tu bang {len(xg)} moc"
              f" [{xg[0]:.10g}, {xg[-1]:.10g}]")
    print(f"\nNoi suy Newton: n = {n} ({n + 1} moc), " + ("moc bat ky" if h is None else f"moc cach deu, h = {h:.10g}"))
    print(f"  x = {vec(x)}")
    print(f"  y = {vec(y)}")

    chon = [c for c, m in (("tien", 1), ("lui", 2)) if m in muc]
    chieu_x = {}                                   # xbar -> da thuc dung de tinh
    for xb in xbars:
        gan = "tien" if abs(xb - x[0]) <= abs(xb - x[-1]) else "lui"
        chieu_x[xb] = chon[0] if len(chon) == 1 else gan
    can = [c for c in ("tien", "lui") if c in chon or c in chieu_x.values()]

    print("\nCONG THUC:")
    if trich:
        print("  Trich xuat : j_1 = argmin |xbar - x_i|;  ket nap dan x_(L-1) neu xbar - x_(L-1) <= x_(R+1) - xbar,"
              " nguoc lai x_(R+1)")
    if h is None:
        print("  Ty sai phan: T_(i,0) = y_i,  T_(i,k) = (T_(i,k-1) - T_(i-1,k-1)) / (x_i - x_(i-k)) = f[x_(i-k), ..., x_i]")
        if "tien" in can:
            print("  Newton tien: P_n(x) = sum_(k=0..n) c_k w_k(x),  c_k = T_(k,k) = f[x_0, ..., x_k],"
                  "  w_k(x) = (x - x_0)...(x - x_(k-1))")
        if "lui" in can:
            print("  Newton lui : P_n(x) = sum_(k=0..n) c_k w_k(x),  c_k = T_(n,k) = f[x_(n-k), ..., x_n],"
                  "  w_k(x) = (x - x_n)...(x - x_(n-k+1))")
    else:
        print("  Sai phan   : T_(i,0) = y_i,  T_(i,k) = T_(i,k-1) - T_(i-1,k-1) = Delta^k y_(i-k) = Nabla^k y_i")
        if "tien" in can:
            print("  Newton tien: t = (x - x_0)/h,  P_n = sum_(k=0..n) c_k w_k(t),  c_k = Delta^k y_0 / k!,"
                  "  w_k(t) = t(t-1)...(t-k+1)")
        if "lui" in can:
            print("  Newton lui : t = (x - x_n)/h,  P_n = sum_(k=0..n) c_k w_k(t),  c_k = Nabla^k y_n / k!,"
                  "  w_k(t) = t(t+1)...(t+k-1)")
    print(f"  Bang tich  : w_0 = 1,  w_k({u}) = w_(k-1)({u}) * ({u} - z_(k-1))  (Horner nhan)")
    if h is not None:
        print("  Doi bien   : a = (b_n);  voi j = n-1..0: a = a * (x - s) / h,  a_0 = a_0 + b_j"
              "  (s = x_0 tien, s = x_n lui)")
    if xbars:
        if h is None:
            print("  Tai xbar   : f^(j)(xbar) ~ P^(j)(xbar) = j! * r_j,  r_j = du lan chia thu j+1 cho (x - xbar)")
        else:
            print("  Tai xbar   : t = (xbar - s)/h,  f^(j)(xbar) ~ P^(j)(t) / h^j = j! * r_j / h^j,"
                  "  r_j = du lan chia thu j+1 cho (t - t_xbar)")
        print("  Sai so     : |f(xbar) - P_n(xbar)| <= M_(n+1) / (n+1)! * |w_(n+1)(xbar)|,"
              "  w_(n+1)(x) = (x - x_0)...(x - x_n)")

    print("\nTINH TOAN:")
    if trich:
        print(f"Trich xuat (muc 7): thu tu ket nap moc gan xbar = {xbars[0]:.10g} nhat:")
        in_bang(["lan", "chi so goc", "x_j", "|xbar - x_j|", "y_j"],
                [[str(s), str(j), xg[j], abs(xbars[0] - xg[j]), yg[j]] for s, j in enumerate(thu_tu, 1)])
        print(f"  => L = {L}, R = {R}: bo moc con x_{L}..x_{R} = [{xg[L]:.10g}, {xg[R]:.10g}],"
              f" danh lai chi so 0..{n}\n")
    T = bang_sai_phan(x, y, h)                     # Muc 1 - lap 1 lan
    ten_cot = "TSP" if h is None else "SP"
    if h is None:
        print("Bang ty sai phan (hang i, cot TSPk: T_(i,k) = f[x_(i-k), ..., x_i]; duong cheo -> tien, hang cuoi -> lui):")
    else:
        print("Bang sai phan (hang i, cot SPk: T_(i,k) = Delta^k y_(i-k) = Nabla^k y_i; duong cheo -> tien, hang cuoi -> lui):")
    in_bang(["i", "x_i", "y_i"] + [f"{ten_cot}{j}" for j in range(1, n + 1)],
            [[str(i), x[i]] + T[i][:i + 1] + [None] * (n - i) for i in range(n + 1)])

    kq = {}
    for chieu in can:
        kq[chieu] = R = newton(x, T, chieu, h)
        cheo = "T_(k,k)" if chieu == "tien" else "T_(n,k)"
        print(f"\n{TEN[chieu]}: c = (c_0, ..., c_{n}) = {vec(R['c'])}   (c_k = {cheo}" + (")" if h is None else " / k!)"))
        print(f"Bang tich {TEN[chieu][7:]} (hang k: he so w_k({u}) bac cao -> thap); P = sum c_k * hang k:")
        in_bang(["k", "nhan", "c_k"] + cot_mu(n, u),
                [[str(kk), "-" if kk == 0 else nhan_tu(u, R["z"][kk - 1]), R["c"][kk]] + [None] * (n - kk) + w
                 for kk, w in enumerate(R["bang_tich"])] + [None] + [[f"P({u})", "", ""] + R["b"]])
        if h is not None:
            print(f"\nDoi bien t = ({nhan_tu('x', R['s'])}) / {h:.10g} -> x (hang j: vector a sau khi cong b_j):")
            in_bang(["j", "b_j"] + cot_mu(n),
                    [[str(n), R["b"][0]] + [None] * n + [R["b"][0]]] +
                    [[str(n - j), R["b"][j]] + [None] * (n - j) + a for j, a in enumerate(R["bang_doi_bien"], 1)])

    tinh = {}
    for xb in xbars:
        R = kq[chieu_x[xb]]
        ly_do = "" if len(chon) == 1 else ("  (xbar gan x_0)" if chieu_x[xb] == "tien" else "  (xbar gan x_n)")
        print(f"\nxbar = {xb:.10g} -> {TEN[chieu_x[xb]]}{ly_do}:")
        ub, r, d, v, hang = tai_xbar(R, xb, k, h)
        if h is not None:
            print(f"  t = ({nhan_tu('xbar', R['s'])}) / {h:.10g} = {ub:.10g}")
        print(f"  Horner chia lap tai c = {ub:.10g} (hang j: (b_n, ..., b_j) sau lan chia thu j+1, o cuoi r_j):")
        in_bang([""] + cot_mu(n, u), [[f"P({u})"] + R["b"]] + [[f"j = {j}"] + hh for j, hh in enumerate(hang)])
        for j in range(len(r)):
            dong = f"  P^({j})({'xbar' if h is None else 't'}) = {j}! * {so_ngoac(r[j])} = {fmt(d[j], '.10g')}"
            if h is not None and j:
                dong += f"  ->  f^({j})(xbar) ~ {so_ngoac(d[j])} / {h:.10g}^{j} = {fmt(v[j], '.10g')}"
            print(dong)
        tinh[xb] = v

    print("\nKET QUA (vector he so bac cao -> thap):")
    for chieu in [c for c in can if c in chon]:
        R = kq[chieu]
        print(f"  {TEN[chieu]}:")
        if h is not None:
            print(f"    P_{n}(t) = b = (b_{n}, ..., b_0) = {vec(R['b'])},  t = ({nhan_tu('x', R['s'])}) / {h:.10g}")
            print(f"    P_{n}(t) = {da_thuc_str(R['b'], 't')}")
        print(f"    P_{n}(x) = a = (a_{n}, ..., a_0) = {vec(R['a'])}" if n else f"    P_0(x) = a = (a_0) = {vec(R['a'])}")
        print(f"    P_{n}(x) = {da_thuc_str(R['a'])}")
    for xb, v in tinh.items():
        ten = "(f(xbar))" if k == 0 else f"(f(xbar), ..., f^({k})(xbar))"
        print(f"  xbar = {xb:.10g} ({TEN[chieu_x[xb]]}): v = {ten} ~ {vec(v)}")
        print(f"    f({xb:.10g}) ~ {fmt(v[0], '.10g')}" + (f",  f^({k})({xb:.10g}) ~ {fmt(v[k], '.10g')}" if k else ""))
        lE = log_E(x, xb)
        E = math.exp(lE) if lE < 709 else math.inf
        print(f"    sai so: |f({xb:.10g}) - P_{n}({xb:.10g})| <= M_{n + 1} / {n + 1}! * |w_{n + 1}(xbar)|"
              f" = M_{n + 1} * {E:.6e}")

    print("\nKIEM TRA:")
    if trich:
        def log_w(lo):                             # log|w_m(xbar)| cua cua so x_lo..x_(lo+m-1)
            return sum(math.log(max(abs(xbars[0] - xg[i]), 1e-300)) for i in range(lo, lo + m))
        ke = [lo for lo in (L - 1, L + 1) if 0 <= lo <= len(xg) - m]
        if ke:
            print(f"  trich xuat: |w_m(xbar)| = {math.exp(log_w(L)):.6e} <= cua so lien ke "
                  + ", ".join(f"x_{lo}..x_{lo + m - 1}: {math.exp(log_w(lo)):.6e}" for lo in ke)
                  + ("  -> dung" if all(log_w(L) <= log_w(lo) + 1e-12 for lo in ke) else "  -> SAI"))
    a_np = np.linalg.solve(np.vander(x, n + 1), y) if n else np.array(y)
    tl = max(1.0, np.max(np.abs(a_np)))
    for chieu in can:
        R = kq[chieu]
        kiem(f"{TEN[chieu]}: max |P(x_i) - y_i|", np.max(np.abs(np.polyval(R["a"], x) - y)))
        if h is not None:
            t_i = (np.array(x) - R["s"]) / h
            kiem(f"{TEN[chieu]}: max |P(t_i) - y_i|, t_i = (x_i - s)/h", np.max(np.abs(np.polyval(R["b"], t_i) - y)))
        kiem(f"{TEN[chieu]}: he so vs numpy.linalg.solve(vander), tuong doi", np.max(np.abs(np.array(R["a"]) - a_np)) / tl)
    if len(can) == 2:
        kiem("Newton tien vs Newton lui: he so, tuong doi", np.max(np.abs(np.array(kq["tien"]["a"]) - kq["lui"]["a"])) / tl)
    for xb, v in tinh.items():
        R = kq[chieu_x[xb]]
        ub = xb if h is None else (xb - R["s"]) / h
        kiem(f"xbar = {xb:.10g}: f(xbar) vs dang Newton long nhau", abs(newton_long_nhau(R["c"], R["z"], ub) - v[0]))
        kiem(f"xbar = {xb:.10g}: f^(j) vs numpy.polyder, j = 0..{min(k, n)}",
             max(abs(np.polyval(np.polyder(a_np, j) if j else a_np, xb) - v[j]) for j in range(min(k, n) + 1)))
    return kq, tinh


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
    try:
        if tra_loi is None:
            print("Muc dich (chon 1 hoac nhieu, cach nhau boi khoang trang):")
            print("  1. Da thuc noi suy Newton tien")
            print("  2. Da thuc noi suy Newton lui")
            print("  3. Gia tri f(xbar) va dao ham f^(j)(xbar), j = 1..k")
            print("  4. Bang dai: trich xuat m moc gan xbar nhat roi lam 1/2/3 tren cac moc do")
        goc["muc dich"] = nhap("Chon muc dich", "1 3")
        so_muc = doc_day_so(goc["muc dich"], "muc dich", bao)
        muc = {int(v) for v in so_muc if v in (1, 2, 3, 4)}
        if len(muc) != len(set(so_muc)):
            bao.append("muc dich: loai cac gia tri ngoai 1..4")
        if not muc - {4}:
            raise ValueError("Khong co muc dich hop le (1..3).")
        if 4 in muc and 3 not in muc:
            muc.add(3)
            bao.append("muc dich 4 can xbar -> them muc dich 3")

        if bang is None:
            goc["x"] = nhap("Cac moc x_i", "1.2 1.5 1.7 1.9 2.1 2.4")
            goc["y"] = nhap("Cac gia tri y_i", "0.7247 0.1415 -0.2577 -0.6466 -1.0097 -1.4748")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            ox, oy, vi_tri = bang
            goc["x (file)"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao)

        xbars, k = [], 0
        if 3 in muc:
            vd = "1.8" if bang is None else f"{(x[0] + x[-1]) / 2:.10g}"   # bang tu file: trung diem
            goc["xbar"] = nhap("Cac diem xbar", vd)
            xbars = doc_day_so(goc["xbar"], "xbar", bao)
            if not xbars:
                raise ValueError("Khong co diem xbar hop le.")
            for xb in xbars:
                if not x[0] <= xb <= x[-1]:
                    bao.append(f"xbar = {xb:.10g} ngoai [x_0, x_n] = [{x[0]:.10g}, {x[-1]:.10g}]"
                               " -> ngoai suy, sai so co the lon")
            goc["k"] = nhap("Cap dao ham k", "3")
            ks = doc_day_so(goc["k"], "k", bao)
            if len(ks) != 1 or ks[0] < 0 or ks[0] != int(ks[0]):
                raise ValueError("k phai la 1 so nguyen >= 0.")
            k = int(ks[0])
        m = None
        if 4 in muc:
            goc["m"] = nhap("So moc trich xuat m", "9" if len(x) >= 9 else str(len(x)))
            ms = doc_day_so(goc["m"], "m", bao)
            if len(ms) != 1 or ms[0] < 1 or ms[0] != int(ms[0]):
                raise ValueError("m phai la 1 so nguyen >= 1.")
            m = int(ms[0])
            if m > len(x):
                bao.append(f"m = {m} > so moc {len(x)} -> dung ca {len(x)} moc")
                m = len(x)
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
        print(f"    x = {ngan(vec(x))}")
        print(f"    y = {ngan(vec(y))}")
        if xbars:
            print(f"    xbar = {vec(xbars)},  k = {k}" + (f",  m = {m}" if m else ""))

    if m is None:
        giai(x, y, muc, xbars, k)
        return
    for xb in xbars:                               # muc 4: moi xbar 1 bo moc con
        L, R, thu_tu = trich_xuat(x, xb, m)
        giai(x[L:R + 1], y[L:R + 1], muc - {4}, [xb], k, (x, y, m, L, R, thu_tu))


if __name__ == "__main__":
    main()
