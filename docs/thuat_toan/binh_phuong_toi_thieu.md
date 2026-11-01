# Phương pháp bình phương tối thiểu

Quy ước (theo slide): dữ liệu $(x_i,y_i)$, $i=1..n$; hệ hàm cơ sở $\varphi_1,\dots,\varphi_m$; hàm thực nghiệm $g(x)=\sum_{j=1}^{m}a_j\varphi_j(x)$. Kết quả in dạng vector $a=(a_1,\dots,a_m)$ theo đúng thứ tự cơ sở người dùng nhập.

$$\Phi=\big(\varphi_j(x_i)\big)_{n\times m},\qquad M=\Phi^t\Phi,\quad d=\Phi^ty,\quad Ma=d,\qquad \sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(g(x_i)-y_i\big)^2}.$$

| Dạng | Đưa về tuyến tính | Điều kiện |
|---|---|---|
| $y=\sum a_j\varphi_j(x)$ | sẵn tuyến tính theo $a$ | $\varphi_j$ độc lập tuyến tính trên lưới ($M$ không suy biến) |
| $y=a\,e^{b_1\varphi_1(x)+\dots+b_m\varphi_m(x)}$ | $\ln(sy)=\ln(sa)+b_1\varphi_1+\dots+b_m\varphi_m$, $s=\operatorname{sign}y$ | mọi $y_i$ cùng dấu, khác 0; $\varphi_j$ không là hằng (hằng trùng vai trò với $\ln a$) |
| $y=a\,x^b$ | $\ln(sy)=\ln(sa)+b\ln x$ (dạng trên với $\varphi_1=\ln x$) | mọi $x_i>0$; $y_i$ cùng dấu, khác 0 |

> Ghi chú: slide `19_binhphuongtoithieu_20261.pdf` — hệ chuẩn bậc nhất, bậc hai, tổng quát $Ma=\Phi^ty$ ($M=\Phi^t\Phi$) và cách tuyến tính hoá $y=ae^{b_1\varphi_1+\dots}$ (kể cả trường hợp $y_i<0$: $\ln(-y)=\ln(-a)+\dots$) đúng (tr.5–9). Tr.7 viết $S=a^tMa-2y^t\Phi a+y^ty$, $S'=2a^tM-2y^t\Phi=0$ — đúng.
>
> **Lưu ý tuyến tính hoá:** bình phương tối thiểu trên $\ln y$ cực tiểu hoá $\sum(\ln y_i-\ln g_i)^2\approx\sum\big((y_i-g_i)/y_i\big)^2$ — tức sai số **tương đối**, nên các điểm có $|y_i|$ rất nhỏ (cỡ nhiễu đo) bị khuếch đại. Data câu 23c có đuôi $y\approx10^{-3}$ toàn nhiễu: tuyến tính hoá thẳng cho $\sigma\approx1.1$ (rất tệ) trong khi nghiệm đúng của bài toán $\sum(y_i-g_i)^2\to\min$ có $\sigma\approx0.0042$. Vì vậy dạng mũ/luỹ thừa có thêm **mục 4 (hiệu chỉnh Gauss–Newton)**, luôn so sánh $\sigma$ trên $y$ gốc. Mục 4 ẩn mặc định (kết quả mặc định như slide/lời giải: chỉ tuyến tính hoá), bật bằng cờ `--gn` khi chạy script.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| $g$ tuyến tính theo tham số (đa thức, $ax+b/x$, $ax^2+b\cos x+c$, …) | mục 1 (+ mục 2 giải hệ) | $\sim nm^2$ lập $M$ + $\sim m^3/6$ giải (Cholesky) |
| $y=ae^{\sum b_j\varphi_j}$, $y=ax^b$ — theo slide | mục 3 (tuyến tính hoá) | như mục 1 |
| như trên, cực tiểu sai số trên $y$ gốc | mục 3 rồi mục 4 (hiệu chỉnh, cờ `--gn`) | mỗi lần lặp như mục 1 |

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ / hàng $y$, hoặc cặp cột $x,y$ (file `.csv`/`.xlsx`/`.txt` dạng bảng; file có **nhiều bộ dữ liệu cạnh nhau** — vd data câu 23 có 4 bộ "Câu a…d" — thì liệt kê các bộ và cho chọn). Dấu trừ Unicode → `-`; `,` giữa hai chữ số → `.`; bỏ ký tự lạ; ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp, báo vị trí và lý do.
* **Không** gộp mốc trùng $x$ (bình phương tối thiểu cho phép nhiều quan sát tại cùng $x$) — chỉ báo số mốc trùng. Không cần sắp xếp.
* Cơ sở: biểu thức theo `x`, cách nhau bởi `;` (vd `x; 1/x`, `x^2; cos(x); 1`), hàm cho phép: `sin cos tan exp ln log sqrt abs arctan`, hằng `pi e`; `^` hiểu là luỹ thừa. Biểu thức sai cú pháp → dừng, báo lỗi. Điểm làm $\varphi_j(x_i)$ không xác định (vd $1/x$ tại $x=0$, $\ln x$ tại $x\le0$) → loại điểm, báo.
* Dạng mũ / luỹ thừa: $y_i=0$ hoặc trái dấu với đa số → loại điểm, báo (không lấy $\ln$ được); loại quá nửa → dừng. Dạng mũ có $\varphi_j$ là hằng trên lưới → dừng, báo (trùng vai trò với $a$).
* Cần $n\ge m$ điểm (số tham số), ngược lại dừng, báo lỗi.

---

## 1. Hàm thực nghiệm tuyến tính theo tham số

**Input:** dữ liệu $(x_i,y_i)$, $i=1..n$; cơ sở $\varphi_1..\varphi_m$; trọng số $w_i>0$ (mặc định $w_i=1$; mục 4 dùng trọng số khác).

**Output:** vector $a=(a_1,\dots,a_m)$; sai số trung bình phương $\sigma$; bảng $\Phi$, $M$, $d$.

**Bước 1 — Ma trận cơ sở:** $\Phi_{ij}:=\varphi_j(x_i)$, $i=1..n$, $j=1..m$.

**Bước 2 — Hệ chuẩn:** với $j,k=1..m$: $M_{jk}:=\sum_{i=1}^{n}w_i\Phi_{ij}\Phi_{ik}$, $d_j:=\sum_{i=1}^{n}w_i\Phi_{ij}y_i$.

**Bước 3 — Giải:** $Ma=d$ theo mục 2.

**Bước 4 — Sai số:** $g_i:=\sum_j a_j\Phi_{ij}$; $\sigma:=\sqrt{\frac1n\sum_i(g_i-y_i)^2}$.

**Bước 5 — Kết thúc:** trả về $a$, $\sigma$.

---

## 2. Giải hệ chuẩn $Ma=d$ (Cholesky $M=LL^T$)

**Input:** $M\in\mathbb R^{m\times m}$ đối xứng, $d\in\mathbb R^m$. **Output:** $a$; $L$ (tam giác dưới), $u$; hoặc thông báo suy biến.

**Bước 1 — Phân tích, với $j=1..m$:**
* **1.1 — Đường chéo:** $p:=M_{jj}-\sum_{k<j}L_{jk}^2$; nếu $p\le10^{-12}\max_k|M_{kk}|$ → dừng, báo "M không xác định dương: các hàm cơ sở phụ thuộc tuyến tính trên dữ liệu"; $L_{jj}:=\sqrt p$.
* **1.2 — Cột $j$:** với $i=j+1..m$: $L_{ij}:=\Big(M_{ij}-\sum_{k<j}L_{ik}L_{jk}\Big)/L_{jj}$.

**Bước 2 — Thế xuôi $Lu=d$, với $j=1..m$:** $u_j:=\Big(d_j-\sum_{k<j}L_{jk}u_k\Big)/L_{jj}$.

**Bước 3 — Thế ngược $L^Ta=u$, với $j=m..1$:** $a_j:=\Big(u_j-\sum_{k>j}L_{kj}a_k\Big)/L_{jj}$.

**Bước 4 — Kết thúc:** trả về $a$, $L$, $u$.

---

## 3. Dạng mũ $y=a\,e^{b_1\varphi_1+\dots+b_m\varphi_m}$ và luỹ thừa $y=a\,x^b$ (tuyến tính hoá)

**Input:** dữ liệu đã qua Bước 0; cơ sở $\varphi_1..\varphi_m$ (luỹ thừa: $m=1$, $\varphi_1=\ln x$).

**Output:** $a$, $b=(b_1,\dots,b_m)$; $\sigma$ trên $y$ gốc.

**Bước 1 — Dấu:** $s:=\operatorname{sign}(y_i)$ (chung cho mọi $i$ sau Bước 0).

**Bước 2 — Đổi biến:** $z_i:=\ln(s\,y_i)$; cơ sở mới $(1,\varphi_1,\dots,\varphi_m)$.

**Bước 3 — Bình phương tối thiểu:** mục 1 với dữ liệu $(x_i,z_i)$, cơ sở $m+1$ hàm $(1,\varphi_1,\dots,\varphi_m)$, $w_i=1$ → vector hệ số, đặt tên $(c_0,c_1,\dots,c_m)$ ($c_0$ ứng với hàm $1$).

**Bước 4 — Trả biến:** $a:=s\,e^{c_0}$, $b_j:=c_j$.

**Bước 5 — Sai số trên $y$ gốc:** $g_i:=a\,e^{\sum_jb_j\varphi_j(x_i)}$; $\sigma:=\sqrt{\frac1n\sum_i(g_i-y_i)^2}$ (và $\sigma_z$ trên $z$ để tham khảo).

**Bước 6 — Kết thúc:** trả về $a$, $b$, $\sigma$.

---

## 4. Hiệu chỉnh Gauss–Newton: $\sum_i(y_i-g(x_i))^2\to\min$ với $g=s\,e^{c_0+\sum c_j\varphi_j}$

Tuyến tính hoá quanh $c$ hiện tại: $g(c+\delta)\approx g\,(1+\delta_0+\sum\delta_j\varphi_j)$, nên một bước Gauss–Newton chính là mục 1 với dữ liệu $z_i=\ln(sg_i)+\frac{y_i-g_i}{g_i}$ và trọng số $w_i=g_i^2$.

**Input:** dữ liệu, cơ sở $(1,\varphi_1..\varphi_m)$, $s$; sai số $\varepsilon$ (mặc định $10^{-10}$); số lần lặp tối đa $N$ (mặc định 100).

**Output:** $c=(c_0,\dots,c_m)$, $a=s\,e^{c_0}$, $b_j=c_j$, $\sigma$; hoặc "Không hội tụ".

**Bước 1 — Khởi tạo:** $c^{(0)}$ := mục 1 với $z_i=\ln(sy_i)$, $w_i=y_i^2$ (xấp xỉ sai số tuyệt đối ngay từ đầu).

**Bước 2 — Lặp, với $j=0,1,\dots,N-1$:**
* **2.1 — Giá trị:** $g_i:=s\,e^{c_0^{(j)}+\sum_kc_k^{(j)}\varphi_k(x_i)}$.
* **2.2 — Dữ liệu, trọng số:** $z_i:=\ln(sg_i)+\dfrac{y_i-g_i}{g_i}$, $w_i:=g_i^2$.
* **2.3 — Giải:** $c^{(j+1)}$ := mục 1 với dữ liệu $(x_i,z_i)$, cơ sở $(1,\varphi_1,\dots,\varphi_m)$, trọng số $w_i$.
* **2.4 — Dừng:** nếu $\max_k|c_k^{(j+1)}-c_k^{(j)}|<\varepsilon\,(1+\max_k|c_k^{(j+1)}|)$: trả về $c^{(j+1)}$, dừng thuật toán.

**Bước 3 — Không hội tụ:** hết $N$ lần → báo "Không hội tụ sau $N$ lần lặp", giữ kết quả tuyến tính hoá (mục 3).

**Bước 4 — Kết thúc:** $a:=s\,e^{c_0}$, $b_k:=c_k$, $\sigma$ như Bước 5 mục 3; so sánh $\sigma$ với mục 3, chọn kết quả có $\sigma$ nhỏ hơn.
