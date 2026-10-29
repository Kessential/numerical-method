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
RONG = 480.0                 # be ngang toi da (pt) cua 1 dong cong thuc hien thi (le trang 493pt)
RONG_KL = 466.0              # ... trong khung Ket luan (481pt)


# ===== DINH DANG =====

def so(v):
    """So tinh ra -> LaTeX: toi da 6 chu so thap phan; |v| < 1e-4 viet a.bcdefg*10^k (6 chu so sau dau phay)."""
    v = float(v)
    if abs(v) < 1e-12:
        return "0"
    if abs(v) < 1e-4 or abs(v) >= 1e9:
        m, e = f"{v:.6e}".split("e")
        m = m.rstrip("0").rstrip(".")
        return f"{m}\\cdot10^{{{int(e)}}}"
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def se(v):
    """Can sai so (co the rat nho): nhu so() nhung khong bao gio lam tron ve 0."""
    v = float(v)
    if v == 0 or 1e-4 <= abs(v) < 1e9:
        return so(v)
    m, e = f"{v:.6e}".split("e")
    m = m.rstrip("0").rstrip(".")
    return f"{m}\\cdot10^{{{int(e)}}}"


def dmu(k, ky="\\Delta"):
    """Delta^k (k = 1 viet Delta)."""
    return ky + " " if k == 1 else f"{ky}^{{{k}}}"


def sl(v):
    """So lieu de cho: giu nguyen chu so."""
    s = f"{float(v):.10g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m}\\cdot10^{{{int(e)}}}"
    return s


def sd(v, d):
    """So co dinh d chu so thap phan (sai phan cua du lieu d chu so: dung tuyet doi)."""
    s = f"{round(v, d):.{d}f}"
    return "0." + "0" * d if re.fullmatch(r"-0\.0*", s) else s


def sn(v):
    """So trong bieu thuc: so am dat trong ngoac."""
    s = so(v)
    return f"({s})" if s.startswith("-") else s


def ob(s):
    return r"\ob{" + s + "}"


def vecl(v):
    return r"\left(" + r";\ ".join(so(t) for t in v) + r"\right)"


def boc(c):
    if c is None or c == "":
        return ""
    c = str(c)
    if c.startswith("\\ob") or "$" in c or c.startswith("\\multicolumn"):
        return c
    return "$" + c + "$"


def bang(dau, hang, can=None, co="small", cao=None, nhom=None):
    """Bang LaTeX co gian theo be ngang trang. hang: list (None = ke ngang); o \\multicolumn{k} tinh k cot;
    cao: khoang them duoi moi hang (vd "5pt" cho o co phan so); nhom = (a, b, nhan): tieu de chung cot a..b."""
    n = len(dau)
    can = can or ("r" * n)
    het = r" \\" if cao is None else r" \\[" + cao + "]"
    out = [r"\begin{center}", "{\\" + co, r"\begin{adjustbox}{max width=\linewidth}",
           r"\begin{tabular}{" + can + "}", r"\toprule"]
    if nhom:
        a, b, nhan = nhom
        out += ["& " * (a - 1) + r"\multicolumn{%d}{c}{%s}" % (b - a + 1, nhan) + " &" * (n - b) + r" \\",
                r"\cmidrule(lr){%d-%d}" % (a, b)]
    out += [" & ".join(boc(c) for c in dau) + r" \\", r"\midrule"]
    for h in hang:
        if h is None:
            out.append(r"\midrule")
            continue
        rong_h = sum(int(re.match(r"\\multicolumn\{(\d+)\}", str(c)).group(1)) if str(c).startswith("\\multicolumn")
                     else 1 for c in h)
        h = list(h) + [""] * (n - rong_h)
        out.append(" & ".join(boc(c) for c in h) + het)
    out += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}}", r"\end{center}"]
    return "\n".join(out)


def mu(e, bien="x"):
    return f"{bien}^{{{e}}}" if e > 1 else (bien if e == 1 else "1")


def cot_mu(n, bien="x"):
    return [mu(e, bien) for e in range(n, -1, -1)]


# --- cong thuc hien thi: 1 dong neu vua, khong thi it dong nhat va chia deu ---

LENH = {"cdot": 7.9, "quad": 11.0, "qquad": 22.0, ",": 1.8, ";": 3.1, " ": 3.7, "!": -1.8, "left": 0.0,
        "right": 0.0, "big": 0.5, "bigl": 0.5, "bigr": 0.5, "Big": 0.8, "biggl": 2.5, "biggr": 2.5, "dots": 13.0, "cdots": 13.0, "pi": 6.3, "omega": 7.2,
        "sigma": 6.3, "varphi": 6.6, "tfrac": 0.0, "dfrac": 0.0, "frac": 0.0, "text": 0.0, "sum": 12.0}
KT = {".": 3.1, ",": 3.1, ";": 3.1, ":": 3.1, "(": 4.3, ")": 4.3, "[": 3.1, "]": 3.1, "|": 3.1,
      "+": 13.4, "-": 13.4, "=": 14.7, " ": 0.0, "'": 3.0, "!": 3.1}


def dong_ngoac(t, i):
    sau = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            sau += 1
        elif t[j] == "}":
            sau -= 1
            if sau == 0:
                return j
    return len(t) - 1


def rong(t, k=1.0):
    """Uoc luong be ngang (pt) cua doan LaTeX toan hoc (Computer Modern 11pt); chi so tren/duoi x0.7."""
    w, i, truoc = 0.0, 0, ""
    while i < len(t):
        ch = t[i]
        if ch == "\\":
            m = re.match(r"\\([a-zA-Z]+|.)", t[i:])
            j = i + len(m.group(0))
            if m.group(1) in ("frac", "dfrac", "tfrac") and t[j:j + 1] == "{":   # phan so: rong = max(tu, mau)
                j1 = dong_ngoac(t, j)
                j2 = dong_ngoac(t, j1 + 1)
                kp = k * (0.7 if m.group(1) == "tfrac" else 1.0)
                w += max(rong(t[j + 1:j1], kp), rong(t[j1 + 2:j2], kp)) + 2.4 * k
                i, truoc = j2 + 1, ")"
                continue
            w += k * LENH.get(m.group(1), 7.0)
            i = j
            if m.group(1) in ("bigl", "biggl", "left"):
                truoc = "("
        elif ch in "+-" and truoc in ("", "(", ";", "{", "=", "[", ","):
            w += k * 8.6                               # dau mot ngoi (sau mo ngoac, dau ;, dau =)
            truoc = ch
            i += 1
        elif ch in "^_":
            i += 1
            if i < len(t) and t[i] == "{":
                j = dong_ngoac(t, i)
                w += rong(t[i + 1:j], k * 0.7)
                i = j + 1
            elif i < len(t):
                w += rong(t[i], k * 0.7)
                i += 1
        elif ch in "{}":
            i += 1
        else:
            w += k * KT.get(ch, 6.0 if ch.isalpha() else 5.5)
            if ch != " ":
                truoc = ch
            i += 1
    return w


def chia(ws, con):
    """Chia day so hang (do rong ws) thanh it dong nhat, moi dong <= con, can bang (cuc tieu dong dai nhat)."""
    n = len(ws)
    pre = [0.0]
    for w in ws:
        pre.append(pre[-1] + w)
    for L_ in range(1, n + 1):
        dp = [[(math.inf, -1)] * (n + 1) for _ in range(L_ + 1)]
        dp[0][0] = (0.0, -1)
        for l in range(1, L_ + 1):
            for i in range(1, n + 1):
                for j in range(l - 1, i):
                    m = max(dp[l - 1][j][0], pre[i] - pre[j])
                    if m < dp[l][i][0]:
                        dp[l][i] = (m, j)
        if dp[L_][n][0] <= con:
            cat, i = [], n
            for l in range(L_, 0, -1):
                j = dp[l][i][1]
                cat.append((j, i))
                i = j
            return cat[::-1]
    return [(i, i + 1) for i in range(n)]


def hien(ten, so_hang, rong_max=RONG, mo="", dong=""):
    """'ten = so_hang...' dang hien thi: 1 dong neu vua be ngang, khong thi align* it dong nhat, chia deu."""
    w0 = rong(ten) + 14.7 + rong(mo) + rong(dong)
    ws = [rong(s) + 0.5 for s in so_hang]
    if w0 + sum(ws) <= rong_max:
        return r"\[ " + ten + " = " + mo + " ".join(so_hang) + dong + r" \]"
    nhom = chia(ws, rong_max - w0 - 11.0)
    dong_tex = [" ".join(so_hang[a:b]) for a, b in nhom]
    dong_tex[0] = mo + dong_tex[0]
    dong_tex[-1] = dong_tex[-1] + dong
    return "\\begin{align*}\n" + ten + " &= " + " \\\\\n&\\quad ".join(dong_tex) + "\n\\end{align*}"


def hang_tu(he, bien="x"):
    """Cac so hang cua da thuc (he so bac cao -> thap), so hang dau khong co dau +."""
    n = len(he) - 1
    out = []
    for i, a in enumerate(he):
        if abs(a) < 1e-12:
            continue
        e = n - i
        s = so(abs(a))
        if e == 0:
            t = s
        elif s == "1":
            t = mu(e, bien)
        else:
            t = s + ("\\," if "cdot" in s else "") + mu(e, bien)
        out.append(("-" if a < 0 else "") + t if not out else ("- " if a < 0 else "+ ") + t)
    return out or ["0"]


def da_thuc(he, bien="x", ten="P(x)", rong_max=RONG):
    return hien(ten, hang_tu(he, bien), rong_max)


def muc_vec(phan):
    """Cac thanh phan vector (da la LaTeX) -> so hang cho hien(): ngan cach '; '."""
    return [p + r";\ " for p in phan[:-1]] + [phan[-1]]


def vec_hien(v, ten, rong_max=RONG):
    return hien(ten, muc_vec([so(t) for t in v]), rong_max, mo=r"\bigl(", dong=r"\bigr)")


def hien_nhieu(muc, rong_max=RONG):
    """Nhieu dang thuc (ten, so_hang, mo, dong) trong 1 align*, thang dau '='; dang thuc dai thi chia dong."""
    wt = max(rong(m[0]) for m in muc) + 14.7
    out = []
    for ten, so_hang, mo, dg in muc:
        ws = [rong(s) + 0.5 for s in so_hang]
        w_mo = rong(mo) + rong(dg)
        nhom = [(0, len(so_hang))] if wt + w_mo + sum(ws) <= rong_max else chia(ws, rong_max - wt - w_mo - 11.0)
        ds = [" ".join(so_hang[a:b]) for a, b in nhom]
        ds[0] = mo + ds[0]
        ds[-1] = ds[-1] + dg
        out.append(ten + " &= " + " \\\\\n&\\quad ".join(ds))
    return "\\begin{align*}\n" + " \\\\\n".join(out) + "\n\\end{align*}"


def vec_ct(ten, chi, ct, gia):
    """2 dong cho hien_nhieu: ten = (c_chi) = (cong thuc tung thanh phan) = (gia tri)."""
    ds = ",".join(f"c_{{{k}}}" for k in chi) if len(chi) <= 5 else f"c_{{{chi[0]}}},\\dots,c_{{{chi[-1]}}}"
    lon = "bigg" if any("frac" in s for s in ct) else "big"   # ngoac cao theo phan so
    return [(ten, muc_vec(ct), "(" + ds + rf")=\{lon}l(", rf"\{lon}r)"),
            ("", muc_vec([so(v) for v in gia]), r"\bigl(", r"\bigr)")]


def L(_mau, **kw):
    """Thay @khoa@ trong doan LaTeX (tranh phai nhan doi ngoac nhon)."""
    for k, v in kw.items():
        _mau = _mau.replace("@" + k + "@", str(v))
    return _mau


def tong_hang(nhan, k, gia):
    """Hang tong cuoi bang: nhan gop k cot dau, sau do cac o gia (dong khung)."""
    return [r"\multicolumn{" + str(k) + r"}{l}{$" + nhan + "$}"] + [ob(so(t)) for t in gia]


def bang_horner_lap(a, c, k, bien="x"):
    """Bang Horner chia lap tai c (muc 2, horner.md), o r_j dong khung. Tra ve (bang, r, v)."""
    n = len(a) - 1
    r, v, hang = nw.horner_dao_ham(list(a), c, k)
    rows = [[r"\text{Hệ số}"] + [so(t) for t in a]]
    for j, sau in enumerate(hang):
        tich = [""] + [so(c * sau[l - 1]) for l in range(1, len(sau))]
        rows.append([f"c={so(c)}"] + tich)
        rows.append([f"j={j}"] + [so(t) for t in sau[:-1]] + [ob(so(sau[-1]))])
        rows.append(None)
    rows.pop()
    return bang([""] + cot_mu(n, bien), rows), r, v


# ===== CAU 3 =====

def cau3():
    for n, a, b, ten in ((9, -1.0, 1.0, "a"), (12, 3.0, 6.0, "b")):
        t, x, W = mt.moc_toi_uu(n, a, b, verbose=False)
        p, q = (a + b) / 2, (b - a) / 2
        V[f"c3_bang_{ten}"] = bang(["i", r"t_i=-\cos\dfrac{(2i+1)\pi}{2n}", r"x_i=p+q\,t_i"],
                                   [[str(i), so(t[i]), so(x[i])] for i in range(n)])
        V[f"c3_p_{ten}"], V[f"c3_q_{ten}"] = so(p), so(q)
        V[f"c3_W_{ten}"] = so(W)
        V[f"c3_E_{ten}"] = se(W / math.factorial(n))
        V[f"c3_x_{ten}"] = vec_hien(x, "x")
        # kiem tra voi chebroots
        tc = np.sort(np.polynomial.chebyshev.chebroots([0] * n + [1]))
        V[f"c3_kt_{ten}"] = so(float(np.max(np.abs(np.array(t) - tc))))


# ===== CAU 4, 5 =====

def cau4():
    a = [3.0, 0.0, -2.0, -1.0]
    ten_dh = ["P", "P'", "P''", "P'''"]
    for c, ten in ((0.0, "0"), (2.15, "1")):
        B, r, v = bang_horner_lap(a, c, 3)
        V[f"c4_bang_{ten}"] = B
        Q = nw.horner_dao_ham(list(a), c, 0)[2][0][:-1]
        V[f"c4_P_{ten}"] = so(r[0])
        V[f"c4_Q_{ten}"] = da_thuc(Q, ten=r"Q_2(x)")
        V[f"c4_Qv_{ten}"] = vecl(Q)
        V[f"c4_r_{ten}"] = vecl(r)
        V[f"c4_v_{ten}"] = vecl(v)
        V[f"c4_dh_{ten}"] = (r"\[ P^{(j)}(c)=j!\,r_j:\qquad " +
                             r",\quad ".join(f"{t}({sl(c)})={so(v[j])}" for j, t in enumerate(ten_dh)) + r". \]")
        # kiem tra numpy
        V[f"c4_kt_{ten}"] = so(max(abs(np.polyval(np.polyder(a, j) if j else a, c) - v[j]) for j in range(4)))


def cau5():
    xs = [2, 2.4, 2.7, 3, 3.1, 3.4]
    m = len(xs)
    p = [1.0]
    rows = [[""] + [""] * m + ["1"]]
    for i, z in enumerate(xs):
        p = nw.horner_nhan(p, z)
        hang = [so(t) for t in p]
        if i == m - 1:
            hang = [ob(t) for t in hang]
        rows.append([sl(z)] + [""] * (m - i - 1) + hang)
    V["c5_bang"] = bang(["x_k"] + cot_mu(m), rows)
    V["c5_p"] = vecl(p)
    V["c5_w"] = da_thuc(p, ten="w_6(x)", rong_max=RONG_KL)
    V["c5_kt"] = so(float(np.max(np.abs(np.array(p) - np.poly(xs)))))


# ===== CAU 7 =====

def cau7():
    x = [1.2, 1.5, 1.7, 1.8, 2.1, 2.3]
    y = [0.892, 1.179, 1.358, 1.445, 1.688, 1.839]
    n = len(x) - 1
    a, D, bang_t, bang_c = lg.lagrange(x, y)
    rows = [[""] + [""] * (n + 1) + ["1"]]
    for i, p in enumerate(bang_t):
        rows.append([sl(x[i])] + [""] * (n - i) + [so(t) for t in p])
    V["c7_bang_tich"] = bang(["x_i"] + cot_mu(n + 1), rows)
    V["c7_bang_D"] = bang(["i", "x_i", "y_i", "D_i", "y_i/D_i"],
                          [[str(i), sl(x[i]), sl(y[i]), so(D[i]), so(y[i] / D[i])] for i in range(n + 1)])
    rows = []
    for i, (q, du) in enumerate(bang_c):
        du = 0.0 if abs(du) < 1e-9 * max(1.0, max(abs(t) for t in bang_t[-1])) else du   # du = 0 (sai so lam tron)
        rows.append([str(i), sl(x[i]), so(y[i] / D[i])] + [so(t) for t in q] + [so(du)])
    rows.append(None)
    rows.append(tong_hang(r"\sum_i\frac{y_i}{D_i}\,q^{(i)}", 3, a) + [""])
    V["c7_bang_chia"] = bang(["i", "x_i", "y_i/D_i"] + cot_mu(n) + [r"\text{dư}"], rows)
    V["c7_a"] = vec_hien(a, "a", RONG_KL)
    V["c7_P"] = da_thuc(a, ten="P_5(x)", rong_max=RONG_KL)
    V["c7_kt"] = so(float(np.max(np.abs(np.polyval(a, x) - np.array(y)))))
    V["c7_kt2"] = so(float(np.max(np.abs(np.array(a) - np.linalg.solve(np.vander(x), y))) / np.max(np.abs(a))))


# ===== CAU 8, 9: NEWTON MOC BAT KY =====

def bang_tsp(x, T, khung, ten_y="y_i", d=None):
    """Bang ty sai phan / sai phan tam giac duoi T[i][k]; khung = tap (i, k) dong khung."""
    n = len(x) - 1
    rows = []
    for i in range(n + 1):
        h = [str(i), sl(x[i])]
        for k in range(i + 1):
            s = sd(T[i][k], d) if d is not None else (sl(T[i][k]) if k == 0 else so(T[i][k]))
            h.append(ob(s) if (i, k) in khung else s)
        rows.append(h + [""] * (n - i))
    return bang(["i", "x_i", ten_y] + [f"\\text{{TSP{k}}}" if d is None else f"\\Delta^{{{k}}}" for k in range(1, n + 1)],
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
        tq.append(("- " if c[kk] < 0 else "+ ") + so(abs(c[kk])) + "".join(f"(x-{sl(zz)})" for zz in z[:kk]))
    V[tien_to + "_dang_newton"] = hien(f"P_{{{n}}}(x)", tq)
    ct = []                                        # c_k = f[x_0..x_k] (tien) / f[x_{n-k}..x_n] (lui)
    for kk in range(n + 1):
        a_, b_ = (0, kk) if chieu == "tien" else (n - kk, n)
        ct.append(f"y_{{{a_}}}" if kk == 0 else f"f[x_{{{a_}}},x_{{{b_}}}]" if kk == 1
                  else f"f[x_{{{a_}}},\\dots,x_{{{b_}}}]")
    V[tien_to + "_C"] = hien_nhieu(vec_ct("C", list(range(n + 1)), ct, c))
    rows = [[str(kk), "" if kk == 0 else sl(z[kk - 1])] + [""] * (n - kk) + [so(t) for t in w]
            for kk, w in enumerate(R["bang_tich"])]
    nut = "x_{k-1}" if chieu == "tien" else f"x_{{{n + 1}-k}}"
    V[tien_to + "_bang_tich"] = bang(["k", nut] + cot_mu(n), rows,
                                     nhom=(3, n + 3, r"ma trận $A$ (hàng $k$: hệ số của $\omega_k(x)$)"))
    V[tien_to + "_CA"] = vec_hien(R["b"], r"a=C\cdot A")
    V[tien_to + "_a"] = vec_hien(R["b"], "a", RONG_KL)
    V[tien_to + "_P"] = da_thuc(R["b"], ten=f"P_{{{n}}}(x)", rong_max=RONG_KL)
    r, v, _ = nw.horner_dao_ham(list(R["b"]), xbar, k)          # Horner chia lap (Cau 4c), khong in bang
    V[tien_to + "_f"] = so(v[0])
    V[tien_to + "_rk"] = sn(r[k])
    V[tien_to + "_fk"] = so(v[k])
    a_np = np.linalg.solve(np.vander(x), y)
    V[tien_to + "_kt"] = so(float(np.max(np.abs(np.polyval(R["b"], x) - np.array(y)))))
    V[tien_to + "_kt2"] = so(max(abs(np.polyval(np.polyder(a_np, j) if j else a_np, xbar) - v[j]) for j in range(k + 1)))


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
    """Bang qua trinh trich xuat (Cau 11a): moc tam = moc dau tien, dem so moc trai / phai sau moi lan ket nap.
    Tra ve (bang, cau ket luan)."""
    tam = thu_tu[0]
    rows, trai, phai = [], 0, 0
    for s, j in enumerate(thu_tu, 1):
        trai, phai = trai + (j < tam), phai + (j > tam)
        phia = "tâm" if j == tam else ("trái" if j < tam else "phải")
        rows.append([str(s), str(j), sl(x[j]), so(abs(xbar - x[j])), rf"\text{{{phia}}}", str(trai), str(phai)])
    L_, R_ = min(thu_tu), max(thu_tu)

    def ben(so_moc, a, b, ten):
        if so_moc == 0:
            return f"không có mốc {ten}"
        ds = f"x_{{{a}}}" if a == b else f"x_{{{a}}},\\dots,x_{{{b}}}"
        return f"${so_moc}$ mốc {ten} (${ds}$)"

    cau = (f"Mốc tâm (gần $\\bar x$ nhất) là $x_{{{tam}}}={sl(x[tam])}$; {ben(trai, L_, tam - 1, 'trái')}, "
           f"{ben(phai, tam + 1, R_, 'phải')} $\\Rightarrow L={L_}$, $R={R_}$.")
    return bang([r"\text{lần}", r"j\ \text{(chỉ số gốc)}", "x_j", r"|\bar x-x_j|", r"\text{phía}",
                 r"\text{số mốc trái}", r"\text{số mốc phải}"], rows), cau


# ===== CAU 11 =====

def cau11():
    x, y, bao = doc_excel("data Câu 11.xlsx")
    V["c11_N"] = str(len(x))
    V["c11_x0"], V["c11_xn"] = sl(x[0]), sl(x[-1])
    h = nw.cach_deu(x)
    V["c11_h"] = sl(h)
    xbar, m = 3.52, 9
    L_, R_, thu_tu = nw.trich_xuat(x, xbar, m)
    V["c11_trich"], V["c11_ket_trich"] = bang_trich_xuat(x, xbar, thu_tu)
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    V["c11_bang_xy"] = bang(["i"] + [str(i) for i in range(m)],
                            [["x_i"] + [sl(t) for t in xs], ["y_i"] + [sl(t) for t in ys]])
    n = m - 1
    T = nw.bang_sai_phan(xs, ys, h)
    V["c11_bang_sp"] = bang_tsp(xs, T, {(i, i) for i in range(n + 1)}, d=7)
    R = nw.newton(xs, T, "tien", h)
    c = R["c"]
    ct = ["y_0", r"\Delta y_0"] + [f"\\dfrac{{\\Delta^{{{kk}}}y_0}}{{{kk}!}}" for kk in range(2, n + 1)]
    V["c11_C"] = hien_nhieu(vec_ct("C", list(range(n + 1)), ct, c))
    rows = [[str(kk), "" if kk == 0 else str(kk - 1)] + [""] * (n - kk) + [so(t) for t in w]
            for kk, w in enumerate(R["bang_tich"])]
    V["c11_bang_tich"] = bang(["k", "z_{k-1}"] + cot_mu(n, "t"), rows,
                              nhom=(3, n + 3, r"ma trận $A$ (hàng $k$: hệ số của $\omega_k(t)$)"))
    V["c11_Pt"] = da_thuc(R["b"], "t", ten=r"P_8(t)")
    tb = (xbar - xs[0]) / h
    V["c11_t"] = so(tb)
    r, v, _ = nw.horner_dao_ham(list(R["b"]), tb, 1)          # Horner chia lap tai t (Cau 4c), khong in bang
    V["c11_f"] = so(v[0])
    V["c11_dP"] = so(r[1])
    V["c11_df"] = so(r[1] / h)
    a_np = np.linalg.solve(np.vander(np.arange(n + 1.0)), ys)
    V["c11_kt"] = so(abs(np.polyval(a_np, tb) - r[0]))
    V["c11_kt2"] = so(abs(np.polyval(np.polyder(a_np), tb) / h - r[1] / h))
    return x, y


# ===== CAU 12 - 17: NOI SUY TRUNG TAM =====

def trung_tam(x, y, ct, xbar, k, m, tien_to):
    """ct: 1 Gauss I, 2 Gauss II (bang tich theo t, nut z); 3 Stirling, 4 Bessel (theo file Excel: tach le / chan,
    bang tich theo u = t^2 hoac u = (t - 1/2)^2)."""
    N = len(x) - 1
    h = tt.cach_deu(x)
    if m < N + 1:
        L_, R_, thu_tu = tt.trich_xuat(x, xbar, m)
        V[tien_to + "_trich"], V[tien_to + "_ket_trich"] = bang_trich_xuat(x, xbar, thu_tu)
    else:
        L_, R_ = 0, N
    xs, ys = x[L_:R_ + 1], y[L_:R_ + 1]
    n = m - 1
    q = tt.vi_tri_tam(n, ct)
    p = -q
    x0 = xs[q]
    tb = (xbar - x0) / h
    d = tt.so_le(ys)
    V[tien_to + "_x0"], V[tien_to + "_t"] = sl(x0), so(tb)
    V[tien_to + "_p"], V[tien_to + "_pn"] = str(p), str(p + n)
    if m < N + 1:
        V[tien_to + "_xs"] = sl(xs[0]) + r",\ " + sl(xs[1]) + r",\ \dots,\ " + sl(xs[-1])
    D = tt.bang_sai_phan(ys)
    c, chon = tt.he_so(D, p, ct)
    khung = {o for ds in chon for o in ds}
    rows = []
    for s in range(n + 1):
        i = p + s
        h_ = [str(i), sl(xs[s])]
        for kk in range(n + 1 - s):
            v = sd(D[s][kk], d)
            h_.append(ob(v) if (i, kk) in khung else v)
        rows.append(h_ + [""] * s)
    V[tien_to + "_bang_sp"] = bang(["i", "x_i", "y_i"] + [dmu(kk) + "y_i" for kk in range(1, n + 1)], rows)
    ctk = []                                       # cong thuc c_k theo cac o khung
    for kk in range(n + 1):
        o = chon[kk]
        ten = " + ".join((dmu(kk) + f"y_{{{i}}}" if kk else f"y_{{{i}}}") for i, _ in o)
        if len(o) == 2:
            ten = f"\\dfrac{{{ten}}}{{2\\cdot{kk}!}}" if kk > 1 else f"\\dfrac{{{ten}}}{{2}}"
        elif kk > 1:
            ten = f"\\dfrac{{{ten}}}{{{kk}!}}"
        ctk.append(ten)
    P = tt.lap_P(c, n, ct)                         # muc 3, trung_tam.md (Stirling/Bessel: tach le / chan)
    b, bien, lech = P["b"], P["bien"], P["lech"]
    s0, diem = x0 + lech * h, tb - lech
    if ct in (1, 2):
        V[tien_to + "_C"] = hien_nhieu(vec_ct("C", list(range(n + 1)), ctk, c))
        z = P["z"]
        rows = [[str(kk), "" if kk == 0 else sl(z[kk - 1])] + [""] * (n - kk) + [so(t) for t in P["pi"][kk]]
                for kk in range(n + 1)]
        V[tien_to + "_bang_tich"] = bang(["k", "z_{k-1}"] + cot_mu(n, "t"), rows,
                                         nhom=(3, n + 3, r"ma trận $A$ (hàng $k$: hệ số của $\pi_k(t)$)"))
    else:
        s = len(P["cl"])
        chan = list(range(2, 2 * s + 1, 2)) if ct == 3 else list(range(0, 2 * s - 1, 2))
        le = list(range(1, 2 * s, 2))
        muc = [("c_0", ["y_0=" + sl(c[0])], "", "")] if ct == 3 else []
        for ten_, ds in ((r"C_{\text{chẵn}}", chan), (r"C_{\text{lẻ}}", le)):
            muc += vec_ct(ten_, ds, [ctk[i] for i in ds], [c[i] for i in ds])
        V[tien_to + "_C"] = hien_nhieu(muc)
        rows = [[str(j), "" if j == 0 else so(P["zeta"][j - 1])] + [""] * (s - 1 - j) + [so(t) for t in P["Pi"][j]]
                for j in range(s)]
        V[tien_to + "_bang_tich"] = bang(["j", "j^2" if ct == 3 else r"(j-\tfrac12)^2"] + cot_mu(s - 1, "u"), rows,
                                         nhom=(3, s + 2, r"ma trận $A$ (hàng $j$: hệ số của $\Pi_j(u)$)"))
        V[tien_to + "_CA"] = hien_nhieu([(r"P_{\text{chẵn}}=C_{\text{chẵn}}\cdot A", muc_vec([so(t) for t in P["Pc"]]),
                                          r"\bigl(", r"\bigr)"),
                                         (r"P_{\text{lẻ}}=C_{\text{lẻ}}\cdot A", muc_vec([so(t) for t in P["Pl"]]),
                                          r"\bigl(", r"\bigr)")])
    # kiem tra: P(w_i) = y_i, w_i = i - lech
    wi = np.arange(p, p + n + 1, dtype=float) - lech
    V[tien_to + "_kt3"] = so(float(np.max(np.abs(np.polyval(b, wi) - np.array(ys)))))
    V[tien_to + "_Pt"] = da_thuc(b, bien, ten=f"P_{{{n}}}({bien})")
    if ct == 4:
        V[tien_to + "_s0"] = sl(round(s0, 10))
        V[tien_to + "_v"] = so(diem)
    r, v, _ = nw.horner_dao_ham(list(b), diem, k)    # Horner chia lap (Cau 4c), khong in bang
    V[tien_to + "_f"] = so(v[0])
    if k:
        V[tien_to + "_dP"] = so(r[1])
        V[tien_to + "_df"] = so(r[1] / h)
    ti = np.arange(p, p + n + 1, dtype=float)
    a_t = np.linalg.solve(np.vander(ti), ys)
    V[tien_to + "_kt"] = so(abs(tt.lagrange_tai(xs, ys, xbar) - v[0]))
    if k:
        V[tien_to + "_kt2"] = so(abs(np.polyval(np.polyder(a_t), tb) / h - r[1] / h))
    return v[0], (r[1] / h if k else None)


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
    V["c17_ss"] = so(abs(v16[0] - v17[0]))
    V["c17_ss1"] = so(abs(v16[1] - v17[1]))


# ===== CAU 19 =====

CHIEU = {1: "tăng", -1: "giảm", 0: "hằng"}


def cau19():
    x, y, bao = doc_excel("data Câu 19.xlsx")
    V["c19_N"] = str(len(x))
    h = nsn.cach_deu(x)
    doan = nsn.khoang_don_dieu(y)
    V["c19_dd"] = bang([r"\text{đoạn}", r"[x_a,x_b]", r"\text{chỉ số}", r"y_a", r"y_b", r"\text{chiều}"],
                       [[str(r), f"[{sl(x[a])};\\ {sl(x[b])}]", f"{a}..{b}", sl(y[a]), sl(y[b]), f"\\text{{{CHIEU[s]}}}"]
                        for r, (a, b, s) in enumerate(doan, 1)])
    # a) ybar = 2.5: ham nguoc
    yb, m = 2.5, 6
    tai_moc, kh = nsn.khoang_cach_ly(y, yb)
    V["c19a_cl"] = bang(["k", "x_k", "x_{k+1}", r"g_k=y_k-\bar y", r"g_{k+1}"],
                        [[str(k), sl(x[k]), sl(x[k + 1]), sd(y[k] - yb, 7), sd(y[k + 1] - yb, 7)] for k in kh])
    k = kh[0]
    a_, b_, s_ = next(dd for dd in doan if dd[0] <= k < dd[1])
    V["c19a_k"], V["c19a_xk"], V["c19a_xk1"] = str(k), sl(x[k]), sl(x[k + 1])
    V["c19a_doan"] = f"[{sl(x[a_])};\\ {sl(x[b_])}]"
    hn_ = nsn.ham_nguoc(x, y, yb, k, a_, b_, m)
    V["c19a_chon"] = bang([r"\text{lần}", "j", "x_j", "y_j", r"|y_j-\bar y|"],
                          [[str(s), str(j), sl(x[j]), sl(y[j]), so(abs(y[j] - yb))] for s, j in enumerate(hn_["thu_tu"], 1)])
    u, vv, T = hn_["u"], hn_["v"], hn_["T"]
    r_ = len(u) - 1
    rows = []
    for s in range(r_ + 1):
        hh = [str(s), sl(u[s]), sl(vv[s])]
        for kk in range(1, s + 1):
            hh.append(ob(so(T[s][kk])) if kk == s else so(T[s][kk]))
        rows.append(hh + [""] * (r_ - s))
    rows[0][2] = ob(rows[0][2])
    V["c19a_tsp"] = bang(["s", r"u_s=y", r"v_s=x"] + [f"\\text{{TSP{kk}}}" for kk in range(1, r_ + 1)], rows)
    tong, rows = 0.0, []
    for j in range(r_ + 1):
        tong += hn_["so_hang"][j]
        rows.append([str(j), so(hn_["c"][j]), so(hn_["omega"][j]), so(hn_["so_hang"][j]), so(tong)])
    V["c19a_tong"] = bang(["j", "c_j", r"\omega_j(\bar y)", r"c_j\,\omega_j(\bar y)", r"\text{tổng}"], rows)
    V["c19a_x"] = so(hn_["xbar"])
    V["c19a_cuoi"] = so(abs(hn_["so_hang"][-1]))
    V["c19a_kt"] = so(abs(nsn.y_tai(x, y, hn_["xbar"], m) - yb))
    lp = nsn.lap(x, y, yb, k, h, m, 1e-6, 100)
    V["c19a_lap"] = so(lp["xbar"])
    V["c19a_ss"] = so(abs(lp["xbar"] - hn_["xbar"]))
    # b) ybar = 3.15: lap
    yb = 3.15
    tai_moc, kh = nsn.khoang_cach_ly(y, yb)
    V["c19b_cl"] = bang(["k", "x_k", "x_{k+1}", r"g_k=y_k-\bar y", r"g_{k+1}", r"\text{thuộc đoạn đơn điệu}"],
                        [[str(k), sl(x[k]), sl(x[k + 1]), sd(y[k] - yb, 7), sd(y[k + 1] - yb, 7),
                          "[{};\\ {}]".format(*(sl(x[e]) for e in next(dd for dd in doan if dd[0] <= k < dd[1])[:2]))]
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
            hh = [str(idx[rr]), sl(x[idx[rr]])]
            for kk in range(rr + 1):
                s_ = sd(D[rr][kk], 7)
                la = (kk == rr) if lp["huong"] == "tien" else (rr == mm - 1)
                hh.append(ob(s_) if la else s_)
            rows.append(hh + [""] * (mm - 1 - rr))
        b_sp = bang(["i", "x_i", "y_i"] + [dmu(kk) for kk in range(1, mm)], rows)
        ten_d = "\\Delta" if lp["huong"] == "tien" else "\\nabla"
        s = lp["s"]
        rows = [[str(j), f"{ten_d}^{{{j}}}y_{{{s}}}", sd(d[j], 7), "" if j < 2 else so(lp["B"][j])] for j in range(mm)]
        b_B = bang(["j", "", "d_j", r"B_j=\dfrac{d_j}{j!\,d_1}"], rows)
        t = lp["t"]
        rows = [["0", so(t[0]), so(x[s] + t[0] * h), ""]]
        for j in range(1, len(t)):
            rows.append([str(j), so(t[j]), so(x[s] + t[j] * h), so(h * abs(t[j] - t[j - 1]))])
        rows[-1][2] = ob(rows[-1][2])
        b_it = bang(["l", "t_l", r"x_{" + str(s) + r"}+t_lh", r"h|t_l-t_{l-1}|"], rows)
        phi = hien(r"\varphi(t)", [so(lp["A"])] + [
            ("- " if lp["B"][j] >= 0 else "+ ") + so(abs(lp["B"][j])) +
            "".join(f"(t{'-' if lp['huong'] == 'tien' else '+'}{l})" if l else "t" for l in range(j))
            for j in range(2, mm)])
        khoi.append(L(r"""
\paragraph{Nghiệm @r@: khoảng cách ly $(x_{@k@};x_{@k1@})=(@xk@;\ @xk1@)$.}
@huong_txt@, dùng $@m@$ mốc $x_{@i0@},\dots,x_{@i1@}$, $d_j=@ten_d@^jy_{@s@}$ (các ô khung):
@b_sp@
@b_B@
@phi@
\[t_0=\frac{\bar y-d_0}{d_1}=@t0@,\qquad t_{l+1}=\varphi(t_l),\ \text{dừng khi } h|t_{l+1}-t_l|<\varepsilon=10^{-6}.\]
@b_it@
Hội tụ sau $@lan@$ lần lặp; $|\varphi'(t^*)|=@q@<1$ (điều kiện hội tụ thoả). Nghiệm
$\bar x_{@r@}=x_{@s@}+t^*h=@x@$.
""", r=r, k=k, k1=k + 1, xk=sl(x[k]), xk1=sl(x[k + 1]), m=mm, i0=idx[0], i1=idx[-1], ten_d=ten_d, s=s,
            huong_txt=("Đủ mốc bên phải nên dùng lặp Newton tiến xuất phát từ $x_{%d}=%s$, $t=(x-x_{%d})/h$"
                       % (s, sl(x[s]), s)) if lp["huong"] == "tien" else
            ("Không đủ mốc bên phải nên dùng lặp Newton lùi xuất phát từ $x_{%d}=%s$, $t=(x-x_{%d})/h$"
             % (s, sl(x[s]), s)),
            b_sp=b_sp, b_B=b_B, phi=phi, t0=so(t[0]), b_it=b_it, lan=len(t) - 1, q=so(lp["q"]), x=so(lp["xbar"])))
        nghiem.append(lp["xbar"])
        V[f"c19b_kt{r}"] = so(abs(nsn.y_tai(x, y, lp["xbar"], m) - yb))
        hn_ = nsn.ham_nguoc(x, y, yb, k, *next(dd for dd in doan if dd[0] <= k < dd[1])[:2], m)
        V[f"c19b_hn{r}"] = so(hn_["xbar"])
        V[f"c19b_hnss{r}"] = so(abs(hn_["xbar"] - lp["xbar"]))
    V["c19b_khoi"] = "\n".join(khoi)
    V["c19b_x"] = vecl(nghiem)


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
                       [["x_i"] + [sl(t) for t in x], ["y_i"] + [sl(t) for t in y]])
    V["c21_h"] = bang(["k", r"[x_k;x_{k+1}]", "h_k", r"s_k=\frac{y_{k+1}-y_k}{h_k}"],
                      [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]", so(h[k]), so((y[k + 1] - y[k]) / h[k])]
                       for k in range(n)])

    def bang_he(he, p):
        ten = "abcd"[:p + 1]
        return bang(["k", r"[x_k;x_{k+1}]"] + [f"{t}_k" for t in ten],
                    [[str(k), f"[{sl(x[k])};\\ {sl(x[k + 1])}]"] + [so(v) for v in he[k]] for k in range(n)])

    def ham(he):
        dong = [f"S_{{{k}}}(x) &= " + " ".join(hang_tu(he[k])) + f",\\quad x\\in[{sl(x[k])};\\ {sl(x[k + 1])}]"
                for k in range(n)]
        return "\\begin{align*}\n" + " \\\\\n".join(dong) + "\n\\end{align*}"

    # a) bac 2, S'(0) = 0
    g, m_, he = sp.spline2(x, y, [(1, 0, 0.0)])
    V["c21a_m"] = bang(["k", r"\gamma_k=\frac{2(y_{k+1}-y_k)}{h_k}", r"m_{k+1}=\gamma_k-m_k"],
                       [[str(k), so(g[k]), so(m_[k + 1])] for k in range(n)])
    V["c21a_mv"] = vecl(m_)
    V["c21a_he"] = bang_he(he, 2)
    V["c21a_S"] = ham(he)
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
                                    [[f"i={i}"] + [so(v) for v in M[i]] + [so(R[i])] for i in range(n + 1)])
        V[f"c21{ten}_duoi"] = bang(["i", r"\ell_i", "d_i", "u_i", "r_i", "P_i", "Q_i", r"\sigma_i"],
                                   [[str(i), so(Lr[i]), so(Dg[i]), so(U[i]), so(R[i]), so(P[i]),
                                     so(Q[i]), ob(so(sg[i]))] for i in range(n + 1)])
        V[f"c21{ten}_sigma"] = vecl(sg)
        V[f"c21{ten}_he"] = bang_he(he, 3)
        V[f"c21{ten}_S"] = ham(he)
        V[f"c21{ten}_kt"] = kiem_spline(x, y, he, 3, dk)
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(x, y, bc_type=((dk[0][0], dk[0][2]), (dk[1][0], dk[1][2])))
        V[f"c21{ten}_sc"] = so(float(np.max(np.abs(cs(x, 2) - np.array(sg)))))


def kiem_spline(x, y, he, p, dk):
    n = len(x) - 1
    e0 = max(max(abs(np.polyval(he[k], x[k]) - y[k]), abs(np.polyval(he[k], x[k + 1]) - y[k + 1])) for k in range(n))
    e1 = max((abs(np.polyval(np.polyder(he[k], r), x[k + 1]) - np.polyval(np.polyder(he[k + 1], r), x[k + 1]))
              for k in range(n - 1) for r in range(1, p)), default=0.0)
    e2 = max(abs(np.polyval(np.polyder(he[0 if k == 0 else n - 1], r), x[k]) - v) for r, k, v in dk)
    return f"noi suy {so(e0)}, tron {so(e1)}, bien {so(e2)}"


# ===== CAU 23 =====

def he_chuan_tex(M, b, an):
    m = len(b)
    A = r"\begin{pmatrix}" + r"\\".join("&".join(so(M[i][j]) for j in range(m)) for i in range(m)) + r"\end{pmatrix}"
    X = r"\begin{pmatrix}" + r"\\".join(an) + r"\end{pmatrix}"
    B = r"\begin{pmatrix}" + r"\\".join(so(v) for v in b) + r"\end{pmatrix}"
    return r"\[" + A + X + "=" + B + r"\]"


def cau23():
    khoi = bp.tim_khoi(bp.doc_luoi(os.path.join(GOC, "slide_example", "data Câu 23.xlsx")))
    du = {}
    for ten, (nhan, ox, oy, vt) in zip("abcd", khoi):
        bao = []
        x, y = bp.lam_sach(ox, oy, vt, bao)
        du[ten] = (np.array(x), np.array(y), bao)
    # a, b: tuyen tinh theo tham so
    for ten, cs, an in (("a", [("x", lambda t: t), ("1/x", lambda t: 1 / t)], ["a", "b"]),
                        ("b", [("x^2", lambda t: t ** 2), (r"\cos x", np.cos), ("1", np.ones_like)], ["a", "b", "c"])):
        x, y, _ = du[ten]
        Phi = np.column_stack([f(x) for _, f in cs])
        a, M, b, A, g, sigma = bp.bptt(Phi, y)
        V[f"c23{ten}_he"] = he_chuan_tex(M, b, an)
        for j, t in enumerate(an):
            V[f"c23{ten}_{t}"] = so(a[j])
        V[f"c23{ten}_sigma"] = so(sigma)
        a_np = np.linalg.lstsq(Phi, y, rcond=None)[0]
        V[f"c23{ten}_kt"] = so(float(np.max(np.abs(a - a_np))))
    # c: y = a e^(bx + cx^2); d: y = a x^b
    for ten, cs, an in (("c", [("1", np.ones_like), ("x", lambda t: t), ("x^2", lambda t: t ** 2)], [r"\ln a", "b", "c"]),
                        ("d", [("1", np.ones_like), (r"\ln x", np.log)], [r"\ln(-a)", "b"])):
        x, y, _ = du[ten]
        s = 1.0 if y[0] > 0 else -1.0
        Phi1 = np.column_stack([f(x) for _, f in cs])
        c, M, b, A, z, gY, sigma, sz = bp.tuyen_tinh_hoa(Phi1, y, s)
        m = len(cs)
        V[f"c23{ten}_he"] = he_chuan_tex(M, b, an)
        V[f"c23{ten}_c"] = vecl(c)
        V[f"c23{ten}_a"] = so(s * math.exp(c[0]))
        V[f"c23{ten}_b"] = so(c[1])
        if m > 2:
            V[f"c23{ten}_cc"] = so(c[2])
        V[f"c23{ten}_sigma"] = so(sigma)
        V[f"c23{ten}_sz"] = so(sz)
        c2, lan, ok = bp.gauss_newton(Phi1, y, s)
        rows = [[str(j)] + [so(v) for v in cc] + [so(sg)] for j, cc, sg in lan]
        rows[-1] = rows[-1][:1] + [ob(v) for v in rows[-1][1:]]
        V[f"c23{ten}_gn"] = bang(["l"] + an + [r"\sigma"], rows)
        V[f"c23{ten}_gn_lan"] = str(len(lan) - 1)
        V[f"c23{ten}_a2"] = so(s * math.exp(c2[0]))
        V[f"c23{ten}_b2"] = so(c2[1])
        if m > 2:
            V[f"c23{ten}_cc2"] = so(c2[2])
        V[f"c23{ten}_sigma2"] = so(lan[-1][2])
        V[f"c23{ten}_kt"] = so(float(np.max(np.abs(c - np.linalg.lstsq(Phi1, z, rcond=None)[0]))))
        from scipy.optimize import curve_fit
        f = lambda xx, *cc: s * np.exp(np.column_stack([fn(np.asarray(xx, dtype=float)) for _, fn in cs]) @ np.array(cc))
        c_sp = curve_fit(f, x, y, p0=lan[0][1])[0]
        V[f"c23{ten}_kt2"] = so(float(np.max(np.abs(c2 - c_sp))))


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
    # Khoa kiem tra (so voi numpy/scipy, so sanh phuong phap) khong in vao loi giai: chi in ra man hinh
    kiem = re.compile(r"_kt\w*$|_(sc|ss\d*|lap|hn\d+|hnss\d+)$")
    kt = sorted(k for k in set(V) - dung if kiem.search(k))
    if kt:
        print("KIEM TRA (khong dua vao loi giai):")
        for k in kt:
            print(f"  {k} = {V[k]}")
    thua = sorted(k for k in set(V) - dung if not kiem.search(k))
    if thua:
        print("Canh bao: khoa sinh ra nhung khong dung:", ", ".join(thua))
    dich = os.path.join(THU_MUC, "loi_giai_bai_tap.tex")
    with open(dich, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"Da ghi {dich} ({len(dung)} khoa).")


if __name__ == "__main__":
    main()
