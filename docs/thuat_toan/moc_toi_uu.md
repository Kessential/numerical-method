# Mốc nội suy tối ưu

Quy ước: các mốc lưu dạng vector $x=(x_0,x_1,\dots,x_{n-1})$ **xếp tăng dần** (chỉ số = thứ tự mốc); $w_n(x)=\prod_{i=0}^{n-1}(x-x_i)$; đa thức Chebyshev $T_n(t)=\cos(n\arccos t)$ trên $[-1,1]$. Mốc tối ưu là nghiệm của $T_n$ sau khi đổi biến $t\in[-1,1]\mapsto x\in[a,b]$, khi đó $\max_{[a,b]}|w_n|$ nhỏ nhất.

> Ghi chú: slide `13_Bai toan Noi suy 20261.pdf` dùng $n+1$ mốc = nghiệm của $T_{n+1}$: $x_i=\cos\big(\frac{\pi}{2(n+1)}+\frac{i\pi}{n+1}\big)$, $i=0..n$ — đúng, nhưng xếp **giảm dần**. Ở đây dùng $n$ mốc và $-\cos$ để xếp tăng dần; đã kiểm tra bằng `numpy.polynomial.chebyshev.chebroots`.

**Bước 0 — Xử lý dữ liệu:**
* Đọc dãy số: tách theo khoảng trắng hoặc `;`, dấu trừ Unicode `−` `–` (copy từ PDF) → `-`, dấu `,` giữa hai chữ số → `.`; token không phải số → loại và báo.
* Có NaN hoặc $\pm\infty$ → dừng, báo lỗi.
* Mỗi bộ phải có đúng 3 số $n,a,b$, ngược lại dừng, báo lỗi.
* Số mốc $n$: phải là số nguyên $\ge1$ (`9.0` chấp nhận là 9), ngược lại dừng, báo lỗi.
* Đoạn $[a,b]$: $a=b$ → dừng, báo lỗi; $a>b$ → đổi chỗ $a\leftrightarrow b$ và báo.

---

## 1. $n$ mốc nội suy tối ưu trên $[a,b]$

**Input:** số mốc $n\in\mathbb N$, $n\ge1$; đoạn $[a,b]$, $a<b$.

**Output:**
* vector $t=(t_0,\dots,t_{n-1})\in\mathbb R^{n}$ với $t_i$ là nghiệm của $T_n$ trên $[-1,1]$, $t_0<\dots<t_{n-1}$;
* vector $x=(x_0,\dots,x_{n-1})\in\mathbb R^{n}$ với $x_i$ là mốc tối ưu trên $[a,b]$, $x_0<\dots<x_{n-1}$;
* $W=\max_{[a,b]}|w_n(x)|$ — độ lệch nhỏ nhất.

**Bước 1 — Đổi biến:** $p:=\dfrac{a+b}{2}$, $q:=\dfrac{b-a}{2}$ (khi đó $x=p+q\,t$).

**Bước 2 — Với $i=0,1,\dots,n-1$:**
* **Bước 2.1 — Nghiệm của $T_n$:** $t_i:=-\cos\dfrac{(2i+1)\pi}{2n}$.
* **Bước 2.2 — Mốc trên $[a,b]$:** $x_i:=p+q\,t_i$.

**Bước 3 — Độ lệch nhỏ nhất:** $W:=\dfrac{(b-a)^n}{2^{2n-1}}$.

**Bước 4 — Kết thúc:** trả về $t$, $x$ và $W$.

Bước 2.1 dùng $-\cos$ nên $t_i$ tăng dần theo $i$ (vì $\cos$ giảm trên $(0,\pi)$), không cần sắp xếp lại.
