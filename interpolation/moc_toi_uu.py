"""
MOC NOI SUY TOI UU (NGHIEM DA THUC CHEBYSHEV)
Thuat toan: docs/thuat_toan/moc_toi_uu.md

Moc luu dang vector x = (x_0, ..., x_(n-1)) xep TANG DAN; w_n(x) = (x - x_0)...(x - x_(n-1)).
Input : moi bo gom so moc n va doan [a, b]
Output: t = (t_0, ..., t_(n-1)) nghiem T_n tren [-1, 1], x = (x_0, ..., x_(n-1)) moc toi uu tren [a, b],
        W = max|w_n(x)| tren [a, b]

Cach chay:
  python interpolation/moc_toi_uu.py                 -> nhap tu ban phim (Enter = mac dinh), nhieu bo cach nhau boi ';'
  python interpolation/moc_toi_uu.py data/<file>.txt -> moi dong la 1 bo: n a b
Phan tach so bang khoang trang. Dau ',' giua hai chu so = dau thap phan.
"""

import math
import re
import sys

import numpy as np

W_COT = 18  # do rong cot bang

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


# ===== THUAT TOAN =====

def kiem_tra_bo(so):
    """Buoc 0 (bo n a b): dung 3 so, n nguyen >= 1, a != b (doi cho neu a > b). Tra ve (n, a, b, canh bao)."""
    if len(so) != 3:
        raise ValueError(f"can dung 3 so (n a b), doc duoc {len(so)}.")
    n, a, b = so
    if n != int(n) or n < 1:
        raise ValueError(f"so moc n = {n:g} phai la so nguyen >= 1.")
    if a == b:
        raise ValueError("a = b: doan noi suy suy bien.")
    canh_bao = []
    if a > b:
        canh_bao.append(f"doan: a = {a:g} > b = {b:g} -> doi cho a <-> b")
        a, b = b, a
    return int(n), a, b, canh_bao


def moc_toi_uu(n, a, b, verbose=True):
    """Muc 1: t_i = -cos((2i+1)pi/(2n)), x_i = p + q*t_i. Tra ve (t, x, W)."""
    p = (a + b) / 2                                # Buoc 1 - Doi bien
    q = (b - a) / 2
    if verbose:
        print(f"  p = (a+b)/2 = {p:.10g},  q = (b-a)/2 = {q:.10g}")
        print()
        print(f"  {'i':>3}{'x_i':>{W_COT}}")
        print("  " + "-" * (3 + W_COT))
    t = [0.0] * n
    x = [0.0] * n
    for i in range(n):                             # Buoc 2
        goc = (2 * i + 1) * math.pi / (2 * n)
        t[i] = -math.cos(goc)                      # Buoc 2.1 - Nghiem cua T_n
        x[i] = p + q * t[i]                        # Buoc 2.2 - Moc tren [a, b]
        if verbose:
            print(f"  {i:>3}{fmt(x[i]):>{W_COT}}")
    log_W = math.log(2) + n * math.log((b - a) / 4)   # Buoc 3 - W = (b-a)^n / 2^(2n-1), tinh qua log de khong tran so
    W = math.exp(log_W) if log_W < 709 else math.inf
    return t, x, W                                 # Buoc 4 - Ket thuc


# ===== GIAI =====

CONG_THUC = "CONG THUC: x_i = (a+b)/2 - (b-a)/2 cos((2i+1)pi/(2n)),  i = 0..n-1  (moc xep tang dan)"


def cong_thuc_so(n, a, b):
    """Cong thuc moc da thay so, vd '4.5 - 1.5 cos((2i+1)pi/24)'."""
    p, q = (a + b) / 2, (b - a) / 2
    return (f"{p:.10g} - " if p else "-") + ("" if q == 1 else f"{q:.10g} ") + f"cos((2i+1)pi/{2 * n})"


def giai(n, a, b):
    print(f"\nn = {n},  [a, b] = [{a:g}, {b:g}]:  x_i = {cong_thuc_so(n, a, b)},  i = 0..{n - 1}")

    print("\nTINH TOAN:")
    t, x, W = moc_toi_uu(n, a, b)

    print("\nKET QUA (moc xep tang dan):")
    ten = "(x_0)" if n == 1 else f"(x_0, ..., x_{n - 1})"
    print(f"  x = {ten} = {vec(x)}")
    print(f"  W = ({b - a:g})^{n} / 2^{2 * n - 1} = {fmt(W)}")
    log_hs = math.log(2) + n * math.log((b - a) / 4) - math.lgamma(n + 1)   # log(W / n!)
    he_so = math.exp(log_hs) if log_hs < 709 else math.inf
    print(f"  => |f(x) - P(x)| <= M_{n} / {n}! * W = M_{n} * {fmt(he_so, nho=0)}")

    print("\nKIEM TRA (numpy):")
    nghiem = np.sort(np.real(np.polynomial.chebyshev.chebroots([0] * n + [1])))
    print(f"  max sai lech t voi chebroots              = {np.max(np.abs(np.array(t) - nghiem)):.2e}")
    print(f"  doi xung: max |x_i + x_(n-1-i) - (a+b)|    = {max(abs(x[i] + x[n - 1 - i] - (a + b)) for i in range(n)):.2e}")
    if not math.isfinite(W):
        print("  W vuot gioi han so thuc (n qua lon so voi b - a) -> bo qua kiem tra tren luoi")
        return t, x, W
    luoi = np.linspace(a, b, 200001)
    w, w_deu = np.ones_like(luoi), np.ones_like(luoi)
    with np.errstate(over="ignore", invalid="ignore"):
        for xi, xd in zip(x, np.linspace(a, b, n)):    # nhan dan tung thua so, khong tao mang 200001 x n
            w *= luoi - xi
            w_deu *= luoi - xd
    print(f"  max|w_n| tren luoi 200001 diem            = {np.max(np.abs(w)):.10e}  (W = {W:.10e})")
    print(f"  so sanh: max|w_n| voi n moc cach deu      = {np.max(np.abs(w_deu)):.10e}")
    return t, x, W


# ===== CHUONG TRINH CHINH =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")   # in du lieu goc co ky tu la khong bi crash
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                cac_bo = [d for d in f.read().splitlines() if d.strip()]
        except OSError:
            print(f"Loi: khong mo duoc file '{sys.argv[1]}'.")
            return
    else:
        mac_dinh = "9 -1 1; 12 3 6"
        try:
            s = input(f"Cac bo (n a b), cach nhau boi ';' (VD [{mac_dinh}]): ").strip()
        except EOFError:
            s = ""
        cac_bo = [bo for bo in (s or mac_dinh).split(";") if bo.strip()]
    if not cac_bo:
        print("Loi: khong co du lieu.")
        return

    print(CONG_THUC)
    for bo in cac_bo:
        bao_cao = []      # Buoc 0: chi in khi du lieu ban / loi
        loi = False
        try:
            so, cb = doc_day_so(bo, "bo")
            bao_cao += cb
            n, a, b, cb = kiem_tra_bo(so)
            bao_cao += cb
        except ValueError as e:
            bao_cao.append(f"Loi: {e} -> bo qua bo nay.")
            loi = True

        if bao_cao:
            print("\nXU LY DU LIEU")
            print("-" * 78)
            print(f"  bo (goc): {bo.strip()!r}")
            for m in bao_cao:
                print("  " + m)
            if loi:
                continue
            print(f"  Du lieu sach: n = {n},  [a, b] = [{a:g}, {b:g}]")
        giai(n, a, b)


if __name__ == "__main__":
    main()
