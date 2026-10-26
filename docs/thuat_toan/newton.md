# Đa thức nội suy Newton

Quy ước: bộ điểm $(x_i,y_i)$, $i=0..n$, mốc phân biệt, **xếp tăng dần**; đa thức lưu dạng vector hệ số **từ bậc cao xuống bậc thấp** như `horner.md`. Mốc cách đều: $x_i=x_0+ih$, $h>0$; $\Delta y_i=y_{i+1}-y_i$, $\nabla y_i=y_i-y_{i-1}$, $\nabla^ky_n=\Delta^ky_{n-k}$.

| Biến thể | Biến | Đa thức |
|---|---|---|
| Tiến, mốc bất kỳ | $x$ | $P_n(x)=\sum_{k=0}^{n}f[x_0,\dots,x_k]\prod_{i=0}^{k-1}(x-x_i)$ |
| Lùi, mốc bất kỳ | $x$ | $P_n(x)=\sum_{k=0}^{n}f[x_{n-k},\dots,x_n]\prod_{i=0}^{k-1}(x-x_{n-i})$ |
| Tiến, mốc cách đều | $t=\frac{x-x_0}{h}$ | $P_n=\sum_{k=0}^{n}\frac{\Delta^ky_0}{k!}\,t(t-1)\cdots(t-k+1)$ |
| Lùi, mốc cách đều | $t=\frac{x-x_n}{h}$ | $P_n=\sum_{k=0}^{n}\frac{\nabla^ky_n}{k!}\,t(t+1)\cdots(t+k-1)$ |

Sai số: $|f(x)-P_n(x)|\le\dfrac{M_{n+1}}{(n+1)!}|w_{n+1}(x)|$, $w_{n+1}(x)=\prod_{i=0}^n(x-x_i)$.

> Ghi chú: slide `15_NoisuyNewton_2026.pdf` — công thức tỷ sai phân (tr.5), $P_n$, $R_n$ (tr.7), mốc cách đều (tr.12, 14) và ví dụ bảng tỷ sai phân, bảng tích, $P_5$ (tr.9–11) đều đúng, đã kiểm tra bằng `numpy.linalg.solve(np.vander(x), y)`. Ô cuối bảng tỷ sai phân tr.9 bị ngắt dòng: `222.658` / `7302` là một số $222.6587302$. Cách lập đa thức theo $t$ (bảng tích theo $t$, đạo hàm $f'(x)=P'(t)/h$) theo file `VD nội suy mốc cách đều.xlsx`.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| Đa thức Newton tiến | mục 3: TH1 nếu mốc bất kỳ, TH2 nếu mốc cách đều | bảng mục 1 + $\sim n^2$ nhân |
| Đa thức Newton lùi | mục 4: TH1 / TH2 như trên | như trên |
| $f(\bar x)$, $f^{(j)}(\bar x)$, $j=1..k$ | mục 6 trên đa thức đã lập (chỉ lập một trong tiến/lùi); lập cả hai hoặc chưa lập: tiến nếu $|\bar x-x_0|\le|\bar x-x_n|$, lùi nếu ngược lại | $\sim(k+1)n$ nhân |
| Đa thức theo biến $x$ khi mốc cách đều | mục 5 (đổi biến $t\to x$) | $\sim n^2/2$ nhân |
| Bảng dài, chỉ dùng $m$ mốc phù hợp để tính tại $\bar x$ | mục 7 (trích xuất) rồi mục 3/4 + 6 trên bộ mốc con | $\sim m$ phép so sánh |

Mốc cách đều → dùng sai phân (TH2): bảng chỉ có phép trừ, không có phép chia. Bảng (mục 1) lập **một lần** dùng chung cho tiến và lùi: hệ số tiến là đường chéo, hệ số lùi là hàng cuối. Cùng bộ mốc thì tiến và lùi cho cùng một đa thức, chỉ khác thứ tự cộng (sai số làm tròn). Mốc bất kỳ mà $|x_i|$ lớn so với khoảng cách mốc thì hệ số chính tắc rất lớn, triệt tiêu nhau, Horner ở mục 6 mất vài chữ số; mốc cách đều tính theo $t$ (cỡ $0..n$) nên không bị.

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ và hàng $y$ (hoặc 2 cột $x$, $y$); ô tách theo khoảng trắng, `;` hoặc tab; nhãn đầu hàng (`x`, `y`) bỏ qua. Dấu trừ Unicode `−` `–` → `-`; dấu `,` giữa hai chữ số → `.`; bỏ ký tự lạ không phải chữ (vd `*`, khoảng trắng đặc biệt).
* Hàng $x$ và hàng $y$ khác số ô → dừng, báo lỗi.
* Ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp $(x_i,y_i)$; báo vị trí và lý do.
* Mốc trùng: cùng $y$ → giữ 1; khác $y$ nhưng $\max y-\min y\le\varepsilon_y=10^{-3}\max(1,\max_i|y_i|)$ → thay bằng trung bình; ngược lại dừng, báo lỗi.
* Sắp tăng theo $x$ (báo nếu đổi thứ tự); sau bước này các mốc phân biệt. Còn ít nhất 1 mốc ($n\ge0$), ngược lại dừng.
* Kiểm tra cách đều (khi $n\ge1$): $h:=\dfrac{x_n-x_0}{n}$; nếu $|x_{i+1}-x_i-h|\le\delta h$ với mọi $i$ ($\delta=10^{-6}$) → mốc cách đều (TH2), ngược lại mốc bất kỳ (TH1).
* Điểm $\bar x$ (mục 6): đọc như trên; $\bar x\notin[x_0,x_n]$ → cảnh báo ngoại suy. Cấp $k$: số nguyên $\ge0$, ngược lại dừng, báo lỗi.
* Số mốc trích xuất $m$ (mục 7): số nguyên $\ge1$, ngược lại dừng, báo lỗi; $m>n+1$ → dùng cả $n+1$ mốc và báo.

---

## 1. Bảng tỷ sai phân (TH1) / bảng sai phân (TH2)

**Input:** $x=(x_0,\dots,x_n)$, $y=(y_0,\dots,y_n)$; loại mốc TH1 / TH2.

**Output:** bảng tam giác dưới $T_{i,k}$, $0\le k\le i\le n$, với
* TH1: $T_{i,k}=f[x_{i-k},\dots,x_i]$;
* TH2: $T_{i,k}=\Delta^ky_{i-k}=\nabla^ky_i$.

**Bước 1 — Cột 0:** $T_{i,0}:=y_i$, $i=0..n$.

**Bước 2 — Với $k=1,\dots,n$, với $i=k,\dots,n$:**
* TH1: $T_{i,k}:=\dfrac{T_{i,k-1}-T_{i-1,k-1}}{x_i-x_{i-k}}$;
* TH2: $T_{i,k}:=T_{i,k-1}-T_{i-1,k-1}$; nếu mọi $y_i$ có không quá $d$ chữ số thập phân thì $T_{i,k}$ cũng đúng $d$ chữ số → làm tròn $T_{i,k}$ về $d$ chữ số (khử sai số dấu phẩy động tích luỹ ở sai phân bậc cao).

**Bước 3 — Kết thúc:** trả về $T$.

---

## 2. Tổ hợp Newton $\sum_{k=0}^{n}c_k\prod_{i=0}^{k-1}(u-z_i)$ (bảng tích)

**Input:** hệ số $c=(c_0,\dots,c_n)$; nút $z=(z_0,\dots,z_{n-1})$.

**Output:** vector $b=(b_n,\dots,b_0)$ với $b_l$ là hệ số của $u^l$ trong $\sum_{k=0}^{n}c_k\,\omega_k(u)$, $\omega_k(u)=\prod_{i=0}^{k-1}(u-z_i)$.

**Bước 1 — Khởi tạo:** $\omega:=(1)$ (đa thức hằng $\omega_0=1$); $b_0:=c_0$, $b_l:=0$ với $l=1..n$.

**Bước 2 — Với $k=1,\dots,n$:**
* **Bước 2.1 — Bảng tích:** $\omega:=\omega\cdot(u-z_{k-1})$ theo mục 3, `horner.md` (được $\omega_k$, bậc $k$).
* **Bước 2.2 — Cộng dồn:** $b_l:=b_l+c_k\,\omega_l$, $l=0..k$ ($\omega_l$ là hệ số của $u^l$ trong $\omega_k$).

**Bước 3 — Kết thúc:** trả về $b$.

---

## 3. Đa thức nội suy Newton tiến

**Input:** $x$, $y$ đã qua Bước 0; loại mốc TH1 (bất kỳ) / TH2 (cách đều, bước $h$).

**Output:**
* vector $c=(c_0,\dots,c_n)$ — hệ số Newton tiến;
* vector $b=(b_n,\dots,b_0)$ — hệ số $P_n$ theo biến $u$: TH1 $u=x$; TH2 $u=t=\frac{x-x_0}{h}$;
* TH2: thêm vector $a=(a_n,\dots,a_0)$ — hệ số $P_n$ theo biến $x$.

**Bước 1 — Bảng:** $T$ theo mục 1.

**Bước 2 — Hệ số (đường chéo):** với $k=0..n$:
* TH1: $c_k:=T_{k,k}=f[x_0,\dots,x_k]$;
* TH2: $c_k:=\dfrac{T_{k,k}}{k!}=\dfrac{\Delta^ky_0}{k!}$.

**Bước 3 — Nút tích:** với $i=0..n-1$: TH1 $z_i:=x_i$; TH2 $z_i:=i$.

**Bước 4 — Đa thức:** $b$ := tổ hợp Newton (mục 2) với $c$, $z$. TH1: dừng, trả về $c$, $b$ (khi đó $a=b$). TH2: sang Bước 5.

**Bước 5 — Đổi biến:** $a$ := mục 5 với $b$, $s:=x_0$, $h$.

**Bước 6 — Kết thúc:** trả về $c$, $b$, $a$.

---

## 4. Đa thức nội suy Newton lùi

**Input:** như mục 3.

**Output:** như mục 3, với TH2 $u=t=\frac{x-x_n}{h}$.

**Bước 1 — Bảng:** $T$ theo mục 1 (dùng lại nếu đã lập ở mục 3).

**Bước 2 — Hệ số (hàng cuối):** với $k=0..n$:
* TH1: $c_k:=T_{n,k}=f[x_{n-k},\dots,x_n]$;
* TH2: $c_k:=\dfrac{T_{n,k}}{k!}=\dfrac{\nabla^ky_n}{k!}$.

**Bước 3 — Nút tích:** với $i=0..n-1$: TH1 $z_i:=x_{n-i}$; TH2 $z_i:=-i$.

**Bước 4 — Đa thức:** $b$ := tổ hợp Newton (mục 2) với $c$, $z$. TH1: dừng, trả về $c$, $b$. TH2: sang Bước 5.

**Bước 5 — Đổi biến:** $a$ := mục 5 với $b$, $s:=x_n$, $h$.

**Bước 6 — Kết thúc:** trả về $c$, $b$, $a$.

---

## 5. Đổi biến $t\to x$: $t=\dfrac{x-s}{h}$

**Input:** vector $b=(b_n,\dots,b_0)$ — hệ số đa thức theo $t$; $s\in\mathbb R$; $h>0$.

**Output:** vector $a=(a_n,\dots,a_0)$ với $\sum_l a_lx^l=\sum_l b_l\left(\frac{x-s}{h}\right)^l$.

**Bước 1 — Khởi tạo:** $a:=(b_n)$ (đa thức hằng).

**Bước 2 — Với $j=n-1,n-2,\dots,0$:**
* **Bước 2.1 — Nhân:** $a:=a\cdot(x-s)$ theo mục 3, `horner.md`.
* **Bước 2.2 — Chia $h$:** $a_l:=a_l/h$ với mọi $l$.
* **Bước 2.3 — Cộng:** $a_0:=a_0+b_j$.

**Bước 3 — Kết thúc:** trả về $a$.

---

## 6. Giá trị, đạo hàm cấp $0..k$ tại $\bar x$ và đánh giá sai số

**Input:** vector $b$ của mục 3 hoặc 4 (đa thức theo $u$); loại mốc; mốc $x$; điểm $\bar x$; cấp $k\in\mathbb N$.

**Output:**
* vector $v=(v_0,\dots,v_k)$ với $v_j\approx f^{(j)}(\bar x)$;
* $E=\dfrac{|w_{n+1}(\bar x)|}{(n+1)!}$, khi đó $|f(\bar x)-P_n(\bar x)|\le M_{n+1}E$.

**Bước 1 — Biến:**
* TH1: $\bar u:=\bar x$, $g:=1$;
* TH2: $\bar u:=\bar t=\dfrac{\bar x-s}{h}$ với $s=x_0$ (tiến) hoặc $s=x_n$ (lùi), $g:=h$.

**Bước 2 — Horner chia lặp:** $d_j:=P_n^{(j)}(\bar u)$, $j=0..k$, theo mục 2, `horner.md` với vector $b$ và $c:=\bar u$.

**Bước 3 — Đạo hàm theo $x$:** $v_j:=d_j/g^j$, $j=0..k$.

**Bước 4 — Sai số:** $E:=\dfrac{1}{(n+1)!}\prod_{i=0}^{n}|\bar x-x_i|$.

**Bước 5 — Kết thúc:** trả về $v$ và $E$.

---

## 7. Trích xuất $m$ mốc gần $\bar x$ nhất

Sai số $|f(\bar x)-P(\bar x)|\le\frac{M_m}{m!}\prod|\bar x-x_i|$ nhỏ nhất khi bộ mốc gồm $m$ mốc có $|\bar x-x_i|$ nhỏ nhất → kết nạp dần mốc gần $\bar x$ nhất về cả hai phía.

**Input:** mốc $x=(x_0,\dots,x_n)$ tăng dần, $y=(y_0,\dots,y_n)$ (đã qua Bước 0); điểm $\bar x$; số mốc $m$, $1\le m\le n+1$.

**Output:**
* chỉ số $L\le R$ với $R-L+1=m$; bộ mốc con $(x_L,\dots,x_R)$, $(y_L,\dots,y_R)$ (vẫn tăng dần, cách đều nếu bảng gốc cách đều);
* thứ tự kết nạp $j_1,j_2,\dots,j_m$ (mốc gần $\bar x$ nhất trước).

**Bước 1 — Mốc gần nhất:** $j:=\arg\min_i|\bar x-x_i|$ (bằng nhau → lấy chỉ số nhỏ); $L:=R:=j$; $j_1:=j$.

**Bước 2 — Kết nạp dần, với $s=2,\dots,m$:**
* TH1 $L=0$: $R:=R+1$, $j_s:=R$;
* TH2 $R=n$: $L:=L-1$, $j_s:=L$;
* TH3 còn lại: nếu $\bar x-x_{L-1}\le x_{R+1}-\bar x$ thì $L:=L-1$, $j_s:=L$; ngược lại $R:=R+1$, $j_s:=R$.

**Bước 3 — Kết thúc:** trả về $L$, $R$, bộ mốc con và $(j_1,\dots,j_m)$.

Mốc cách đều, không chạm biên: $m$ lẻ → $x_{j_1}$ nằm chính giữa bộ mốc con và $|\bar x-x_{j_1}|\le\frac h2$ (hợp Gauss, Stirling); $m$ chẵn → $\bar x$ nằm giữa hai mốc chính giữa (hợp Bessel). Chạm biên → bộ mốc lệch về phía còn mốc.
