"""
SINH LOI GIAI LATEX BAI TAP CAU 3-23 (BaitapPPS_2026)

Van ban (de, phuong phap, cong thuc, thuat toan): docs/loi_giai/mau_loi_giai.tex, cho can so lieu ghi <<khoa>>.
So lieu / bang: tinh bang CHINH CAC HAM THUAT TOAN trong interpolation/*.py (nap truc tiep tu file),
nen loi giai luon khop voi output cua code.

Chay : python docs/loi_giai/sinh_loi_giai.py      -> docs/loi_giai/loi_giai_bai_tap.tex
Dich : xelatex loi_giai_bai_tap.tex (2 lan, trong thu muc docs/loi_giai)
"""

import importlib.util
import math
import os
import re
import sys

import numpy as np

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))


def nap(ten):
    spec = importlib.util.spec_from_file_location(ten, os.path.join(GOC, "interpolation", ten + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


hn, mt, lg, nw, tt, nsn, sp, bp = (nap(t) for t in (
    "horner", "moc_toi_uu", "lagrange", "newton", "trung_tam", "noi_suy_nguoc", "spline", "binh_phuong_toi_thieu"))

V = {}                       # khoa -> doan LaTeX


# ===== DINH DANG =====

def so(v, sig=10):
    """So -> LaTeX: toi da sig chu so co nghia, mu -> \\cdot10^{k}."""
    if abs(v) < 1e-14:
        return "0"
    s = f"{v:.{sig}g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m}\\cdot10^{{{int(e)}}}"
    return s


def sd(v, d):
    """So co dinh d chu so thap phan (sai phan cua du lieu d chu so: dung tuyet doi)."""
    s = f"{round(v, d):.{d}f}"
    return "0." + "0" * d if re.fullmatch(r"-0\.0*", s) else s


def sn(v, sig=10):
    """So trong bieu thuc: so am dat trong ngoac."""
    s = so(v, sig)
    return f"({s})" if s.startswith("-") else s


def ob(s):
    return r"\ob{" + s + "}"


def vecl(v, sig=10):
    return r"\left(" + r";\ ".join(so(t, sig) for t in v) + r"\right)"


def boc(c):
    if c is None or c == "":
        return ""
    c = str(c)
    if c.startswith("\\ob") or "$" in c or c.startswith("\\multicolumn"):
        return c
    return "$" + c + "$"


def bang(dau, hang, can=None, co="small"):
    """Bang LaTeX co gian theo be ngang trang. hang: list (None = ke ngang)."""
    n = len(dau)
    can = can or ("r" * n)
    out = [r"\begin{center}", "{\\" + co, r"\begin{adjustbox}{max width=\linewidth}",
           r"\begin{tabular}{" + can + "}", r"\toprule", " & ".join(boc(c) for c in dau) + r" \\", r"\midrule"]
    for h in hang:
        if h is None:
            out.append(r"\midrule")
            continue
        h = list(h) + [""] * (n - len(h))
        out.append(" & ".join(boc(c) for c in h) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}}", r"\end{center}"]
    return "\n".join(out)


def mu(e, bien="x"):
    return f"{bien}^{{{e}}}" if e > 1 else (bien if e == 1 else "1")


def cot_mu(n, bien="x"):
    return [mu(e, bien) for e in range(n, -1, -1)]


def da_thuc(he, bien="x", sig=10, moi_dong=3, ten="P(x)"):
    """Da thuc (he so bac cao -> thap) dang align*, xuong dong sau moi_dong so hang."""
    n = len(he) - 1
    hang = []
    for i, a in enumerate(he):
        if abs(a) < 1e-14:
            continue
        e = n - i
        s = so(abs(a), sig)
        hang.append(("-" if a < 0 else "+", s + ("" if e == 0 else ("\\," if "cdot" in s else "") + mu(e, bien))))
    if not hang:
        return r"\[" + ten + "=0\\]"
    dong, cur = [], []
    for k, (dau, t) in enumerate(hang):
        cur.append((dau if k else ("-" if dau == "-" else "")) + ("" if k == 0 else " ") + t)
        if len(cur) == moi_dong:
            dong.append(" ".join(cur))
            cur = []
    if cur:
        dong.append(" ".join(cur))
    return "\\begin{align*}\n" + ten + " &= " + " \\\\\n&\\quad ".join(dong) + "\n\\end{align*}"


def do_dai(t):
    """Do dai hien thi uoc luong cua 1 doan LaTeX (bo lenh, ngoac)."""
    return len(re.sub(r"\\[a-zA-Z]+|[{}]", "", t))


def noi_dong(ten, so_hang, toi_da=62):
    """align*: 'ten = so_hang[0] so_hang[1] ...', xuong dong khi dai qua toi_da ky tu."""
    dong, cur, dai = [], [], 0
    for t in so_hang:
        if cur and dai + do_dai(t) > toi_da:
            dong.append(" ".join(cur))
            cur, dai = [], 0
        cur.append(t)
        dai += do_dai(t)
    dong.append(" ".join(cur))
    return "\\begin{align*}\n" + ten + " &= " + " \\\\\n&\\quad ".join(dong) + "\n\\end{align*}"


def vec_hien(v, ten, moi_dong=4, sig=10):
    """Vector dai: align*, moi dong moi_dong phan tu."""
    phan = [so(t, sig) for t in v]
    nhom = [r";\ ".join(phan[i:i + moi_dong]) for i in range(0, len(phan), moi_dong)]
    return ("\\begin{align*}\n" + ten + r" &= \big(" + (";\\\\\n&\\qquad ").join(nhom) + r"\big)" + "\n\\end{align*}")


def L(_mau, **kw):
    """Thay @khoa@ trong doan LaTeX (tranh phai nhan doi ngoac nhon)."""
    for k, v in kw.items():
        _mau = _mau.replace("@" + k + "@", str(v))
    return _mau


def ket_luan(noi_dung):
    return (r"\begin{ketluan}" + "\n" + noi_dung + "\n" + r"\end{ketluan}")


def bang_horner_lap(a, c, k, bien="x", sig=10):
    """Bang Horner chia lap tai c (muc 2, horner.md), o r_j dong khung. Tra ve (bang, r, v)."""
    n = len(a) - 1
    r, v, hang = nw.horner_dao_ham(list(a), c, k)
    if n >= 6:                                     # bang doc: hang = luy thua, moi lan chia j = 2 cot (c*b, b)
        rows = []
        for i in range(n, -1, -1):
            h = [mu(i, bien), so(a[n - i], sig)]
            for j, sau in enumerate(hang):
                if i >= j:
                    gia = so(sau[n - i], sig)
                    h += ["" if i == n else so(c * sau[n - i - 1], sig), ob(gia) if i == j else gia]
                else:
                    h += ["", ""]
            rows.append(h)
        dau = ["", r"\text{hệ số}"]
        for j in range(len(hang)):
            dau += [f"c\\cdot b\\ (j={j})", f"b\\ (j={j})"]
        return bang(dau, rows), r, v
    rows = [[r"\text{Hệ số}"] + [so(t, sig) for t in a]]
    for j, sau in enumerate(hang):
        tich = [""] + [so(c * sau[l - 1], sig) for l in range(1, len(sau))]
        rows.append([f"c={so(c)}"] + tich)
        rows.append([f"j={j}"] + [so(t, sig) for t in sau[:-1]] + [ob(so(sau[-1], sig))])
        rows.append(None)
    rows.pop()
    return bang([""] + cot_mu(n, bien), rows), r, v


# ===== CAU 3 =====

def cau3():
    for n, a, b, ten in ((9, -1.0, 1.0, "a"), (12, 3.0, 6.0, "b")):
        t, x, W = mt.moc_toi_uu(n, a, b, verbose=False)
        p, q = (a + b) / 2, (b - a) / 2
        rows = [[str(i), f"{(2 * i + 1)}\\pi/{2 * n}", sd((2 * i + 1) * math.pi / (2 * n), 10), sd(t[i], 10), sd(x[i], 10)]
                for i in range(n)]
        V[f"c3_bang_{ten}"] = bang(["i", r"\theta_i=\frac{(2i+1)\pi}{2n}", r"\theta_i", r"t_i=-\cos\theta_i",
                                    r"x_i=p+q\,t_i"], rows)
        V[f"c3_p_{ten}"], V[f"c3_q_{ten}"] = so(p), so(q)
        V[f"c3_W_{ten}"] = so(W, 8)
        V[f"c3_E_{ten}"] = so(W / math.factorial(n), 6)
        V[f"c3_x_{ten}"] = vec_hien(x, "x", moi_dong=4)
        # kiem tra voi chebroots
        tc = np.sort(np.polynomial.chebyshev.chebroots([0] * n + [1]))
        V[f"c3_kt_{ten}"] = so(float(np.max(np.abs(np.array(t) - tc))), 2)


# ===== CAU 4, 5 =====

def cau4():
    a = [3.0, 0.0, -2.0, -1.0]
    for c, ten in ((0.0, "0"), (2.15, "1")):
        B, r, v = bang_horner_lap(a, c, 3)
        V[f"c4_bang_{ten}"] = B
        Q, du = nw.horner_dao_ham(list(a), c, 0)[2][0][:-1], r[0]
        V[f"c4_P_{ten}"] = so(r[0])
        V[f"c4_Q_{ten}"] = da_thuc(Q, ten=r"Q_2(x)").replace("align*", "align*")
        V[f"c4_Qv_{ten}"] = vecl(Q)
        V[f"c4_r_{ten}"] = vecl(r)
        V[f"c4_v_{ten}"] = vecl(v)
        dh = [f"P^{{({j})}}({so(c)})={j}!\\cdot{sn(r[j])}={so(v[j])}" for j in range(4)]
        V[f"c4_dh_{ten}"] = ("\\begin{gather*}\n" + r",\qquad ".join(dh[:2]) + r",\\" + "\n"
                             + r",\qquad ".join(dh[2:]) + ".\n\\end{gather*}")
        # kiem tra numpy
        V[f"c4_kt_{ten}"] = so(max(abs(np.polyval(np.polyder(a, j) if j else a, c) - v[j]) for j in range(4)), 2)


def cau5():
    xs = [2, 2.4, 2.7, 3, 3.1, 3.4]
    m = len(xs)
    p = [1.0]
    rows = [[r"\text{bắt đầu}"] + [""] * m + ["1"]]
    for i, z in enumerate(xs):
        p = nw.horner_nhan(p, z)
        hang = [so(t) for t in p]
        if i == m - 1:
            hang = [ob(t) for t in hang]
        rows.append([f"\\times(x-{so(z)})"] + [""] * (m - i - 1) + hang)
    V["c5_bang"] = bang(["\\text{nhân}"] + cot_mu(m), rows)
    V["c5_p"] = vecl(p)
    V["c5_w"] = da_thuc(p, ten="w_6(x)")
    V["c5_kt"] = so(float(np.max(np.abs(np.array(p) - np.poly(xs)))), 2)


# ===== CAU 7 =====

def cau7():
    x = [1.2, 1.5, 1.7, 1.8, 2.1, 2.3]
    y = [0.892, 1.179, 1.358, 1.445, 1.688, 1.839]
    n = len(x) - 1
    a, D, bang_t, bang_c = lg.lagrange(x, y)
    rows = [[r"\text{bắt đầu}"] + [""] * (n + 1) + ["1"]]
    for i, p in enumerate(bang_t):
        rows.append([f"\\times(x-{so(x[i])})"] + [""] * (n - i) + [so(t) for t in p])
    V["c7_bang_tich"] = bang(["\\text{nhân}"] + cot_mu(n + 1), rows)
    V["c7_w"] = vecl(bang_t[-1])
    rows = []
    for i in range(n + 1):
        tich = r"\cdot".join(f"({so(x[i])}-{so(x[j])})" for j in range(n + 1) if j != i)
        rows.append([str(i), so(x[i]), so(y[i]), tich, so(D[i], 8), so(y[i] / D[i], 10)])
    V["c7_bang_D"] = bang(["i", "x_i", "y_i", r"D_i=\prod_{j\ne i}(x_i-x_j)", "D_i", "y_i/D_i"], rows, co="footnotesize")
    rows = []
    for i, (q, du) in enumerate(bang_c):
        du = 0.0 if abs(du) < 1e-9 * max(1.0, max(abs(t) for t in bang_t[-1])) else du   # du = 0 (sai so lam tron)
        rows.append([f"x_{i}={so(x[i])}", so(y[i] / D[i], 10)] + [so(t, 8) for t in q] + [so(du, 3)])
    rows.append(None)
    rows.append([r"\text{Tổng } \sum\frac{y_i}{D_i}q^{(i)}", ""] + [ob(so(t, 10)) for t in a] + [""])
    V["c7_bang_chia"] = bang(["", "y_i/D_i"] + cot_mu(n) + [r"\text{dư}"], rows)
    V["c7_a"] = vec_hien(a, "a", moi_dong=3)
    V["c7_P"] = da_thuc(a, ten="P_5(x)")
    V["c7_kt"] = so(float(np.max(np.abs(np.polyval(a, x) - np.array(y)))), 2)
    V["c7_kt2"] = so(float(np.max(np.abs(np.array(a) - np.linalg.solve(np.vander(x), y))) /
                           np.max(np.abs(a))), 2)


# ===== CAU 8, 9: NEWTON MOC BAT KY =====

def bang_tsp(x, T, khung, sig=7, ten_y="y_i", d=None):
    """Bang ty sai phan / sai phan tam giac duoi T[i][k]; khung = tap (i, k) dong khung."""
    n = len(x) - 1
    rows = []
    for i in range(n + 1):
        h = [str(i), so(x[i])]
        for k in range(i + 1):
            s = sd(T[i][k], d) if d is not None else so(T[i][k], sig)
            h.append(ob(s) if (i, k) in khung else s)
        rows.append(h + [""] * (n - i))
    ten = "TSP" if d is None else "\\Delta"
    return bang(["i", "x_i", ten_y] + [f"\\text{{{ten}{k}}}" if d is None else f"\\Delta^{{{k}}}" for k in range(1, n + 1)],
                rows)


def newton_bat_ky(x, y, chieu, xbar, k, tien_to):
    n = len(x) - 1
    T = nw.bang_sai_phan(x, y)
    khung = {(i, i) for i in range(n + 1)} if chieu == "tien" else {(n, kk) for kk in range(n + 1)}
    V[tien_to + "_bang_tsp"] = bang_tsp(x, T, khung)
    R = nw.newton(x, T, chieu)
    c, z = R["c"], R["z"]
    # dang Newton
    tq = [so(c[0])]
    for kk in range(1, n + 1):
        tq.append(("-" if c[kk] < 0 else "+") + so(abs(c[kk])) +
                  "".join(f"(x-{so(zz)})" for zz in z[:kk]))
    V[tien_to + "_dang_newton"] = noi_dong(f"P_{{{n}}}(x)", tq)
    rows = []
    for kk, w in enumerate(R["bang_tich"]):
        rows.append([str(kk), "1" if kk == 0 else f"\\omega_{kk - 1}\\cdot(x-{so(z[kk - 1])})", so(c[kk], 7)]
                    + [""] * (n - kk) + [so(t) for t in w])
    rows.append(None)
    rows.append([r"P_{" + str(n) + r"}=\sum c_k\omega_k", "", ""] + [ob(so(t, 7)) for t in R["b"]])
    V[tien_to + "_bang_tich"] = bang(["k", r"\omega_k(x)", "c_k"] + cot_mu(n), rows)
    V[tien_to + "_a"] = vec_hien(R["b"], "a", moi_dong=3)
    V[tien_to + "_P"] = da_thuc(R["b"], ten=f"P_{{{n}}}(x)")
    B, r, v = bang_horner_lap(R["b"], xbar, k, sig=8)
    V[tien_to + "_horner"] = B
    V[tien_to + "_r"] = vecl(r)
    V[tien_to + "_v"] = vecl(v)
    V[tien_to + "_f"] = so(v[0])
    V[tien_to + "_fk"] = so(v[k])
    V[tien_to + "_rk"] = sn(r[k])
    V[tien_to + "_c"] = vecl(c)
    w = math.prod(abs(xbar - xi) for xi in x)
    V[tien_to + "_w"] = so(w, 6)
    V[tien_to + "_E"] = so(w / math.factorial(n + 1), 6)
    V[tien_to + "_w_tich"] = r"\cdot".join(f"|{so(xbar)}-{so(xi)}|" for xi in x)
    a_np = np.linalg.solve(np.vander(x), y)
    V[tien_to + "_kt"] = so(float(np.max(np.abs(np.polyval(R["b"], x) - np.array(y)))), 2)
    V[tien_to + "_kt2"] = so(max(abs(np.polyval(np.polyder(a_np, j) if j else a_np, xbar) - v[j]) for j in range(k + 1)), 2)


def cau8():
    newton_bat_ky([1.2, 1.5, 1.7, 1.9, 2.1, 2.4], [0.7247, 0.1415, -0.2577, -0.6466, -1.0097, -1.4748],
                  "tien", 1.8, 3, "c8")


def cau9():
    newton_bat_ky([2.2, 2.3, 2.6, 2.7, 3, 3.2], [1.617, 1.4914, 1.031, 0.8548, 0.2822, -0.1167],
                  "lui", 2.4, 4, "c9")


# ===== DU LIEU EXCEL =====

def doc_excel(ten):
    bao = []
    ox, oy, vt = nw.doc_bang_file(os.path.join(GOC, "slide_example", ten))
    x, y = nw.lam_sach(ox, oy, vt, bao)
    return [round(v, 10) for v in x], y, bao


def bang_trich_xuat(x, xbar, thu_tu):
    rows = [[str(s), str(j), so(x[j]), so(abs(xbar - x[j]))] for s, j in enumerate(thu_tu, 1)]
    return bang([r"\text{lần}", r"j\ \text{(chỉ số gốc)}", "x_j", r"|\bar x-x_j|"], rows)


# ===== CAU 11 =====

def cau11():
    x, y, bao = doc_excel("data Câu 11.xlsx")
    V["c11_bao"] = "; ".join(bao)
    V["c11_N"] = str(len(x))
    V["c11_x0"], V["c11_xn"] = so(x[0]), so(x[-1])
    h = nw.cach_deu(x)
    V["c11_h"] = so(h)
    xbar, m = 3.52, 9
    L_, R_, thu_tu = nw.trich_xuat(x, xbar, m)
    V["c11_trich"] = bang_trich_xuat(x, xbar, thu_tu)
    V["c11_L"], V["c11_R"] = str(L_), str(R_)
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    V["c11_bang_xy"] = bang(["i"] + [str(i) for i in range(m)],
                            [["x_i"] + [so(t) for t in xs], ["y_i"] + [so(t) for t in ys]])
    n = m - 1
    T = nw.bang_sai_phan(xs, ys, h)
    V["c11_bang_sp"] = bang_tsp(xs, T, {(i, i) for i in range(n + 1)}, d=7)
    R = nw.newton(xs, T, "tien", h)
    c = R["c"]
    rows = []
    for kk in range(n + 1):
        rows.append([str(kk), sd(T[kk][kk], 7), f"{kk}!", so(c[kk], 10)])
    V["c11_bang_c"] = bang(["k", r"\Delta^k y_0", "k!", r"c_k=\Delta^ky_0/k!"], rows)
    rows = []
    for kk, w in enumerate(R["bang_tich"]):
        rows.append([str(kk), "1" if kk == 0 else f"\\omega_{kk - 1}\\cdot(t-{kk - 1})", so(c[kk], 7)]
                    + [""] * (n - kk) + [so(t) for t in w])
    V["c11_bang_tich"] = bang(["k", r"\omega_k(t)", "c_k"] + cot_mu(n, "t"), rows)
    V["c11_Pt"] = da_thuc(R["b"], "t", ten=r"P_8(t)=\sum_{k=0}^8c_k\omega_k(t)")
    V["c11_Px"] = vec_hien(R["a"], "a", moi_dong=3)
    tb = (xbar - xs[0]) / h
    V["c11_t"] = so(tb)
    B, r, v = bang_horner_lap(R["b"], tb, 1, bien="t", sig=7)
    V["c11_horner"] = B
    d1 = r[1]
    V["c11_P"] = so(r[0])
    V["c11_dP"] = so(d1)
    V["c11_f"] = so(v[0])
    V["c11_df"] = so(d1 / h)
    E = math.exp(tt.log_E(0, n, tb, h))
    V["c11_E"] = so(E, 6)
    V["c11_prod"] = so(math.prod(abs(tb - i) for i in range(n + 1)), 8)
    a_np = np.linalg.solve(np.vander(np.arange(n + 1.0)), ys)
    V["c11_kt"] = so(abs(np.polyval(a_np, tb) - r[0]), 2)
    V["c11_kt2"] = so(abs(np.polyval(np.polyder(a_np), tb) / h - d1 / h), 2)
    return x, y


# ===== CAU 12 - 17: NOI SUY TRUNG TAM =====

TEN_CT = {1: "Gauss I", 2: "Gauss II", 3: "Stirling", 4: "Bessel"}


def trung_tam(x, y, ct, xbar, k, m, tien_to):
    N = len(x) - 1
    h = tt.cach_deu(x)
    trich = m < N + 1
    if trich:
        L_, R_, thu_tu = tt.trich_xuat(x, xbar, m)
        V[tien_to + "_trich"] = bang_trich_xuat(x, xbar, thu_tu)
        V[tien_to + "_L"], V[tien_to + "_R"] = str(L_), str(R_)
    else:
        L_, R_ = 0, N
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    n = m - 1
    q = tt.vi_tri_tam(n, ct)
    p = -q
    x0 = xs[q]
    tb = (xbar - x0) / h
    d = tt.so_le(ys)
    V[tien_to + "_x0"], V[tien_to + "_h"], V[tien_to + "_t"] = so(x0), so(h), so(tb)
    V[tien_to + "_p"], V[tien_to + "_pn"] = str(p), str(p + n)
    V[tien_to + "_xs"] = so(xs[0]) + r",\ " + so(xs[1]) + r",\ \dots,\ " + so(xs[-1])
    D = tt.bang_sai_phan(ys)
    c, chon = tt.he_so(D, p, ct)
    khung = {o for ds in chon for o in ds}
    rows = []
    for s in range(n + 1):
        i = p + s
        h_ = [str(i), so(xs[s])]
        for kk in range(n + 1 - s):
            v = sd(D[s][kk], d)
            h_.append(ob(v) if (i, kk) in khung else v)
        rows.append(h_ + [""] * s)
    V[tien_to + "_bang_sp"] = bang(["i", "x_i", "y_i"] + [f"\\Delta^{{{kk}}}y_i" for kk in range(1, n + 1)], rows)
    rows = []
    gt = 1
    for kk in range(n + 1):
        gt *= max(kk, 1)
        o = chon[kk]
        ten = " + ".join((f"\\Delta^{{{kk}}}y_{{{i}}}" if kk else f"y_{{{i}}}") for i, _ in o)
        gia = " + ".join(("(" + sd(D[i - p][kk], d) + ")" if j and D[i - p][kk] < 0 else sd(D[i - p][kk], d))
                         for j, (i, _) in enumerate(o))
        if len(o) == 2:
            ten = f"\\dfrac{{{ten}}}{{2\\cdot{kk}!}}" if kk > 1 else f"\\dfrac{{{ten}}}{{2}}"
            gia = f"\\dfrac{{{gia}}}{{{2 * gt}}}"
        elif kk > 1:
            ten = f"\\dfrac{{{ten}}}{{{kk}!}}"
            gia = f"\\dfrac{{{gia}}}{{{gt}}}"
        rows.append([str(kk), ten, gia, so(c[kk], 10)])
    V[tien_to + "_bang_c"] = bang(["k", r"\text{công thức}", r"\text{thay số}", r"c_k"], rows, can="rccr")
    pi, nhan = tt.bang_tich(n, ct)
    b = tt.to_hop(c, pi)
    rows = []
    for kk, pk in enumerate(pi):
        lb = nhan[kk]
        lb = re.sub(r"pi_(\d+)", r"\\pi_{\1}", lb).replace(" * ", r"\cdot ").replace("^2", "^{2}").replace("0.5", r"\tfrac12")
        rows.append([str(kk), lb, so(c[kk], 7)] + [""] * (n - kk) + [so(t) for t in pk])
    V[tien_to + "_bang_tich"] = bang(["k", r"\pi_k(t)", "c_k"] + cot_mu(n, "t"), rows)
    V[tien_to + "_Pt"] = da_thuc(b, "t", ten=f"P_{{{n}}}(t)=\\sum_{{k=0}}^{{{n}}}c_k\\pi_k(t)")
    a, _ = tt.doi_bien(b, x0, h)
    V[tien_to + "_Px"] = vec_hien(a, "a", moi_dong=3)
    B, r, v = bang_horner_lap(b, tb, k, bien="t", sig=7)
    V[tien_to + "_horner"] = B
    V[tien_to + "_P"] = so(r[0])
    V[tien_to + "_f"] = so(v[0])
    if k:
        V[tien_to + "_dP"] = so(r[1])
        V[tien_to + "_df"] = so(r[1] / h)
    V[tien_to + "_prod"] = so(math.prod(abs(tb - i) for i in range(p, p + n + 1)), 8)
    V[tien_to + "_E"] = so(math.exp(tt.log_E(p, n, tb, h)), 6)
    V[tien_to + "_n1"] = str(n + 1)
    V[tien_to + "_n"] = str(n)
    ti = np.arange(p, p + n + 1, dtype=float)
    b_np = np.linalg.solve(np.vander(ti), ys)
    V[tien_to + "_kt"] = so(float(np.max(np.abs(np.array(b) - b_np)) / np.max(np.abs(b_np))), 2)
    V[tien_to + "_kt2"] = so(abs(tt.lagrange_tai(xs, ys, xbar) - v[0]), 2)
    return v


def cau12_17(x11, y11):
    trung_tam([9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10],
              [9.4341319, 9.4307764, 9.4261142, 9.421191, 9.4170553, 9.4147476, 9.41529, 9.4196762, 9.4288617],
              1, 9.68, 0, 9, "c12")
    trung_tam([1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2],
              [2.4347052, 2.5473627, 2.6495552, 2.741261, 2.8225627, 2.8936474, 2.9548, 3.0064203, 3.0489801],
              3, 1.63, 1, 9, "c13")
    trung_tam([5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7],
              [3.9931011, 4.1278568, 4.2723258, 4.426064, 4.5885338, 4.7591118, 4.93709, 5.1216967],
              4, 5.23, 1, 8, "c14")
    v16 = trung_tam(x11, y11, 3, 7.83, 1, 9, "c16")
    v17 = trung_tam(x11, y11, 4, 7.83, 1, 8, "c17")
    V["c17_ss"] = so(abs(v16[0] - v17[0]), 2)
    V["c17_ss1"] = so(abs(v16[1] - v17[1]), 2)


# ===== CAU 19 =====

CHIEU = {1: "tăng", -1: "giảm", 0: "hằng"}


def cau19():
    x, y, bao = doc_excel("data Câu 19.xlsx")
    V["c19_bao"] = "; ".join(bao)
    V["c19_N"] = str(len(x))
    h = nsn.cach_deu(x)
    doan = nsn.khoang_don_dieu(y)
    V["c19_dd"] = bang([r"\text{đoạn}", r"[x_a,x_b]", r"\text{chỉ số}", r"y_a", r"y_b", r"\text{chiều}"],
                       [[str(r), f"[{so(x[a])};\\ {so(x[b])}]", f"{a}..{b}", so(y[a]), so(y[b]), f"\\text{{{CHIEU[s]}}}"]
                        for r, (a, b, s) in enumerate(doan, 1)])
    # a) ybar = 2.5: ham nguoc
    yb, m = 2.5, 6
    tai_moc, kh = nsn.khoang_cach_ly(y, yb)
    V["c19a_cl"] = bang(["k", "x_k", "x_{k+1}", r"g_k=y_k-\bar y", r"g_{k+1}"],
                        [[str(k), so(x[k]), so(x[k + 1]), sd(y[k] - yb, 7), sd(y[k + 1] - yb, 7)] for k in kh])
    k = kh[0]
    a_, b_, s_ = next(dd for dd in doan if dd[0] <= k < dd[1])
    V["c19a_k"], V["c19a_xk"], V["c19a_xk1"] = str(k), so(x[k]), so(x[k + 1])
    V["c19a_doan"] = f"[{so(x[a_])};\\ {so(x[b_])}]"
    hn_ = nsn.ham_nguoc(x, y, yb, k, a_, b_, m)
    V["c19a_chon"] = bang([r"\text{lần}", "j", "x_j", "y_j", r"|y_j-\bar y|"],
                          [[str(s), str(j), so(x[j]), so(y[j]), so(abs(y[j] - yb))] for s, j in enumerate(hn_["thu_tu"], 1)])
    u, vv, T = hn_["u"], hn_["v"], hn_["T"]
    r_ = len(u) - 1
    rows = []
    for s in range(r_ + 1):
        hh = [str(s), so(u[s]), so(vv[s])]
        for kk in range(1, s + 1):
            hh.append(ob(so(T[s][kk], 7)) if kk == s else so(T[s][kk], 7))
        rows.append(hh + [""] * (r_ - s))
    rows[0][2] = ob(rows[0][2])
    V["c19a_tsp"] = bang(["s", r"u_s=y", r"v_s=x"] + [f"\\text{{TSP{kk}}}" for kk in range(1, r_ + 1)], rows)
    tong, rows = 0.0, []
    for j in range(r_ + 1):
        tong += hn_["so_hang"][j]
        rows.append([str(j), so(hn_["c"][j], 10), so(hn_["omega"][j], 8), so(hn_["so_hang"][j], 8), sd(tong, 10)])
    V["c19a_tong"] = bang(["j", "c_j", r"\omega_j(\bar y)", r"c_j\,\omega_j(\bar y)", r"\text{tổng}"], rows)
    V["c19a_x"] = so(hn_["xbar"])
    V["c19a_cuoi"] = so(abs(hn_["so_hang"][-1]), 3)
    V["c19a_kt"] = so(abs(nsn.y_tai(x, y, hn_["xbar"], m) - yb), 2)
    lp = nsn.lap(x, y, yb, k, h, m, 1e-6, 100)
    V["c19a_lap"] = so(lp["xbar"])
    V["c19a_ss"] = so(abs(lp["xbar"] - hn_["xbar"]), 2)
    # b) ybar = 3.15: lap
    yb = 3.15
    tai_moc, kh = nsn.khoang_cach_ly(y, yb)
    V["c19b_cl"] = bang(["k", "x_k", "x_{k+1}", r"g_k=y_k-\bar y", r"g_{k+1}", r"\text{thuộc đoạn đơn điệu}"],
                        [[str(k), so(x[k]), so(x[k + 1]), sd(y[k] - yb, 7), sd(y[k + 1] - yb, 7),
                          "[{};\\ {}]".format(*(so(x[e]) for e in next(dd for dd in doan if dd[0] <= k < dd[1])[:2]))]
                         for k in kh])
    V["c19b_so"] = str(len(kh))
    khoi = []
    nghiem = []
    for r, k in enumerate(kh, 1):
        lp = nsn.lap(x, y, yb, k, h, m, 1e-6, 100)
        idx, D, d = lp["idx"], lp["D"], lp["d"]
        mm = lp["m"]
        rows = []
        for rr in range(mm):
            hh = [str(idx[rr]), so(x[idx[rr]])]
            for kk in range(rr + 1):
                s_ = sd(D[rr][kk], 7)
                la = (kk == rr) if lp["huong"] == "tien" else (rr == mm - 1)
                hh.append(ob(s_) if la else s_)
            rows.append(hh + [""] * (mm - 1 - rr))
        b_sp = bang(["i", "x_i", "y_i"] + [f"\\Delta^{{{kk}}}" for kk in range(1, mm)], rows)
        ten_d = "\\Delta" if lp["huong"] == "tien" else "\\nabla"
        s = lp["s"]
        rows = [[str(j), f"{ten_d}^{{{j}}}y_{{{s}}}", sd(d[j], 7), "" if j < 2 else so(lp["B"][j], 8)] for j in range(mm)]
        b_B = bang(["j", "d_j", "", r"B_j=\dfrac{d_j}{j!\,d_1}"], rows)
        t = lp["t"]
        rows = [["0", sd(t[0], 10), sd(x[s] + t[0] * h, 10), ""]]
        for j in range(1, len(t)):
            rows.append([str(j), sd(t[j], 10), sd(x[s] + t[j] * h, 10), so(h * abs(t[j] - t[j - 1]), 3)])
        rows[-1][2] = ob(rows[-1][2])
        b_it = bang(["j", "t_j", r"x_j=x_{" + str(s) + r"}+t_jh", r"h|t_j-t_{j-1}|"], rows)
        w = "t(t-1)\\cdots(t-j+1)" if lp["huong"] == "tien" else "t(t+1)\\cdots(t+j-1)"
        phi = noi_dong(r"\varphi(t)", [so(lp["A"])] + [
            ("-" if lp["B"][j] >= 0 else "+") + so(abs(lp["B"][j]), 8) +
            "".join(f"(t{'-' if lp['huong'] == 'tien' else '+'}{l})" if l else "t" for l in range(j))
            for j in range(2, mm)], toi_da=60)
        khoi.append(L(r"""
\paragraph{Nghiệm @r@: khoảng cách ly $(x_{@k@};x_{@k1@})=(@xk@;\ @xk1@)$.}
@huong_txt@, dùng $@m@$ mốc $x_{@i0@},\dots,x_{@i1@}$, $d_j=@ten_d@^jy_{@s@}$ (các ô khung):
@b_sp@
@b_B@
@phi@
\[t_0=\frac{\bar y-d_0}{d_1}=\frac{3.15-@d0@}{@d1@}=@t0@,\qquad t_{j+1}=\varphi(t_j),\ \text{dừng khi } h|t_{j+1}-t_j|<\varepsilon=10^{-6}.\]
@b_it@
Hội tụ sau $@lan@$ lần lặp; $|\varphi'(t^*)|=@q@<1$ (điều kiện hội tụ thoả). Nghiệm
$\bar x_{@r@}=x_{@s@}+t^*h=@x@$.
""", r=r, k=k, k1=k + 1, xk=so(x[k]), xk1=so(x[k + 1]), m=mm, i0=idx[0], i1=idx[-1], ten_d=ten_d, s=s,
            huong_txt=("Đủ mốc bên phải nên dùng Newton tiến xuất phát từ $x_{%d}=%s$, $t=(x-x_{%d})/h$" % (s, so(x[s]), s))
            if lp["huong"] == "tien" else
            ("Không đủ mốc bên phải nên dùng Newton lùi xuất phát từ $x_{%d}=%s$, $t=(x-x_{%d})/h$" % (s, so(x[s]), s)),
            b_sp=b_sp, b_B=b_B, phi=phi, d0=sd(d[0], 7), d1=sn(d[1], 7), t0=so(t[0]), b_it=b_it, lan=len(t) - 1,
            q=so(lp["q"], 4), x=so(lp["xbar"])))
        nghiem.append(lp["xbar"])
        V[f"c19b_kt{r}"] = so(abs(nsn.y_tai(x, y, lp["xbar"], m) - yb), 2)
        hn_ = nsn.ham_nguoc(x, y, yb, k, *next(dd for dd in doan if dd[0] <= k < dd[1])[:2], m)
        V[f"c19b_hn{r}"] = so(hn_["xbar"])
        V[f"c19b_hnss{r}"] = so(abs(hn_["xbar"] - lp["xbar"]), 2)
    V["c19b_khoi"] = "\n".join(khoi)
    V["c19b_x"] = vecl(nghiem)
    V["c19b_kt"] = ",\\ ".join(V[f"c19b_kt{r}"] for r in range(1, len(kh) + 1))


# ===== CAU 21 =====

def cau21():
    x0 = [0, 0.5236, 1.5708, 1.0472, 3.1416]
    y0 = [1, 0.866, 0, -0.866, -1]
    thu_tu = sorted(range(5), key=lambda i: x0[i])
    x = [x0[i] for i in thu_tu]
    y = [y0[i] for i in thu_tu]
    n = len(x) - 1
    h = [x[k + 1] - x[k] for k in range(n)]
    V["c21_xy"] = bang(["i"] + [str(i) for i in range(n + 1)],
                       [["x_i"] + [so(t) for t in x], ["y_i"] + [so(t) for t in y]])
    V["c21_h"] = bang(["k", r"[x_k;x_{k+1}]", "h_k", r"s_k=\frac{y_{k+1}-y_k}{h_k}"],
                      [[str(k), f"[{so(x[k])};\\ {so(x[k + 1])}]", so(h[k]), so((y[k + 1] - y[k]) / h[k], 10)]
                       for k in range(n)])

    def bang_he(he, p):
        ten = "abcd"[:p + 1]
        return bang(["k", r"[x_k;x_{k+1}]"] + [f"{t}_k" for t in ten],
                    [[str(k), f"[{so(x[k])};\\ {so(x[k + 1])}]"] + [so(v, 10) for v in he[k]] for k in range(n)])

    def ham(he, p):
        dong = []
        for k in range(n):
            dong.append(da_thuc(he[k], ten=f"S_{{{k}}}(x)").replace("\\begin{align*}\n", "").replace("\n\\end{align*}", "")
                        .replace("&= ", "&= ").replace(" \\\\\n&\\quad ", " ") + f",\\quad x\\in[{so(x[k])};\\ {so(x[k + 1])}]")
        return "\\begin{align*}\n" + " \\\\\n".join(dong) + "\n\\end{align*}"

    # a) bac 2, S'(0) = 0
    g, m_, he = sp.spline2(x, y, [(1, 0, 0.0)])
    V["c21a_m"] = bang(["k", r"\gamma_k=\frac{2(y_{k+1}-y_k)}{h_k}", r"m_{k+1}=\gamma_k-m_k"],
                       [[str(k), so(g[k], 10), f"m_{{{k + 1}}}={so(g[k])}-{sn(m_[k])}={so(m_[k + 1], 10)}"]
                        for k in range(n)], can="rrl")
    V["c21a_mv"] = vecl(m_)
    V["c21a_he"] = bang_he(he, 2)
    V["c21a_S"] = ham(he, 2)
    V["c21a_kt"] = kiem_spline(x, y, he, 2, [(1, 0, 0.0)])
    # b), c) bac 3
    for ten, dk in (("b", [(2, 0, -1.0), (2, n, 1.0)]), ("c", [(1, 0, 0.0), (1, n, 0.0)])):
        hh, s, (Lr, Dg, U, R), P, Q, sg, he = sp.spline3(x, y, dk)
        M = [[0.0] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            M[i][i] = Dg[i]
            if i:
                M[i][i - 1] = Lr[i]
            if i < n:
                M[i][i + 1] = U[i]
        V[f"c21{ten}_he_pt"] = bang([""] + [f"\\sigma_{{{j}}}" for j in range(n + 1)] + [r"\text{vế phải}"],
                                    [[f"i={i}"] + [so(v, 8) for v in M[i]] + [so(R[i], 8)] for i in range(n + 1)])
        V[f"c21{ten}_duoi"] = bang(["i", r"\ell_i", "d_i", "u_i", "r_i", "P_i", "Q_i", r"\sigma_i"],
                                   [[str(i), so(Lr[i], 7), so(Dg[i], 7), so(U[i], 7), so(R[i], 8), so(P[i], 8),
                                     so(Q[i], 8), ob(so(sg[i], 10))] for i in range(n + 1)])
        V[f"c21{ten}_sigma"] = vecl(sg)
        V[f"c21{ten}_he"] = bang_he(he, 3)
        V[f"c21{ten}_S"] = ham(he, 3)
        V[f"c21{ten}_kt"] = kiem_spline(x, y, he, 3, dk)
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(x, y, bc_type=((dk[0][0], dk[0][2]), (dk[1][0], dk[1][2])))
        V[f"c21{ten}_sc"] = so(float(np.max(np.abs(cs(x, 2) - np.array(sg)))), 2)


def kiem_spline(x, y, he, p, dk):
    n = len(x) - 1
    e0 = max(max(abs(np.polyval(he[k], x[k]) - y[k]), abs(np.polyval(he[k], x[k + 1]) - y[k + 1])) for k in range(n))
    e1 = max((abs(np.polyval(np.polyder(he[k], r), x[k + 1]) - np.polyval(np.polyder(he[k + 1], r), x[k + 1]))
              for k in range(n - 1) for r in range(1, p)), default=0.0)
    e2 = max(abs(np.polyval(np.polyder(he[0 if k == 0 else n - 1], r), x[k]) - v) for r, k, v in dk)
    return f"{so(e0, 2)}$, trơn: ${so(e1, 2)}$, biên: ${so(e2, 2)}"


# ===== CAU 23 =====

def bang_bptt(x, cot, ten_cot, khung):
    n = len(x)
    chon = list(range(5)) + [None] + list(range(n - 2, n))
    rows = []
    for i in chon:
        if i is None:
            rows.append([r"\vdots"] * (len(cot) + 2))
        else:
            rows.append([str(i + 1), so(x[i])] + [so(c[i], 7) for c in cot])
    rows.append(None)
    rows.append([r"\sum", so(sum(x), 10)] + [ob(so(float(np.sum(c)), 10)) if k else so(float(np.sum(c)), 10)
                                             for c, k in zip(cot, khung)])
    return bang(["i", "x_i"] + ten_cot, rows, co="footnotesize")


def he_chuan_tex(M, b, an):
    m = len(b)
    A = r"\begin{pmatrix}" + r"\\".join("&".join(so(M[i][j], 10) for j in range(m)) for i in range(m)) + r"\end{pmatrix}"
    X = r"\begin{pmatrix}" + r"\\".join(an) + r"\end{pmatrix}"
    B = r"\begin{pmatrix}" + r"\\".join(so(v, 10) for v in b) + r"\end{pmatrix}"
    return r"\[" + A + X + "=" + B + r"\]"


def tam_giac_tex(A, an):
    """Ma tran bo sung sau khu xuoi; duoi duong cheo ghi 0 (gia tri khu, chi con sai so lam tron)."""
    m = len(A)
    return (r"\[\left(\begin{array}{" + "r" * m + "|r}" +
            r"\\".join("&".join("0" if j < i else so(A[i][j], 10) for j in range(m + 1)) for i in range(m))
            + r"\end{array}\right)\]")


def ten_tich(u, v):
    """Ten cot tich hai ham co so (x -> x_i)."""
    if u == v:
        t = f"({u})^2" if len(u) > 1 else f"{u}^2"
    else:
        t = f"({u})({v})" if " " in u or " " in v or "/" in u or "/" in v or "^" in u or "^" in v else f"{u}{v}"
    return t.replace("x", "x_i")


def cot_bptt(cs, Phi, y, ten_y):
    """Cot bang tinh he chuan: y, phi_j, phi_j*phi_k, phi_j*y (bo cac cot co thua so la hang 1 vi trung cot khac)."""
    m = len(cs)
    co_1 = any(t == "1" for t, _ in cs)            # co ham hang: tong phi_j va tong y cung la phan tu he chuan
    cot, tc, khung = [y], [ten_y], [co_1]
    yy = ten_y.split("=")[0]
    for j in range(m):
        if cs[j][0] != "1":
            cot.append(Phi[:, j])
            tc.append(cs[j][0].replace("x", "x_i"))
            khung.append(co_1)
    for j in range(m):
        for kk in range(j, m):
            if "1" not in (cs[j][0], cs[kk][0]):
                cot.append(Phi[:, j] * Phi[:, kk])
                tc.append(ten_tich(cs[j][0], cs[kk][0]))
                khung.append(True)
    for j in range(m):
        if cs[j][0] != "1":
            cot.append(Phi[:, j] * y)
            tc.append(f"({cs[j][0]})".replace("x", "x_i") + yy)
            khung.append(True)
    return cot, tc, khung


def cau23():
    khoi = bp.tim_khoi(bp.doc_luoi(os.path.join(GOC, "slide_example", "data Câu 23.xlsx")))
    du = {}
    for ten, (nhan, ox, oy, vt) in zip("abcd", khoi):
        bao = []
        x, y = bp.lam_sach(ox, oy, vt, bao)
        du[ten] = (np.array(x), np.array(y), bao)
        V[f"c23{ten}_n"] = str(len(x))
        V[f"c23{ten}_bao"] = "; ".join(bao) if bao else "dữ liệu sạch"
    # a, b: tuyen tinh theo tham so
    for ten, cs, an in (("a", [("x", lambda t: t), ("1/x", lambda t: 1 / t)], ["a", "b"]),
                        ("b", [("x^2", lambda t: t ** 2), (r"\cos x", np.cos), ("1", np.ones_like)], ["a", "b", "c"])):
        x, y, _ = du[ten]
        Phi = np.column_stack([f(x) for _, f in cs])
        a, M, b, A, g, sigma = bp.bptt(Phi, y)
        m = len(cs)
        cot, tc, kh = cot_bptt(cs, Phi, y, "y_i")
        V[f"c23{ten}_bang"] = bang_bptt(x, cot, tc, kh)
        V[f"c23{ten}_he"] = he_chuan_tex(M, b, an)
        V[f"c23{ten}_tg"] = tam_giac_tex(A, an)
        for j, t in enumerate(an):
            V[f"c23{ten}_{t}"] = so(a[j])
        V[f"c23{ten}_sigma"] = so(sigma, 6)
        a_np = np.linalg.lstsq(Phi, y, rcond=None)[0]
        V[f"c23{ten}_kt"] = so(float(np.max(np.abs(a - a_np))), 2)
    # c: y = a e^(bx + cx^2); d: y = a x^b
    for ten, cs, an in (("c", [("1", np.ones_like), ("x", lambda t: t), ("x^2", lambda t: t ** 2)], [r"\ln a", "b", "c"]),
                        ("d", [("1", np.ones_like), (r"\ln x", np.log)], [r"\ln(-a)", "b"])):
        x, y, _ = du[ten]
        s = 1.0 if y[0] > 0 else -1.0
        Phi1 = np.column_stack([f(x) for _, f in cs])
        c, M, b, A, z, gY, sigma, sz = bp.tuyen_tinh_hoa(Phi1, y, s)
        m = len(cs)
        cot, tc, kh = cot_bptt(cs, Phi1, z, r"z_i=\ln(" + ("" if s > 0 else "-") + "y_i)")
        cot, tc, kh = [y] + cot, ["y_i"] + tc, [False] + kh
        V[f"c23{ten}_bang"] = bang_bptt(x, cot, tc, kh)
        V[f"c23{ten}_he"] = he_chuan_tex(M, b, an)
        V[f"c23{ten}_tg"] = tam_giac_tex(A, an)
        V[f"c23{ten}_c"] = vecl(c)
        V[f"c23{ten}_a"] = so(s * math.exp(c[0]))
        V[f"c23{ten}_b"] = so(c[1])
        if m > 2:
            V[f"c23{ten}_cc"] = so(c[2])
        V[f"c23{ten}_sigma"] = so(sigma, 6)
        V[f"c23{ten}_sz"] = so(sz, 6)
        c2, lan, ok = bp.gauss_newton(Phi1, y, s)
        rows = [[str(j)] + [so(v, 10) for v in cc] + [so(sg, 6)] for j, cc, sg in lan]
        rows[-1] = rows[-1][:1] + [ob(v) for v in rows[-1][1:]]
        V[f"c23{ten}_gn"] = bang(["j"] + an + [r"\sigma"], rows)
        V[f"c23{ten}_gn_lan"] = str(len(lan) - 1)
        V[f"c23{ten}_a2"] = so(s * math.exp(c2[0]))
        V[f"c23{ten}_b2"] = so(c2[1])
        if m > 2:
            V[f"c23{ten}_cc2"] = so(c2[2])
        V[f"c23{ten}_sigma2"] = so(lan[-1][2], 6)
        V[f"c23{ten}_kt"] = so(float(np.max(np.abs(c - np.linalg.lstsq(Phi1, z, rcond=None)[0]))), 2)
        from scipy.optimize import curve_fit
        f = lambda xx, *cc: s * np.exp(np.column_stack([fn(np.asarray(xx, dtype=float)) for _, fn in cs]) @ np.array(cc))
        c_sp = curve_fit(f, x, y, p0=lan[0][1])[0]
        V[f"c23{ten}_kt2"] = so(float(np.max(np.abs(c2 - c_sp))), 2)


# ===== GHEP =====

def main():
    sys.stdout.reconfigure(errors="backslashreplace")
    cau3()
    cau4()
    cau5()
    cau7()
    cau8()
    cau9()
    x11, y11 = cau11()
    cau12_17(x11, y11)
    cau19()
    cau21()
    cau23()
    mau = open(os.path.join(THU_MUC, "mau_loi_giai.tex"), encoding="utf-8").read()
    dung = set()

    def thay(m):
        k = m.group(1)
        if k not in V:
            sys.exit(f"Loi: mau can khoa <<{k}>> nhung chua sinh.")
        dung.add(k)
        return V[k]

    out = re.sub(r"<<([A-Za-z0-9_]+)>>", thay, mau)
    thua = sorted(set(V) - dung)
    if thua:
        print("Canh bao: khoa sinh ra nhung khong dung:", ", ".join(thua))
    dich = os.path.join(THU_MUC, "loi_giai_bai_tap.tex")
    with open(dich, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"Da ghi {dich} ({len(dung)} khoa).")


if __name__ == "__main__":
    main()
