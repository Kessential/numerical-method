# Nội suy ngược — giải $f(x)=\bar y$ từ bảng dữ liệu

Quy ước: bảng $(x_i,y_i)$, $i=0..n$, $y_i=f(x_i)$, mốc phân biệt **xếp tăng dần**; $g_i=y_i-\bar y$. Mốc cách đều: $x_i=x_0+ih$; $\Delta y_i=y_{i+1}-y_i$, $\nabla y_i=y_i-y_{i-1}$.

| Phương pháp | Điều kiện | Ý tưởng |
|---|---|---|
| Hàm ngược | $f$ đơn điệu trên đoạn chứa các mốc dùng | nội suy $x=f^{-1}(y)$ qua các mốc $(y_j,x_j)$, thay $y=\bar y$ |
| Lặp (Newton tiến) | mốc cách đều, khoảng cách ly $(x_k,x_{k+1})$ | $\bar y=P(t)$, $t=\varphi(t)=\dfrac{\bar y-y_k}{\Delta y_k}-\dfrac{1}{\Delta y_k}\displaystyle\sum_{j\ge2}\frac{\Delta^jy_k}{j!}t(t-1)\cdots(t-j+1)$, $x=x_k+th$ |
| Lặp (Newton lùi) | như trên, xuất phát từ $x_{k+1}$ | $t=\psi(t)=\dfrac{\bar y-y_{k+1}}{\nabla y_{k+1}}-\dfrac{1}{\nabla y_{k+1}}\displaystyle\sum_{j\ge2}\frac{\nabla^jy_{k+1}}{j!}t(t+1)\cdots(t+j-1)$, $x=x_{k+1}+th$ |

Sai số hàm ngược: $|x^*-\bar x|\le\dfrac{\max|(f^{-1})^{(m)}|}{m!}\prod_j|\bar y-y_j|$ — nhỏ khi chọn các mốc có $|y_j-\bar y|$ nhỏ nhất. Lặp hội tụ khi $|\varphi'(t)|<1$ quanh nghiệm.

> Ghi chú: slide `17_NoisuyNguoc_20261.pdf` — công thức lặp Newton tiến (tr.6–7) và lùi (tr.8–9) đúng: $t_0=\frac{\bar y-y_k}{\Delta y_k}$, $t_{j+1}=\varphi(t_j)$, $x=x_k+t_{j+1}h$; với Newton lùi $t\in[-1,0]$ và $x=x_{k+1}+th$. Slide không nêu tiêu chuẩn dừng; ở đây dừng khi $|x_{j+1}-x_j|=h|t_{j+1}-t_j|<\varepsilon$. Đã kiểm tra bằng thay ngược nghiệm vào đa thức nội suy trực tiếp $y(x)$.
>
> Lưu ý: gần điểm cực trị của bảng ($\Delta y_k$ nhỏ) hàm ngược có đạo hàm rất lớn nên **phương pháp hàm ngược kém chính xác** (vd data câu 19 với $\bar y=3.15$, sai cỡ $10^{-2}$); phương pháp lặp vẫn chính xác vì nội suy $y$ theo $x$.

**Chọn biến thể theo mục đích:**

| Mục đích | Biến thể | Chi phí |
|---|---|---|
| Liệt kê mọi khoảng chứa nghiệm | mục 1 | $n$ phép nhân dấu |
| Các khoảng đơn điệu | mục 2 | $n$ phép trừ |
| Nghiệm, mốc bất kỳ / xa cực trị | mục 3 (hàm ngược) trên từng khoảng cách ly | bảng tỷ sai phân $\sim m^2/2$ phép chia |
| Nghiệm, mốc cách đều / gần cực trị | mục 4 (lặp): TH1 tiến nếu đủ $m$ mốc bên phải, TH2 lùi nếu không | bảng sai phân $\sim m^2/2$ + mỗi lần lặp $\sim m$ nhân |

**Bước 0 — Xử lý dữ liệu (dùng chung):**
* Đọc bảng: hàng $x$ và hàng $y$ (hoặc 2 cột, file `.csv`/`.xlsx`); dấu trừ Unicode → `-`; `,` giữa hai chữ số → `.`; bỏ ký tự lạ; ô rỗng, ô chữ, NaN, $\pm\infty$ → loại cả cặp, báo vị trí và lý do.
* Mốc trùng: cùng $y$ → giữ 1; chênh $\le\varepsilon_y=10^{-3}\max(1,\max|y_i|)$ → lấy trung bình; ngược lại dừng, báo lỗi. Sắp tăng theo $x$ (báo). Cần ít nhất 2 mốc.
* $\bar y$: đọc như trên; $\bar y\notin[\min y_i,\max y_i]$ → báo "không có nghiệm trong bảng" cho $\bar y$ đó.
* Số mốc dùng $m\ge2$ (nguyên); $\varepsilon>0$; $N\ge1$ (nguyên); sai → dừng, báo lỗi.
* Mục 4 cần mốc cách đều ($|x_{i+1}-x_i-h|\le\delta h$, $\delta=10^{-6}$); không thoả → bỏ mục 4, báo, dùng mục 3.

---

## 1. Khoảng cách ly nghiệm của $f(x)=\bar y$

**Input:** $x$, $y$ (đã qua Bước 0); $\bar y$.

**Output:** danh sách nghiệm đúng tại mốc $\{x_i: y_i=\bar y\}$ và danh sách khoảng cách ly $\{(x_i,x_{i+1}): g_ig_{i+1}<0\}$, theo thứ tự tăng của $x$.

**Bước 1 — Độ lệch:** $g_i:=y_i-\bar y$, $i=0..n$.

**Bước 2 — Với $i=0..n$:**
* **2.1 — Nghiệm tại mốc:** nếu $g_i=0$: thêm $x_i$ vào danh sách nghiệm đúng.
* **2.2 — Đổi dấu:** nếu $i<n$ và $g_ig_{i+1}<0$: thêm $(x_i,x_{i+1})$ vào danh sách khoảng cách ly.

**Bước 3 — Kết thúc:** trả về hai danh sách (cả hai rỗng → không có nghiệm trong bảng).

Giả thiết lưới đủ mịn: mỗi khoảng $(x_i,x_{i+1})$ chứa không quá 1 nghiệm. Trường hợp đặc biệt: có đoạn hằng (mục 2) với $y=\bar y$ → theo bảng, mọi $x$ trong đoạn đều là nghiệm — báo riêng.

---

## 2. Các khoảng đơn điệu

**Input:** $x$, $y$ (đã qua Bước 0, $n\ge1$).

**Output:** danh sách đoạn $[x_a,x_b]$ kèm chiều (tăng / giảm / hằng), phủ kín $[x_0,x_n]$, hai đoạn liền nhau chung một mốc (mốc cực trị).

**Bước 1 — Dấu sai phân:** $s_i:=\operatorname{sign}(y_{i+1}-y_i)$, $i=0..n-1$.

**Bước 2 — Khởi tạo:** $a:=0$.

**Bước 3 — Với $i=1..n-1$:** nếu $s_i\ne s_{i-1}$: ghi đoạn $[x_a,x_i]$ với chiều $s_{i-1}$; $a:=i$.

**Bước 4 — Đoạn cuối:** ghi $[x_a,x_n]$ với chiều $s_{n-1}$.

**Bước 5 — Kết thúc:** trả về danh sách đoạn.

---

## 3. Phương pháp hàm ngược

**Input:** $x$, $y$; $\bar y$; một khoảng cách ly $(x_k,x_{k+1})$ nằm trong đoạn đơn điệu $[x_a,x_b]$ (mục 2, chiều tăng hoặc giảm); số mốc $m$.

**Output:** nghiệm gần đúng $\bar x$; bảng tỷ sai phân; bảng số hạng (để ước lượng sai số).

**Bước 1 — Chọn mốc:** kết nạp dần mốc có $|y_j-\bar y|$ nhỏ nhất trong $[a,b]$:
* **1.1 — Khởi tạo:** $L:=k$, $R:=k+1$.
* **1.2 — Khi $R-L+1<m$:** TH1 $L=a$ và $R=b$: dừng kết nạp, báo "đoạn đơn điệu chỉ có $R-L+1$ mốc"; TH2 $L=a$: $R:=R+1$; TH3 $R=b$: $L:=L-1$; TH4 còn lại: nếu $|y_{L-1}-\bar y|\le|y_{R+1}-\bar y|$ thì $L:=L-1$, ngược lại $R:=R+1$.

**Bước 2 — Đổi vai:** $u_s:=y_{L+s}$, $v_s:=x_{L+s}$, $s=0..R-L$; nếu đoạn giảm thì đảo thứ tự để $u_0<u_1<\dots$ (các $u_s$ phân biệt vì $f$ đơn điệu chặt).

**Bước 3 — Bảng tỷ sai phân:** $T$ của $v$ theo $u$ theo mục 1 (TH1), `newton.md`; $c_j:=T_{j,j}=v[u_0,\dots,u_j]$.

**Bước 4 — Giá trị tại $\bar y$ (Newton tiến):** $\omega_0:=1$, $S:=c_0$; với $j=1..R-L$: $\omega_j:=\omega_{j-1}(\bar y-u_{j-1})$, $S:=S+c_j\omega_j$.

**Bước 5 — Kết thúc:** $\bar x:=S$; số hạng cuối $|c_{R-L}\,\omega_{R-L}|$ là ước lượng sai số; trả về $\bar x$.

---

## 4. Phương pháp lặp (mốc cách đều)

**Input:** $x$, $y$ cách đều bước $h$; $\bar y$; khoảng cách ly $(x_k,x_{k+1})$; số mốc $m$; sai số $\varepsilon$; số lần lặp tối đa $N$.

**Output:** nghiệm $\bar x$, số lần lặp, các $t_j$; hoặc thông báo "Không hội tụ".

**Bước 1 — Chọn hướng:** $m:=\min(m,n+1)$.
* TH1 (tiến) nếu $k+m-1\le n$: mốc $x_k,\dots,x_{k+m-1}$, $s:=k$;
* TH2 (lùi) nếu không mà $k+2-m\ge0$: mốc $x_{k+2-m},\dots,x_{k+1}$, $s:=k+1$;
* còn lại: $m:=\max(n-k+1,\,k+2)$ rồi chọn lại TH1/TH2 (báo).

**Bước 2 — Sai phân:** bảng $T$ theo mục 1 (TH2), `newton.md`, với Input là $m$ mốc vừa chọn (đánh số lại $0..m-1$); TH1: $d_j:=T_{j,j}=\Delta^jy_k$ (đường chéo); TH2: $d_j:=T_{m-1,j}=\nabla^jy_{k+1}$ (hàng cuối); $j=0..m-1$.

**Bước 3 — Hàm lặp:** với $\sigma=-1$ (TH1), $\sigma=+1$ (TH2):
$$\varphi(t)=\frac{\bar y-d_0}{d_1}-\frac{1}{d_1}\sum_{j=2}^{m-1}\frac{d_j}{j!}\prod_{l=0}^{j-1}(t+\sigma l).$$

**Bước 4 — Khởi tạo:** $t_0:=\dfrac{\bar y-d_0}{d_1}$ ($d_1\ne0$ vì $g_kg_{k+1}<0$).

**Bước 5 — Lặp, với $j=0,1,\dots,N-1$:**
* **5.1:** $t_{j+1}:=\varphi(t_j)$.
* **5.2 — Dừng:** nếu $h\,|t_{j+1}-t_j|<\varepsilon$: $\bar x:=x_s+t_{j+1}h$, trả về $\bar x$, $j+1$; dừng thuật toán.

**Bước 6 — Không hội tụ:** hết $N$ lần lặp → báo "Không hội tụ sau $N$ lần lặp", trả về $t_N$ để tham khảo.

Kiểm tra hội tụ sau khi có nghiệm: $q=|\varphi'(t^*)|<1$ ($q$ càng nhỏ hội tụ càng nhanh, sai số $|t^*-t_{j+1}|\le\frac{q}{1-q}|t_{j+1}-t_j|$).
