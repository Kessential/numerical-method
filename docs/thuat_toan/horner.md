 # Sơ đồ Horner

Quy ước: $P_n(x)=a_nx^n+a_{n-1}x^{n-1}+\dots+a_1x+a_0$ — **$a_i$ là hệ số của $x^i$**, $a_n\ne0$. Mọi đa thức được nhập và in dạng vector hệ số **từ bậc cao xuống bậc thấp**: $a=(a_n,a_{n-1},\dots,a_0)$. Ví dụ $3x^3-2x-1$ ↔ $a=(3,0,-2,-1)$, tức $a_3=3,a_2=0,a_1=-2,a_0=-1$.

> Ghi chú: slide 13–19 không có phần Horner; thuật toán theo sơ đồ Horner chuẩn, đã kiểm tra bằng `numpy.polyval`, `numpy.polydiv`, `numpy.polyder`, `numpy.poly`.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| Giá trị $P_n(c)$ | Chia (mục 1), chỉ giữ $r$ | $n$ nhân, $n$ cộng |
| Thương và dư của $P_n(x):(x-c)$ | Chia (mục 1) | $n$ nhân, $n$ cộng |
| Đạo hàm $P_n^{(j)}(c)$, $j=0..k$ | Chia lặp (mục 2), dừng sau $\min(k,n)+1$ lần | $\sim(k+1)n$ nhân |
| Tích $P_n(x)(x-c)$ | Nhân (mục 3) | $n+1$ nhân, $n$ cộng |
| Đa thức $w_{m}(x)=\prod_{i=0}^{m-1}(x-x_i)$ | Nhân lặp (mục 4) | $\sim m^2/2$ nhân |
| Đa thức đạo hàm $P_n^{(k)}(x)$ | Đạo hàm lặp trên vector hệ số (mục 5, không phải Horner) | $\sim kn$ nhân |

Nếu cần nhiều mục đích tại cùng $c$: lần chia đầu tiên của mục 2 cho luôn $P_n(c)$ và thương, không chia lại.

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc dãy số: tách theo khoảng trắng hoặc `;`, dấu trừ Unicode `−` `–` (copy từ PDF) → `-`, dấu `,` giữa hai chữ số → `.`; token không phải số → loại và báo.
* Có NaN hoặc $\pm\infty$ → dừng, báo lỗi.
* Vector hệ số $a$: bỏ các số 0 ở đầu (bậc cao) cho tới khi $a_n\ne0$; mọi hệ số bằng 0 → $P\equiv0$: đặt $a:=(0)$, $n:=0$, mọi kết quả bằng 0 (không dừng). Bậc $n:=$ số phần tử còn lại $-1$.
* Cấp $k$ (mục 2, 5): phải là số nguyên $\ge0$, ngược lại dừng, báo lỗi.
* Vector mốc $x$ (mục 4): phải có ít nhất 1 mốc, ngược lại dừng, báo lỗi.

---

## 1. Horner chia: $P_n(x)=(x-c)Q_{n-1}(x)+r$

**Input:** vector $a=(a_n,\dots,a_0)\in\mathbb R^{n+1}$; $c\in\mathbb R$.

**Output:** vector thương $b=(b_{n-1},\dots,b_0)\in\mathbb R^{n}$ ($b_i$ là hệ số của $x^i$ trong $Q_{n-1}$); số dư $r=P_n(c)$.

**Bước 1 — Bậc 0:** nếu $n=0$: $Q\equiv0$, $r:=a_0$, dừng thuật toán; trái lại sang Bước 2.

**Bước 2 — Khởi tạo:** $b_{n-1}:=a_n$.

**Bước 3 — Với $i=n-1,n-2,\dots,1$:** $b_{i-1}:=a_i+c\,b_i$.

**Bước 4 — Số dư:** $r:=a_0+c\,b_0$.

**Bước 5 — Kết thúc:** trả về $b$ và $r$.

Bảng Horner:

| | $a_n$ | $a_{n-1}$ | $\dots$ | $a_1$ | $a_0$ |
|---|---|---|---|---|---|
| $c$ | | $c\,b_{n-1}$ | $\dots$ | $c\,b_1$ | $c\,b_0$ |
| | $b_{n-1}$ | $b_{n-2}$ | $\dots$ | $b_0$ | $r$ |

---

## 2. Đạo hàm cấp $0..k$ tại $c$ (chia lặp)

**Input:** vector $a=(a_n,\dots,a_0)\in\mathbb R^{n+1}$; $c\in\mathbb R$; cấp $k\in\mathbb N$.

**Output:**
* vector $r=(r_0,r_1,\dots,r_K)\in\mathbb R^{K+1}$, $K=\min(k,n)$, với $r_j$ là số dư của lần chia thứ $j+1$ cho $(x-c)$, $r_j=P_n^{(j)}(c)/j!$;
* vector $v=(v_0,v_1,\dots,v_k)\in\mathbb R^{k+1}$ với $v_j=P_n^{(j)}(c)$.

**Bước 1 — Xử lý $k$:** $K:=\min(k,n)$.

**Bước 2 — Khởi tạo:** vector làm việc $b$: $b_i:=a_i$ với $i=0,\dots,n$.

**Bước 3 — Với $j=0,\dots,K$:**
* **Bước 3.1 — Chia cho $(x-c)$:** với $i=n-1,n-2,\dots,j$: $b_i:=b_i+c\,b_{i+1}$.
* **Bước 3.2 — Đạo hàm:** $r_j:=b_j$, $v_j:=j!\,r_j$.

**Bước 4 — Cấp lớn hơn $n$:** nếu $k>n$: với $j=K+1,\dots,k$: $v_j:=0$; trái lại sang Bước 5.

**Bước 5 — Kết thúc:** trả về $r$ và $v$.

---

## 3. Horner nhân: $P_n(x)(x-c)$

**Input:** vector $a=(a_n,\dots,a_0)\in\mathbb R^{n+1}$; $c\in\mathbb R$.

**Output:** vector $d=(d_{n+1},\dots,d_0)\in\mathbb R^{n+2}$ với $d_i$ là hệ số của $x^i$ trong $P_n(x)(x-c)$.

**Bước 1 — Khởi tạo:** $d_{n+1}:=a_n$.

**Bước 2 — Với $i=n,n-1,\dots,1$:** $d_i:=a_{i-1}-c\,a_i$.

**Bước 3 — Hệ số tự do:** $d_0:=-c\,a_0$.

**Bước 4 — Kết thúc:** trả về $d$.

---

## 4. Đa thức $w_m(x)=\prod_{i=0}^{m-1}(x-x_i)$ (nhân lặp)

**Input:** vector mốc $x=(x_0,\dots,x_{m-1})\in\mathbb R^m$.

**Output:** vector $p=(1,p_{m-1},\dots,p_0)\in\mathbb R^{m+1}$ với $p_l$ là hệ số của $x^l$: $w_m(x)=x^m+p_{m-1}x^{m-1}+\dots+p_0$.

**Bước 1 — Khởi tạo:** bắt đầu từ đa thức hằng $1$: $p_0:=1$.

**Bước 2 — Với $i=0,\dots,m-1$** (đa thức hiện có bậc $i$, nhân thêm $(x-x_i)$ theo mục 3):
* **Bước 2.1 — Hệ số cao nhất:** $p_{i+1}:=p_i$ (vector $p$ dài thêm một phần tử).
* **Bước 2.2 — Với $l=i,i-1,\dots,1$:** $p_l:=p_{l-1}-x_i\,p_l$.
* **Bước 2.3 — Hệ số tự do:** $p_0:=-x_i\,p_0$.

**Bước 3 — Kết thúc:** trả về $p$ (luôn có $p_m=1$).

---

## 5. Đa thức đạo hàm $P_n^{(k)}(x)$

Cơ sở: $\big(e_{i+1}x^{i+1}\big)'=(i+1)\,e_{i+1}x^{i}$ — mỗi lần đạo hàm, hệ số mới của $x^i$ bằng $(i+1)\times$ hệ số cũ của $x^{i+1}$.

**Input:** vector $a=(a_n,\dots,a_0)\in\mathbb R^{n+1}$; cấp $k\in\mathbb N$.

**Output:** vector $e=(e_{n-k},\dots,e_0)\in\mathbb R^{n-k+1}$ với $e_i$ là hệ số của $x^i$ trong $P_n^{(k)}(x)$ hoặc $(0)$ nếu $k>n$.

**Bước 1 — Xử lý $k$:** nếu $k>n$: trả về $(0)$, dừng thuật toán; trái lại sang Bước 2.

**Bước 2 — Khởi tạo:** $e_i:=a_i$ với $i=0,\dots,n$.

**Bước 3 — Với $j=1,\dots,k$**:
* **Bước 3.1 — Với $i=0,1,\dots,n-j$:** $e_i:=(i+1)\,e_{i+1}$.
* **Bước 3.2 — Hạ bậc:** bỏ $e_{n-j+1}$; lúc này $(e_{n-j},\dots,e_0)$ là hệ số của $P_n^{(j)}(x)$.

**Bước 4 — Kết thúc:** trả về $e=(e_{n-k},\dots,e_0)$.


