# Nội suy trung tâm (Gauss I, Gauss II, Stirling, Bessel)

Quy ước: mốc **cách đều** $x_i=x_0+ih$, chỉ số đánh **tương đối với mốc trung tâm** $x_0$ (có chỉ số âm); $t=\dfrac{x-x_0}{h}$; sai phân tiến $\Delta y_i=y_{i+1}-y_i$, $\Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i$. Bảng sai phân viết như slide: **hàng $i$ chứa $\Delta^ky_i$** ($y_i,\Delta y_i,\Delta^2y_i,\dots$). Đa thức lưu dạng vector hệ số **từ bậc cao xuống bậc thấp** như `horner.md`.

$$P(x_0+th)=\sum_{k=0}^{n}c_k\,\pi_k(t),\qquad f^{(j)}(\bar x)\approx\frac{P^{(j)}(\bar t)}{h^j},\qquad |f(\bar x)-P(\bar x)|\le\frac{M_{n+1}h^{n+1}}{(n+1)!}\prod_{i}|\bar t-i|$$

| Công thức | Bộ mốc ($n+1$ mốc) | Hệ số $c_k$ | Đa thức cơ sở $\pi_k(t)$, $\pi_0=1$ |
|---|---|---|---|
| Gauss I | $x_{-\lfloor n/2\rfloor},\dots,x_{\lceil n/2\rceil}$ | $\dfrac{\Delta^ky_{-\lfloor k/2\rfloor}}{k!}$ | $\pi_k=\pi_{k-1}\,(t-z_{k-1})$, $z=0,1,-1,2,-2,\dots$ |
| Gauss II | $x_{-\lceil n/2\rceil},\dots,x_{\lfloor n/2\rfloor}$ | $\dfrac{\Delta^ky_{-\lceil k/2\rceil}}{k!}$ | $\pi_k=\pi_{k-1}\,(t-z_{k-1})$, $z=0,-1,1,-2,2,\dots$ |
| Stirling | $n=2r$ chẵn: $x_{-r},\dots,x_r$ | $c_{2j-1}=\dfrac{\Delta^{2j-1}y_{-j}+\Delta^{2j-1}y_{-j+1}}{2\,(2j-1)!}$, $c_{2j}=\dfrac{\Delta^{2j}y_{-j}}{(2j)!}$ | $\pi_1=t$, $\pi_{2j+1}=\pi_{2j-1}(t^2-j^2)$, $\pi_{2j}=t\,\pi_{2j-1}$ |
| Bessel | $n=2r-1$ lẻ: $x_{-r+1},\dots,x_r$ | $c_{2j}=\dfrac{\Delta^{2j}y_{-j}+\Delta^{2j}y_{-j+1}}{2\,(2j)!}$, $c_{2j+1}=\dfrac{\Delta^{2j+1}y_{-j}}{(2j+1)!}$ | $\pi_{2j}=\pi_{2j-2}(t+j-1)(t-j)$, $\pi_{2j+1}=(t-\tfrac12)\pi_{2j}$ |

Gauss I kết nạp mốc theo thứ tự $x_0,x_1,x_{-1},x_2,\dots$ (phải trước); Gauss II: $x_0,x_{-1},x_1,x_{-2},\dots$ (trái trước); Stirling $=\frac12$(Gauss I + Gauss II) với số mốc lẻ; Bessel $=\frac12$(Gauss I tại $x_0$ + Gauss II tại $x_1$) với số mốc chẵn. Cùng một bộ mốc thì mọi công thức cho **cùng một đa thức** (tính duy nhất), chỉ khác cách viết.

> Ghi chú: slide `16_NoisuyTrungtam_20261.pdf`:
> * tr.3 và tr.8 ghi dạng $P(x)$ của Gauss I/II với cùng hệ số $a_2$ cho các số hạng bậc 2, 3, 4 — đúng là $a_2,a_3,a_4$.
> * tr.12 có tiêu đề "Công thức Gauss I" nhưng nội dung là bảng tích của Gauss II ($t(t+1)$, …).
> * tr.19–20 ghi số hạng cuối của $P_{GII}(x_0+th)$ (Gauss II tại $x_1$, mốc $x_{-n}..x_{n+1}$) là $\frac{\Delta^{2n+1}y_{-n}}{(2n+1)!}t(t^2-1)\cdots(t^2-(n-1)^2)(t-n)$ (tr.19) và $\cdots(t^2-(n-2)^2)(t-n+1)(t-n)$ (tr.20); đúng là $\frac{\Delta^{2n+1}y_{-n}}{(2n+1)!}\,t\prod_{i=1}^{n-1}(t^2-i^2)\,(t-n)(t-n-1)$ vì $2n+1$ mốc đầu theo thứ tự Gauss II tại $x_1$ là $x_{-n+1},\dots,x_{n+1}$.
> * tr.20, công thức Bessel cuối ghi $\frac{\Delta y_0}{2}\left(t-\frac12\right)$ và $\frac{\Delta^3y_{-1}}{2\times3!}t(t-1)\left(t-\frac12\right)$; đúng là $\Delta y_0\left(t-\frac12\right)$ và $\frac{\Delta^3y_{-1}}{3!}t(t-1)\left(t-\frac12\right)$ (trung bình của $t\Delta y_0$ và $(t-1)\Delta y_0$ là $\left(t-\frac12\right)\Delta y_0$; thử với 2 mốc: $P(0)$ phải bằng $y_0$). Hệ số $\frac{\Delta^2y_0+\Delta^2y_{-1}}{2\times2!}$ đúng.
>
> Các công thức trong bảng trên đã kiểm tra bằng `numpy.linalg.solve(np.vander(...))`: cùng bộ mốc phải ra cùng đa thức.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| $\bar t$ gần $0$, phía phải ($0<\bar t<\frac12$) | Gauss I (mục 3) | bảng sai phân $\sim n^2/2$ phép trừ + bảng tích $\sim n^2/2$ nhân |
| $\bar t$ gần $0$, phía trái ($-\frac12<\bar t<0$) | Gauss II (mục 3) | như trên |
| $|\bar t|\le\frac14$, số mốc lẻ | Stirling (mục 3) | như trên |
| $\frac14\le\bar t\le\frac34$, số mốc chẵn | Bessel (mục 3) | như trên |
| Bảng dài, chỉ dùng $m$ mốc quanh $\bar x$ | mục 1 trước, rồi một trong các dòng trên | $\sim m$ phép so sánh |
| $f(\bar x)$, $f^{(j)}(\bar x)$ | mục 4 trên $P(t)$ đã lập | $\sim(k+1)n$ nhân |
| Đa thức theo biến $x$ | mục 5, `newton.md` với $s=x_0$ | $\sim n^2/2$ nhân |

Bảng sai phân (mục 2) lập **một lần** dùng chung cho mọi công thức; mỗi công thức chỉ chọn các ô khác nhau.

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ và hàng $y$ (hoặc 2 cột $x$, $y$, file `.csv`/`.xlsx`); ô tách theo khoảng trắng, `;` hoặc tab; nhãn đầu hàng (`x`, `y`) bỏ qua. Dấu trừ Unicode `−` `–` → `-`; dấu `,` giữa hai chữ số → `.`; bỏ ký tự lạ không phải chữ.
* Hàng $x$ và hàng $y$ khác số ô → dừng, báo lỗi. Ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp; báo vị trí và lý do.
* Mốc trùng: cùng $y$ → giữ 1; khác $y$ nhưng chênh $\le\varepsilon_y=10^{-3}\max(1,\max|y_i|)$ → lấy trung bình; ngược lại dừng, báo lỗi.
* Sắp tăng theo $x$ (báo nếu đổi thứ tự). Cần ít nhất 2 mốc.
* **Bắt buộc cách đều:** $h:=\dfrac{x_N-x_0}{N}$ ($N+1$ mốc), $|x_{i+1}-x_i-h|\le\delta h$, $\delta=10^{-6}$; không thoả → dừng, báo lỗi (dùng `newton.md` mục bất kỳ).
* Điểm $\bar x$: ngoài $[x_{\min},x_{\max}]$ → cảnh báo ngoại suy. Cấp $k$: số nguyên $\ge0$.
* Số mốc dùng $m$ (mặc định: cả bảng): số nguyên $\ge2$; $m>$ số mốc → dùng cả bảng, báo. **Điều kiện riêng:** Stirling cần $m$ lẻ, Bessel cần $m$ chẵn — sai thì $m:=m-1$ và báo (mục 1 sẽ bỏ mốc biên xa $\bar x$ nhất).

---

## 1. Trích xuất $m$ mốc quanh $\bar x$

**Input:** bảng $(x_i,y_i)$ cách đều đã qua Bước 0; $\bar x$; $m$.

**Output:** bộ mốc con $m$ mốc liên tiếp có $|\bar x-x_i|$ nhỏ nhất.

**Bước 1 — Kết nạp dần:** theo mục 7, `newton.md`.

**Bước 2 — Kết thúc:** trả về bộ mốc con. (Bảng có đúng $m$ mốc → bộ mốc con là cả bảng.)

---

## 2. Bảng sai phân "hàng $i$ chứa $\Delta^ky_i$"

**Input:** bộ mốc con $m=n+1$ mốc liên tiếp; công thức (Gauss I / Gauss II / Stirling / Bessel).

**Output:** chỉ số tương đối $i=p,\dots,p+n$ ($p\le0$); $t_i=i$; bảng $D_{i,k}=\Delta^ky_i$, $0\le k\le n$, $p\le i\le p+n-k$.

**Bước 1 — Mốc trung tâm:** đánh số bộ mốc con $0..n$ theo thứ tự tăng; chọn vị trí $q$ của $x_0$:
* Gauss I, Bessel: $q:=\lfloor n/2\rfloor$;
* Gauss II, Stirling: $q:=\lceil n/2\rceil$.

Khi đó $p:=-q$ (mốc thứ $s$ của bộ con có chỉ số tương đối $s-q$).

**Bước 2 — Biến:** $\bar t:=\dfrac{\bar x-x_0}{h}$.

**Bước 3 — Cột 0:** $D_{i,0}:=y_i$, $i=p..p+n$.

**Bước 4 — Với $k=1..n$, $i=p..p+n-k$:** $D_{i,k}:=D_{i+1,k-1}-D_{i,k-1}$ (mọi $y_i$ có không quá $d$ chữ số thập phân → làm tròn $D_{i,k}$ về $d$ chữ số, vì sai phân đúng $d$ chữ số; khử sai số dấu phẩy động ở bậc cao).

**Bước 5 — Kết thúc:** trả về $p$, $\bar t$, $D$.

---

## 3. Hệ số $c_k$ và bảng tích → $P(t)$

**Input:** bảng $D$ (mục 2); công thức.

**Output:**
* vector $c=(c_0,\dots,c_n)$ và danh sách ô được chọn trong bảng $D$;
* bảng tích: hệ số của $\pi_0,\dots,\pi_n$;
* vector $b=(b_n,\dots,b_0)$ với $P(t)=\sum_l b_lt^l$.

**Bước 1 — Hệ số:** với $k=0..n$ ($k!$ tính dần):
* Gauss I: $c_k:=D_{-\lfloor k/2\rfloor,k}/k!$;
* Gauss II: $c_k:=D_{-\lceil k/2\rceil,k}/k!$;
* Stirling: $c_0:=D_{0,0}$; $k=2j-1$ lẻ: $c_k:=\dfrac{D_{-j,k}+D_{-j+1,k}}{2\,k!}$; $k=2j$ chẵn: $c_k:=D_{-j,k}/k!$;
* Bessel: $k=2j$ chẵn: $c_k:=\dfrac{D_{-j,k}+D_{-j+1,k}}{2\,k!}$; $k=2j+1$ lẻ: $c_k:=D_{-j,k}/k!$.

**Bước 2 — Bảng tích:** $\pi_0:=(1)$; với $k=1..n$, nhân đa thức đi trước với các thừa số bậc nhất theo mục 3, `horner.md`:
* Gauss I / II: $\pi_k:=\pi_{k-1}\cdot(t-z_{k-1})$ với Gauss I: $z_{2j-1}=j$, $z_{2j}=-j$ ($z=0,1,-1,2,-2,\dots$); Gauss II: $z_{2j-1}=-j$, $z_{2j}=j$ ($z=0,-1,1,-2,2,\dots$);
* Stirling: $k=1$: $\pi_1:=t$; $k=2j+1\ge3$: $\pi_k:=\pi_{k-2}\cdot(t-j)\cdot(t+j)$; $k=2j$: $\pi_k:=\pi_{k-1}\cdot t$;
* Bessel: $k=2j$: $\pi_k:=\pi_{k-2}\cdot(t+j-1)\cdot(t-j)$; $k=2j+1$: $\pi_k:=\pi_{k-1}\cdot(t-\tfrac12)$.

**Bước 3 — Cộng dồn:** $b_l:=\sum_{k=0}^{n}c_k\,\pi_{k,l}$ ($\pi_{k,l}$ là hệ số của $t^l$ trong $\pi_k$), $l=0..n$.

**Bước 4 — Kết thúc:** trả về $c$, bảng tích, $b$.

---

## 4. Giá trị, đạo hàm tại $\bar x$ và sai số

**Input:** $b$ (mục 3); $\bar t$, $h$; cấp $k$; chỉ số tương đối $p..p+n$.

**Output:** vector $v=(v_0,\dots,v_k)$, $v_j\approx f^{(j)}(\bar x)$; $E$ với $|f(\bar x)-P(\bar x)|\le M_{n+1}E$.

**Bước 1 — Horner chia lặp:** $d_j:=P^{(j)}(\bar t)$, $j=0..k$, theo mục 2, `horner.md` với $c:=\bar t$.

**Bước 2 — Đạo hàm theo $x$:** $v_j:=d_j/h^j$.

**Bước 3 — Sai số:** $E:=\dfrac{h^{n+1}}{(n+1)!}\prod_{i=p}^{p+n}|\bar t-i|$.

**Bước 4 — Kết thúc:** trả về $v$, $E$.
