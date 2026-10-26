"""
PHUONG PHAP BINH PHUONG TOI THIEU
Thuat toan: docs/thuat_toan/binh_phuong_toi_thieu.md

Du lieu (x_i, y_i), i = 1..n; co so phi_1..phi_m nhap bang bieu thuc theo x, cach nhau boi ';'
(vd "x; 1/x", "x^2; cos(x); 1"; ham: sin cos tan exp ln log sqrt abs arctan, hang pi e).
Dang ham (chon 1):
  1. y = a_1 phi_1(x) + ... + a_m phi_m(x)          -> he chuan M a = Phi^t y (muc 1, 2)
  2. y = a e^(b_1 phi_1(x) + ... + b_m phi_m(x)) + d -> tuyen tinh hoa ln(s(y - d)) (muc 3) + hieu chinh Gauss-Newton (muc 4)
  3. y = a x^b + d                                  -> nhu 2 voi phi_1 = ln x
(d la hang so biet truoc, mac dinh 0, vd y = a e^(bx) - 2 thi d = -2.)
Sai so trung binh phuong sigma = sqrt(1/n sum (g(x_i) - y_i)^2) luon tinh tren y goc.

Cach chay:
  python interpolation/binh_phuong_toi_thieu.py                 -> nhap tu ban phim (Enter = mac dinh)
  python interpolation/binh_phuong_toi_thieu.py data/<file>.txt -> moi dong la 1 cau tra loi, theo thu tu cau hoi:
                                         dang ham / x / y / co so (dang 1, 2) / d (dang 2, 3) / hieu chinh (dang 2, 3)
  python interpolation/binh_phuong_toi_thieu.py <file>.xlsx|.csv -> bang du lieu; file co nhieu bo du lieu canh nhau
                                         (vd data cau 23) -> chon bo; cac cau con lai nhap tu ban phim
  VD cau 23a: python interpolation/binh_phuong_toi_thieu.py "slide_example/data Câu 23.xlsx"  roi nhap: 1 / 1 / x; 1/x
O tach bang khoang trang, ';' hoac tab. Dau ',' giua hai chu so = dau thap phan.
"""

import csv
import math
import re
import sys
import unicodedata

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


def khong_dau(s):
    """Bo dau tieng Viet de in ra console."""
    s = unicodedata.normalize("NFKD", s).replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def doc_luoi(duong_dan):
    """File -> luoi o (list hang, moi hang list chuoi)."""
    if duong_dan.lower().endswith((".xlsx", ".xls")):
        try:
            import pandas as pd
            df = pd.read_excel(duong_dan, header=None, dtype=str)
        except ImportError as e:
            raise ValueError(f"doc file Excel can pandas + openpyxl ({e}); hay luu bang thanh .csv.")
        return [["" if not isinstance(v, str) else v for v in h] for h in df.values.tolist()]
    with open(duong_dan, encoding="utf-8-sig") as f:
        dong = f.read().splitlines()
    if any(re.search(r"[;\t]", d) for d in dong):
        return [tach_o(d) for d in dong]
    return [list(h) for h in csv.reader(dong)]


def tim_khoi(luoi):
    """Cac bo du lieu: 2 hang (x, y) hoac cac cap cot lien ke cung co >= 3 o so tren cung dong.
    Tra ve [(nhan, o_x, o_y, vi_tri)]."""
    luoi = [h for h in luoi if any(c.strip() for c in h)]
    if not luoi:
        raise ValueError("file khong co du lieu.")
    C = max(len(h) for h in luoi)
    luoi = [h + [""] * (C - len(h)) for h in luoi]
    giu = [j for j in range(C) if any(h[j].strip() for h in luoi)]
    if len(luoi) == 2 and len(giu) > 2:                           # 2 hang: x / y
        return [("2 hang x, y", bo_nhan([luoi[0][j] for j in giu]), bo_nhan([luoi[1][j] for j in giu]), "o thu")]
    so = [[doc_o(c)[0] is not None for c in h] for h in luoi]
    khoi, j = [], 0
    while j < C - 1:
        dong = [i for i in range(len(luoi)) if so[i][j] and so[i][j + 1]]
        if len(dong) >= 3:
            i0, i1 = dong[0], dong[-1]
            chu = [luoi[i][c].strip() for i in range(i0) for c in (j - 1, j, j + 1)
                   if 0 <= c < C and luoi[i][c].strip() and doc_o(luoi[i][c])[0] is None]
            ten = khong_dau(" ".join(chu)) or f"cot {j + 1}-{j + 2}"
            khoi.append((f"{ten} (cot {j + 1}-{j + 2}, dong {i0 + 1}-{i1 + 1})",
                         [luoi[i][j] for i in range(i0, i1 + 1)], [luoi[i][j + 1] for i in range(i0, i1 + 1)],
                         f"dong (tu {i0 + 1}) thu"))
            j += 2
        else:
            j += 1
    if not khoi:
        raise ValueError("khong tim thay cap cot (x, y) nao co it nhat 3 dong so.")
    return khoi


def lam_sach(ox, oy, vi_tri, bao):
    """Buoc 0: cap o (x, y) -> x, y sach (khong gop moc trung, khong sap xep)."""
    if len(ox) != len(oy):
        raise ValueError(f"hang x co {len(ox)} o, hang y co {len(oy)} o -> khong ghep cap duoc.")
    sua, x, y = {}, [], []
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
            x.append(vx)
            y.append(vy)
    bao[:0] = [f"{g} ({vi_tri} {', '.join(map(str, ds))})" for g, ds in sorted(sua.items(), key=lambda m: m[0][0])]
    trung = len(x) - len(set(x))
    if trung:
        bao.append(f"co {trung} moc x trung (giu nguyen: binh phuong toi thieu cho phep nhieu quan sat tai 1 x)")
    return x, y


HAM = {"sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "ln": np.log, "log": np.log,
       "sqrt": np.sqrt, "abs": np.abs, "arctan": np.arctan, "atan": np.arctan, "pi": math.pi, "e": math.e}


def doc_co_so(text):
    """Buoc 0: chuoi co so -> [(ten, ham)]; sai cu phap -> ValueError."""
    s = re.sub("[−–—]", "-", text)
    co_so = []
    for t in (t.strip() for t in re.split(r";|\n", s)):
        if not t:
            continue
        bt = t.replace("^", "**")
        if re.search(r"__|[\[\]{}]|lambda|import", bt):
            raise ValueError(f"co so {t!r} khong hop le.")
        try:
            ma = compile(bt, "<co so>", "eval")
        except SyntaxError:
            raise ValueError(f"co so {t!r} sai cu phap.")
        la = [ten for ten in ma.co_names if ten not in HAM and ten != "x"]
        if la:
            raise ValueError(f"co so {t!r} co ten la {la} (chi dung x va {', '.join(HAM)}).")
        co_so.append((t, lambda xv, ma=ma: np.broadcast_to(
            np.asarray(eval(ma, {"__builtins__": {}}, dict(HAM, x=xv)), dtype=float), np.shape(xv)).copy()))
    if not co_so:
        raise ValueError("chua nhap ham co so.")
    return co_so


def gia_tri_co_so(co_so, x, bao):
    """Phi (n x m); loai diem lam phi_j khong xac dinh. Tra ve (Phi, chi so giu)."""
    xv = np.array(x, dtype=float)
    with np.errstate(all="ignore"):
        Phi = np.column_stack([f(xv) for _, f in co_so])
    tot = np.all(np.isfinite(Phi), axis=1)
    for i in np.where(~tot)[0]:
        bad = [ten for (ten, _), v in zip(co_so, Phi[i]) if not np.isfinite(v)]
        bao.append(f"loai diem x = {x[i]:.10g}: co so {', '.join(bad)} khong xac dinh")
    return Phi[tot], np.where(tot)[0]


# ===== THUAT TOAN =====

def gauss(M, b):
    """Muc 2: khu Gauss chon tru. Tra ve (a, ma tran bo sung sau khu xuoi)."""
    m = len(b)
    A = [list(map(float, h)) + [float(v)] for h, v in zip(M, b)]   # Buoc 1
    for c in range(m):                                            # Buoc 2
        p = max(range(c, m), key=lambda i: abs(A[i][c]))          # 2.1 - Chon tru
        if abs(A[p][c]) < 1e-12 * max(abs(v) for v in A[p][:m] + [1e-300]):
            raise ValueError("ma tran suy bien: cac ham co so phu thuoc tuyen tinh tren bo du lieu.")
        A[c], A[p] = A[p], A[c]
        for i in range(c + 1, m):                                 # 2.2 - Khu
            f = A[i][c] / A[c][c]
            A[i] = [u - f * v for u, v in zip(A[i], A[c])]
    a = [0.0] * m
    for i in range(m - 1, -1, -1):                                # Buoc 3 - The nguoc
        a[i] = (A[i][m] - sum(A[i][k] * a[k] for k in range(i + 1, m))) / A[i][i]
    return a, A                                                   # Buoc 4


def bptt(Phi, y, w=None):
    """Muc 1: (a, M, b, tam giac, g, sigma)."""
    Phi = np.asarray(Phi, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    M = (Phi * w[:, None]).T @ Phi                                # Buoc 2 - He chuan
    b = (Phi * w[:, None]).T @ y
    a, A = gauss(M.tolist(), b.tolist())                          # Buoc 3 - Giai (muc 2)
    g = Phi @ np.array(a)                                         # Buoc 4 - Sai so
    return np.array(a), M, b, A, g, float(np.sqrt(np.mean((g - y) ** 2)))


def tuyen_tinh_hoa(Phi1, Y, s):
    """Muc 3: Phi1 = [1, phi_1..phi_m]; Y = y - d (cung dau s). Tra ve (c, M, b, A, z, g_Y, sigma)."""
    z = np.log(s * np.asarray(Y))                                 # Buoc 2 - Doi bien
    c, M, b, A, gz, sz = bptt(Phi1, z)                            # Buoc 3
    gY = s * np.exp(Phi1 @ c)                                     # Buoc 5 - Sai so tren y goc
    return c, M, b, A, z, gY, float(np.sqrt(np.mean((gY - Y) ** 2))), sz


def gauss_newton(Phi1, Y, s, eps=1e-10, N=100):
    """Muc 4: (c, cac lan lap [(j, c, sigma)], hoi_tu)."""
    Y = np.asarray(Y, dtype=float)
    c = bptt(Phi1, np.log(s * Y), Y ** 2)[0]                      # Buoc 1 - Khoi tao, w = y^2
    lan = [(0, c, float(np.sqrt(np.mean((s * np.exp(Phi1 @ c) - Y) ** 2))))]
    for j in range(N):                                            # Buoc 2
        g = s * np.exp(Phi1 @ c)                                  # 2.1
        z = np.log(s * g) + (Y - g) / g                           # 2.2
        c_moi = bptt(Phi1, z, g ** 2)[0]                          # 2.3
        lan.append((j + 1, c_moi, float(np.sqrt(np.mean((s * np.exp(Phi1 @ c_moi) - Y) ** 2)))))
        if np.max(np.abs(c_moi - c)) < eps * (1 + np.max(np.abs(c_moi))):   # 2.4 - Dung
            return c_moi, lan, True
        c = c_moi
    return c, lan, False                                          # Buoc 3 - Khong hoi tu


# ===== GIAI =====

def in_bang_du_lieu(x, cot, ten_cot, tong=True, toi_da=10 ** 9):
    """Bang du lieu (in toan bo; n > toi_da: 6 dong dau ... 3 dong cuoi) va dong Tong."""
    n = len(x)
    chon = list(range(n)) if n <= toi_da else list(range(6)) + [None] + list(range(n - 3, n))
    hang = []
    for i in chon:
        hang.append(["...", ""] + [""] * len(cot) if i is None else [str(i + 1), f"{x[i]:.10g}"] + [c[i] for c in cot])
    if tong:
        hang += [None, ["Tong", fmt(sum(x), ".10g")] + [float(np.sum(c)) for c in cot]]
    in_bang(["i", "x_i"] + ten_cot, hang)


def in_he(M, b, ten, A):
    print("  He chuan M a = b (ma tran bo sung):")
    in_bang([""] + ten + ["| b"], [[f"pt {j + 1}"] + list(M[j]) + [b[j]] for j in range(len(b))], le="    ")
    print("  Khu Gauss chon tru (ma tran tam giac tren):")
    in_bang([""] + ten + ["| b"], [[f"pt {j + 1}"] + A[j] for j in range(len(A))], le="    ")


def giai(x, y, dang, co_so, d, hieu_chinh):
    n = len(x)
    xv, yv = np.array(x), np.array(y)
    ten = [t for t, _ in co_so]
    print(f"\nBinh phuong toi thieu: n = {n} diem, ", end="")
    if dang == 1:
        print("g(x) = " + " + ".join(f"a_{j + 1}*({t})" for j, t in enumerate(ten)))
    elif dang == 2:
        print(f"g(x) = a e^(" + " + ".join(f"b_{j + 1}*({t})" for j, t in enumerate(ten)) + ")"
              + (f" + ({d:.10g})" if d else ""))
    else:
        print("g(x) = a x^b" + (f" + ({d:.10g})" if d else ""))

    print("\nCONG THUC:")
    print("  Phi = (phi_j(x_i))_(n x m),  M = Phi^t Phi,  b = Phi^t y,  M a = b  (khu Gauss);"
          "  sigma = sqrt(1/n * sum (g(x_i) - y_i)^2)")
    if dang > 1:
        print(f"  Tuyen tinh hoa: Y = y - d, s = sign(Y), z = ln(s Y) = ln(s a) + "
              + (" + ".join(f"b_{j + 1} phi_{j + 1}" for j in range(len(ten))) if dang == 2 else "b ln x")
              + ";  co so (1, " + (", ".join(ten) if dang == 2 else "ln x") + ")")
        if hieu_chinh:
            print("  Hieu chinh Gauss-Newton: g_i = s e^(Phi c), z_i = ln(s g_i) + (Y_i - g_i)/g_i, w_i = g_i^2,"
                  "  M = Phi^t W Phi, b = Phi^t W z;  c^(0): w_i = Y_i^2")

    print("\nTINH TOAN:")
    kq = {}
    if dang == 1:
        Phi = np.column_stack([f(xv) for _, f in co_so])
        a, M, b, A, g, sigma = bptt(Phi, yv)
        print("Bang du lieu va gia tri co so (cot cuoi: g(x_i), y_i - g(x_i)):")
        in_bang_du_lieu(x, [yv] + [Phi[:, j] for j in range(len(ten))] + [g, yv - g],
                        ["y_i"] + [f"phi_{j + 1}={t}" for j, t in enumerate(ten)] + ["g(x_i)", "y_i - g"])
        in_he(M, b, [f"a_{j + 1}" for j in range(len(ten))], A)
        print(f"  => a = (a_1, ..., a_{len(ten)}) = {vec(a)}")
        print(f"  sigma = sqrt(1/{n} * sum (g(x_i) - y_i)^2) = {sigma:.10g}")
        kq.update(a=a, sigma=sigma, g=g, M=M, b=b)
        ham = " + ".join(f"({fmt(v, '.10g')})*{t}" for v, t in zip(a, ten))
        ket = [f"  a = {vec(a)}", f"  g(x) = {ham}", f"  sigma = {sigma:.10g}"]
    else:
        Y = yv - d
        s = 1.0 if Y[0] > 0 else -1.0
        cs = [("1", lambda t: np.ones_like(t))] + (co_so if dang == 2 else [("ln x", np.log)])
        Phi1 = np.column_stack([f(xv) for _, f in cs])
        ten1 = [t for t, _ in cs]
        c, M, b, A, z, gY, sigma, sz = tuyen_tinh_hoa(Phi1, Y, s)
        print(f"Tuyen tinh hoa (muc 3): s = {s:+.0f}, z_i = ln({'' if s > 0 else '-'}(y_i"
              + (f" - ({d:.10g})" if d else "") + "))")
        in_bang_du_lieu(x, [yv, z] + [Phi1[:, j] for j in range(1, len(ten1))] + [gY + d, yv - gY - d],
                        ["y_i", "z_i"] + [f"phi={t}" for t in ten1[1:]] + ["g(x_i)", "y_i - g"])
        in_he(M, b, ["ln(sa)"] + [f"b_{j}" for j in range(1, len(ten1))], A)
        a = s * math.exp(c[0])
        print(f"  => c = (ln(s a), b_1, ...) = {vec(c)},  a = s e^(c_0) = {a:.10g}")
        print(f"  sigma (tren y goc) = {sigma:.10g};  sigma_z (tren z = ln) = {sz:.10g}")
        kq.update(c=c, a=a, sigma=sigma, M=M, b=b)
        tot = (c, a, sigma)
        if hieu_chinh:
            c2, lan, ok = gauss_newton(Phi1, Y, s)
            print("\nHieu chinh Gauss-Newton (muc 4), dung khi max|c^(j+1) - c^(j)| < 1e-10 (1 + max|c|):")
            L = len(lan) - 1
            chon = [j for j in range(L + 1) if j <= 2 or j >= L - 1]
            hang = []
            for j in chon:
                if j == L - 1 and L > 4:
                    hang.append(["..."] + [""] * (len(ten1) + 1))
                hang.append([str(lan[j][0])] + list(lan[j][1]) + [lan[j][2]])
            in_bang(["j", "ln(sa)"] + [f"b_{j}" for j in range(1, len(ten1))] + ["sigma"], hang)
            if ok:
                a2 = s * math.exp(c2[0])
                s2 = lan[-1][2]
                print(f"  => hoi tu sau {L} lan: c = {vec(c2)},  a = {a2:.10g},  sigma = {s2:.10g}")
                kq.update(c_gn=c2, a_gn=a2, sigma_gn=s2, lan=lan)
                if s2 < sigma:
                    tot = (c2, a2, s2)
            else:
                print(f"  => KHONG HOI TU sau {L} lan lap -> giu ket qua tuyen tinh hoa")
        cb, ab, sb = tot
        bs = " + ".join(f"({fmt(v, '.10g')})*{t}" for v, t in zip(cb[1:], ten1[1:]))
        dd = f" + ({d:.10g})" if d else ""
        ket = [f"  Tuyen tinh hoa: a = {a:.10g}, b = {vec(c[1:])}, sigma = {sigma:.10g}"]
        if "c_gn" in kq:
            ket.append(f"  Gauss-Newton  : a = {kq['a_gn']:.10g}, b = {vec(kq['c_gn'][1:])}, sigma = {kq['sigma_gn']:.10g}")
        ket.append(f"  Chon (sigma nho hon): g(x) = {ab:.10g} * e^({bs}){dd}" if dang == 2 else
                   f"  Chon (sigma nho hon): g(x) = {ab:.10g} * x^({fmt(cb[1], '.10g')}){dd}")
        ket.append(f"  sigma = {sb:.10g}")

    print("\nKET QUA:")
    for dong in ket:
        print(dong)

    print("\nKIEM TRA:")
    if dang == 1:
        a_np = np.linalg.lstsq(Phi, yv, rcond=None)[0]
        kiem("a vs numpy.linalg.lstsq, tuong doi", np.max(np.abs(a - a_np)) / max(1.0, np.max(np.abs(a_np))))
        kiem("phan du truc giao co so: max |Phi^t (y - g)|", np.max(np.abs(Phi.T @ (yv - g))))
    else:
        c_np = np.linalg.lstsq(Phi1, np.log(s * (yv - d)), rcond=None)[0]
        kiem("tuyen tinh hoa: c vs numpy.linalg.lstsq, tuong doi",
             np.max(np.abs(kq["c"] - c_np)) / max(1.0, np.max(np.abs(c_np))))
        if "c_gn" in kq:
            gY = s * np.exp(Phi1 @ kq["c_gn"])
            J = Phi1 * gY[:, None]                                # dao ham g theo c
            kiem("Gauss-Newton: gradient max |J^t (Y - g)| (phai ~ 0)", np.max(np.abs(J.T @ (yv - d - gY))))
            try:
                from scipy.optimize import curve_fit
                f = lambda xx, *cc: s * np.exp(np.column_stack([fn(np.asarray(xx)) for _, fn in cs]) @ np.array(cc))
                c_sp = curve_fit(f, xv, yv - d, p0=kq["lan"][0][1])[0]   # xuat phat khac (w = y^2)
                kiem("Gauss-Newton vs scipy.optimize.curve_fit, tuong doi",
                     np.max(np.abs(kq["c_gn"] - c_sp)) / max(1.0, np.max(np.abs(c_sp))))
            except ImportError:
                pass
    return kq


# ===== CHUONG TRINH CHINH =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")   # in du lieu goc co ky tu la khong bi crash
    tra_loi, khoi = None, None
    if len(sys.argv) > 1:
        p = sys.argv[1]
        try:
            if p.lower().endswith((".csv", ".xlsx", ".xls")):
                khoi = tim_khoi(doc_luoi(p))
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
        if khoi is not None and len(khoi) > 1:
            print("Cac bo du lieu trong file:")
            for r, (ten, ox, _, _) in enumerate(khoi, 1):
                print(f"  {r}. {ten}: {len(ox)} dong")
            goc["bo du lieu"] = nhap("Chon bo du lieu", "1")
            r = doc_day_so(goc["bo du lieu"], "bo du lieu", bao)
            if len(r) != 1 or r[0] != int(r[0]) or not 1 <= r[0] <= len(khoi):
                raise ValueError(f"bo du lieu phai la 1 so nguyen trong 1..{len(khoi)}.")
            khoi = [khoi[int(r[0]) - 1]]
        if tra_loi is None:
            print("Dang ham:")
            print("  1. y = a_1 phi_1(x) + ... + a_m phi_m(x)")
            print("  2. y = a e^(b_1 phi_1(x) + ... + b_m phi_m(x)) + d")
            print("  3. y = a x^b + d")
        goc["dang ham"] = nhap("Chon dang ham", "1")
        dg = doc_day_so(goc["dang ham"], "dang ham", bao)
        if len(dg) != 1 or dg[0] not in (1, 2, 3):
            raise ValueError("dang ham phai la 1, 2 hoac 3.")
        dang = int(dg[0])
        if khoi is None:
            goc["x"] = nhap("Cac x_i", "1 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2")
            goc["y"] = nhap("Cac y_i", "-0.641 -0.498 -0.34 -0.165 0.028 0.241 0.477 0.737 1.025 1.343 1.695")
            ox, oy, vi_tri = bo_nhan(tach_o(goc["x"])), bo_nhan(tach_o(goc["y"])), "o thu"
        else:
            ten_k, ox, oy, vi_tri = khoi[0]
            goc[f"x (file, {ten_k})"], goc["y (file)"] = "; ".join(ox), "; ".join(oy)
        x, y = lam_sach(ox, oy, vi_tri, bao)
        co_so = []
        if dang in (1, 2):
            goc["co so"] = nhap("Cac ham co so phi_j (cach nhau ';')", "x; 1" if dang == 1 else "x")
            co_so = doc_co_so(goc["co so"])
        d, hieu_chinh = 0.0, False
        if dang in (2, 3):
            goc["d"] = nhap("Hang so cong them d", "0" if khoi is not None or tra_loi is not None else "-2")
            ds = doc_day_so(goc["d"], "d", bao)
            if len(ds) != 1:
                raise ValueError("d phai la 1 so.")
            d = ds[0]
            goc["hieu chinh"] = nhap("Hieu chinh Gauss-Newton (1 = co, 0 = khong)", "1")
            hc = doc_day_so(goc["hieu chinh"], "hieu chinh", bao)
            hieu_chinh = bool(hc and hc[0])
        # loai diem lam co so khong xac dinh
        cs_kt = co_so if dang != 3 else [("ln x", np.log)]
        _, giu = gia_tri_co_so(cs_kt, x, bao)
        x, y = [x[i] for i in giu], [y[i] for i in giu]
        if dang in (2, 3):
            Y = [v - d for v in y]
            duong = sum(v > 0 for v in Y)
            am = sum(v < 0 for v in Y)
            s = 1 if duong >= am else -1
            bo = [i for i, v in enumerate(Y) if v * s <= 0]
            for i in bo:
                bao.append(f"loai diem x = {x[i]:.10g}, y = {y[i]:.10g}: y - d = {Y[i]:.10g}"
                           + (" bang 0" if Y[i] == 0 else " trai dau") + " -> khong lay ln duoc")
            if len(bo) * 2 > len(x):
                raise ValueError("qua nua so diem khong lay ln duoc -> dang ham khong phu hop.")
            x = [v for i, v in enumerate(x) if i not in bo]
            y = [v for i, v in enumerate(y) if i not in bo]
            if dang == 2:
                for t, f in co_so:
                    v = f(np.array(x, dtype=float))
                    if np.ptp(v) < 1e-12 * max(1.0, np.max(np.abs(v))):
                        raise ValueError(f"co so {t!r} la hang tren bo du lieu -> trung vai tro voi a.")
        so_tham_so = len(co_so) + (dang > 1) if dang != 3 else 2
        if len(x) < so_tham_so:
            raise ValueError(f"can it nhat {so_tham_so} diem cho {so_tham_so} tham so, con {len(x)}.")
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
        print(f"  Du lieu sach ({len(x)} diem):")
        print(f"    x = {ngan(vec(x))}")
        print(f"    y = {ngan(vec(y))}")

    try:
        giai(x, y, dang, co_so, d, hieu_chinh)
    except ValueError as e:
        print(f"\nLoi: {e}")


if __name__ == "__main__":
    main()
