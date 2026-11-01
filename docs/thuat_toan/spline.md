# Hàm ghép trơn (spline) bậc $p\le4$

Quy ước: bộ điểm $(x_i,y_i)$, $i=0..n$, mốc phân biệt **xếp tăng dần**; $h_k=x_{k+1}-x_k>0$; $S(x)=S_k(x)$ trên $[x_k,x_{k+1}]$, $k=0..n-1$; $S_k$ là đa thức bậc $p$, $S\in C^{p-1}[x_0,x_n]$. Hệ số $S_k$ in dạng vector **từ bậc cao xuống bậc thấp**, như `horner.md` (dạng chính tắc theo $x$ như slide; dạng địa phương theo $u=x-x_k$).

Đếm điều kiện: $n(p+1)$ hệ số; nội suy $2n$ phương trình; trơn cấp $1..p-1$ tại $n-1$ mốc trong: $(p-1)(n-1)$ → thiếu **$p-1$ điều kiện biên** $S^{(r)}(x_0)$ hoặc $S^{(r)}(x_n)$ cho trước, $1\le r\le p-1$.

| Bậc | Ẩn | Hệ / công thức | Điều kiện biên |
|---|---|---|---|
| $p=1$ | — | $S_k(x)=\dfrac{-y_k(x-x_{k+1})+y_{k+1}(x-x_k)}{h_k}$ | không cần |
| $p=2$ | $m_k=S'(x_k)$ | $m_k+m_{k+1}=\gamma_k:=\dfrac{2(y_{k+1}-y_k)}{h_k}$, $S_k(x)=\dfrac{-m_k(x-x_{k+1})^2+m_{k+1}(x-x_k)^2}{2h_k}+y_k+\dfrac{m_kh_k}{2}$ | 1: $S'(x_0)$ hoặc $S'(x_n)$ |
| $p=3$ | $\sigma_k=S''(x_k)$ | $\dfrac{h_k}{6}\sigma_k+\dfrac{h_k+h_{k+1}}{3}\sigma_{k+1}+\dfrac{h_{k+1}}{6}\sigma_{k+2}=\delta_k:=\dfrac{y_{k+2}-y_{k+1}}{h_{k+1}}-\dfrac{y_{k+1}-y_k}{h_k}$ | 2 |
| $p\le4$ tổng quát | $D_{k,r}=S^{(r)}(x_k)$, $r=1..p-1$ | $S_k(x)=\displaystyle\sum_{j=0}^{p-1}\frac{D_{k,j}}{j!}(x-x_k)^j+\frac{D_{k+1,p-1}-D_{k,p-1}}{p!\,h_k}(x-x_k)^p$, $D_{k,0}=y_k$ | $p-1$ |

Spline bậc 3, dạng của slide:
$$S_k(x)=\frac{-\sigma_k(x-x_{k+1})^3+\sigma_{k+1}(x-x_k)^3}{6h_k}+\alpha_k(x-x_k)-\beta_k(x-x_{k+1}),\quad \alpha_k=\frac{y_{k+1}}{h_k}-\frac{\sigma_{k+1}h_k}{6},\ \beta_k=\frac{y_k}{h_k}-\frac{\sigma_kh_k}{6}.$$
Điều kiện biên đạo hàm cấp 1 đưa về hàng đầu/cuối của hệ $\sigma$:
$$S'(x_0)=A:\ \frac{h_0}{3}\sigma_0+\frac{h_0}{6}\sigma_1=\frac{y_1-y_0}{h_0}-A;\qquad S'(x_n)=B:\ \frac{h_{n-1}}{6}\sigma_{n-1}+\frac{h_{n-1}}{3}\sigma_n=B-\frac{y_n-y_{n-1}}{h_{n-1}}.$$

> Ghi chú: slide `18_Spline_20261.pdf` đánh chỉ số mốc $i=1..n$; ở đây dùng $i=0..n$. Đã kiểm tra lại các công thức: spline bậc 2 (tr.6–9: $\alpha_k=y_k+\frac{m_kh_k}{2}$, $m_{k+1}+m_k=\gamma_k$, hệ số $a_k,b_k,c_k$) và bậc 3 (tr.11–18: $\alpha_k,\beta_k$, hệ ba đường chéo, hệ số $a_k,b_k,c_k,d_k$) đều đúng — đã đối chiếu bằng số với lời giải hệ tổng quát mục 4. Slide viết hệ bậc 2 là "$n-1$ phương trình, $n$ ẩn" và hệ bậc 3 "$n-2$ phương trình, $n$ ẩn" (với $n$ mốc) — đúng, thiếu đúng $p-1$ phương trình là điều kiện biên.
>
> Đề câu 21b ghi "$S''(0)=-1,\ S''(0)=1$" — lặp mốc $0$; hiểu là $S''(0)=-1$, $S''(3.1416)=1$ (khớp với $y=\cos x$: $-\cos0=-1$, $-\cos\pi=1$).

**Chọn biến thể theo mục đích:**

| Bậc $p$ / điều kiện biên | Biến thể | Chi phí |
|---|---|---|
| $p=1$ | mục 1 | $\sim2n$ phép tính |
| $p=2$, cho $S'(x_0)$ hoặc $S'(x_n)$ | mục 2 (truy hồi $m_k$) | $\sim2n$ |
| $p=3$, mỗi đầu một điều kiện $S'$ hoặc $S''$ | mục 3 (hệ ba đường chéo, phương pháp truy đuổi) | $\sim8n$ |
| $p=4$, hoặc điều kiện biên dồn về một đầu | mục 4 (hệ tổng quát, khử Gauss) | $\sim((p-1)(n+1))^3/3$ (ma trận băng: $\sim p^3n$) |
| Dạng chính tắc $S_k(x)=a_kx^p+\dots$ | công thức hệ số của mục 2/3, hoặc mục 5 từ dạng địa phương | $\sim p^2$ mỗi khoảng |

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ và hàng $y$ (hoặc 2 cột); dấu trừ Unicode → `-`; `,` giữa hai chữ số → `.`; bỏ ký tự lạ; ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp, báo vị trí và lý do.
* Mốc trùng: cùng $y$ → giữ 1; chênh $\le\varepsilon_y=10^{-3}\max(1,\max|y_i|)$ → lấy trung bình; ngược lại hỏi giữ giá trị nào (1 = đầu, 2 = sau, 3 = trung bình, 0 = dừng; Enter = đầu), đọc từ file trả lời thì giữ giá trị đầu; báo số dòng của từng $y$ và lựa chọn. **Sắp tăng theo $x$** (báo); cần ít nhất 2 mốc ($n\ge1$).
* Bậc $p$: số nguyên $1\le p\le4$, ngược lại dừng, báo lỗi.
* Điều kiện biên: dạng `S'(0) = 0`, `S''(3.1416) = 1` (dấu `"` hiểu là `''`, dấu nháy Unicode `’ ′` → `'`) hoặc bộ ba `r x v` ($S^{(r)}(x)=v$), cách nhau bởi `;`. Điểm phải là $x_0$ hoặc $x_n$ (lệch $\le10^{-6}(x_n-x_0)$ → coi là trùng); cấp $1\le r\le p-1$; không lặp cùng $(r,\text{điểm})$; **đúng $p-1$ điều kiện**. Sai → dừng, báo lỗi (điểm lặp như $S''(0)$ hai lần → báo rõ).

---

## 1. Spline bậc 1

**Input:** $x,y$ ($n\ge1$). **Output:** hệ số chính tắc $(a_k,b_k)$, $S_k(x)=a_kx+b_k$, $k=0..n-1$.

**Bước 1 — Với $k=0..n-1$:** $h_k:=x_{k+1}-x_k$; $a_k:=\dfrac{y_{k+1}-y_k}{h_k}$; $b_k:=\dfrac{y_kx_{k+1}-y_{k+1}x_k}{h_k}$.

**Bước 2 — Kết thúc:** trả về các $(a_k,b_k)$.

---

## 2. Spline bậc 2 (truy hồi $m_k$)

**Input:** $x,y$; một điều kiện biên $S'(x_0)=A$ hoặc $S'(x_n)=B$.

**Output:** vector $m=(m_0,\dots,m_n)$; hệ số chính tắc $(a_k,b_k,c_k)$, $S_k(x)=a_kx^2+b_kx+c_k$.

**Bước 1 — Hệ số vế phải:** $h_k:=x_{k+1}-x_k$, $\gamma_k:=\dfrac{2(y_{k+1}-y_k)}{h_k}$, $k=0..n-1$.

**Bước 2 — Truy hồi:**
* TH1 cho $S'(x_0)=A$: $m_0:=A$; với $k=0..n-1$: $m_{k+1}:=\gamma_k-m_k$;
* TH2 cho $S'(x_n)=B$: $m_n:=B$; với $k=n-1..0$: $m_k:=\gamma_k-m_{k+1}$.

**Bước 3 — Hệ số, với $k=0..n-1$:**
$$a_k:=\frac{m_{k+1}-m_k}{2h_k},\quad b_k:=\frac{m_kx_{k+1}-m_{k+1}x_k}{h_k},\quad c_k:=\frac{-m_kx_{k+1}^2+m_{k+1}x_k^2}{2h_k}+y_k+\frac{m_kh_k}{2}.$$

**Bước 4 — Kết thúc:** trả về $m$ và các $(a_k,b_k,c_k)$.

---

## 3. Spline bậc 3 (hệ ba đường chéo theo $\sigma_k$)

**Input:** $x,y$ ($n\ge1$); điều kiện biên tại $x_0$: $S''(x_0)=A$ hoặc $S'(x_0)=A$; tại $x_n$: $S''(x_n)=B$ hoặc $S'(x_n)=B$.

**Output:** vector $\sigma=(\sigma_0,\dots,\sigma_n)$; hệ số chính tắc $(a_k,b_k,c_k,d_k)$, $S_k(x)=a_kx^3+b_kx^2+c_kx+d_k$.

**Bước 1 — Khoảng cách, tỷ sai phân:** $h_k:=x_{k+1}-x_k$, $s_k:=\dfrac{y_{k+1}-y_k}{h_k}$, $k=0..n-1$.

**Bước 2 — Lập hệ** $\ell_i\sigma_{i-1}+d_i\sigma_i+u_i\sigma_{i+1}=r_i$, $i=0..n$ ($\ell_0=u_n=0$):
* **2.1 — Hàng $0$:** TH1 $S''(x_0)=A$: $d_0:=1$, $u_0:=0$, $r_0:=A$; TH2 $S'(x_0)=A$: $d_0:=\frac{h_0}{3}$, $u_0:=\frac{h_0}{6}$, $r_0:=s_0-A$.
* **2.2 — Hàng $i=1..n-1$:** $\ell_i:=\frac{h_{i-1}}{6}$, $d_i:=\frac{h_{i-1}+h_i}{3}$, $u_i:=\frac{h_i}{6}$, $r_i:=s_i-s_{i-1}$.
* **2.3 — Hàng $n$:** TH1 $S''(x_n)=B$: $\ell_n:=0$, $d_n:=1$, $r_n:=B$; TH2 $S'(x_n)=B$: $\ell_n:=\frac{h_{n-1}}{6}$, $d_n:=\frac{h_{n-1}}{3}$, $r_n:=B-s_{n-1}$.

**Bước 3 — Truy đuổi xuôi:** $P_0:=-u_0/d_0$, $Q_0:=r_0/d_0$; với $i=1..n$: $\mu:=d_i+\ell_iP_{i-1}$ ($\mu=0$ → dừng, báo hệ suy biến); $P_i:=-u_i/\mu$, $Q_i:=(r_i-\ell_iQ_{i-1})/\mu$.

**Bước 4 — Truy đuổi ngược:** $\sigma_n:=Q_n$; với $i=n-1..0$: $\sigma_i:=P_i\sigma_{i+1}+Q_i$.

**Bước 5 — Hệ số, với $k=0..n-1$:**
$$a_k:=\frac{\sigma_{k+1}-\sigma_k}{6h_k},\quad b_k:=\frac{\sigma_kx_{k+1}-\sigma_{k+1}x_k}{2h_k},\quad c_k:=\frac{-\sigma_kx_{k+1}^2+\sigma_{k+1}x_k^2}{2h_k}+s_k-\frac{(\sigma_{k+1}-\sigma_k)h_k}{6},$$
$$d_k:=\frac{\sigma_kx_{k+1}^3-\sigma_{k+1}x_k^3}{6h_k}+\frac{y_kx_{k+1}-y_{k+1}x_k}{h_k}+\frac{(\sigma_{k+1}x_k-\sigma_kx_{k+1})h_k}{6}.$$

**Bước 6 — Kết thúc:** trả về $\sigma$ và các $(a_k,b_k,c_k,d_k)$.

Hệ chéo trội ($|d_i|\ge|\ell_i|+|u_i|$, chặt ở hàng trong) nên truy đuổi ổn định, không cần chọn trụ.

---

## 4. Spline bậc $p\le4$ tổng quát (dạng Taylor địa phương)

**Input:** $x,y$ ($n\ge1$); bậc $p$, $1\le p\le4$; $p-1$ điều kiện biên $S^{(r_q)}(\xi_q)=v_q$, $\xi_q\in\{x_0,x_n\}$.

**Output:** $D_{k,r}=S^{(r)}(x_k)$; hệ số địa phương $e_{k,j}$ với $S_k(x)=\sum_{j=0}^{p}e_{k,j}(x-x_k)^j$.

**Bước 1 — Ẩn:** $D_{k,r}$, $k=0..n$, $r=1..p-1$ — tổng $M:=(p-1)(n+1)$ ẩn ($D_{k,0}:=y_k$ đã biết). $p=1$: không có ẩn, sang Bước 4.

**Bước 2 — Lập hệ $M\times M$:**
* **2.1 — Trơn và nội suy tại $x_{k+1}$**, với $k=0..n-1$, $r=0..p-2$ (điều kiện $S_k^{(r)}(x_{k+1})=D_{k+1,r}$):
$$\sum_{j=\max(r,1)}^{p-1}\frac{h_k^{\,j-r}}{(j-r)!}D_{k,j}+\frac{h_k^{\,p-r-1}}{(p-r)!}\big(D_{k+1,p-1}-D_{k,p-1}\big)-[r\ge1]\,D_{k+1,r}=[r=0]\,(y_{k+1}-y_k)$$
  (với $r=0$ và $p=1$ tổng rỗng);
* **2.2 — Biên:** với mỗi điều kiện $q$: $D_{k_q,r_q}=v_q$ ($k_q=0$ nếu $\xi_q=x_0$, $k_q=n$ nếu $\xi_q=x_n$).

**Bước 3 — Giải:** khử Gauss có chọn trụ theo cột; trụ $|\cdot|<10^{-12}\cdot$(chuẩn hàng) → dừng, báo "điều kiện biên không xác định duy nhất spline".

**Bước 4 — Hệ số địa phương, với $k=0..n-1$:** $e_{k,j}:=D_{k,j}/j!$, $j=0..p-1$; $e_{k,p}:=\dfrac{D_{k+1,p-1}-D_{k,p-1}}{p!\,h_k}$ (với $p=1$: $e_{k,1}=(y_{k+1}-y_k)/h_k$).

**Bước 5 — Kết thúc:** trả về $D$ và $e$.

---

## 5. Dạng chính tắc từ dạng địa phương

**Input:** $(e_{k,p},\dots,e_{k,0})$ — đa thức theo $u=x-x_k$. **Output:** hệ số chính tắc theo $x$.

**Bước 1:** đổi biến $u=\frac{x-s}{h}$ với $s:=x_k$, $h:=1$ theo mục 5, `newton.md`.

**Bước 2 — Kết thúc:** trả về vector hệ số theo $x$.
