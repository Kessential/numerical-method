"""
SO DO HORNER (BIEN THE CHIA VA BIEN THE NHAN)
Thuat toan: docs/thuat_toan/horner.md

P(x) = a_n*x^n + ... + a_1*x + a_0   (a_i la he so cua x^i)
Vector he so nhap / in tu BAC CAO xuong BAC THAP: a = (a_n, ..., a_0), vd 3x^3 - 2x - 1 -> 3 0 -2 -1
Muc dich -> bien the duoc chon:
  1. Gia tri P(c)                   -> Horner chia (chi giu r)
  2. Chia P(x) cho (x - c)          -> Horner chia
  3. Dao ham cap 0..k tai c         -> Horner chia lap (lan chia 1 cho luon muc 1, 2)
  4. Nhan P(x) voi (x - c)          -> Horner nhan
  5. w(x) = (x - x_0)...(x - x_m-1) -> Horner nhan lap
  6. Da thuc dao ham P^(k)(x)       -> dao ham lap tren vector he so

Cach chay:
  python interpolation/horner.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/horner.py data/<file>.txt -> moi dong la 1 cau tra loi, theo dung thu tu cau hoi
Phan tach bang khoang trang hoac ';'. Dau ',' giua hai chu so = dau thap phan.
"""

import math
import re
import sys

import numpy as np

W = 14  # do rong cot bang

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


def doc_day_so(text, ten):
    """Buoc 0: tach chuoi thanh day so; tra ve (day so, danh sach canh bao)."""
    canh_bao = []
    s0 = re.sub("[−–—]", "-", text)   # dau tru Unicode (copy tu PDF) -> '-'
    if s0 != text:
        canh_bao.append(f"{ten}: doi dau tru Unicode thanh '-'")
    text = s0
    s = re.sub(r"(?<=\d),(?=\d)", ".", text)          # ',' thap phan -> '.'
    if s != text:
        canh_bao.append(f"{ten}: doi dau ',' thap phan thanh '.'")
    s = s.replace(",", " ")                            # ',' con lai: phan tach
    so = []
    for tok in re.split(r"[\s;]+", s.strip()):
        if tok == "":
            continue
        try:
            v = float(tok)
        except ValueError:
            canh_bao.append(f"{ten}: loai token khong phai so '{tok}'")
            continue
        if not math.isfinite(v):
            raise ValueError(f"{ten}: co NaN hoac vo cung ('{tok}').")
        so.append(v)
    return so, canh_bao


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


def in_hang(nhan, gia_tri, so_cot_trong=0):
    print(f"{nhan:>{W}}" + " " * (W * so_cot_trong) + "".join(f"{fmt(v):>{W}}" for v in gia_tri))


def in_bang_chia(a, c, b, r):
    """Bang Horner chia: (a_n..a_0) | (c*b_(n-1)..c*b_0) | (b_(n-1)..b_0, r)."""
    in_hang("", a)
    in_hang(f"c = {fmt(c, '.6g')}", [c * v for v in b], 1)
    print("-" * (W * (len(a) + 1)))
    in_hang("", list(b) + [r])


def in_bang_nhan(a, c, d):
    """Bang Horner nhan: (a_n..a_0, 0) | (-c*a_n..-c*a_0) | (d_(n+1)..d_0)."""
    in_hang("", list(a) + [0.0])
    in_hang(f"-c = {fmt(-c, '.6g')}", [-c * v for v in a], 1)
    print("-" * (W * (len(d) + 1)))
    in_hang("", d)


def in_bang(cot, hang, le="  "):
    """In bang; o la so / chuoi / None (trong). Do rong tung cot tu dong."""
    S = [["" if v is None else v if isinstance(v, str) else fmt(v) for v in h] for h in hang]
    so_cot = max([len(cot)] + [len(h) for h in S])
    rong = [len(cot[j]) if j < len(cot) else 0 for j in range(so_cot)]
    for h in S:
        for j, o in enumerate(h):
            rong[j] = max(rong[j], len(o))
    rong = [r + 2 for r in rong]
    print(le + "".join(f"{c:>{r}}" for c, r in zip(cot, rong)))
    print(le + "-" * sum(rong))
    for h in S:
        print(le + "".join(f"{o:>{r}}" for o, r in zip(list(h) + [""] * (so_cot - len(h)), rong)))


def cot_mu(bac):
    """Ten cot bac cao -> thap: x^bac, ..., x, 1."""
    return [f"x^{e}" if e > 1 else ("x" if e == 1 else "1") for e in range(bac, -1, -1)]


def ten_dh(j):
    """Ten dao ham cap j: P, P', P'' (toi da 3 dau phay), roi P^(4), P^(5), ..."""
    return "P" + "'" * j if j <= 3 else f"P^({j})"


# ===== THUAT TOAN =====

def chuan_hoa_he_so(a):
    """Buoc 0 (he so): bo cac he so 0 o dau; moi he so bang 0 -> P = 0, tra ve (0). Tra ve (he so, canh bao)."""
    if not a:
        raise ValueError("Khong co he so nao hop le.")
    if all(v == 0 for v in a):
        return [0.0], ["he so: moi he so bang 0 -> P(x) = 0, moi ket qua bang 0"]
    k = 0
    while k < len(a) - 1 and a[k] == 0:
        k += 1
    return a[k:], ([f"he so: bo {k} so 0 o dau (bac cao) de a_n != 0"] if k else [])


# Vector trong code luu tu bac cao -> thap (giong luc nhap/in);
# dao nguoc thanh A voi A[i] = a_i (he so cua x^i) de viet dung chi so nhu trong .md.

def horner_chia(a, c):
    """Muc 1: b_(n-1) = a_n, b_(i-1) = a_i + c*b_i, r = a_0 + c*b_0. Tra ve (b, r), b bac cao -> thap."""
    n = len(a) - 1
    A = a[::-1]
    if n == 0:                                     # Buoc 1 - bac 0: Q = 0, r = a_0
        return [], A[0]
    B = [0.0] * n                                  # B[i] = b_i
    B[n - 1] = A[n]                                # Buoc 2 - Khoi tao: b_(n-1) = a_n
    for i in range(n - 1, 0, -1):                  # Buoc 3
        B[i - 1] = A[i] + c * B[i]
    r = A[0] + c * B[0]                            # Buoc 4
    return B[::-1], r                              # Buoc 5 - Ket thuc


def horner_dao_ham(a, c, k, verbose=True):
    """Muc 2: Horner lap tren 1 vector b; r_j = b_j, P^(j)(c) = j! * r_j. Tra ve (r, v), v_j = P^(j)(c).
    verbose: 1 bang chung (hang He so; moi lan chia j: hang c*b_(i+1) va hang j, o cuoi [r_j])."""
    n = len(a) - 1
    K = min(k, n)                                  # Buoc 1 - xu ly k
    b = a[::-1]                                    # Buoc 2 - Khoi tao: b_i = a_i, i = 0..n
    r, dh = [], []
    hang = [["He so"] + list(a)]
    for j in range(K + 1):                         # Buoc 3
        tich = [None] * (n - j + 1)                # c*b_(i+1) dat duoi cot x^i
        for i in range(n - 1, j - 1, -1):          # Buoc 3.1 - chia cho (x - c)
            tich[n - i] = c * b[i + 1]
            b[i] = b[i] + c * b[i + 1]
        r.append(b[j])                             # Buoc 3.2 - r_j = b_j, v_j = j! * r_j
        dh.append(math.factorial(j) * b[j])
        sau = [b[i] for i in range(n, j - 1, -1)]  # (b_n, ..., b_j) sau khi chia
        hang.append([f"c = {c:.10g}"] + tich)
        hang.append([f"j = {j}"] + sau[:-1] + [f"[{fmt(sau[-1])}]"])
    if verbose:
        in_bang([""] + cot_mu(n), hang)
    dh += [0.0] * (k - K)                          # Buoc 4 - v_j = 0 voi j > n
    return r, dh                                   # Buoc 5 - Ket thuc


def horner_nhan(a, c):
    """Muc 3: d_(n+1) = a_n, d_i = a_(i-1) - c*a_i, d_0 = -c*a_0. Tra ve d bac cao -> thap."""
    n = len(a) - 1
    A = a[::-1]
    D = [0.0] * (n + 2)                            # D[i] = d_i
    D[n + 1] = A[n]                                # Buoc 1 - Khoi tao: d_(n+1) = a_n
    for i in range(n, 0, -1):                      # Buoc 2
        D[i] = A[i - 1] - c * A[i]
    D[0] = -c * A[0]                               # Buoc 3
    return D[::-1]                                 # Buoc 4 - Ket thuc


def tich_moc(xs, verbose=True):
    """Muc 4: nhan lap (x - x_i) tren 1 vector p (p[l] = p_l). Tra ve (p_m, ..., p_0)."""
    m = len(xs)
    p = [0.0] * (m + 1)
    p[0] = 1.0                                     # Buoc 1 - Khoi tao: p_0 = 1 (da thuc hang 1)
    if verbose:
        print(f"{'x_i':>{W}}" + "".join(f"{('x^' + str(e)) if e else '1':>{W}}" for e in range(m, -1, -1)))
        print("-" * (W * (m + 2)))
        in_hang("bat dau", [1.0], m)
    for i, xi in enumerate(xs):                    # Buoc 2
        p[i + 1] = p[i]                            # Buoc 2.1 - p dai them 1 phan tu
        for l in range(i, 0, -1):                  # Buoc 2.2
            p[l] = p[l - 1] - xi * p[l]
        p[0] = -xi * p[0]                          # Buoc 2.3
        if verbose:
            in_hang(fmt(xi, ".6g"), p[i + 1::-1], m - i - 1)
    return p[::-1]                                 # Buoc 3 - Ket thuc


def da_thuc_dao_ham(a, k, verbose=True):
    """Muc 5: dao ham lap tren 1 vector e (e[i] = e_i): e_i = (i+1)*e_(i+1). Tra ve (e_(n-k), ..., e_0)."""
    n = len(a) - 1
    if k > n:                                      # Buoc 1 - xu ly k
        if verbose:
            print(f"  k = {k} > n = {n}  =>  P^({k})(x) = 0")
        return [0.0]
    e = a[::-1]                                    # Buoc 2 - Khoi tao: e_i = a_i
    if verbose:
        print(f"{'':>{W}}" + "".join(f"{('x^' + str(p)) if p else '1':>{W}}" for p in range(n, -1, -1)))
        print("-" * (W * (n + 2)))
        in_hang("P", a)
    for j in range(1, k + 1):                      # Buoc 3
        for i in range(n - j + 1):                 # Buoc 3.1
            e[i] = (i + 1) * e[i + 1]
        e.pop()                                    # Buoc 3.2 - Ha bac: bo e_(n-j+1)
        if verbose:
            in_hang(f"P^({j})", e[::-1], j)
    return e[::-1]                                 # Buoc 4 - Ket thuc


# ===== GIAI THEO MUC DICH (chon bien the toi uu) =====

def giai_tai_c(a, c, muc, k):
    n = len(a) - 1
    print(f"\na = (a_{n}, ..., a_0) = {vec(a)}  (P(x) = {da_thuc_str(a)}),   c = {fmt(c, '.10g')}")

    print("\nTINH TOAN:")
    ket_qua = {}
    if 3 in muc:
        K = min(k, n)
        print(f"Horner chia lap {K + 1} lan (lan chia 1 cho luon P(c) va thuong):")
        print("  b_i = a_i;  voi j = 0..min(k,n): b_i = b_i + c*b_(i+1) (i = n-1..j),  r_j = b_j,  P^(j)(c) = j! * r_j")
        r, dh = horner_dao_ham(a, c, k)
        Q, du = horner_chia(a, c)
        ket_qua.update(r=r, dh=dh)
        print(f"  P({c:.10g}) = r_0 = {fmt(du)}; thuong {da_thuc_str(Q) if n >= 1 else '0'}, du {fmt(du)}")
        print(f"  ({', '.join(ten_dh(j) for j in range(k + 1))})({c:.10g})"
              f" = ({'; '.join(f'{j}! r_{j}' if j <= K else '0' for j in range(k + 1))}) = ({'; '.join(fmt(v) for v in dh)})")
    elif muc & {1, 2}:
        print(f"Horner chia P(x) cho (x - {fmt(c, '.6g')}):")
        print("  b_(n-1) = a_n,  b_(i-1) = a_i + c*b_i (i = n-1..1),  r = P(c) = a_0 + c*b_0")
        print("  P(x) = (x - c)(b_(n-1) x^(n-1) + ... + b_1 x + b_0) + r")
        Q, du = horner_chia(a, c)
        in_bang_chia(a, c, Q, du)
    if 4 in muc:
        print(("\n" if muc & {1, 2, 3} else "") + f"Horner nhan P(x) voi (x - {fmt(c, '.6g')}):")
        print("  d_(n+1) = a_n,  d_i = a_(i-1) - c*a_i (i = n..1),  d_0 = -c*a_0")
        d = horner_nhan(a, c)
        in_bang_nhan(a, c, d)

    print("\nKET QUA (vector he so bac cao -> thap):")
    if 1 in muc:
        print(f"  P({fmt(c, '.10g')}) = {fmt(du)}")
        ket_qua["P(c)"] = du
    if 2 in muc:
        ten_b = f"(b_{n - 1}, ..., b_0) = {vec(Q)}" if n >= 1 else "[] (Q = 0 vi P la hang so)"
        print(f"  Thuong b = {ten_b},   du r = {fmt(du)}")
        ket_qua.update(Q=np.array(Q), du=du)
    if 3 in muc:
        ten_r = "(r_0)" if len(r) == 1 else f"(r_0, ..., r_{len(r) - 1})"
        ten_v = "(v_0) = (P(c))" if k == 0 else f"(v_0, ..., v_{k}) = (P(c), ..., P^({k})(c))"
        print(f"  r = {ten_r} = {vec(r)}   (r_j = P^(j)(c)/j!)")
        print(f"  v = {ten_v} = {vec(dh)}")
        if k <= n:
            print(f"  => P^({k})({fmt(c, '.6g')}) = {k}! * r_{k} = {k}! * ({fmt(r[k])}) = {fmt(dh[k])}")
        else:
            print(f"  => P^({k})({fmt(c, '.6g')}) = 0   (k = {k} > bac n = {n})")
        ket_qua["dh"] = np.array(dh)
    if 4 in muc:
        print(f"  P(x)(x - {fmt(c, '.6g')}): d = (d_{n + 1}, ..., d_0) = {vec(d)}")
        ket_qua["d"] = np.array(d)

    print("\nKIEM TRA (numpy):")
    if muc & {1, 2, 3}:
        q_np, r_np = np.polydiv(a, [1.0, -c])
        sai = abs(np.polyval(a, c) - du)
        if n >= 1:
            sai = max(sai, np.max(np.abs(np.array(Q) - q_np)))
        print(f"  Horner chia: max sai lech voi polyval/polydiv = {sai:.2e}")
    if 3 in muc:
        sai = max(abs(np.polyval(np.polyder(a, j) if j else a, c) - dh[j]) for j in range(len(dh)))
        print(f"  Dao ham    : max sai lech voi polyder       = {sai:.2e}")
    if 4 in muc:
        print(f"  Horner nhan: max sai lech voi polymul       = {np.max(np.abs(np.polymul(a, [1.0, -c]) - d)):.2e}")
    return ket_qua


def giai_tich(xs):
    m = len(xs)
    print(f"\nw_{m}(x) = (x - x_0)(x - x_1)...(x - x_{m - 1})")
    print("\nTINH TOAN (hang x_i la vector he so sau khi nhan them (x - x_i)):")
    print("  p_0 = 1;  voi i = 0..m-1: p_(i+1) = p_i,  p_l = p_(l-1) - x_i*p_l (l = i..1),  p_0 = -x_i*p_0")
    w = tich_moc(xs)
    print("\nKET QUA (vector he so bac cao -> thap):")
    print(f"  p = (1, p_{m - 1}, ..., p_0) = {vec(w)}")
    print("\nKIEM TRA (numpy):")
    print(f"  max sai lech voi numpy.poly = {np.max(np.abs(np.poly(xs) - w)):.2e}")
    return np.array(w)


def giai_da_thuc_dao_ham(a, k):
    n = len(a) - 1
    print(f"\na = (a_{n}, ..., a_0) = {vec(a)}  (P(x) = {da_thuc_str(a)}),   da thuc dao ham cap k = {k}")
    print("\nTINH TOAN (hang P^(j) la vector he so (e_(n-j), ..., e_0) sau lan dao ham thu j):")
    print("  e_i = a_i;  voi j = 1..k: e_i = (i+1)*e_(i+1) (i = 0..n-j), bo e_(n-j+1)   (k > n => P^(k) = 0)")
    D = da_thuc_dao_ham(a, k)
    print("\nKET QUA (vector he so bac cao -> thap):")
    ten_e = "" if k > n else ("(e_0) = " if k == n else f"(e_{n - k}, ..., e_0) = ")
    print(f"  P^({k})(x): e = {ten_e}{vec(D)}")
    print("\nKIEM TRA (numpy):")
    D_np = np.polyder(a, k) if k <= n else np.array([0.0])
    print(f"  max sai lech voi polyder = {np.max(np.abs(np.atleast_1d(D_np) - D)):.2e}")
    return np.array(D)


# ===== CHUONG TRINH CHINH =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")   # in du lieu goc co ky tu la khong bi crash
    tra_loi = None
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                tra_loi = [d for d in f.read().splitlines() if d.strip()]
        except OSError:
            print(f"Loi: khong mo duoc file '{sys.argv[1]}'.")
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

    bao_cao = []      # Buoc 0: chi in khi du lieu ban
    goc = {}
    try:
        if tra_loi is None:
            print("Muc dich (chon 1 hoac nhieu, cach nhau boi khoang trang):")
            print("  1. Gia tri P(c)")
            print("  2. Chia P(x) cho (x - c)")
            print("  3. Dao ham cap 0..k tai c")
            print("  4. Nhan P(x) voi (x - c)")
            print("  5. Tich w(x) = (x - x_0)(x - x_1)...")
            print("  6. Da thuc dao ham P^(k)(x)")
        goc["muc dich"] = nhap("Chon muc dich", "1 2 3")
        so_muc, cb = doc_day_so(goc["muc dich"], "muc dich")
        bao_cao += cb
        muc = {int(v) for v in so_muc if v in (1, 2, 3, 4, 5, 6)}
        if len(muc) != len(set(so_muc)):
            bao_cao.append("muc dich: loai cac gia tri ngoai 1..6")
        if not muc:
            raise ValueError("Khong co muc dich hop le (1..6).")

        if muc & {1, 2, 3, 4, 6}:
            goc["he so"] = nhap("He so P(x) tu bac cao -> thap", "3 0 -2 -1")
            a, cb = doc_day_so(goc["he so"], "he so")
            bao_cao += cb
            a, cb = chuan_hoa_he_so(a)
            bao_cao += cb
            if muc & {1, 2, 3, 4}:
                goc["c"] = nhap("Cac gia tri c", "0; 2.15")
                cs, cb = doc_day_so(goc["c"], "c")
                bao_cao += cb
                if not cs:
                    raise ValueError("Khong co gia tri c hop le.")
            k = len(a) - 1
            if muc & {3, 6}:
                goc["k"] = nhap("Cap dao ham k", str(k))
                ks, cb = doc_day_so(goc["k"], "k")
                bao_cao += cb
                if len(ks) != 1 or ks[0] < 0 or ks[0] != int(ks[0]):
                    raise ValueError("k phai la 1 so nguyen >= 0.")
                k = int(ks[0])
        if 5 in muc:
            goc["moc x_i"] = nhap("Cac moc x_i", "2 2.4 2.7 3 3.1 3.4")
            xs, cb = doc_day_so(goc["moc x_i"], "moc x_i")
            bao_cao += cb
            if not xs:
                raise ValueError("Khong co moc x_i hop le.")
    except ValueError as e:
        bao_cao.append(f"Loi: {e}")
        bao_cao = [None] + bao_cao   # danh dau dung
    bao_cao += thieu

    if bao_cao:
        print("\nXU LY DU LIEU")
        print("-" * 78)
        for ten, s in goc.items():
            print(f"  {ten} (goc): {s!r}")
        for m in bao_cao:
            if m is not None:
                print("  " + m)
        if bao_cao[0] is None:
            return
        print("  Du lieu sach:")
        if muc & {1, 2, 3, 4, 6}:
            print(f"    he so = {vec(a)} (bac {len(a) - 1})" + (f",  c = {vec(cs)}" if muc & {1, 2, 3, 4} else ""))
        if 5 in muc:
            print(f"    x_i = {xs}")

    if muc & {1, 2, 3, 4}:
        for c in cs:
            giai_tai_c(a, c, muc & {1, 2, 3, 4}, k)
    if 6 in muc:
        giai_da_thuc_dao_ham(a, k)
    if 5 in muc:
        giai_tich(xs)


if __name__ == "__main__":
    main()
