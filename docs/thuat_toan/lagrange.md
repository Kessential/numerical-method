# Đa thức nội suy Lagrange

Quy ước: bộ điểm $(x_i,y_i)$, $i=0..n$, mốc phân biệt, **xếp tăng dần**; đa thức lưu dạng vector hệ số **từ bậc cao xuống bậc thấp** như `horner.md` ($a_i$ là hệ số của $x^i$).

$$w_{n+1}(x)=\prod_{i=0}^{n}(x-x_i),\qquad D_i=\prod_{j=0,\,j\ne i}^{n}(x_i-x_j),\qquad P_n(x)=\sum_{i=0}^{n}\frac{y_i}{D_i}\cdot\frac{w_{n+1}(x)}{x-x_i}$$

$$|f(x)-P_n(x)|\le\frac{M_{n+1}}{(n+1)!}\,|w_{n+1}(x)|,\qquad M_{n+1}=\max_{[x_0,x_n]}|f^{(n+1)}|$$

> Ghi chú: slide `14_NoisuyLagrange 20261.pdf` tr.8 (ví dụ $y=3^x$, mốc $-1,0,1$) đặt tên đa thức cơ bản là $L_1,L_2,L_3$ cho các mốc $x_0,x_1,x_2$, lệch chỉ số so với công thức $P_n=\sum_{i=0}^n y_iL_i$ ở tr.4 (đúng là $L_0,L_1,L_2$); kết quả $L(x)=\frac23x^2+\frac43x+1$, $L(0.1)=1.14$ đúng. Công thức tr.5–6 đúng; đã kiểm tra bằng `numpy.linalg.solve(np.vander(x), y)` và file `Ví dụ nội suy Lagrange.xlsx`.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| Hệ số $P_n(x)$ dạng chính tắc | Bảng tích + bảng chia (mục 1) | $\sim\frac72n^2$ nhân |
| Giá trị $P_n(\bar x)$ | Công thức trực tiếp (mục 2) | $\sim n^2$ nhân (tính $D_i$), mỗi $\bar x$ thêm $\sim 2n$ |
| Đạo hàm $P_n^{(j)}(\bar x)$, $j=0..k$ | Mục 1 rồi Horner chia lặp (mục 3) | mục 1 + $\sim(k+1)n$ nhân |

$D_i$ tính một lần, dùng chung cho mục 1 và mục 2. Giá trị $P_n(\bar x)$ luôn tính theo mục 2, kể cả khi đã lập hệ số: khi $|x_i|$ lớn so với khoảng cách mốc, hệ số chính tắc rất lớn và triệt tiêu nhau nên Horner trên hệ số chính tắc mất vài chữ số.

> Ghi chú: file `Ví dụ nội suy Lagrange.xlsx` (Sheet2, $\bar x=3.95$) tính bằng Horner trên hệ số chính tắc (cỡ $10^6$) được $P(3.95)=17.01307655$; giá trị đúng (tính bằng phân số) là $17.0130764509$, đúng như mục 2. Đạo hàm vẫn tính qua hệ số chính tắc nên mang sai số cùng cỡ ($\sim10^{-7}$ ở ví dụ này).

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ và hàng $y$ (hoặc 2 cột $x$, $y$); ô tách theo khoảng trắng, `;` hoặc tab; nhãn đầu hàng (`x`, `y`) bỏ qua. Dấu trừ Unicode `−` `–` → `-`; dấu `,` giữa hai chữ số → `.`; bỏ ký tự lạ không phải chữ (vd `*`, khoảng trắng đặc biệt).
* Hàng $x$ và hàng $y$ khác số ô → dừng, báo lỗi.
* Ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp $(x_i,y_i)$; báo vị trí và lý do.
* Mốc trùng: cùng $y$ → giữ 1; khác $y$ nhưng $\max y-\min y\le\varepsilon_y=10^{-3}\max(1,\max_i|y_i|)$ → thay bằng trung bình; ngược lại dừng, báo lỗi (không có đa thức nào đi qua cả hai điểm).
* Sắp tăng theo $x$ (báo nếu đổi thứ tự); sau bước này các mốc phân biệt. Còn ít nhất 1 mốc ($n\ge0$), ngược lại dừng.
* Điểm $\bar x$ (mục 2, 3): đọc như trên; $\bar x\notin[x_0,x_n]$ → cảnh báo ngoại suy. Cấp $k$ (mục 3): số nguyên $\ge0$, ngược lại dừng, báo lỗi.

---

## 1. Đa thức nội suy Lagrange dạng chính tắc

**Input:** vector mốc $x=(x_0,\dots,x_n)$ phân biệt; vector $y=(y_0,\dots,y_n)$.

**Output:**
* vector $a=(a_n,\dots,a_0)\in\mathbb R^{n+1}$ với $P_n(x)=a_nx^n+\dots+a_1x+a_0$;
* vector $D=(D_0,\dots,D_n)$.

**Bước 1 — Bảng tích:** hệ số $p=(1,p_n,\dots,p_0)$ của $w_{n+1}(x)$ theo mục 4, `horner.md`.

**Bước 2 — Khởi tạo:** $a_l:=0$, $l=0..n$.

**Bước 3 — Với $i=0,1,\dots,n$:**
* **Bước 3.1 — Bảng chia:** chia $w_{n+1}(x)$ cho $(x-x_i)$ theo mục 1, `horner.md` → thương $q^{(i)}=(q^{(i)}_n,\dots,q^{(i)}_0)$ (dư bằng 0).
* **Bước 3.2 — Hệ số:** $D_i:=\prod_{j=0,\,j\ne i}^{n}(x_i-x_j)$.
* **Bước 3.3 — Cộng dồn:** $a_l:=a_l+\dfrac{y_i}{D_i}\,q^{(i)}_l$, $l=0..n$.

**Bước 4 — Kết thúc:** trả về $a$ và $D$.

Hàng $i$ của bảng chia chia cho $D_i$ là hệ số của đa thức Lagrange cơ bản $L_i(x)$.

---

## 2. Giá trị $P_n(\bar x)$ (không lập đa thức)

**Input:** $x$, $y$ như mục 1; điểm $\bar x\in\mathbb R$.

**Output:** $P_n(\bar x)$; $w_{n+1}(\bar x)$.

**Bước 1 — Trùng mốc:** nếu $\bar x=x_m$ với $m$ nào đó: $P_n(\bar x):=y_m$, $w_{n+1}(\bar x):=0$, dừng thuật toán; trái lại sang Bước 2.

**Bước 2 — Tích:** $w:=\prod_{i=0}^{n}(\bar x-x_i)$.

**Bước 3 — Hệ số:** $D_i$ như Bước 3.2 mục 1 (dùng lại nếu đã tính), $i=0..n$.

**Bước 4 — Tổng:** $S:=\displaystyle\sum_{i=0}^{n}\frac{y_i}{D_i\,(\bar x-x_i)}$.

**Bước 5 — Kết thúc:** $P_n(\bar x):=w\,S$; trả về $P_n(\bar x)$ và $w$.

---

## 3. Đạo hàm cấp $0..k$ tại $\bar x$ và đánh giá sai số

**Input:** vector hệ số $a$ (mục 1); mốc $x$; điểm $\bar x$; cấp $k\in\mathbb N$.

**Output:**
* vector $v=(v_0,\dots,v_k)$ với $v_j=P_n^{(j)}(\bar x)\approx f^{(j)}(\bar x)$;
* $E=\dfrac{|w_{n+1}(\bar x)|}{(n+1)!}$, khi đó $|f(\bar x)-P_n(\bar x)|\le M_{n+1}E$.

**Bước 1 — Horner chia lặp:** $v$ theo mục 2, `horner.md` với $c:=\bar x$.

**Bước 2 — Sai số:** $E:=\dfrac{1}{(n+1)!}\prod_{i=0}^{n}|\bar x-x_i|$.

**Bước 3 — Kết thúc:** trả về $v$ và $E$.
