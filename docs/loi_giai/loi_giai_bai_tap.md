# LỜI GIẢI BÀI TẬP PHƯƠNG PHÁP SỐ (MI3042)

*Câu 3 – Câu 23 (Chương 1: Xấp xỉ hàm số)*

**Quy ước chung.**

- Đa thức $P_n(x)=a_nx^n+\dots+a_1x+a_0$: chỉ số $=$ số mũ; vector hệ số viết **từ bậc cao xuống bậc thấp** $(a_n;\dots;a_0)$, vd $3x^3-2x-1\leftrightarrow(3;\,0;\,-2;\,-1)$.
- Trong các bảng (tỷ) sai phân, **các ô được chọn để lập đa thức được khoanh khung**, vd $\boxed{0.1234}$. Trong bảng Horner, ô khung là số dư $r_j$.
- Bảng tích: hàng đầu là đa thức hằng $1$; mỗi hàng sau nhân hàng trên với $(x-\text{mốc ghi ở cột đầu})$ bằng Horner nhân: với $A_{k,l}$ là hệ số của $x^l$ ở hàng $k$ và $z$ là mốc ở cột đầu hàng $k$ thì $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-z\,A_{k-1,l}$. Các hàng hệ số của bảng tích tạo thành ma trận $A$; với $C$ là vector hàng các hệ số $c_k$ thì vector hệ số của $\sum_kc_k\omega_k$ là $C\cdot A$.
- Bảng nhân (Câu 8–17): cột đầu ghi tích cơ sở (vd $t(t-1)$, $t^2(t^2-1)$), mỗi hàng là hệ số của tích đó theo luỹ thừa của biến; nhân từng hàng với hệ số $c_k$ tương ứng rồi cộng theo cột được dạng chính tắc.
- Số tính ra ghi tối đa 6 chữ số thập phân; số có $|v|<10^{-4}$ ghi dạng $a\cdot10^k$ với 6 chữ số thập phân ở $a$. Số liệu đề cho và sai phân của số liệu cách đều (hiệu các số cùng số chữ số thập phân) ghi đúng, không làm tròn.

## Câu 3. Mốc nội suy tối ưu

### a) Xây dựng công thức $n$ mốc nội suy tối ưu trên $[-1,1]$ và trên $[a,b]$

**Sai số nội suy.** Với $n$ mốc $x_0,\dots,x_{n-1}\in[a,b]$ và $P$ bậc $\le n-1$:

$$
f(x)-P(x)=\frac{f^{(n)}(\xi)}{n!}\,w_n(x),\qquad w_n(x)=\prod_{i=0}^{n-1}(x-x_i).
$$

$w_n$ là đa thức bậc $n$ có hệ số cao nhất bằng 1; mốc tối ưu là mốc làm $\max_{[a,b]}|w_n(x)|$ nhỏ nhất.

**Trên $[-1,1]$.** Đa thức Chebyshev $T_n(t)=\cos(n\arccos t)$ có hệ số cao nhất $2^{n-1}$ và $|T_n(t)|\le1$. Trong các đa thức bậc $n$ có hệ số cao nhất bằng 1, $\tilde T_n=2^{1-n}T_n$ có $\max_{[-1,1]}|\tilde T_n|=2^{1-n}$ nhỏ nhất. Vậy chọn $w_n=\tilde T_n$, tức các mốc là nghiệm của $T_n$:

$$
\boxed{t_i=\cos\frac{(2i+1)\pi}{2n},\ i=0,\dots,n-1,\qquad \min\max_{[-1,1]}|w_n|=\frac{1}{2^{n-1}}.}
$$

**Trên $[a,b]$.** Đổi biến $x=\dfrac{a+b}{2}+\dfrac{b-a}{2}t$ ánh xạ $[-1,1]$ lên $[a,b]$. Khi đó $x-x_i=\frac{b-a}{2}(t-t_i)$ nên $w_n(x)=\left(\frac{b-a}{2}\right)^n\prod(t-t_i)$; bài toán trên $[a,b]$ tương đương bài toán trên $[-1,1]$:

$$
\boxed{x_i=\frac{a+b}{2}+\frac{b-a}{2}\cos\frac{(2i+1)\pi}{2n},\qquad \min\max_{[a,b]}|w_n|=\left(\frac{b-a}{2}\right)^n\frac{1}{2^{n-1}}=\frac{(b-a)^n}{2^{2n-1}},}
$$

và khi đó $|f(x)-P(x)|\le\dfrac{M_n}{n!}\cdot\dfrac{(b-a)^n}{2^{2n-1}}$, $M_n=\max_{[a,b]}|f^{(n)}|$.

**Sắp tăng dần.** $\cos$ giảm trên $[0,\pi]$ nên $t_i$ ở trên giảm theo $i$. Dùng $t_i=-\cos\frac{(2i+1)\pi}{2n}=\cos\frac{(2(n-1-i)+1)\pi}{2n}$ (cùng tập nghiệm, đánh số ngược) thì $t_0<t_1<\dots<t_{n-1}$.

### b) Thuật toán xác định $n$ mốc tối ưu sắp tăng dần trên $[a,b]$

**Thuật toán: Mốc nội suy tối ưu**

- **Input:** số mốc $n$; đoạn $[a,b]$.
- **Output:** mảng $x=(x_0,\dots,x_{n-1})$, $x_0<x_1<\dots<x_{n-1}$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $n<1$ thì báo lỗi, dừng thuật toán.<br> Nếu $a=b$ thì báo lỗi, dừng thuật toán.<br> Nếu $a>b$ thì đổi chỗ $a$ và $b$.
- **Bước 1:** **Tính các mốc:** Lặp $i=0,\dots,n-1$: tính $x_i:=\dfrac{a+b}{2}-\dfrac{b-a}{2}\cos\dfrac{(2i+1)\pi}{2n}$.
- **Bước 2:** **Kết thúc:** Dừng thuật toán, trả về $x$.

### c) Áp dụng

**Phương pháp.** Mốc tối ưu là nghiệm của đa thức Chebyshev $T_n$ đổi biến từ $[-1,1]$ sang $[a,b]$, sắp tăng dần (câu a, b): $x_i=\dfrac{a+b}{2}-\dfrac{b-a}{2}\cos\dfrac{(2i+1)\pi}{2n}$, $i=0,\dots,n-1$.

**$n=9$, $[a,b]=[-1,1]$:** $x_i=-\cos\dfrac{(2i+1)\pi}{18}$, $i=0,\dots,8$:

| $i$ | $0$ | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ | $7$ | $8$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $x_i$ | $-0.984808$ | $-0.866025$ | $-0.642788$ | $-0.34202$ | $0$ | $0.34202$ | $0.642788$ | $0.866025$ | $0.984808$ |

$$
x = \bigl(-0.984808;\ -0.866025;\ -0.642788;\ -0.34202;\ 0;\ 0.34202;\ 0.642788;\ 0.866025;\ 0.984808\bigr)
$$

**$n=12$, $[a,b]=[3,6]$:** $x_i=4.5-1.5\cos\dfrac{(2i+1)\pi}{24}$, $i=0,\dots,11$:

| $i$ | $0$ | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ | $7$ | $8$ | $9$ | $10$ | $11$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $x_i$ | $3.012833$ | $3.114181$ | $3.30997$ | $3.586858$ | $3.925975$ | $4.304211$ | $4.695789$ | $5.074025$ | $5.413142$ | $5.69003$ | $5.885819$ | $5.987167$ |

$$
\begin{aligned}
x &= \bigl(3.012833;\ 3.114181;\ 3.30997;\ 3.586858;\ 3.925975;\ 4.304211;\ \\
&\quad 4.695789;\ 5.074025;\ 5.413142;\ 5.69003;\ 5.885819;\ 5.987167\bigr)
\end{aligned}
$$

## Câu 4. Sơ đồ Horner: giá trị, phép chia, đạo hàm

### a) Giá trị $P_n(c)$ b) Chia $P_n(x)$ cho $(x-c)$

**Thuật toán: Horner chia (giá trị, thương, số dư)**

- **Input:** vector hệ số $a=(a_n,\dots,a_0)$; số $c$.
- **Output:** thương $b=(b_{n-1},\dots,b_0)$; số dư $r=P_n(c)$.
- **Bước 0:** **Xử lý dữ liệu:** Bỏ các hệ số $0$ ở đầu vector $a$.<br> Nếu không còn hệ số nào ($P_n\equiv0$) thì dừng thuật toán, trả về $b:=(0)$ và $r:=0$.<br> Đặt $n:=(\text{số phần tử của }a)-1$.
- **Bước 1:** **Đa thức hằng:** Nếu $n=0$ thì dừng thuật toán, trả về $b:=(0)$ và $r:=a_0$.
- **Bước 2:** **Khởi tạo:** Đặt $b_{n-1}:=a_n$.
- **Bước 3:** **Lặp chia:** Lặp $i=n-1,\dots,1$: tính $b_{i-1}:=a_i+c\,b_i$.
- **Bước 4:** **Số dư:** Tính $r:=a_0+c\,b_0$.<br> Dừng thuật toán, trả về $b$ và $r$.

### c) Đạo hàm cấp $k$ của $P_n$ tại $c$

**Thuật toán: Đạo hàm cấp $0..k$ tại $c$ (Horner chia lặp)**

- **Input:** vector hệ số $a=(a_n,\dots,a_0)$; số $c$; cấp $k$.
- **Output:** vector $r=(r_0,\dots,r_K)$, $K=\min(k,n)$; vector $v=(v_0,\dots,v_k)$ với $v_j=P_n^{(j)}(c)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $k<0$ thì báo lỗi, dừng thuật toán.<br> Bỏ các hệ số $0$ ở đầu vector $a$.<br> Nếu không còn hệ số nào ($P_n\equiv0$) thì dừng thuật toán, trả về $r:=(0)$ và $v:=(0,\dots,0)$ ($k+1$ phần tử).<br> Đặt $n:=(\text{số phần tử của }a)-1$.
- **Bước 1:** **Khởi tạo:** Đặt $K:=\min(k,n)$.<br> Lặp $i=0,\dots,n$: đặt $b_i:=a_i$.
- **Bước 2:** **Chia lặp:** Lặp $j=0,\dots,K$:
  - **2.1:** Lặp $i=n-1,\dots,j$: tính $b_i:=b_i+c\,b_{i+1}$ (chia cho $x-c$).
  - **2.2:** Đặt $r_j:=b_j$. Tính $v_j:=j!\,r_j$.
- **Bước 3:** **Đạo hàm bậc cao:** Lặp $j=K+1,\dots,k$: đặt $v_j:=0$.<br> Dừng thuật toán, trả về $r$ và $v$.

### d) Áp dụng: $P(x)=3x^3-2x-1$, $a=(3;\,0;\,-2;\,-1)$

**Phương pháp** (Horner chia lặp, câu c). Chia liên tiếp $P$ cho $(x-c)$; số dư lần chia thứ $j$ là $r_j=\frac{P^{(j)}(c)}{j!}$. Hàng “Hệ số” là $b^{(-1)}_i=a_i$; hàng $j$ ghi $b^{(j)}_i$ ($i=3,\dots,j$) sau lần chia thứ $j$, hàng $c$ phía trên ghi $c\,b^{(j)}_{i+1}$:

$$
b^{(j)}_3=a_3,\qquad b^{(j)}_i=b^{(j-1)}_i+c\,b^{(j)}_{i+1}\ \ (i=2,\dots,j),\qquad r_j=b^{(j)}_j,\qquad P^{(j)}(c)=j!\,r_j,\qquad j=0,\dots,3.
$$

Lần chia $j=0$ cho thương $b^{(0)}_3x^2+b^{(0)}_2x+b^{(0)}_1$ và số dư $r_0=P(c)$; $P^{(j)}(c)=0$ với $j\ge4$.

**$c=0$:**

| | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|---:|---:|---:|---:|---:|
| $\text{Hệ số}$ | $3$ | $0$ | $-2$ | $-1$ |
| $c=0$ | | $0$ | $0$ | $0$ |
| $j=0$ | $3$ | $0$ | $-2$ | $\boxed{-1}$ |
| $c=0$ | | $0$ | $0$ | |
| $j=1$ | $3$ | $0$ | $\boxed{-2}$ | |
| $c=0$ | | $0$ | | |
| $j=2$ | $3$ | $\boxed{0}$ | | |
| $c=0$ | | | | |
| $j=3$ | $\boxed{3}$ | | | |

$P(0)=r_0=-1$; thương $3x^{2} - 2$, dư $-1$;<br>
$(P,P',P'',P''')(0)=(0!\,r_0;\ 1!\,r_1;\ 2!\,r_2;\ 3!\,r_3)=\left(-1;\ -2;\ 0;\ 18\right)$.

**$c=2.15$:**

| | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|---:|---:|---:|---:|---:|
| $\text{Hệ số}$ | $3$ | $0$ | $-2$ | $-1$ |
| $c=2.15$ | | $6.45$ | $13.8675$ | $25.515125$ |
| $j=0$ | $3$ | $6.45$ | $11.8675$ | $\boxed{24.515125}$ |
| $c=2.15$ | | $6.45$ | $27.735$ | |
| $j=1$ | $3$ | $12.9$ | $\boxed{39.6025}$ | |
| $c=2.15$ | | $6.45$ | | |
| $j=2$ | $3$ | $\boxed{19.35}$ | | |
| $c=2.15$ | | | | |
| $j=3$ | $\boxed{3}$ | | | |

$P(2.15)=r_0=24.515125$; thương $3x^{2} + 6.45x + 11.8675$, dư $24.515125$;<br>
$(P,P',P'',P''')(2.15)=(0!\,r_0;\ 1!\,r_1;\ 2!\,r_2;\ 3!\,r_3)=\left(24.515125;\ 39.6025;\ 38.7;\ 18\right)$.

## Câu 5. Phép nhân Horner, đa thức $w_{n+1}(x)$

### a) Nhân $P_n(x)$ với $(x-c)$

**Thuật toán: Horner nhân**

- **Input:** vector hệ số $a=(a_n,\dots,a_0)$; số $c$.
- **Output:** vector $d=(d_{n+1},\dots,d_0)$ với $P_n(x)\,(x-c)=\sum_{i=0}^{n+1}d_ix^i$.
- **Bước 0:** **Xử lý dữ liệu:** Bỏ các hệ số $0$ ở đầu vector $a$.<br> Nếu không còn hệ số nào ($P_n\equiv0$) thì dừng thuật toán, trả về $d:=(0)$.<br> Đặt $n:=(\text{số phần tử của }a)-1$.
- **Bước 1:** **Hệ số đầu:** Đặt $d_{n+1}:=a_n$.
- **Bước 2:** **Lặp nhân:** Lặp $i=n,\dots,1$: tính $d_i:=a_{i-1}-c\,a_i$.
- **Bước 3:** **Hệ số tự do:** Tính $d_0:=-c\,a_0$.<br> Dừng thuật toán, trả về $d$.

### b) Hệ số của $w_{n+1}(x)=\prod_{k=0}^{n}(x-x_k)$

**Thuật toán: Bảng tích (nhân Horner lặp)**

- **Input:** vector mốc $x=(x_0,\dots,x_n)$.
- **Output:** vector $p=(p_{n+1},\dots,p_0)$, $p_{n+1}=1$, với $w_{n+1}(x)=\sum_{l=0}^{n+1}p_lx^l$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu không có mốc nào thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.
- **Bước 1:** **Khởi tạo:** Đặt $p_0:=1$.
- **Bước 2:** **Nhân dần từng thừa số:** Lặp $i=0,\dots,n$:
  - **2.1:** Đặt $p_{i+1}:=p_i$.
  - **2.2:** Lặp $l=i,\dots,1$: tính $p_l:=p_{l-1}-x_i\,p_l$.
  - **2.3:** Tính $p_0:=-x_i\,p_0$.
- **Bước 3:** **Kết thúc:** Dừng thuật toán, trả về $p$.

### c) Áp dụng: $x_k=2;\ 2.4;\ 2.7;\ 3;\ 3.1;\ 3.4$

**Phương pháp** (bảng tích, câu b). Nhân dần $1$ với từng thừa số $(x-x_{k-1})$ bằng Horner nhân; $A_{k,l}$ là hệ số của $x^l$ ở hàng $k$ ($k=0,\dots,6$); hàng $0$ là đa thức $1$, hàng $k$ là hàng $k-1$ nhân với $(x-x_{k-1})$ (cột đầu ghi $x_{k-1}$):

$$
A_{0,0}=1,\qquad A_{k,l}=A_{k-1,l-1}-x_{k-1}\,A_{k-1,l}\quad(l=0,\dots,k;\ A_{k-1,-1}=A_{k-1,k}=0);
$$

hàng cuối là $w_6$.

| $x_{k-1}$ | $x^{6}$ | $x^{5}$ | $x^{4}$ | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | $1$ |
| $2$ | | | | | | $1$ | $-2$ |
| $2.4$ | | | | | $1$ | $-4.4$ | $4.8$ |
| $2.7$ | | | | $1$ | $-7.1$ | $16.68$ | $-12.96$ |
| $3$ | | | $1$ | $-10.1$ | $37.98$ | $-63$ | $38.88$ |
| $3.1$ | | $1$ | $-13.2$ | $69.29$ | $-180.738$ | $234.18$ | $-120.528$ |
| $3.4$ | $\boxed{1}$ | $\boxed{-16.6}$ | $\boxed{114.17}$ | $\boxed{-416.324}$ | $\boxed{848.6892}$ | $\boxed{-916.74}$ | $\boxed{409.7952}$ |

> **Kết luận.** Dạng chính tắc của $w_6(x)=(x-2)(x-2.4)(x-2.7)(x-3)(x-3.1)(x-3.4)$:
>
> $$
> w_6(x) = x^{6} - 16.6x^{5} + 114.17x^{4} - 416.324x^{3} + 848.6892x^{2} - 916.74x + 409.7952
> $$

## Câu 6. Thuật toán đa thức nội suy Lagrange

**Thuật toán: Đa thức nội suy Lagrange dạng chính tắc**

- **Input:** vector $x=(x_0,\dots,x_n)$, $y=(y_0,\dots,y_n)$.
- **Output:** vector $a=(a_n,\dots,a_0)$ — hệ số của đa thức nội suy Lagrange $P_n(x)=\sum_{l=0}^{n}a_lx^l$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.
- **Bước 1:** **Tích $w_{n+1}$:** Tính vector $p=(p_{n+1},\dots,p_0)$ — hệ số của $w_{n+1}(x)$ — theo thuật toán Câu 5b.
- **Bước 2:** **Khởi tạo:** Khởi tạo vector $a:=(0,\dots,0)$ ($n+1$ phần tử).
- **Bước 3:** **Cộng dồn từng mốc:** Lặp $i=0,\dots,n$:
  - **3.1:** Chia $w_{n+1}$ cho $(x-x_i)$ theo thuật toán Câu 4a (vector $p$, $c:=x_i$), được vector thương $q=(q_n,\dots,q_0)$.
  - **3.2:** Đặt $D_i:=1$.<br> Lặp $j=0,\dots,n$, $j\ne i$: tính $D_i:=D_i\,(x_i-x_j)$.
  - **3.3:** Lặp $l=0,\dots,n$: tính $a_l:=a_l+\dfrac{y_i}{D_i}\,q_l$.
- **Bước 4:** **Kết thúc:** Dừng thuật toán, trả về $a$.

## Câu 7. Đa thức nội suy Lagrange của bảng số liệu

**Phương pháp** (thuật toán Câu 6). Đa thức nội suy Lagrange viết qua đa thức $w_{n+1}$ và các thương $q^{(i)}$:

$$
P_5(x)=\sum_{i=0}^{5}\frac{y_i}{D_i}\,q^{(i)}(x),\qquad q^{(i)}(x)=\frac{w_6(x)}{x-x_i},\qquad D_i=\prod_{j\ne i}(x_i-x_j).
$$

**Bảng tích** (hàng cuối là hệ số của $w_6=\sum p_lx^l$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-x_{k-1}A_{k-1,l}$):

| $x_{k-1}$ | $x^{6}$ | $x^{5}$ | $x^{4}$ | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | $1$ |
| $1.2$ | | | | | | $1$ | $-1.2$ |
| $1.5$ | | | | | $1$ | $-2.7$ | $1.8$ |
| $1.7$ | | | | $1$ | $-4.4$ | $6.39$ | $-3.06$ |
| $1.8$ | | | $1$ | $-6.2$ | $14.31$ | $-14.562$ | $5.508$ |
| $2.1$ | | $1$ | $-8.3$ | $27.33$ | $-44.613$ | $36.0882$ | $-11.5668$ |
| $2.3$ | $1$ | $-10.6$ | $46.42$ | $-107.472$ | $138.6981$ | $-94.56966$ | $26.60364$ |

**Bảng thương** (hàng $i$: chia $w_6$ cho $(x-x_i)$ bằng Horner; $Q_{i,l}$ là hệ số của $x^l$ trong $q^{(i)}$, $p_l$ lấy ở hàng cuối bảng tích):

$$
Q_{i,5}=p_6=1,\qquad Q_{i,l-1}=p_l+x_i\,Q_{i,l}\ \ (l=5,\dots,1),\qquad \text{dư}=p_0+x_i\,Q_{i,0}=0.
$$

| $i$ | $x_i$ | $x^{5}$ | $x^{4}$ | $x^{3}$ | $x^{2}$ | $x$ | $1$ | $\text{dư}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $1.2$ | $1$ | $-9.4$ | $35.14$ | $-65.304$ | $60.3333$ | $-22.1697$ | $0$ |
| $1$ | $1.5$ | $1$ | $-9.1$ | $32.77$ | $-58.317$ | $51.2226$ | $-17.73576$ | $0$ |
| $2$ | $1.7$ | $1$ | $-8.9$ | $31.29$ | $-54.279$ | $46.4238$ | $-15.6492$ | $0$ |
| $3$ | $1.8$ | $1$ | $-8.8$ | $30.58$ | $-52.428$ | $44.3277$ | $-14.7798$ | $0$ |
| $4$ | $2.1$ | $1$ | $-8.5$ | $28.57$ | $-47.475$ | $39.0006$ | $-12.6684$ | $0$ |
| $5$ | $2.3$ | $1$ | $-8.3$ | $27.33$ | $-44.613$ | $36.0882$ | $-11.5668$ | $0$ |

**Bảng hệ số** (ô hàng $i$, cột $j$: $x_i-x_j$; $D_i$ là tích các ô $j\ne i$ của hàng $i$):

| $i$ | $x_i$ | $j=0$ | $1$ | $2$ | $3$ | $4$ | $5$ | $D_i$ | $y_i$ | $y_i/D_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $1.2$ | $\text{--}$ | $-0.3$ | $-0.5$ | $-0.6$ | $-0.9$ | $-1.1$ | $-0.0891$ | $0.892$ | $-10.011223$ |
| $1$ | $1.5$ | $0.3$ | $\text{--}$ | $-0.2$ | $-0.3$ | $-0.6$ | $-0.8$ | $0.00864$ | $1.179$ | $136.458333$ |
| $2$ | $1.7$ | $0.5$ | $0.2$ | $\text{--}$ | $-0.1$ | $-0.4$ | $-0.6$ | $-0.0024$ | $1.358$ | $-565.833333$ |
| $3$ | $1.8$ | $0.6$ | $0.3$ | $0.1$ | $\text{--}$ | $-0.3$ | $-0.5$ | $0.0027$ | $1.445$ | $535.185185$ |
| $4$ | $2.1$ | $0.9$ | $0.6$ | $0.4$ | $0.3$ | $\text{--}$ | $-0.2$ | $-0.01296$ | $1.688$ | $-130.246914$ |
| $5$ | $2.3$ | $1.1$ | $0.8$ | $0.6$ | $0.5$ | $0.2$ | $\text{--}$ | $0.0528$ | $1.839$ | $34.829545$ |

**Hệ số của $P_5$:** với vector hàng $Y=\bigl(\frac{y_0}{D_0},\dots,\frac{y_5}{D_5}\bigr)$ và ma trận $Q$ (6 cột hệ số của bảng thương):

$$
P_5=Y\cdot Q = \bigl(0.381594;\ -3.364759;\ 11.720314;\ -20.267374;\ 18.363141;\ -6.183818\bigr)
$$

> **Kết luận.**
>
> $$
> P_5(x) = 0.381594x^{5} - 3.364759x^{4} + 11.720314x^{3} - 20.267374x^{2} + 18.363141x - 6.183818
> $$

## Câu 8. Đa thức nội suy Newton tiến (mốc bất kỳ)

**Phương pháp.** Mốc không cách đều nên dùng tỷ sai phân. Công thức nội suy Newton tiến bậc $5$ có dạng:

$$
\begin{aligned}
P_{5}(x) &= y_{0} +f[x_{0},x_{1}]\,(x-x_{0}) +f[x_{0},\dots,x_{2}]\,(x-x_{0})(x-x_{1}) +f[x_{0},\dots,x_{3}]\,(x-x_{0})(x-x_{1})(x-x_{2}) \\
&\quad +f[x_{0},\dots,x_{4}]\,(x-x_{0})(x-x_{1})\cdots(x-x_{3}) +f[x_{0},\dots,x_{5}]\,(x-x_{0})(x-x_{1})\cdots(x-x_{4})
\end{aligned}
$$

### a) Đa thức Newton tiến

**Bảng tỷ sai phân** (hàng $i$, cột TSP$k$ là $f[x_{i-k},\dots,x_i]$; đường chéo khung $=c_k$):

$$
f[x_{i-k},\dots,x_i]=\frac{f[x_{i-k+1},\dots,x_i]-f[x_{i-k},\dots,x_{i-1}]}{x_i-x_{i-k}}.
$$

| $i$ | $x_i$ | $y_i$ | $\text{TSP1}$ | $\text{TSP2}$ | $\text{TSP3}$ | $\text{TSP4}$ | $\text{TSP5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $1.2$ | $\boxed{0.7247}$ | | | | | |
| $1$ | $1.5$ | $0.1415$ | $\boxed{-1.944}$ | | | | |
| $2$ | $1.7$ | $-0.2577$ | $-1.996$ | $\boxed{-0.104}$ | | | |
| $3$ | $1.9$ | $-0.6466$ | $-1.9445$ | $0.12875$ | $\boxed{0.3325}$ | | |
| $4$ | $2.1$ | $-1.0097$ | $-1.8155$ | $0.3225$ | $0.322917$ | $\boxed{-0.010648}$ | |
| $5$ | $2.4$ | $-1.4748$ | $-1.550333$ | $0.530333$ | $0.296905$ | $-0.028902$ | $\boxed{-0.015212}$ |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{5}(x) &= 0.7247 -1.944(x-1.2) -0.104(x-1.2)(x-1.5) +0.3325(x-1.2)(x-1.5)(x-1.7) \\
&\quad -0.010648(x-1.2)(x-1.5)\cdots(x-1.9) -0.015212(x-1.2)(x-1.5)\cdots(x-2.1)
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
c = \bigl(0.7247;\ -1.944;\ -0.104;\ 0.3325;\ -0.010648;\ -0.015212\bigr)
$$

Khai triển các tích cơ sở theo luỹ thừa của $x$ ta có bảng nhân (hàng $k$: $\omega_k(x)=\omega_{k-1}(x)\cdot(x-x_{k-1})$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-x_{k-1}\,A_{k-1,l}$):

| | $x^{5}$ | $x^{4}$ | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $(x-1.2)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-1.2$ |
| $(x-1.2)(x-1.5)$ | $0$ | $0$ | $0$ | $1$ | $-2.7$ | $1.8$ |
| $(x-1.2)(x-1.5)(x-1.7)$ | $0$ | $0$ | $1$ | $-4.4$ | $6.39$ | $-3.06$ |
| $(x-1.2)(x-1.5)\cdots(x-1.9)$ | $0$ | $1$ | $-6.3$ | $14.75$ | $-15.201$ | $5.814$ |
| $(x-1.2)(x-1.5)\cdots(x-2.1)$ | $1$ | $-8.4$ | $27.98$ | $-46.176$ | $37.7361$ | $-12.2094$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
P_{5}(x) = -0.015212x^{5} + 0.11713x^{4} - 0.026038x^{3} - 1.021647x^{2} + 0.04931x + 1.976667
$$

### b) Tính gần đúng $f(1.8)$, $f'''(1.8)$

Tại $\bar x=1.8$, tính $P_5(1.8)$ và $P_5'''(1.8)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(1.8)\approx P_5(1.8)=r_0=-0.454424,\qquad f'''(1.8)\approx P_5'''(1.8)=3!\,r_3=6\cdot0.324438=1.946627.
$$

## Câu 9. Đa thức nội suy Newton lùi (mốc bất kỳ)

**Phương pháp.** Mốc không cách đều nên dùng tỷ sai phân; Newton lùi xuất phát từ $x_5=3.2$. Công thức nội suy Newton lùi bậc $5$ có dạng:

$$
\begin{aligned}
P_{5}(x) &= y_{5} +f[x_{4},x_{5}]\,(x-x_{5}) +f[x_{3},\dots,x_{5}]\,(x-x_{5})(x-x_{4}) +f[x_{2},\dots,x_{5}]\,(x-x_{5})(x-x_{4})(x-x_{3}) \\
&\quad +f[x_{1},\dots,x_{5}]\,(x-x_{5})(x-x_{4})\cdots(x-x_{2}) +f[x_{0},\dots,x_{5}]\,(x-x_{5})(x-x_{4})\cdots(x-x_{1})
\end{aligned}
$$

### a) Đa thức Newton lùi

**Bảng tỷ sai phân** (hàng $i$, cột TSP$k$ là $f[x_{i-k},\dots,x_i]$; hàng cuối khung $=c_k$):

$$
f[x_{i-k},\dots,x_i]=\frac{f[x_{i-k+1},\dots,x_i]-f[x_{i-k},\dots,x_{i-1}]}{x_i-x_{i-k}}.
$$

| $i$ | $x_i$ | $y_i$ | $\text{TSP1}$ | $\text{TSP2}$ | $\text{TSP3}$ | $\text{TSP4}$ | $\text{TSP5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $2.2$ | $1.617$ | | | | | |
| $1$ | $2.3$ | $1.4914$ | $-1.256$ | | | | |
| $2$ | $2.6$ | $1.031$ | $-1.534667$ | $-0.696667$ | | | |
| $3$ | $2.7$ | $0.8548$ | $-1.762$ | $-0.568333$ | $0.256667$ | | |
| $4$ | $3$ | $0.2822$ | $-1.908667$ | $-0.366667$ | $0.288095$ | $0.039286$ | |
| $5$ | $3.2$ | $\boxed{-0.1167}$ | $\boxed{-1.9945}$ | $\boxed{-0.171667}$ | $\boxed{0.325}$ | $\boxed{0.041005}$ | $\boxed{0.00172}$ |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{5}(x) &= -0.1167 -1.9945(x-3.2) -0.171667(x-3.2)(x-3) +0.325(x-3.2)(x-3)(x-2.7) \\
&\quad +0.041005(x-3.2)(x-3)\cdots(x-2.6) +0.00172(x-3.2)(x-3)\cdots(x-2.3)
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
c = \bigl(-0.1167;\ -1.9945;\ -0.171667;\ 0.325;\ 0.041005;\ 0.00172\bigr)
$$

Khai triển các tích cơ sở theo luỹ thừa của $x$ ta có bảng nhân (hàng $k$: $\omega_k(x)=\omega_{k-1}(x)\cdot(x-x_{6-k})$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-x_{6-k}\,A_{k-1,l}$):

| | $x^{5}$ | $x^{4}$ | $x^{3}$ | $x^{2}$ | $x$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $(x-3.2)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-3.2$ |
| $(x-3.2)(x-3)$ | $0$ | $0$ | $0$ | $1$ | $-6.2$ | $9.6$ |
| $(x-3.2)(x-3)(x-2.7)$ | $0$ | $0$ | $1$ | $-8.9$ | $26.34$ | $-25.92$ |
| $(x-3.2)(x-3)\cdots(x-2.6)$ | $0$ | $1$ | $-11.5$ | $49.48$ | $-94.404$ | $67.392$ |
| $(x-3.2)(x-3)\cdots(x-2.3)$ | $1$ | $-13.8$ | $75.93$ | $-208.208$ | $284.5212$ | $-155.0016$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
P_{5}(x) = 0.00172x^{5} + 0.017275x^{4} - 0.015993x^{3} - 1.393254x^{2} + 4.248526x - 1.309409
$$

### b) Tính gần đúng $f(2.4)$, $f^{(4)}(2.4)$

Tại $\bar x=2.4$, tính $P_5(2.4)$ và $P_5^{(4)}(2.4)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(2.4)\approx P_5(2.4)=r_0=1.350886,\qquad f^{(4)}(2.4)\approx P_5^{(4)}(2.4)=4!\,r_4=24\cdot0.03791=0.909841.
$$

## Câu 10. Thuật toán đa thức nội suy Newton tiến / lùi

**Thuật toán: Newton tiến / lùi, mốc bất kỳ**

- **Input:** vector $x=(x_0,\dots,x_n)$, $y=(y_0,\dots,y_n)$; chiều (tiến hoặc lùi); điểm $\bar x$; cấp đạo hàm $r$.
- **Output:** vector $a=(a_n,\dots,a_0)$ với $P_n(x)=\sum_la_lx^l$; vector $f=(f_0,\dots,f_r)$, $f_j\approx f^{(j)}(\bar x)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $r<0$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Bảng tỷ sai phân:** Khởi tạo ma trận $T$ cỡ $(n+1)\times(n+1)$ ($T_{i,k}=f[x_{i-k},\dots,x_i]$).<br> Lặp $i=0,\dots,n$: đặt $T_{i,0}:=y_i$.<br> Lặp lồng $k=1,\dots,n$; $i=k,\dots,n$: tính $T_{i,k}:=\dfrac{T_{i,k-1}-T_{i-1,k-1}}{x_i-x_{i-k}}$.
- **Bước 2:** **Hệ số:** Lặp $k=0,\dots,n$:<br>&emsp;&emsp; nếu tiến thì đặt $c_k:=T_{k,k}$;<br>&emsp;&emsp; nếu lùi thì đặt $c_k:=T_{n,k}$.
- **Bước 3:** **Bảng tích, cộng dồn:** Khởi tạo vector $e=(e_0,e_1,\dots,e_n):=(1,0,\dots,0)$, $a=(a_0,a_1,\dots,a_n):=(c_0,0,\dots,0)$, gồm $n+1$ phần tử.<br> Lặp $k=1,\dots,n$:
  - **3.1:** Nếu tiến thì đặt $z:=x_{k-1}$; nếu lùi thì đặt $z:=x_{n-k+1}$.<br> Nhân vector $e$ với $(x-z)$ theo thuật toán Câu 5a.
  - **3.2:** Lặp $l=0,\dots,k$: tính $a_l:=a_l+c_k\,e_l$.
- **Bước 4:** **Giá trị, đạo hàm:** Gọi thuật toán Câu 4c với vector $a$, $c:=\bar x$, cấp $k:=r$, được vector $f=(f_0,\dots,f_r)$, $f_j=P_n^{(j)}(\bar x)$.<br> Dừng thuật toán, trả về $a$ và $f$.

**Thuật toán: Newton tiến / lùi, mốc cách đều**

- **Input:** vector $x=(x_0,\dots,x_n)$ cách đều, $y=(y_0,\dots,y_n)$; chiều (tiến hoặc lùi); điểm $\bar x$; cấp đạo hàm $r$.
- **Output:** vector $b=(b_n,\dots,b_0)$ với $P_n(t)=\sum_lb_lt^l$ ($t=\frac{x-x_0}{h}$ nếu tiến, $t=\frac{x-x_n}{h}$ nếu lùi); vector $f=(f_0,\dots,f_r)$, $f_j\approx f^{(j)}(\bar x)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Nếu $r<0$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Kiểm tra cách đều:** Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì báo “mốc không cách đều”, dùng thuật toán mốc bất kỳ, dừng thuật toán.
- **Bước 2:** **Bảng sai phân:** Khởi tạo ma trận $T$ cỡ $(n+1)\times(n+1)$ ($T_{i,k}=\Delta^ky_{i-k}$).<br> Lặp $i=0,\dots,n$: đặt $T_{i,0}:=y_i$.<br> Lặp lồng $k=1,\dots,n$; $i=k,\dots,n$: tính $T_{i,k}:=T_{i,k-1}-T_{i-1,k-1}$.
- **Bước 3:** **Hệ số:** Lặp $k=0,\dots,n$:<br>&emsp;&emsp; nếu tiến thì tính $c_k:=T_{k,k}/k!$;<br>&emsp;&emsp; nếu lùi thì tính $c_k:=T_{n,k}/k!$.
- **Bước 4:** **Bảng tích, cộng dồn:** Khởi tạo vector $e=(e_0,e_1,\dots,e_n):=(1,0,\dots,0)$, $b=(b_0,b_1,\dots,b_n):=(c_0,0,\dots,0)$, gồm $n+1$ phần tử.<br> Lặp $k=1,\dots,n$:
  - **4.1:** Nếu tiến thì đặt $z:=k-1$; nếu lùi thì đặt $z:=-(k-1)$.<br> Nhân vector $e$ với $(t-z)$ theo thuật toán Câu 5a.
  - **4.2:** Lặp $l=0,\dots,k$: tính $b_l:=b_l+c_k\,e_l$.
- **Bước 5:** **Biến chuẩn hoá:** Nếu tiến thì tính $\bar t:=(\bar x-x_0)/h$; nếu lùi thì tính $\bar t:=(\bar x-x_n)/h$.
- **Bước 6:** **Giá trị, đạo hàm:** Gọi thuật toán Câu 4c với vector $b$, $c:=\bar t$, cấp $k:=r$, được vector $d=(d_0,\dots,d_r)$.<br> Lặp $j=0,\dots,r$: tính $f_j:=d_j/h^j$.<br> Dừng thuật toán, trả về $b$ và $f$.

## Câu 11. Trích xuất mốc và nội suy Newton trên bảng dài

### a) Thuật toán trích xuất $k$ điểm nội suy phù hợp để tính $f(\bar x)$

**Thuật toán: Trích xuất $k$ mốc gần $\bar x$ nhất**

- **Input:** vector $x=(x_0,\dots,x_n)$ cách đều, $y=(y_0,\dots,y_n)$; điểm $\bar x$; số mốc $k$.
- **Output:** chỉ số $L$, $R$ ($R-L+1=k$); vector $X=(x_L,\dots,x_R)$, $Y=(y_L,\dots,y_R)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì báo “mốc không cách đều”, dừng thuật toán.<br> Nếu $k<1$ thì báo lỗi, dừng thuật toán.<br> Nếu $k>n+1$ thì báo “không đủ mốc”, đặt $k:=n+1$.<br> Nếu $\bar x<x_0$ hoặc $\bar x>x_n$ thì cảnh báo ngoại suy.
- **Bước 1:** **Mốc gần nhất:** Tính $j:=\operatorname{round}\dfrac{\bar x-x_0}{h}$ (số nguyên gần nhất).<br> Nếu $j<0$ thì đặt $j:=0$; nếu $j>n$ thì đặt $j:=n$.<br> Đặt $L:=j$, $R:=j$.
- **Bước 2:** **Kết nạp dần:** Lặp $s=2,\dots,k$:<br>&emsp;&emsp; nếu $L=0$ thì $R:=R+1$;<br>&emsp;&emsp; ngược lại nếu $R=n$ thì $L:=L-1$;<br>&emsp;&emsp; ngược lại nếu $\bar x-x_{L-1}\le x_{R+1}-\bar x$ thì $L:=L-1$, còn không thì $R:=R+1$.
- **Bước 3:** **Kết thúc:** Đặt $X:=(x_L,\dots,x_R)$, $Y:=(y_L,\dots,y_R)$.<br> Dừng thuật toán, trả về $L$, $R$, $X$, $Y$.

### b) Trích xuất 9 điểm cho $\bar x=3.52$

**Xử lý dữ liệu.** File `data Câu 11.xlsx` (sheet đầu): cột A là $x$, cột B là $y$; ô B1 $=2.95$ không có $x$ đi kèm nên bị loại (dòng 1, ô $x$ rỗng). Ta có bảng dữ liệu gồm $N=141$ mốc cách đều $x_i=1+0.1\,i$ ($i=\overline{0,140}$, $x_i\in[1;\,15]$, bước lưới $h=0.1$).

Thuật toán câu a ($\bar x=3.52$, $k=9$): mốc gần $\bar x$ nhất là $x_{25}=3.5$ ($j=\operatorname{round}\tfrac{3.52-1}{0.1}=25$); thêm lần lượt $x_{26},x_{24},x_{27},x_{23},x_{28},x_{22},x_{29},x_{21}$ $\Rightarrow$ $L=21$, $R=29$. Đánh số lại $i=0..8$:

| $i$ | $0$ | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ | $7$ | $8$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $\text{chỉ số gốc}$ | $21$ | $22$ | $23$ | $24$ | $25$ | $26$ | $27$ | $28$ | $29$ |
| $x_i$ | $3.1$ | $3.2$ | $3.3$ | $3.4$ | $3.5$ | $3.6$ | $3.7$ | $3.8$ | $3.9$ |
| $y_i$ | $3.1624709$ | $3.1125386$ | $3.0634802$ | $3.016785$ | $2.9739188$ | $2.936309$ | $2.9053306$ | $2.8822923$ | $2.8684234$ |

### c) Đa thức Newton tiến, $f(\bar x)$, $f'(\bar x)$

**Phương pháp.** 9 mốc cách đều $h=0.1$ nên dùng Newton tiến mốc cách đều. Đặt biến chuẩn hoá $t=\dfrac{x-x_0}{h}=\dfrac{x-3.1}{0.1}$. Công thức nội suy Newton tiến bậc $8$ có dạng:

$$
\begin{aligned}
P_{8}(t) &= y_0 +\Delta y_0\,t +\dfrac{\Delta^{2}y_0}{2!}t(t-1) +\dfrac{\Delta^{3}y_0}{3!}t(t-1)(t-2) \\
&\quad +\dfrac{\Delta^{4}y_0}{4!}t(t-1)(t-2)(t-3) +\cdots +\dfrac{\Delta^{8}y_0}{8!}t(t-1)\cdots(t-7)
\end{aligned}
$$

**Bảng sai phân** (hàng $i$, cột $\Delta^k$ là $\Delta^ky_{i-k}$; đường chéo khung $=\Delta^ky_0$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,8;\ i=0,\dots,8-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta^{1}$ | $\Delta^{2}$ | $\Delta^{3}$ | $\Delta^{4}$ | $\Delta^{5}$ | $\Delta^{6}$ | $\Delta^{7}$ | $\Delta^{8}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $3.1$ | $\boxed{3.1624709}$ | | | | | | | | |
| $1$ | $3.2$ | $3.1125386$ | $\boxed{-0.0499323}$ | | | | | | | |
| $2$ | $3.3$ | $3.0634802$ | $-0.0490584$ | $\boxed{0.0008739}$ | | | | | | |
| $3$ | $3.4$ | $3.0167850$ | $-0.0466952$ | $0.0023632$ | $\boxed{0.0014893}$ | | | | | |
| $4$ | $3.5$ | $2.9739188$ | $-0.0428662$ | $0.0038290$ | $0.0014658$ | $\boxed{-0.0000235}$ | | | | |
| $5$ | $3.6$ | $2.9363090$ | $-0.0376098$ | $0.0052564$ | $0.0014274$ | $-0.0000384$ | $\boxed{-0.0000149}$ | | | |
| $6$ | $3.7$ | $2.9053306$ | $-0.0309784$ | $0.0066314$ | $0.0013750$ | $-0.0000524$ | $-0.0000140$ | $\boxed{0.0000009}$ | | |
| $7$ | $3.8$ | $2.8822923$ | $-0.0230383$ | $0.0079401$ | $0.0013087$ | $-0.0000663$ | $-0.0000139$ | $0.0000001$ | $\boxed{-0.0000008}$ | |
| $8$ | $3.9$ | $2.8684234$ | $-0.0138689$ | $0.0091694$ | $0.0012293$ | $-0.0000794$ | $-0.0000131$ | $0.0000008$ | $0.0000007$ | $\boxed{0.0000015}$ |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{8}(t) &= 3.1624709 -0.0499323t +\dfrac{0.0008739}{2!}t(t-1) \\
&\quad +\dfrac{0.0014893}{3!}t(t-1)(t-2) +\dfrac{-0.0000235}{4!}t(t-1)(t-2)(t-3) +\cdots \\
 &= 3.162471 -0.049932t +0.000437t(t-1) +0.000248t(t-1)(t-2) \\
&\quad -9.791667\cdot10^{-7}\,t(t-1)(t-2)(t-3) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
\begin{aligned}
c &= \bigl(3.162471;\ -0.049932;\ 0.000437;\ 0.000248;\ -9.791667\cdot10^{-7};\ \\
&\quad -1.241667\cdot10^{-7};\ 1.25\cdot10^{-9};\ -1.587302\cdot10^{-10};\ 3.720238\cdot10^{-11}\bigr)
\end{aligned}
$$

Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân (hàng $k$: $\omega_k(t)=\omega_{k-1}(t)\cdot(t-z_{k-1})$, $z_{k-1}=k-1$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-(k-1)\,A_{k-1,l}$):

| | $t^{8}$ | $t^{7}$ | $t^{6}$ | $t^{5}$ | $t^{4}$ | $t^{3}$ | $t^{2}$ | $t$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $t$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $t(t-1)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-1$ | $0$ |
| $t(t-1)(t-2)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-3$ | $2$ | $0$ |
| $t(t-1)(t-2)(t-3)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-6$ | $11$ | $-6$ | $0$ |
| $t(t-1)\cdots(t-4)$ | $0$ | $0$ | $0$ | $1$ | $-10$ | $35$ | $-50$ | $24$ | $0$ |
| $t(t-1)\cdots(t-5)$ | $0$ | $0$ | $1$ | $-15$ | $85$ | $-225$ | $274$ | $-120$ | $0$ |
| $t(t-1)\cdots(t-6)$ | $0$ | $1$ | $-21$ | $175$ | $-735$ | $1624$ | $-1764$ | $720$ | $0$ |
| $t(t-1)\cdots(t-7)$ | $1$ | $-28$ | $322$ | $-1960$ | $6769$ | $-13132$ | $13068$ | $-5040$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_8(t) &= 3.720238\cdot10^{-11}\,t^{8} - 1.200397\cdot10^{-9}\,t^{7} + 1.65625\cdot10^{-8}\,t^{6} - 2.436111\cdot10^{-7}\,t^{5} \\
&\quad + 7.372396\cdot10^{-7}\,t^{4} + 0.000249t^{3} - 0.000311t^{2} - 0.04987t + 3.162471
\end{aligned}
$$

Tại $\bar x=3.52$, ta có $\bar t=\dfrac{3.52-3.1}{0.1}=4.2$. Tính $P_8(\bar t)$ và $P_8'(\bar t)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(3.52)\approx P_8(\bar t)=2.965931,\qquad \frac{dP_8}{dt}\bigg|_{t=\bar t}=-0.039392.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(3.52)\approx\frac{1}{h}\,\frac{dP_8}{dt}\bigg|_{t=\bar t}=\frac{-0.039392}{0.1}=-0.393918.
$$

## Câu 12. Đa thức nội suy Gauss I

**Phương pháp.** 9 mốc cách đều, $\bar t=0.8>0$ nên dùng Gauss I, mốc trung tâm $x_0=9.6$ ($i=-4..4$), $h=0.1$. Đặt biến chuẩn hoá $t=\dfrac{x-x_0}{h}=\dfrac{x-9.6}{0.1}$. Công thức nội suy Gauss I bậc $8$ có dạng:

$$
\begin{aligned}
P_{8}(t) &= y_{0} +\Delta y_{0}\,t +\dfrac{\Delta^{2}y_{-1}}{2!}t(t-1) +\dfrac{\Delta^{3}y_{-1}}{3!}(t+1)t(t-1) \\
&\quad +\dfrac{\Delta^{4}y_{-2}}{4!}(t+1)t(t-1)(t-2) +\cdots +\dfrac{\Delta^{8}y_{-4}}{8!}(t+3)(t+2)\cdots(t-4)
\end{aligned}
$$

### a) Lập đa thức Gauss I

**Bảng sai phân** (hàng $i$ chứa $y_i,\Delta y_i,\Delta^2y_i,\dots$; ô khung: $\Delta^ky_{-\lfloor k/2\rfloor}$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,8;\ i=-4,\dots,4-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ | $\Delta^{7}y_i$ | $\Delta^{8}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-4$ | $9.2$ | $9.4341319$ | $-0.0033555$ | $-0.0013067$ | $0.0010457$ | $0.0000028$ | $-0.0000108$ | $0.0000004$ | $0.0000000$ | $\boxed{-0.0000002}$ |
| $-3$ | $9.3$ | $9.4307764$ | $-0.0046622$ | $-0.0002610$ | $0.0010485$ | $-0.0000080$ | $-0.0000104$ | $\boxed{0.0000004}$ | $\boxed{-0.0000002}$ | |
| $-2$ | $9.4$ | $9.4261142$ | $-0.0049232$ | $0.0007875$ | $0.0010405$ | $\boxed{-0.0000184}$ | $\boxed{-0.0000100}$ | $0.0000002$ | | |
| $-1$ | $9.5$ | $9.4211910$ | $-0.0041357$ | $\boxed{0.0018280}$ | $\boxed{0.0010221}$ | $-0.0000284$ | $-0.0000098$ | | | |
| $0$ | $9.6$ | $\boxed{9.4170553}$ | $\boxed{-0.0023077}$ | $0.0028501$ | $0.0009937$ | $-0.0000382$ | | | | |
| $1$ | $9.7$ | $9.4147476$ | $0.0005424$ | $0.0038438$ | $0.0009555$ | | | | | |
| $2$ | $9.8$ | $9.4152900$ | $0.0043862$ | $0.0047993$ | | | | | | |
| $3$ | $9.9$ | $9.4196762$ | $0.0091855$ | | | | | | | |
| $4$ | $10$ | $9.4288617$ | | | | | | | | |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{8}(t) &= 9.4170553 -0.0023077t +\dfrac{0.0018280}{2!}t(t-1) \\
&\quad +\dfrac{0.0010221}{3!}(t+1)t(t-1) +\dfrac{-0.0000184}{4!}(t+1)t(t-1)(t-2) +\cdots \\
 &= 9.417055 -0.002308t +0.000914t(t-1) +0.00017(t+1)t(t-1) \\
&\quad -7.666667\cdot10^{-7}\,(t+1)t(t-1)(t-2) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
\begin{aligned}
c &= \bigl(9.417055;\ -0.002308;\ 0.000914;\ 0.00017;\ -7.666667\cdot10^{-7};\ \\
&\quad -8.333333\cdot10^{-8};\ 5.555556\cdot10^{-10};\ -3.968254\cdot10^{-11};\ -4.960317\cdot10^{-12}\bigr)
\end{aligned}
$$

Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân (hàng $k$: $\omega_k(t)=\omega_{k-1}(t)\cdot(t-z_{k-1})$, $z=0,1,-1,2,-2,3,-3,4$; $A_{0,0}=1$, $A_{k,l}=A_{k-1,l-1}-z_{k-1}\,A_{k-1,l}$):

| | $t^{8}$ | $t^{7}$ | $t^{6}$ | $t^{5}$ | $t^{4}$ | $t^{3}$ | $t^{2}$ | $t$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $t$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $t(t-1)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-1$ | $0$ |
| $(t+1)t(t-1)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ |
| $(t+1)t(t-1)(t-2)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $-2$ | $-1$ | $2$ | $0$ |
| $(t+2)(t+1)\cdots(t-2)$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ |
| $(t+2)(t+1)\cdots(t-3)$ | $0$ | $0$ | $1$ | $-3$ | $-5$ | $15$ | $4$ | $-12$ | $0$ |
| $(t+3)(t+2)\cdots(t-3)$ | $0$ | $1$ | $0$ | $-14$ | $0$ | $49$ | $0$ | $-36$ | $0$ |
| $(t+3)(t+2)\cdots(t-4)$ | $1$ | $-4$ | $-14$ | $56$ | $49$ | $-196$ | $-36$ | $144$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_{8}(t) &= -4.960317\cdot10^{-12}\,t^{8} - 1.984127\cdot10^{-11}\,t^{7} + 6.25\cdot10^{-10}\,t^{6} - 8.472222\cdot10^{-8}\,t^{5} \\
&\quad - 7.696875\cdot10^{-7}\,t^{4} + 0.000172t^{3} + 0.000915t^{2} - 0.003394t + 9.417055
\end{aligned}
$$

### b) Tính gần đúng $f(9.68)$

Tại $\bar x=9.68$, ta có $\bar t=\dfrac{9.68-9.6}{0.1}=0.8$. Tính $P_8(\bar t)$ bằng sơ đồ Horner chia (Câu 4a):

$$
f(9.68)\approx P_8(\bar t)=9.415013.
$$

## Câu 13. Đa thức nội suy Stirling

**Phương pháp.** 9 mốc cách đều (số lẻ) nên dùng Stirling, mốc trung tâm $x_0=1.8$ ($i=-4..4$), $h=0.1$. Đặt biến chuẩn hoá $t=\dfrac{x-x_0}{h}=\dfrac{x-1.8}{0.1}$. Công thức nội suy Stirling bậc $8$ có dạng:

$$
\begin{aligned}
P_{8}(t) &= y_{0} +\dfrac{\Delta y_{-1} + \Delta y_{0}}{2}t +\dfrac{\Delta^{2}y_{-1}}{2!}t^2 +\dfrac{\Delta^{3}y_{-2} + \Delta^{3}y_{-1}}{2\cdot3!}t(t^2-1) \\
&\quad +\dfrac{\Delta^{4}y_{-2}}{4!}t^2(t^2-1) +\cdots +\dfrac{\Delta^{8}y_{-4}}{8!}t^2(t^2-1)(t^2-4)(t^2-9)
\end{aligned}
$$

### a) Lập đa thức Stirling

**Bảng sai phân** (ô khung: cặp $\Delta^{2j-1}y_{-j},\Delta^{2j-1}y_{-j+1}$ và $\Delta^{2j}y_{-j}$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,8;\ i=-4,\dots,4-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ | $\Delta^{7}y_i$ | $\Delta^{8}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-4$ | $1.4$ | $2.4347052$ | $0.1126575$ | $-0.0104650$ | $-0.0000217$ | $0.0001043$ | $0.0000002$ | $-0.0000069$ | $\boxed{0.0000307}$ | $\boxed{-0.0001145}$ |
| $-3$ | $1.5$ | $2.5473627$ | $0.1021925$ | $-0.0104867$ | $0.0000826$ | $0.0001045$ | $\boxed{-0.0000067}$ | $\boxed{0.0000238}$ | $\boxed{-0.0000838}$ | |
| $-2$ | $1.6$ | $2.6495552$ | $0.0917058$ | $-0.0104041$ | $\boxed{0.0001871}$ | $\boxed{0.0000978}$ | $\boxed{0.0000171}$ | $-0.0000600$ | | |
| $-1$ | $1.7$ | $2.7412610$ | $\boxed{0.0813017}$ | $\boxed{-0.0102170}$ | $\boxed{0.0002849}$ | $0.0001149$ | $-0.0000429$ | | | |
| $0$ | $1.8$ | $\boxed{2.8225627}$ | $\boxed{0.0710847}$ | $-0.0099321$ | $0.0003998$ | $0.0000720$ | | | | |
| $1$ | $1.9$ | $2.8936474$ | $0.0611526$ | $-0.0095323$ | $0.0004718$ | | | | | |
| $2$ | $2$ | $2.9548000$ | $0.0516203$ | $-0.0090605$ | | | | | | |
| $3$ | $2.1$ | $3.0064203$ | $0.0425598$ | | | | | | | |
| $4$ | $2.2$ | $3.0489801$ | | | | | | | | |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{8}(t) &= 2.8225627 +\dfrac{0.0813017+0.0710847}{2}t +\dfrac{-0.0102170}{2!}t^2 \\
&\quad +\dfrac{0.0001871+0.0002849}{2\cdot3!}t(t^2-1) +\dfrac{0.0000978}{4!}t^2(t^2-1) +\cdots \\
 &= 2.822563 +0.076193t -0.005109t^2 +3.933333\cdot10^{-5}\,t(t^2-1) +4.075\cdot10^{-6}\,t^2(t^2-1) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
\begin{aligned}
c &= \bigl(2.822563;\ 0.076193;\ -0.005109;\ 3.933333\cdot10^{-5};\ 4.075\cdot10^{-6};\ \\
&\quad 4.333333\cdot10^{-8};\ 3.305556\cdot10^{-8};\ -5.267857\cdot10^{-9};\ -2.839782\cdot10^{-9}\bigr)
\end{aligned}
$$

Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân ($\Omega_0=1$, $\Omega_1=t$, $\Omega_{2j}=t\,\Omega_{2j-1}$, $\Omega_{2j+1}=\Omega_{2j-1}\cdot(t^2-j^2)$):

| | $t^{8}$ | $t^{7}$ | $t^{6}$ | $t^{5}$ | $t^{4}$ | $t^{3}$ | $t^{2}$ | $t$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $t$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $t^2$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $0$ |
| $t(t^2-1)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ |
| $t^2(t^2-1)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ | $0$ |
| $t(t^2-1)(t^2-4)$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ |
| $t^2(t^2-1)(t^2-4)$ | $0$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ | $0$ |
| $t(t^2-1)(t^2-4)(t^2-9)$ | $0$ | $1$ | $0$ | $-14$ | $0$ | $49$ | $0$ | $-36$ | $0$ |
| $t^2(t^2-1)(t^2-4)(t^2-9)$ | $1$ | $0$ | $-14$ | $0$ | $49$ | $0$ | $-36$ | $0$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_{8}(t) &= -2.839782\cdot10^{-9}\,t^{8} - 5.267857\cdot10^{-9}\,t^{7} + 7.28125\cdot10^{-8}\,t^{6} + 1.170833\cdot10^{-7}\,t^{5} \\
&\quad + 3.770573\cdot10^{-6}\,t^{4} + 3.885854\cdot10^{-5}\,t^{3} - 0.005112t^{2} + 0.076154t + 2.822563
\end{aligned}
$$

### b) Giá trị và đạo hàm tại $\bar x=1.63$

Tại $\bar x=1.63$, ta có $\bar t=\dfrac{1.63-1.8}{0.1}=-1.7$. Tính $P_8(\bar t)$ và $P_8'(\bar t)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(1.63)\approx P_8(\bar t)=2.678167,\qquad \frac{dP_8}{dt}\bigg|_{t=\bar t}=0.093798.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(1.63)\approx\frac{1}{h}\,\frac{dP_8}{dt}\bigg|_{t=\bar t}=\frac{0.093798}{0.1}=0.937977.
$$

## Câu 14. Đa thức nội suy Bessel

**Đề (đã sửa).** Câu 14b ghi $\bar x=1.63$ (ngoài bảng $[5;5.7]$); sửa thành $\bar x=5.23$.

**Phương pháp.** 8 mốc cách đều (số chẵn) nên dùng Bessel, hai mốc chính giữa $x_0=5.3$, $x_1=5.4$ ($i=-3..4$), $h=0.1$. Đặt $t=\dfrac{x-x_0}{h}=\dfrac{x-5.3}{0.1}$ và biến đối xứng $u=t-\dfrac12=\dfrac{x-5.35}{0.1}$. Công thức nội suy Bessel bậc $7$ theo biến $u$ có dạng:

$$
\begin{aligned}
P_{7}(u) &= \dfrac{y_{0} + y_{1}}{2} +\Delta y_{0}\,u +\dfrac{\Delta^{2}y_{-1} + \Delta^{2}y_{0}}{2\cdot2!}(u^2-\tfrac{1}{4}) +\dfrac{\Delta^{3}y_{-1}}{3!}u(u^2-\tfrac{1}{4}) \\
&\quad +\dfrac{\Delta^{4}y_{-2} + \Delta^{4}y_{-1}}{2\cdot4!}(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots +\dfrac{\Delta^{7}y_{-3}}{7!}u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})
\end{aligned}
$$

### a) Lập đa thức Bessel

**Bảng sai phân** (ô khung: cặp $\Delta^{2j}y_{-j},\Delta^{2j}y_{-j+1}$ và $\Delta^{2j+1}y_{-j}$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,7;\ i=-3,\dots,4-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ | $\Delta^{7}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-3$ | $5$ | $3.9931011$ | $0.1347557$ | $0.0097133$ | $-0.0004441$ | $-0.0000935$ | $0.0000077$ | $\boxed{-0.0000065}$ | $\boxed{0.0000262}$ |
| $-2$ | $5.1$ | $4.1278568$ | $0.1444690$ | $0.0092692$ | $-0.0005376$ | $\boxed{-0.0000858}$ | $\boxed{0.0000012}$ | $\boxed{0.0000197}$ | |
| $-1$ | $5.2$ | $4.2723258$ | $0.1537382$ | $\boxed{0.0087316}$ | $\boxed{-0.0006234}$ | $\boxed{-0.0000846}$ | $0.0000209$ | | |
| $0$ | $5.3$ | $\boxed{4.4260640}$ | $\boxed{0.1624698}$ | $\boxed{0.0081082}$ | $-0.0007080$ | $-0.0000637$ | | | |
| $1$ | $5.4$ | $\boxed{4.5885338}$ | $0.1705780$ | $0.0074002$ | $-0.0007717$ | | | | |
| $2$ | $5.5$ | $4.7591118$ | $0.1779782$ | $0.0066285$ | | | | | |
| $3$ | $5.6$ | $4.9370900$ | $0.1846067$ | | | | | | |
| $4$ | $5.7$ | $5.1216967$ | | | | | | | |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{7}(u) &= \dfrac{4.4260640+4.5885338}{2} +0.1624698u +\dfrac{0.0087316+0.0081082}{2\cdot2!}(u^2-\tfrac{1}{4}) \\
&\quad +\dfrac{-0.0006234}{3!}u(u^2-\tfrac{1}{4}) +\dfrac{-0.0000858-0.0000846}{2\cdot4!}(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots \\
 &= 4.507299 +0.16247u +0.00421(u^2-\tfrac{1}{4}) \\
&\quad -0.000104u(u^2-\tfrac{1}{4}) -3.55\cdot10^{-6}\,(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
c = \bigl(4.507299;\ 0.16247;\ 0.00421;\ -0.000104;\ -3.55\cdot10^{-6};\ 1\cdot10^{-8};\ 9.166667\cdot10^{-9};\ 5.198413\cdot10^{-9}\bigr)
$$

Khai triển các tích cơ sở theo luỹ thừa của $u$ ta có bảng nhân ($\Omega_0=1$, $\Omega_1=u$, $\Omega_{2j}=\Omega_{2j-2}\cdot\big(u^2-(j-\frac12)^2\big)$, $\Omega_{2j+1}=u\,\Omega_{2j}$):

| | $u^{7}$ | $u^{6}$ | $u^{5}$ | $u^{4}$ | $u^{3}$ | $u^{2}$ | $u$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $u$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $(u^2-\tfrac{1}{4})$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-0.25$ |
| $u(u^2-\tfrac{1}{4})$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-0.25$ | $0$ |
| $(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-2.5$ | $0$ | $0.5625$ |
| $u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})$ | $0$ | $0$ | $1$ | $0$ | $-2.5$ | $0$ | $0.5625$ | $0$ |
| $(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})$ | $0$ | $1$ | $0$ | $-8.75$ | $0$ | $16.1875$ | $0$ | $-3.515625$ |
| $u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})$ | $1$ | $0$ | $-8.75$ | $0$ | $16.1875$ | $0$ | $-3.515625$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_{7}(u) &= 5.198413\cdot10^{-9}\,u^{7} + 9.166667\cdot10^{-9}\,u^{6} - 3.548611\cdot10^{-8}\,u^{5} \\
&\quad - 3.630208\cdot10^{-6}\,u^{4} - 0.000104u^{3} + 0.004219u^{2} + 0.162496u + 4.506244
\end{aligned}
$$

### b) Giá trị và đạo hàm tại $\bar x=5.23$

Tại $\bar x=5.23$, ta có $\bar t=\dfrac{5.23-5.3}{0.1}=-0.7\ \Longrightarrow\ \bar u=\bar t-\frac12=-1.2$. Tính $P_7(\bar u)$ và $P_7'(\bar u)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(5.23)\approx P_7(\bar u)=4.317497,\qquad \frac{dP_7}{du}\bigg|_{u=\bar u}=0.151946.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(5.23)\approx\frac{1}{h}\,\frac{dP_7}{du}\bigg|_{u=\bar u}=\frac{0.151946}{0.1}=1.519463.
$$

## Câu 15. Thuật toán Gauss I, Gauss II, Stirling, Bessel

### a) Gauss I, Gauss II

**Thuật toán: Gauss I / Gauss II**

- **Input:** vector $x$, $y$ (mốc cách đều); điểm $\bar x$; cấp đạo hàm $r$; số mốc dùng $m$; công thức (Gauss I hoặc Gauss II).
- **Output:** vector $b=(b_n,\dots,b_0)$ với $P(t)=\sum_lb_lt^l$, $t=\frac{x-x_0}{h}$; vector $f=(f_0,\dots,f_r)$, $f_j\approx f^{(j)}(\bar x)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì báo “mốc không cách đều”, dừng thuật toán.<br> Nếu $m<1$ hoặc $r<0$ thì báo lỗi, dừng thuật toán.<br> Nếu $m>n+1$ thì đặt $m:=n+1$.
- **Bước 1:** **Trích xuất, mốc trung tâm:** Gọi thuật toán Câu 11a với $x$, $y$, $\bar x$, $k:=m$, được $X$, $Y$.<br> Đặt $n:=m-1$.<br> Nếu Gauss I thì đặt $q:=\lfloor n/2\rfloor$; nếu Gauss II thì đặt $q:=\lceil n/2\rceil$.<br> Lấy mốc thứ $q$ của $X$ (đếm từ $0$) làm $x_0$, đánh số lại $X$, $Y$ thành $x_i$, $y_i$, $i=-q,\dots,n-q$.
- **Bước 2:** **Bảng sai phân:** Khởi tạo ma trận $D$, hàng $i=-q,\dots,n-q$, cột $k=0,\dots,n$ ($D_{i,k}=\Delta^ky_i$).<br> Lặp $i=-q,\dots,n-q$: đặt $D_{i,0}:=y_i$.<br> Lặp lồng $k=1,\dots,n$; $i=-q,\dots,n-q-k$: tính $D_{i,k}:=D_{i+1,k-1}-D_{i,k-1}$.
- **Bước 3:** **Hệ số:** Lặp $k=0,\dots,n$:<br>&emsp;&emsp; nếu Gauss I thì tính $c_k:=D_{-\lfloor k/2\rfloor,k}/k!$ và đặt $z_k:=(-1)^{k+1}\lceil k/2\rceil$ ($z=0,1,-1,2,\dots$);<br>&emsp;&emsp; nếu Gauss II thì tính $c_k:=D_{-\lceil k/2\rceil,k}/k!$ và đặt $z_k:=(-1)^{k}\lceil k/2\rceil$ ($z=0,-1,1,-2,\dots$).
- **Bước 4:** **Bảng tích, cộng dồn:** Khởi tạo vector $e=(e_0,e_1,\dots,e_n):=(1,0,\dots,0)$, $b=(b_0,b_1,\dots,b_n):=(c_0,0,\dots,0)$, gồm $n+1$ phần tử.<br> Lặp $k=1,\dots,n$:
  - **4.1:** Nhân vector $e$ với $(t-z_{k-1})$ theo thuật toán Câu 5a.
  - **4.2:** Lặp $l=0,\dots,k$: tính $b_l:=b_l+c_k\,e_l$.
- **Bước 5:** **Giá trị, đạo hàm:** Tính $\bar t:=(\bar x-x_0)/h$.<br> Gọi thuật toán Câu 4c với vector $b$, $c:=\bar t$, cấp $k:=r$, được vector $d=(d_0,\dots,d_r)$.<br> Lặp $j=0,\dots,r$: tính $f_j:=d_j/h^j$.<br> Dừng thuật toán, trả về $b$ và $f$.

### b) Stirling

**Thuật toán: Stirling**

- **Input:** vector $x$, $y$ (mốc cách đều); điểm $\bar x$; cấp đạo hàm $r$; số mốc dùng $m$.
- **Output:** vector $b=(b_n,\dots,b_0)$ với $P(t)=\sum_lb_lt^l$, $t=\frac{x-x_0}{h}$; vector $f=(f_0,\dots,f_r)$, $f_j\approx f^{(j)}(\bar x)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì báo “mốc không cách đều”, dừng thuật toán.<br> Nếu $r<0$ thì báo lỗi, dừng thuật toán.<br> Nếu $m>n+1$ thì đặt $m:=n+1$.<br> Nếu $m$ chẵn thì đặt $m:=m-1$.<br> Nếu $m<3$ thì báo lỗi (cần ít nhất 3 mốc), dừng thuật toán.
- **Bước 1:** **Trích xuất, mốc trung tâm:** Gọi thuật toán Câu 11a với $x$, $y$, $\bar x$, $k:=m$, được $X$, $Y$.<br> Đặt $n:=m-1$, $s:=n/2$.<br> Lấy mốc chính giữa của $X$ làm $x_0$, đánh số lại $X$, $Y$ thành $x_i$, $y_i$, $i=-s,\dots,s$.
- **Bước 2:** **Bảng sai phân:** Khởi tạo ma trận $D$, hàng $i=-s,\dots,s$, cột $k=0,\dots,n$ ($D_{i,k}=\Delta^ky_i$).<br> Lặp $i=-s,\dots,s$: đặt $D_{i,0}:=y_i$.<br> Lặp lồng $k=1,\dots,n$; $i=-s,\dots,s-k$: tính $D_{i,k}:=D_{i+1,k-1}-D_{i,k-1}$.
- **Bước 3:** **Hệ số:** Đặt $c_0:=D_{0,0}$.<br> Lặp $j=1,\dots,s$:<br>&emsp;&emsp; tính $c_{2j-1}:=\dfrac{D_{-j,2j-1}+D_{-j+1,2j-1}}{2\,(2j-1)!}$;<br>&emsp;&emsp; tính $c_{2j}:=\dfrac{D_{-j,2j}}{(2j)!}$.
- **Bước 4:** **Bảng nhân, cộng dồn:** Khởi tạo vector $\Omega_0:=(1)$, $\Omega_1:=(0,1)$ ($\Omega_{k,l}$ là hệ số của $t^l$ trong $\Omega_k$; $\Omega_1=t$) và $b=(b_0,b_1,\dots,b_n):=(c_0,c_1,0,\dots,0)$, gồm $n+1$ phần tử.<br> Lặp $k=2,\dots,n$:
  - **4.1:** Nếu $k$ chẵn thì $\Omega_k:=t\,\Omega_{k-1}$: đặt $\Omega_{k,0}:=0$, lặp $l=1,\dots,k$: đặt $\Omega_{k,l}:=\Omega_{k-1,l-1}$.<br> Nếu $k=2j+1$ lẻ thì $\Omega_k:=\Omega_{k-2}\cdot(t^2-j^2)$: nhân vector $\Omega_{k-2}$ với $(t-j)$ rồi với $(t+j)$ theo thuật toán Câu 5a.
  - **4.2:** Lặp $l=0,\dots,k$: tính $b_l:=b_l+c_k\,\Omega_{k,l}$.
- **Bước 5:** **Giá trị, đạo hàm:** Tính $\bar t:=(\bar x-x_0)/h$.<br> Gọi thuật toán Câu 4c với vector $b$, $c:=\bar t$, cấp $k:=r$, được vector $d=(d_0,\dots,d_r)$.<br> Lặp $j=0,\dots,r$: tính $f_j:=d_j/h^j$.<br> Dừng thuật toán, trả về $b$ và $f$.

### c) Bessel

**Thuật toán: Bessel**

- **Input:** vector $x$, $y$ (mốc cách đều); điểm $\bar x$; cấp đạo hàm $r$; số mốc dùng $m$.
- **Output:** vector $b=(b_n,\dots,b_0)$ với $P(u)=\sum_lb_lu^l$, $u=t-\frac12$; vector $f=(f_0,\dots,f_r)$, $f_j\approx f^{(j)}(\bar x)$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì báo “mốc không cách đều”, dừng thuật toán.<br> Nếu $r<0$ thì báo lỗi, dừng thuật toán.<br> Nếu $m>n+1$ thì đặt $m:=n+1$.<br> Nếu $m$ lẻ thì đặt $m:=m-1$.<br> Nếu $m<2$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.
- **Bước 1:** **Trích xuất, mốc trung tâm:** Gọi thuật toán Câu 11a với $x$, $y$, $\bar x$, $k:=m$, được $X$, $Y$.<br> Đặt $n:=m-1$, $s:=\frac{n+1}{2}$.<br> Lấy mốc thứ $s-1$ của $X$ (đếm từ $0$) làm $x_0$ ($x_0$, $x_1$ là hai mốc chính giữa), đánh số lại $X$, $Y$ thành $x_i$, $y_i$, $i=-(s-1),\dots,s$.
- **Bước 2:** **Bảng sai phân:** Khởi tạo ma trận $D$, hàng $i=-(s-1),\dots,s$, cột $k=0,\dots,n$ ($D_{i,k}=\Delta^ky_i$).<br> Lặp $i=-(s-1),\dots,s$: đặt $D_{i,0}:=y_i$.<br> Lặp lồng $k=1,\dots,n$; $i=-(s-1),\dots,s-k$: tính $D_{i,k}:=D_{i+1,k-1}-D_{i,k-1}$.
- **Bước 3:** **Hệ số:** Lặp $j=0,\dots,s-1$:<br>&emsp;&emsp; tính $c_{2j}:=\dfrac{D_{-j,2j}+D_{-j+1,2j}}{2\,(2j)!}$;<br>&emsp;&emsp; tính $c_{2j+1}:=\dfrac{D_{-j,2j+1}}{(2j+1)!}$.
- **Bước 4:** **Bảng nhân, cộng dồn:** Khởi tạo vector $\Omega_0:=(1)$, $\Omega_1:=(0,1)$ ($\Omega_{k,l}$ là hệ số của $u^l$ trong $\Omega_k$; $\Omega_1=u$, $u=t-\frac12$) và $b=(b_0,b_1,\dots,b_n):=(c_0,c_1,0,\dots,0)$, gồm $n+1$ phần tử.<br> Lặp $k=2,\dots,n$:
  - **4.1:** Nếu $k$ lẻ thì $\Omega_k:=u\,\Omega_{k-1}$: đặt $\Omega_{k,0}:=0$, lặp $l=1,\dots,k$: đặt $\Omega_{k,l}:=\Omega_{k-1,l-1}$.<br> Nếu $k=2j$ chẵn thì $\Omega_k:=\Omega_{k-2}\cdot\big(u^2-(j-\frac12)^2\big)$: nhân vector $\Omega_{k-2}$ với $\big(u-(j-\frac12)\big)$ rồi với $\big(u+(j-\frac12)\big)$ theo thuật toán Câu 5a.
  - **4.2:** Lặp $l=0,\dots,k$: tính $b_l:=b_l+c_k\,\Omega_{k,l}$.
- **Bước 5:** **Giá trị, đạo hàm:** Tính $\bar u:=(\bar x-x_0)/h-\frac12$.<br> Gọi thuật toán Câu 4c với vector $b$, $c:=\bar u$, cấp $k:=r$, được vector $d=(d_0,\dots,d_r)$.<br> Lặp $j=0,\dots,r$: tính $f_j:=d_j/h^j$.<br> Dừng thuật toán, trả về $b$ và $f$.

## Câu 16. Trích xuất 9 điểm và nội suy Stirling tại $\bar x=7.83$

### a) Trích xuất

Dữ liệu `data Câu 11.xlsx` đã xử lý ở câu 11b ($N=141$ mốc cách đều $x_i=1+0.1\,i$ ($i=\overline{0,140}$, $x_i\in[1;\,15]$, bước lưới $h=0.1$)). Thuật toán câu 11a ($\bar x=7.83$, $k=9$): mốc gần $\bar x$ nhất là $x_{68}=7.8$ ($j=\operatorname{round}\tfrac{7.83-1}{0.1}=68$); thêm lần lượt $x_{69},x_{67},x_{70},x_{66},x_{71},x_{65},x_{72},x_{64}$ $\Rightarrow$ $4$ mốc trái, $4$ mốc phải, $L=64$, $R=72$. Chọn tâm $x_0=7.8$ (mốc chính giữa) và trích xuất $9$ mốc đối xứng ứng với chỉ số gốc $64,\dots,72$, đánh số lại $i=-4..4$:

| $i$ | $-4$ | $-3$ | $-2$ | $-1$ | $0$ | $1$ | $2$ | $3$ | $4$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $\text{chỉ số gốc}$ | $64$ | $65$ | $66$ | $67$ | $68$ | $69$ | $70$ | $71$ | $72$ |
| $x_i$ | $7.4$ | $7.5$ | $7.6$ | $7.7$ | $7.8$ | $7.9$ | $8$ | $8.1$ | $8.2$ |
| $y_i$ | $8.7480183$ | $8.9069653$ | $9.0518544$ | $9.182237$ | $9.2978096$ | $9.3984166$ | $9.4840519$ | $9.5548591$ | $9.6111298$ |

### b) Đa thức Stirling, $f(\bar x)$, $f'(\bar x)$

**Phương pháp.** 9 mốc cách đều (số lẻ) nên dùng Stirling, mốc trung tâm $x_0=7.8$ ($i=-4..4$), $h=0.1$. Đặt biến chuẩn hoá $t=\dfrac{x-x_0}{h}=\dfrac{x-7.8}{0.1}$. Công thức nội suy Stirling bậc $8$ có dạng:

$$
\begin{aligned}
P_{8}(t) &= y_{0} +\dfrac{\Delta y_{-1} + \Delta y_{0}}{2}t +\dfrac{\Delta^{2}y_{-1}}{2!}t^2 +\dfrac{\Delta^{3}y_{-2} + \Delta^{3}y_{-1}}{2\cdot3!}t(t^2-1) \\
&\quad +\dfrac{\Delta^{4}y_{-2}}{4!}t^2(t^2-1) +\cdots +\dfrac{\Delta^{8}y_{-4}}{8!}t^2(t^2-1)(t^2-4)(t^2-9)
\end{aligned}
$$

**Bảng sai phân** (ô khung: cặp $\Delta^{2j-1}y_{-j},\Delta^{2j-1}y_{-j+1}$ và $\Delta^{2j}y_{-j}$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,8;\ i=-4,\dots,4-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ | $\Delta^{7}y_i$ | $\Delta^{8}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-4$ | $7.4$ | $8.7480183$ | $0.1589470$ | $-0.0140579$ | $-0.0004486$ | $0.0001451$ | $0.0000028$ | $-0.0000012$ | $\boxed{-0.0000002}$ | $\boxed{-0.0000003}$ |
| $-3$ | $7.5$ | $8.9069653$ | $0.1448891$ | $-0.0145065$ | $-0.0003035$ | $0.0001479$ | $\boxed{0.0000016}$ | $\boxed{-0.0000014}$ | $\boxed{-0.0000005}$ | |
| $-2$ | $7.6$ | $9.0518544$ | $0.1303826$ | $-0.0148100$ | $\boxed{-0.0001556}$ | $\boxed{0.0001495}$ | $\boxed{0.0000002}$ | $-0.0000019$ | | |
| $-1$ | $7.7$ | $9.1822370$ | $\boxed{0.1155726}$ | $\boxed{-0.0149656}$ | $\boxed{-0.0000061}$ | $0.0001497$ | $-0.0000017$ | | | |
| $0$ | $7.8$ | $\boxed{9.2978096}$ | $\boxed{0.1006070}$ | $-0.0149717$ | $0.0001436$ | $0.0001480$ | | | | |
| $1$ | $7.9$ | $9.3984166$ | $0.0856353$ | $-0.0148281$ | $0.0002916$ | | | | | |
| $2$ | $8$ | $9.4840519$ | $0.0708072$ | $-0.0145365$ | | | | | | |
| $3$ | $8.1$ | $9.5548591$ | $0.0562707$ | | | | | | | |
| $4$ | $8.2$ | $9.6111298$ | | | | | | | | |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{8}(t) &= 9.2978096 +\dfrac{0.1155726+0.1006070}{2}t +\dfrac{-0.0149656}{2!}t^2 \\
&\quad +\dfrac{-0.0001556-0.0000061}{2\cdot3!}t(t^2-1) +\dfrac{0.0001495}{4!}t^2(t^2-1) +\cdots \\
 &= 9.29781 +0.10809t -0.007483t^2 -1.3475\cdot10^{-5}\,t(t^2-1) +6.229167\cdot10^{-6}\,t^2(t^2-1) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
\begin{aligned}
c &= \bigl(9.29781;\ 0.10809;\ -0.007483;\ -1.3475\cdot10^{-5};\ 6.229167\cdot10^{-6};\ \\
&\quad 7.5\cdot10^{-9};\ -1.944444\cdot10^{-9};\ -6.944444\cdot10^{-11};\ -7.440476\cdot10^{-12}\bigr)
\end{aligned}
$$

Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân ($\Omega_0=1$, $\Omega_1=t$, $\Omega_{2j}=t\,\Omega_{2j-1}$, $\Omega_{2j+1}=\Omega_{2j-1}\cdot(t^2-j^2)$):

| | $t^{8}$ | $t^{7}$ | $t^{6}$ | $t^{5}$ | $t^{4}$ | $t^{3}$ | $t^{2}$ | $t$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $t$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $t^2$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $0$ |
| $t(t^2-1)$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ |
| $t^2(t^2-1)$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ | $0$ |
| $t(t^2-1)(t^2-4)$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ |
| $t^2(t^2-1)(t^2-4)$ | $0$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ | $0$ |
| $t(t^2-1)(t^2-4)(t^2-9)$ | $0$ | $1$ | $0$ | $-14$ | $0$ | $49$ | $0$ | $-36$ | $0$ |
| $t^2(t^2-1)(t^2-4)(t^2-9)$ | $1$ | $0$ | $-14$ | $0$ | $49$ | $0$ | $-36$ | $0$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_{8}(t) &= -7.440476\cdot10^{-12}\,t^{8} - 6.944444\cdot10^{-11}\,t^{7} - 1.840278\cdot10^{-9}\,t^{6} + 8.472222\cdot10^{-9}\,t^{5} \\
&\quad + 6.238524\cdot10^{-6}\,t^{4} - 1.35159\cdot10^{-5}\,t^{3} - 0.007489t^{2} + 0.108103t + 9.29781
\end{aligned}
$$

Tại $\bar x=7.83$, ta có $\bar t=\dfrac{7.83-7.8}{0.1}=0.3$. Tính $P_8(\bar t)$ và $P_8'(\bar t)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(7.83)\approx P_8(\bar t)=9.329566,\qquad \frac{dP_8}{dt}\bigg|_{t=\bar t}=0.103607.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(7.83)\approx\frac{1}{h}\,\frac{dP_8}{dt}\bigg|_{t=\bar t}=\frac{0.103607}{0.1}=1.036069.
$$

## Câu 17. Trích xuất 8 điểm và nội suy Bessel tại $\bar x=7.83$

### a) Trích xuất

Thuật toán câu 11a ($\bar x=7.83$, $k=8$, dữ liệu câu 11b): mốc gần $\bar x$ nhất là $x_{68}=7.8$ ($j=\operatorname{round}\tfrac{7.83-1}{0.1}=68$); thêm lần lượt $x_{69},x_{67},x_{70},x_{66},x_{71},x_{65},x_{72}$ $\Rightarrow$ $3$ mốc trái, $4$ mốc phải, $L=65$, $R=72$. $\bar x=7.83$ nằm trong khoảng trung tâm $[x_{68};x_{69}]=[7.8;\,7.9]$. Chọn $x_0=7.8$, $x_1=7.9$ (hai mốc chính giữa) và trích xuất $8$ mốc ứng với chỉ số gốc $65,\dots,72$, đánh số lại $i=-3..4$:

| $i$ | $-3$ | $-2$ | $-1$ | $0$ | $1$ | $2$ | $3$ | $4$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $\text{chỉ số gốc}$ | $65$ | $66$ | $67$ | $68$ | $69$ | $70$ | $71$ | $72$ |
| $x_i$ | $7.5$ | $7.6$ | $7.7$ | $7.8$ | $7.9$ | $8$ | $8.1$ | $8.2$ |
| $y_i$ | $8.9069653$ | $9.0518544$ | $9.182237$ | $9.2978096$ | $9.3984166$ | $9.4840519$ | $9.5548591$ | $9.6111298$ |

### b) Đa thức Bessel, $f(\bar x)$, $f'(\bar x)$

**Phương pháp.** 8 mốc cách đều (số chẵn) nên dùng Bessel, hai mốc chính giữa $x_0=7.8$, $x_1=7.9$ ($i=-3..4$), $h=0.1$. Đặt $t=\dfrac{x-x_0}{h}=\dfrac{x-7.8}{0.1}$ và biến đối xứng $u=t-\dfrac12=\dfrac{x-7.85}{0.1}$. Công thức nội suy Bessel bậc $7$ theo biến $u$ có dạng:

$$
\begin{aligned}
P_{7}(u) &= \dfrac{y_{0} + y_{1}}{2} +\Delta y_{0}\,u +\dfrac{\Delta^{2}y_{-1} + \Delta^{2}y_{0}}{2\cdot2!}(u^2-\tfrac{1}{4}) +\dfrac{\Delta^{3}y_{-1}}{3!}u(u^2-\tfrac{1}{4}) \\
&\quad +\dfrac{\Delta^{4}y_{-2} + \Delta^{4}y_{-1}}{2\cdot4!}(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots +\dfrac{\Delta^{7}y_{-3}}{7!}u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})
\end{aligned}
$$

**Bảng sai phân** (ô khung: cặp $\Delta^{2j}y_{-j},\Delta^{2j}y_{-j+1}$ và $\Delta^{2j+1}y_{-j}$):

$$
\Delta^0y_i=y_i,\qquad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i\quad(k=1,\dots,7;\ i=-3,\dots,4-k).
$$

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ | $\Delta^{7}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-3$ | $7.5$ | $8.9069653$ | $0.1448891$ | $-0.0145065$ | $-0.0003035$ | $0.0001479$ | $0.0000016$ | $\boxed{-0.0000014}$ | $\boxed{-0.0000005}$ |
| $-2$ | $7.6$ | $9.0518544$ | $0.1303826$ | $-0.0148100$ | $-0.0001556$ | $\boxed{0.0001495}$ | $\boxed{0.0000002}$ | $\boxed{-0.0000019}$ | |
| $-1$ | $7.7$ | $9.1822370$ | $0.1155726$ | $\boxed{-0.0149656}$ | $\boxed{-0.0000061}$ | $\boxed{0.0001497}$ | $-0.0000017$ | | |
| $0$ | $7.8$ | $\boxed{9.2978096}$ | $\boxed{0.1006070}$ | $\boxed{-0.0149717}$ | $0.0001436$ | $0.0001480$ | | | |
| $1$ | $7.9$ | $\boxed{9.3984166}$ | $0.0856353$ | $-0.0148281$ | $0.0002916$ | | | | |
| $2$ | $8$ | $9.4840519$ | $0.0708072$ | $-0.0145365$ | | | | | |
| $3$ | $8.1$ | $9.5548591$ | $0.0562707$ | | | | | | |
| $4$ | $8.2$ | $9.6111298$ | | | | | | | |

Thay các ô khung vào công thức:

$$
\begin{aligned}
P_{7}(u) &= \dfrac{9.2978096+9.3984166}{2} +0.1006070u +\dfrac{-0.0149656-0.0149717}{2\cdot2!}(u^2-\tfrac{1}{4}) \\
&\quad +\dfrac{-0.0000061}{3!}u(u^2-\tfrac{1}{4}) +\dfrac{0.0001495+0.0001497}{2\cdot4!}(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots \\
 &= 9.348113 +0.100607u -0.007484(u^2-\tfrac{1}{4}) \\
&\quad -1.016667\cdot10^{-6}\,u(u^2-\tfrac{1}{4}) +6.233333\cdot10^{-6}\,(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4}) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
\begin{aligned}
c &= \bigl(9.348113;\ 0.100607;\ -0.007484;\ -1.016667\cdot10^{-6};\ 6.233333\cdot10^{-6};\ \\
&\quad 1.666667\cdot10^{-9};\ -2.291667\cdot10^{-9};\ -9.920635\cdot10^{-11}\bigr)
\end{aligned}
$$

Khai triển các tích cơ sở theo luỹ thừa của $u$ ta có bảng nhân ($\Omega_0=1$, $\Omega_1=u$, $\Omega_{2j}=\Omega_{2j-2}\cdot\big(u^2-(j-\frac12)^2\big)$, $\Omega_{2j+1}=u\,\Omega_{2j}$):

| | $u^{7}$ | $u^{6}$ | $u^{5}$ | $u^{4}$ | $u^{3}$ | $u^{2}$ | $u$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $u$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $(u^2-\tfrac{1}{4})$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-0.25$ |
| $u(u^2-\tfrac{1}{4})$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-0.25$ | $0$ |
| $(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-2.5$ | $0$ | $0.5625$ |
| $u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})$ | $0$ | $0$ | $1$ | $0$ | $-2.5$ | $0$ | $0.5625$ | $0$ |
| $(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})$ | $0$ | $1$ | $0$ | $-8.75$ | $0$ | $16.1875$ | $0$ | $-3.515625$ |
| $u(u^2-\tfrac{1}{4})(u^2-\tfrac{9}{4})(u^2-\tfrac{25}{4})$ | $1$ | $0$ | $-8.75$ | $0$ | $16.1875$ | $0$ | $-3.515625$ | $0$ |

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
\begin{aligned}
P_{7}(u) &= -9.920635\cdot10^{-11}\,u^{7} - 2.291667\cdot10^{-9}\,u^{6} + 2.534722\cdot10^{-9}\,u^{5} \\
&\quad + 6.253385\cdot10^{-6}\,u^{4} - 1.022439\cdot10^{-6}\,u^{3} - 0.0075u^{2} + 0.100607u + 9.349988
\end{aligned}
$$

Tại $\bar x=7.83$, ta có $\bar t=\dfrac{7.83-7.8}{0.1}=0.3\ \Longrightarrow\ \bar u=\bar t-\frac12=-0.2$. Tính $P_7(\bar u)$ và $P_7'(\bar u)$ bằng sơ đồ Horner chia lặp (Câu 4c):

$$
f(7.83)\approx P_7(\bar u)=9.329566,\qquad \frac{dP_7}{du}\bigg|_{u=\bar u}=0.103607.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(7.83)\approx\frac{1}{h}\,\frac{dP_7}{du}\bigg|_{u=\bar u}=\frac{0.103607}{0.1}=1.036069.
$$

## Câu 18. Thuật toán cho bài toán nội suy ngược

### a) Tất cả các khoảng cách ly của $f(x)=\bar y$

**Thuật toán: Khoảng cách ly**

- **Input:** vector $x$, $y$ ($n+1$ mốc); giá trị $\bar y$.
- **Output:** danh sách $N$ các mốc là nghiệm; danh sách $K$ các khoảng cách ly $(x_i,x_{i+1})$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.
- **Bước 1:** **Khởi tạo:** Đặt $N:=\varnothing$, $K:=\varnothing$.<br> Lặp $i=0,\dots,n$: tính $g_i:=y_i-\bar y$.
- **Bước 2:** **Tìm khoảng cách ly:** Lặp $i=0,\dots,n$:<br>&emsp;&emsp; nếu $g_i=0$ thì thêm $x_i$ vào $N$;<br>&emsp;&emsp; nếu $i<n$ và $g_i\,g_{i+1}<0$ thì thêm $(x_i,x_{i+1})$ vào $K$.
- **Bước 3:** **Kết thúc:** Nếu $N$ và $K$ đều rỗng thì báo “phương trình không có nghiệm trong $[x_0,x_n]$”.<br> Dừng thuật toán, trả về $N$ và $K$.

### b) Các khoảng đơn điệu

**Thuật toán: Khoảng đơn điệu**

- **Input:** vector $x$, $y$ ($n+1$ mốc).
- **Output:** danh sách các đoạn $[x_a,x_b]$ kèm chiều tăng / giảm / hằng.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.
- **Bước 1:** **Dấu của $\Delta y_i$:** Lặp $i=0,\dots,n-1$: tính $s_i:=\operatorname{sign}(y_{i+1}-y_i)$.<br> Đặt $a:=0$.
- **Bước 2:** **Tách đoạn:** Lặp $i=1,\dots,n-1$:<br>&emsp;&emsp; nếu $s_i\ne s_{i-1}$ thì ghi đoạn $[x_a,x_i]$ với chiều $s_{i-1}$ và đặt $a:=i$.
- **Bước 3:** **Đoạn cuối:** Ghi đoạn $[x_a,x_n]$ với chiều $s_{n-1}$.<br> Dừng thuật toán, trả về danh sách các đoạn.

### c) Phương pháp hàm ngược

**Thuật toán: Hàm ngược**

- **Input:** vector $x$, $y$; $\bar y$; khoảng cách ly $(x_k,x_{k+1})$ nằm trong đoạn đơn điệu $[x_a,x_b]$ (câu a, b); số mốc $m$.
- **Output:** nghiệm gần đúng $\bar x$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $m<2$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Khởi tạo:** Đặt $L:=k$, $R:=k+1$.
- **Bước 2:** **Chọn mốc:** Lặp $s=3,\dots,m$:<br>&emsp;&emsp; nếu $L=a$ và $R=b$ thì dừng lặp;<br>&emsp;&emsp; ngược lại nếu $L=a$ thì $R:=R+1$;<br>&emsp;&emsp; ngược lại nếu $R=b$ thì $L:=L-1$;<br>&emsp;&emsp; ngược lại nếu $|y_{L-1}-\bar y|\le|y_{R+1}-\bar y|$ thì $L:=L-1$, còn không thì $R:=R+1$.
- **Bước 3:** **Đổi vai trò $x$, $y$:** Đặt $u:=(y_L,\dots,y_R)$, $v:=(x_L,\dots,x_R)$ (đánh số lại $0,\dots,R-L$).<br> Nếu đoạn giảm thì đảo thứ tự $u$, $v$ để $u_0<u_1<\cdots$.
- **Bước 4:** **Bảng tỷ sai phân:** Khởi tạo ma trận $T$ cỡ $(R-L+1)\times(R-L+1)$ (tỷ sai phân của $v$ theo $u$).<br> Lặp $i=0,\dots,R-L$: đặt $T_{i,0}:=v_i$.<br> Lặp lồng $j=1,\dots,R-L$; $i=j,\dots,R-L$: tính $T_{i,j}:=\dfrac{T_{i,j-1}-T_{i-1,j-1}}{u_i-u_{i-j}}$.<br> Lặp $j=0,\dots,R-L$: đặt $c_j:=T_{j,j}$.
- **Bước 5:** **Giá trị tại $\bar y$:** Đặt $\omega:=1$, $S:=c_0$.<br> Lặp $j=1,\dots,R-L$:<br>&emsp;&emsp; tính $\omega:=\omega\,(\bar y-u_{j-1})$;<br>&emsp;&emsp; tính $S:=S+c_j\,\omega$.
- **Bước 6:** **Kết thúc:** Đặt $\bar x:=S$.<br> Dừng thuật toán, trả về $\bar x$ (số hạng cuối $|c_{R-L}\,\omega|$ là ước lượng sai số).

### d) Phương pháp lặp

**Thuật toán: Lặp Newton tiến / lùi giải $f(x)=\bar y$**

- **Input:** vector $x$, $y$ ($n+1$ mốc cách đều bước $h$); $\bar y$; khoảng cách ly $(x_k,x_{k+1})$; số mốc $m$; sai số $\varepsilon$; số lần lặp tối đa $N$.
- **Output:** nghiệm gần đúng $\bar x$, hoặc thông báo “Không hội tụ”.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì: cùng $y$ giữ một mốc, khác $y$ báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Đặt $h:=\dfrac{x_n-x_0}{n}$.<br> Lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $|x_{i+1}-x_i-h|>10^{-6}h$ thì tìm đoạn đơn điệu $[x_a,x_b]$ chứa $(x_k,x_{k+1})$ theo thuật toán câu b, gọi thuật toán câu c với $x$, $y$, $\bar y$, $k$, $a$, $b$, $m$ được $\bar x$, dừng thuật toán, trả về $\bar x$.<br> Nếu $m<2$, $\varepsilon\le0$ hoặc $N<1$ thì báo lỗi, dừng thuật toán.<br> Nếu $k+m-1>n$ và $k+2-m<0$ thì đặt $m:=\max(n-k+1,\,k+2)$.
- **Bước 1:** **Chọn hướng và mốc gốc:**<br>&emsp;&emsp; nếu $k+m-1\le n$ thì lặp tiến, đặt $s:=k$;<br>&emsp;&emsp; trái lại lặp lùi, đặt $s:=k+1$.
- **Bước 2:** **Bảng sai phân:** Khởi tạo ma trận $T$ cỡ $m\times m$ (bảng sai phân của $m$ mốc, đánh số lại $0,\dots,m-1$).<br> Lặp $i=0,\dots,m-1$:<br>&emsp;&emsp; nếu tiến thì đặt $T_{i,0}:=y_{k+i}$;<br>&emsp;&emsp; nếu lùi thì đặt $T_{i,0}:=y_{k+2-m+i}$.<br> Lặp lồng $j=1,\dots,m-1$; $i=j,\dots,m-1$: tính $T_{i,j}:=T_{i,j-1}-T_{i-1,j-1}$.<br> Lặp $j=0,\dots,m-1$:<br>&emsp;&emsp; nếu tiến thì đặt $d_j:=T_{j,j}$ ($=\Delta^jy_k$);<br>&emsp;&emsp; nếu lùi thì đặt $d_j:=T_{m-1,j}$ ($=\nabla^jy_{k+1}$).
- **Bước 3:** **Hàm lặp:** Nếu tiến thì $\varphi(t):=\dfrac{\bar y-d_0}{d_1}-\sum_{j=2}^{m-1}\dfrac{d_j}{j!\,d_1}\,t(t-1)\cdots(t-j+1)$.<br> Nếu lùi thì $\varphi(t):=\dfrac{\bar y-d_0}{d_1}-\sum_{j=2}^{m-1}\dfrac{d_j}{j!\,d_1}\,t(t+1)\cdots(t+j-1)$.
- **Bước 4:** **Khởi tạo:** Đặt $t_0:=\dfrac{\bar y-d_0}{d_1}$, $l:=0$.
- **Bước 5:** **Lặp tìm $t$:** Tính $t_{l+1}:=\varphi(t_l)$.
- **Bước 6:** **Kiểm tra dừng:** Nếu $h\,|t_{l+1}-t_l|<\varepsilon$ thì:<br>&emsp;&emsp; nếu (tiến và $0\le t_{l+1}\le1$) hoặc (lùi và $-1\le t_{l+1}\le0$) thì đặt $\bar x:=x_s+t_{l+1}h$, dừng thuật toán, trả về $\bar x$;<br>&emsp;&emsp; ngược lại báo “nghiệm lặp nằm ngoài khoảng cách ly”, dừng thuật toán.
- **Bước 7:** **Không hội tụ:** Nếu $l+1=N$ thì báo “Không hội tụ”, dừng thuật toán.<br> Trái lại đặt $l:=l+1$, quay lại bước 5.

## Câu 19. Giải phương trình $f(x)=\bar y$ từ file dữ liệu

**Dữ liệu.** `data Câu 19.xlsx` (dòng đầu trống, bỏ qua). Ta có bảng dữ liệu gồm $N=141$ mốc cách đều $x_i=1+0.1\,i$ ($i=\overline{0,140}$, $x_i\in[1;\,15]$, bước lưới $h=0.1$) và các giá trị cho trước $\bar y=2.5$ (câu a), $\bar y=3.15$ (câu b).

**Khoảng đơn điệu** (18b): $\Delta y_i=y_{i+1}-y_i$ đổi dấu tại $i=18,25,81,87$:

| $\text{đoạn}$ | $[1;\ 2.8]$ | $[2.8;\ 3.5]$ | $[3.5;\ 9.1]$ | $[9.1;\ 9.7]$ | $[9.7;\ 15]$ |
|---:|---:|---:|---:|---:|---:|
| $\text{chỉ số}$ | $0..18$ | $18..25$ | $25..81$ | $81..87$ | $87..140$ |
| $y_a$ | $1.8881653$ | $3.1536928$ | $3.1298225$ | $9.4369208$ | $9.4132378$ |
| $y_b$ | $3.1536928$ | $3.1298225$ | $9.4369208$ | $9.4132378$ | $15.6864909$ |
| $\text{chiều}$ | $\text{tăng}$ | $\text{giảm}$ | $\text{tăng}$ | $\text{giảm}$ | $\text{tăng}$ |

**Khoảng cách ly** (18a): $g_i=y_i-\bar y$ đổi dấu giữa $x_k$ và $x_{k+1}$, không có $g_i=0$:

| $\bar y$ | $k$ | $(x_k;x_{k+1})$ | $g_k=y_k-\bar y$ | $g_{k+1}$ | $\text{nằm trong đoạn}$ |
|---:|---:|---:|---:|---:|---:|
| $2.5$ | $4$ | $(1.4;\ 1.5)$ | $-0.0598201$ | $0.0529043$ | $[1;\ 2.8]\ \text{tăng}$ |
| $3.15$ | $16$ | $(2.6;\ 2.7)$ | $-0.0057740$ | $0.0012136$ | $[1;\ 2.8]\ \text{tăng}$ |
| $3.15$ | $19$ | $(2.9;\ 3)$ | $0.0026381$ | $-0.0009410$ | $[2.8;\ 3.5]\ \text{giảm}$ |
| $3.15$ | $27$ | $(3.7;\ 3.8)$ | $-0.0091867$ | $0.0042291$ | $[3.5;\ 9.1]\ \text{tăng}$ |

### a) Phương pháp hàm ngược, $\bar y=2.5$

**Phương pháp** (18c). Trên đoạn đơn điệu chứa khoảng cách ly, $y=f(x)$ có hàm ngược $x=f^{-1}(y)$. Đổi vai trò $x$, $y$: coi $u=y$ là biến, $v=x$ là hàm (mốc $u_s$ không cách đều), lập đa thức Newton tiến của $v$ theo $u$ bằng tỷ sai phân rồi thay $u=\bar y$:

$$
\bar x\approx P(\bar y)=\sum_{j}c_j\,\omega_j(\bar y),\qquad c_j=v[u_0,\dots,u_j],\qquad \omega_0=1,\ \ \omega_j(\bar y)=\prod_{i=0}^{j-1}(\bar y-u_i);
$$

số hạng cuối $|c_j\,\omega_j(\bar y)|$ là ước lượng sai số.

Nghiệm trong $(x_{4};x_{5})=(1.4;\ 1.5)\subset[1;\ 2.8]$, đoạn tăng nên có hàm ngược.

**Chọn 6 mốc** có $|y_j-\bar y|$ nhỏ nhất trong đoạn đơn điệu:

| $\text{lần}$ | $j$ | $x_j$ | $y_j$ | $\vert y_j-\bar y\vert$ |
|---:|---:|---:|---:|---:|
| $1$ | $5$ | $1.5$ | $2.5529043$ | $0.052904$ |
| $2$ | $4$ | $1.4$ | $2.4401799$ | $0.05982$ |
| $3$ | $6$ | $1.6$ | $2.6551084$ | $0.155108$ |
| $4$ | $3$ | $1.3$ | $2.3170624$ | $0.182938$ |
| $5$ | $7$ | $1.7$ | $2.7467702$ | $0.24677$ |
| $6$ | $2$ | $1.2$ | $2.1837828$ | $0.316217$ |

**Bảng tỷ sai phân của $x$ theo $y$** ($u=y$, $v=x$; đường chéo khung $=c_j$):

$$
v[u_{s-k},\dots,u_s]=\frac{v[u_{s-k+1},\dots,u_s]-v[u_{s-k},\dots,u_{s-1}]}{u_s-u_{s-k}}.
$$

| $s$ | $u_s=y$ | $v_s=x$ | $\text{TSP1}$ | $\text{TSP2}$ | $\text{TSP3}$ | $\text{TSP4}$ | $\text{TSP5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $2.1837828$ | $\boxed{1.2}$ | | | | | |
| $1$ | $2.3170624$ | $1.3$ | $\boxed{0.750302}$ | | | | |
| $2$ | $2.4401799$ | $1.4$ | $0.812232$ | $\boxed{0.241539}$ | | | |
| $3$ | $2.5529043$ | $1.5$ | $0.887119$ | $0.317531$ | $\boxed{0.205874}$ | | |
| $4$ | $2.6551084$ | $1.6$ | $0.978434$ | $0.424862$ | $0.317503$ | $\boxed{0.236842}$ | |
| $5$ | $2.7467702$ | $1.7$ | $1.090967$ | $0.580467$ | $0.507533$ | $0.442229$ | $\boxed{0.364817}$ |

**Giá trị tại $\bar y$:** $\bar x=\sum_jc_j\,\omega_j(\bar y)$, $\omega_0=1$, $\omega_j=\omega_{j-1}\cdot(\bar y-u_{j-1})$:

| $j$ | $c_j$ | $\omega_j(\bar y)$ | $c_j\,\omega_j(\bar y)$ | $\text{tổng}$ |
|---:|---:|---:|---:|---:|
| $0$ | $1.2$ | $1$ | $1.2$ | $1.2$ |
| $1$ | $0.750302$ | $0.316217$ | $0.237259$ | $1.437259$ |
| $2$ | $0.241539$ | $0.057848$ | $0.013973$ | $1.451231$ |
| $3$ | $0.205874$ | $0.00346$ | $0.000712$ | $1.451943$ |
| $4$ | $0.236842$ | $-0.000183$ | $-4.33596\cdot10^{-5}$ | $1.4519$ |
| $5$ | $0.364817$ | $2.839631\cdot10^{-5}$ | $1.035945\cdot10^{-5}$ | $1.45191$ |

**Tổng hợp.**

| $\text{Nghiệm}$ | $\text{Khoảng cách ly}$ | $\text{Mốc sử dụng}$ | $\text{Phương pháp áp dụng}$ | $\text{Kết quả}$ |
|:---:|:---:|:---:|:---:|:---:|
| $\bar x$ | $(1.4;\ 1.5)$ | $[1.2;\ 1.7]$ | $\text{hàm ngược (tỷ sai phân } x\text{ theo } y)$ | $1.45191$ |

> **Kết luận.** $f(x)=2.5$ có đúng một nghiệm trong $[1;15]$: $\bar x\approx1.45191$ (số hạng cuối $1.035945\cdot10^{-5}$ — ước lượng sai số).

### b) Phương pháp lặp, $\bar y=3.15$

**Phương pháp** (18d; mỗi khoảng $(x_k;x_{k+1})$ đủ 6 mốc $x_k,\dots,x_{k+5}$ bên phải nên lặp Newton tiến, $t=\frac{x-x_k}{h}$, $\varepsilon=10^{-6}$). Trên mốc cách đều, thay $f$ bằng đa thức nội suy Newton tiến 6 mốc theo $t$; phương trình $P=\bar y$ viết lại thành $t=\varphi(t)$ rồi lặp đơn, nghiệm hợp lệ khi $t^*\in[0;1]$:

$$
\begin{gathered}
\Delta^0y_i=y_i,\qquad \Delta^jy_i=\Delta^{j-1}y_{i+1}-\Delta^{j-1}y_i\quad\text{(bảng sai phân, ô khung }\Delta^jy_k\text{)};\\
\bar y=y_k+\Delta y_k\,t+\frac{\Delta^2y_k}{2!}t(t-1)+\dots+\frac{\Delta^5y_k}{5!}t(t-1)\cdots(t-4)\\
\Longrightarrow\ t=\varphi(t)=\frac{\bar y-y_k}{\Delta y_k}-\frac{\Delta^2y_k}{2!\,\Delta y_k}t(t-1)-\dots-\frac{\Delta^5y_k}{5!\,\Delta y_k}t(t-1)\cdots(t-4),\\
t_0=\frac{\bar y-y_k}{\Delta y_k},\qquad t_{l+1}=\varphi(t_l),\qquad\text{dừng khi } h\,|t_{l+1}-t_l|<\varepsilon,\qquad \bar x=x_k+t_{l+1}h.
\end{gathered}
$$

**Nghiệm 1: $(x_{16};x_{17})=(2.6;\ 2.7)$.** Bảng sai phân:

| $i$ | $x_i$ | $y_i$ | $\Delta$ | $\Delta^{2}$ | $\Delta^{3}$ | $\Delta^{4}$ | $\Delta^{5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $16$ | $2.6$ | $\boxed{3.1442260}$ | | | | | |
| $17$ | $2.7$ | $3.1512136$ | $\boxed{0.0069876}$ | | | | |
| $18$ | $2.8$ | $3.1536928$ | $0.0024792$ | $\boxed{-0.0045084}$ | | | |
| $19$ | $2.9$ | $3.1526381$ | $-0.0010547$ | $-0.0035339$ | $\boxed{0.0009745}$ | | |
| $20$ | $3$ | $3.1490590$ | $-0.0035791$ | $-0.0025244$ | $0.0010095$ | $\boxed{0.0000350}$ | |
| $21$ | $3.1$ | $3.1439906$ | $-0.0050684$ | $-0.0014893$ | $0.0010351$ | $0.0000256$ | $\boxed{-0.0000094}$ |

Thay các ô khung vào $\varphi$:

$$
\begin{aligned}
\varphi(t) &= 0.826321 + 0.3226t(t-1) - 0.023244t(t-1)(t-2) \\
&\quad - 0.000209t(t-1)(t-2)(t-3) + 1.121033\cdot10^{-5}t(t-1)(t-2)(t-3)(t-4)
\end{aligned}
$$

$t_0=0.826321$:

| $l$ | $t_l$ | $h\vert t_l-t_{l-1}\vert$ |
|---:|---:|---:|
| $1$ | $0.776197$ | $0.005012$ |
| $2$ | $0.765455$ | $0.001074$ |
| $\vdots$ | $\vdots$ | $\vdots$ |
| $6$ | $0.76289$ | $1.402065\cdot10^{-6}$ |
| $7$ | $\boxed{0.762887}$ | $2.641891\cdot10^{-7}$ |

Dừng sau $7$ lần, $t_{7}\in[0;1]$: $\bar x_{1}=x_{16}+t_{7}h=2.6+0.762887\cdot0.1=2.676289$.

**Nghiệm 2: $(x_{19};x_{20})=(2.9;\ 3)$.** Bảng sai phân:

| $i$ | $x_i$ | $y_i$ | $\Delta$ | $\Delta^{2}$ | $\Delta^{3}$ | $\Delta^{4}$ | $\Delta^{5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $19$ | $2.9$ | $\boxed{3.1526381}$ | | | | | |
| $20$ | $3$ | $3.1490590$ | $\boxed{-0.0035791}$ | | | | |
| $21$ | $3.1$ | $3.1439906$ | $-0.0050684$ | $\boxed{-0.0014893}$ | | | |
| $22$ | $3.2$ | $3.1384827$ | $-0.0055079$ | $-0.0004395$ | $\boxed{0.0010498}$ | | |
| $23$ | $3.3$ | $3.1335894$ | $-0.0048933$ | $0.0006146$ | $0.0010541$ | $\boxed{0.0000043}$ | |
| $24$ | $3.4$ | $3.1303588$ | $-0.0032306$ | $0.0016627$ | $0.0010481$ | $-0.0000060$ | $\boxed{-0.0000103}$ |

Thay các ô khung vào $\varphi$:

$$
\begin{aligned}
\varphi(t) &= 0.737085 - 0.208055t(t-1) + 0.048886t(t-1)(t-2) \\
&\quad + 5.005914\cdot10^{-5}t(t-1)(t-2)(t-3) - 2.398182\cdot10^{-5}t(t-1)(t-2)(t-3)(t-4)
\end{aligned}
$$

$t_0=0.737085$:

| $l$ | $t_l$ | $h\vert t_l-t_{l-1}\vert$ |
|---:|---:|---:|
| $1$ | $0.789297$ | $0.005221$ |
| $2$ | $0.781472$ | $0.000782$ |
| $\vdots$ | $\vdots$ | $\vdots$ |
| $5$ | $0.782561$ | $3.183231\cdot10^{-6}$ |
| $6$ | $\boxed{0.782556}$ | $5.069014\cdot10^{-7}$ |

Dừng sau $6$ lần, $t_{6}\in[0;1]$: $\bar x_{2}=x_{19}+t_{6}h=2.9+0.782556\cdot0.1=2.978256$.

**Nghiệm 3: $(x_{27};x_{28})=(3.7;\ 3.8)$.** Bảng sai phân:

| $i$ | $x_i$ | $y_i$ | $\Delta$ | $\Delta^{2}$ | $\Delta^{3}$ | $\Delta^{4}$ | $\Delta^{5}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $27$ | $3.7$ | $\boxed{3.1408133}$ | | | | | |
| $28$ | $3.8$ | $3.1542291$ | $\boxed{0.0134158}$ | | | | |
| $29$ | $3.9$ | $3.1740972$ | $0.0198681$ | $\boxed{0.0064523}$ | | | |
| $30$ | $4$ | $3.2012183$ | $0.0271211$ | $0.0072530$ | $\boxed{0.0008007}$ | | |
| $31$ | $4.1$ | $3.2363205$ | $0.0351022$ | $0.0079811$ | $0.0007281$ | $\boxed{-0.0000726}$ | |
| $32$ | $4.2$ | $3.2800524$ | $0.0437319$ | $0.0086297$ | $0.0006486$ | $-0.0000795$ | $\boxed{-0.0000069}$ |

Thay các ô khung vào $\varphi$:

$$
\begin{aligned}
\varphi(t) &= 0.684767 - 0.240474t(t-1) - 0.009947t(t-1)(t-2) \\
&\quad + 0.000225t(t-1)(t-2)(t-3) + 4.285991\cdot10^{-6}t(t-1)(t-2)(t-3)(t-4)
\end{aligned}
$$

$t_0=0.684767$:

| $l$ | $t_l$ | $h\vert t_l-t_{l-1}\vert$ |
|---:|---:|---:|
| $1$ | $0.733713$ | $0.004895$ |
| $2$ | $0.729171$ | $0.000454$ |
| $\vdots$ | $\vdots$ | $\vdots$ |
| $4$ | $0.729591$ | $4.783008\cdot10^{-6}$ |
| $5$ | $\boxed{0.729596}$ | $4.890247\cdot10^{-7}$ |

Dừng sau $5$ lần, $t_{5}\in[0;1]$: $\bar x_{3}=x_{27}+t_{5}h=3.7+0.729596\cdot0.1=3.77296$.

**Tổng hợp.**

| $\text{Nghiệm}$ | $\text{Khoảng cách ly}$ | $\text{Mốc sử dụng}$ | $\text{Phương pháp áp dụng}$ | $\text{Kết quả}$ |
|:---:|:---:|:---:|:---:|:---:|
| $\bar x_{1}$ | $(2.6;\ 2.7)$ | $[2.6;\ 3.1]$ | $\text{lặp Newton tiến (từ } x_{16}=2.6)$ | $2.676289$ |
| $\bar x_{2}$ | $(2.9;\ 3)$ | $[2.9;\ 3.4]$ | $\text{lặp Newton tiến (từ } x_{19}=2.9)$ | $2.978256$ |
| $\bar x_{3}$ | $(3.7;\ 3.8)$ | $[3.7;\ 4.2]$ | $\text{lặp Newton tiến (từ } x_{27}=3.7)$ | $3.77296$ |

> **Kết luận.** $f(x)=3.15$ có $3$ nghiệm trong $[1;15]$: $\bar x=\left(2.676289;\ 2.978256;\ 3.77296\right)$.

## Câu 20. Hàm ghép trơn (spline)

### a) Xây dựng công thức

Spline cấp $p$: $S(x)=S_k(x)$ trên $[x_k,x_{k+1}]$, $S_k$ đa thức bậc $p$, $S\in C^{p-1}[x_0,x_n]$, $S(x_i)=y_i$; $h_k=x_{k+1}-x_k$; cần thêm $p-1$ điều kiện biên.

**Spline cấp 3.** Đặt $\sigma_k=S''(x_k)$. $S_k''$ bậc nhất nên $S_k''(x)=\dfrac{\sigma_k(x_{k+1}-x)+\sigma_{k+1}(x-x_k)}{h_k}$; tích phân hai lần:

$$
S_k(x)=\frac{\sigma_k(x_{k+1}-x)^3+\sigma_{k+1}(x-x_k)^3}{6h_k}+\alpha_k(x-x_k)+\beta_k(x_{k+1}-x).
$$

$S_k(x_k)=y_k\Rightarrow\beta_k=\dfrac{y_k}{h_k}-\dfrac{\sigma_kh_k}{6}$; $S_k(x_{k+1})=y_{k+1}\Rightarrow\alpha_k=\dfrac{y_{k+1}}{h_k}-\dfrac{\sigma_{k+1}h_k}{6}$. Đặt $s_k=\dfrac{y_{k+1}-y_k}{h_k}$:

$$
S_k'(x)=\frac{-\sigma_k(x_{k+1}-x)^2+\sigma_{k+1}(x-x_k)^2}{2h_k}+s_k-\frac{(\sigma_{k+1}-\sigma_k)h_k}{6},
$$

$$
S_k'(x_{k+1})=s_k+\frac{h_k}{6}\sigma_k+\frac{h_k}{3}\sigma_{k+1},\qquad S_{k+1}'(x_{k+1})=s_{k+1}-\frac{h_{k+1}}{3}\sigma_{k+1}-\frac{h_{k+1}}{6}\sigma_{k+2}.
$$

Trơn cấp 1 tại $x_{k+1}$ cho $n-1$ phương trình ($k=0..n-2$):

$$
\boxed{\frac{h_k}{6}\sigma_k+\frac{h_k+h_{k+1}}{3}\sigma_{k+1}+\frac{h_{k+1}}{6}\sigma_{k+2}=s_{k+1}-s_k}
$$

cộng 2 điều kiện biên: $S''(x_0)=A\Rightarrow\sigma_0=A$; $S'(x_0)=A\Rightarrow\frac{h_0}{3}\sigma_0+\frac{h_0}{6}\sigma_1=s_0-A$; $S''(x_n)=B\Rightarrow\sigma_n=B$; $S'(x_n)=B\Rightarrow\frac{h_{n-1}}{6}\sigma_{n-1}+\frac{h_{n-1}}{3}\sigma_n=B-s_{n-1}$. Hệ ba đường chéo, chéo trội. Khai triển được dạng chính tắc $S_k=a_kx^3+b_kx^2+c_kx+d_k$:

$$
a_k=\frac{\sigma_{k+1}-\sigma_k}{6h_k},\ b_k=\frac{\sigma_kx_{k+1}-\sigma_{k+1}x_k}{2h_k},\ c_k=\frac{-\sigma_kx_{k+1}^2+\sigma_{k+1}x_k^2}{2h_k}+s_k-\frac{(\sigma_{k+1}-\sigma_k)h_k}{6},
$$

$$
d_k=\frac{\sigma_kx_{k+1}^3-\sigma_{k+1}x_k^3}{6h_k}+\frac{y_kx_{k+1}-y_{k+1}x_k}{h_k}+\frac{(\sigma_{k+1}x_k-\sigma_kx_{k+1})h_k}{6}.
$$

**Spline cấp 4.** Đặt $m_k=S'(x_k)$, $\sigma_k=S''(x_k)$, $M_k=S'''(x_k)$ ($S\in C^3$ nên các giá trị này chung cho hai mảnh kề). $S_k'''$ bậc nhất: $S_k'''(x)=M_k+\frac{M_{k+1}-M_k}{h_k}u$, $u=x-x_k$. Tích phân ba lần với giá trị ban đầu tại $x_k$ (khai triển Taylor):

$$
S_k(x)=y_k+m_ku+\frac{\sigma_k}{2}u^2+\frac{M_k}{6}u^3+\frac{M_{k+1}-M_k}{24h_k}u^4,\qquad u=x-x_k.
$$

Liên tục của $S,S',S''$ tại $x_{k+1}$ ($S'''$ liên tục sẵn), $k=0..n-1$:

$$
\boxed{\begin{aligned}
&y_k+m_kh_k+\frac{\sigma_k}{2}h_k^2+\frac{3M_k+M_{k+1}}{24}h_k^3=y_{k+1},\\
&m_k+\sigma_kh_k+\frac{2M_k+M_{k+1}}{6}h_k^2=m_{k+1},\\
&\sigma_k+\frac{M_k+M_{k+1}}{2}h_k=\sigma_{k+1}.
\end{aligned}}
$$

$3n$ phương trình, $3(n+1)$ ẩn $(m_k,\sigma_k,M_k)$ $\Rightarrow$ cần 3 điều kiện biên (vd $S'(x_0),S''(x_0),S'(x_n)$). Dạng chính tắc: khai triển $u=x-x_k$ bằng Horner nhân.

### b) Thuật toán spline cấp $p\le4$

**Thuật toán: Spline cấp 1**

- **Input:** vector $x$, $y$.
- **Output:** $S_k(x)=a_kx+b_k$, $k=0..n-1$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.
- **Bước 1:** **Hệ số:** Lặp $k=0,\dots,n-1$:<br>&emsp;&emsp; tính $h_k:=x_{k+1}-x_k$;<br>&emsp;&emsp; tính $a_k:=\dfrac{y_{k+1}-y_k}{h_k}$, $b_k:=\dfrac{y_kx_{k+1}-y_{k+1}x_k}{h_k}$.<br> Dừng thuật toán, trả về các $S_k$.

**Thuật toán: Spline cấp 2**

- **Input:** vector $x$, $y$; một điều kiện biên $S'(x_0)=A$ hoặc $S'(x_n)=B$.
- **Output:** $S_k(x)=a_kx^2+b_kx+c_k$, $k=0..n-1$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Nếu số điều kiện biên khác $1$ hoặc có điều kiện không đặt tại $x_0$, $x_n$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Bước lưới:** Lặp $k=0,\dots,n-1$: tính $h_k:=x_{k+1}-x_k$ và $\gamma_k:=\dfrac{2(y_{k+1}-y_k)}{h_k}$.
- **Bước 2:** **Đạo hàm tại mốc $m_k=S'(x_k)$:** Nếu cho $S'(x_0)=A$ thì:<br>&emsp;&emsp; đặt $m_0:=A$;<br>&emsp;&emsp; lặp $k=0,\dots,n-1$: tính $m_{k+1}:=\gamma_k-m_k$.<br> Nếu cho $S'(x_n)=B$ thì:<br>&emsp;&emsp; đặt $m_n:=B$;<br>&emsp;&emsp; lặp $k=n-1,\dots,0$: tính $m_k:=\gamma_k-m_{k+1}$.
- **Bước 3:** **Hệ số:** Lặp $k=0,\dots,n-1$: tính <br>$\displaystyle a_k:=\frac{m_{k+1}-m_k}{2h_k},\ \ b_k:=\frac{m_kx_{k+1}-m_{k+1}x_k}{h_k},\ \ c_k:=\frac{-m_kx_{k+1}^2+m_{k+1}x_k^2}{2h_k}+y_k+\frac{m_kh_k}{2}.$<br> Dừng thuật toán, trả về các $S_k$.

**Thuật toán: Spline cấp 3**

- **Input:** vector $x$, $y$; hai điều kiện biên dạng $S'(\xi)=v$ hoặc $S''(\xi)=v$, $\xi\in\{x_0,x_n\}$.
- **Output:** $S_k(x)=a_kx^3+b_kx^2+c_kx+d_k$, $k=0..n-1$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Nếu số điều kiện biên khác $2$ hoặc có điều kiện không đặt tại $x_0$, $x_n$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Bước lưới:** Lặp $k=0,\dots,n-1$: tính $h_k:=x_{k+1}-x_k$ và $s_k:=\dfrac{y_{k+1}-y_k}{h_k}$.
- **Bước 2:** **Lập hệ:** Lập hệ $n+1$ phương trình ẩn $\sigma_0,\dots,\sigma_n$:<br>&emsp;&emsp; $n-1$ phương trình trơn (khung, câu a);<br>&emsp;&emsp; 2 phương trình biên (câu a).
- **Bước 3:** **Truy đuổi:** Nếu mỗi đầu có một điều kiện thì hệ có dạng ba đường chéo $\ell_i\sigma_{i-1}+d_i\sigma_i+u_i\sigma_{i+1}=r_i$, giải bằng truy đuổi:
  - **3.1:** Đặt $P_0:=-u_0/d_0$, $Q_0:=r_0/d_0$.<br> Lặp $i=1,\dots,n$:<br>&emsp;&emsp; tính $\mu:=d_i+\ell_iP_{i-1}$; nếu $\mu=0$ thì báo hệ suy biến, dừng thuật toán;<br>&emsp;&emsp; tính $P_i:=-u_i/\mu$, $Q_i:=(r_i-\ell_iQ_{i-1})/\mu$.
  - **3.2:** Đặt $\sigma_n:=Q_n$.<br> Lặp $i=n-1,\dots,0$: tính $\sigma_i:=P_i\sigma_{i+1}+Q_i$.<br> Sang bước 5.
- **Bước 4:** **Khử Gauss:** Nếu hai điều kiện cùng một đầu thì giải hệ bằng khử Gauss chọn trụ; nếu trụ bằng $0$ thì báo “điều kiện biên không xác định duy nhất spline”, dừng thuật toán.
- **Bước 5:** **Hệ số:** Lặp $k=0,\dots,n-1$: tính $a_k,b_k,c_k,d_k$ theo câu a.<br> Dừng thuật toán, trả về các $S_k$.

**Thuật toán: Spline cấp 4**

- **Input:** vector $x$, $y$; ba điều kiện biên $S^{(r)}(\xi)=v$, $r\in\{1,2,3\}$, $\xi\in\{x_0,x_n\}$.
- **Output:** hệ số của $S_k(x)$ (bậc 4, từ bậc cao xuống), $k=0..n-1$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Sắp các mốc tăng theo $x$.<br> Nếu hai mốc trùng nhau thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số mốc})-1$.<br> Nếu $n<1$ thì báo lỗi (cần ít nhất 2 mốc), dừng thuật toán.<br> Nếu số điều kiện biên khác $3$ hoặc có điều kiện không đặt tại $x_0$, $x_n$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Bước lưới:** Lặp $k=0,\dots,n-1$: tính $h_k:=x_{k+1}-x_k$.
- **Bước 2:** **Lập hệ:** Lập hệ $3(n+1)$ phương trình ẩn $m_k,\sigma_k,M_k$ ($k=0..n$):<br>&emsp;&emsp; $3n$ phương trình liên tục (khung, câu a);<br>&emsp;&emsp; 3 phương trình biên: $S'(\xi)=v\Rightarrow m=v$, $S''(\xi)=v\Rightarrow\sigma=v$, $S'''(\xi)=v\Rightarrow M=v$ tại mốc $\xi$.
- **Bước 3:** **Giải hệ:** Giải hệ bằng khử Gauss chọn trụ.<br> Nếu trụ bằng $0$ thì báo “điều kiện biên không xác định duy nhất spline”, dừng thuật toán.
- **Bước 4:** **Hệ số:** Lặp $k=0,\dots,n-1$:
  - **4.1:** Đặt $e:=\Big(\dfrac{M_{k+1}-M_k}{24h_k},\ \dfrac{M_k}{6},\ \dfrac{\sigma_k}{2},\ m_k,\ y_k\Big)$ — hệ số của $S_k$ theo $u=x-x_k$.
  - **4.2:** Đặt $S_k:=(e_4)$.<br> Lặp $j=3,\dots,0$: nhân $S_k$ với $(x-x_k)$ theo thuật toán Câu 5a rồi cộng $e_j$ vào hệ số tự do.
- **Bước 5:** **Kết thúc:** Dừng thuật toán, trả về các $S_k$.

## Câu 21. Spline cho bảng dữ liệu

**Xử lý dữ liệu.** Bảng đề cho $x$ **không tăng dần** (cặp $(1.0472;-0.866)$ đứng sau $(1.5708;0)$), sắp lại theo $x$; $h_k=x_{k+1}-x_k$, $s_k=\frac{y_{k+1}-y_k}{h_k}$:

| $i$ | $0$ | $1$ | $2$ | $3$ | $4$ |
|---:|---:|---:|---:|---:|---:|
| $x_i$ | $0$ | $0.5236$ | $1.0472$ | $1.5708$ | $3.1416$ |
| $y_i$ | $1$ | $0.866$ | $-0.866$ | $0$ | $-1$ |

| $k$ | $[x_k;x_{k+1}]$ | $h_k$ | $s_k=\frac{y_{k+1}-y_k}{h_k}$ |
|---:|---:|---:|---:|
| $0$ | $[0;\ 0.5236]$ | $0.5236$ | $-0.255921$ |
| $1$ | $[0.5236;\ 1.0472]$ | $0.5236$ | $-3.307869$ |
| $2$ | $[1.0472;\ 1.5708]$ | $0.5236$ | $1.653934$ |
| $3$ | $[1.5708;\ 3.1416]$ | $1.5708$ | $-0.636618$ |

### a) Spline cấp 2 với $S'(0)=0$

**Phương pháp** (spline cấp 2, Câu 20b). Trên $[x_k;x_{k+1}]$, $S_k$ bậc 2 qua $(x_k,y_k)$, $(x_{k+1},y_{k+1})$ và $S'$ liên tục nên $m_k+m_{k+1}=\gamma_k$, $m_k=S'(x_k)$; điều kiện biên cho $m$ đầu tiên: $m_0=S'(0)=0$, $m_{k+1}=\gamma_k-m_k$, $\gamma_k=\dfrac{2(y_{k+1}-y_k)}{h_k}$;

$$
a_k=\frac{m_{k+1}-m_k}{2h_k},\qquad b_k=\frac{m_kx_{k+1}-m_{k+1}x_k}{h_k},\qquad c_k=\frac{m_{k+1}x_k^2-m_kx_{k+1}^2}{2h_k}+y_k+\frac{m_kh_k}{2}.
$$

| $k$ | $\gamma_k=\frac{2(y_{k+1}-y_k)}{h_k}$ | $m_{k+1}=\gamma_k-m_k$ |
|---:|---:|---:|
| $0$ | $-0.511841$ | $-0.511841$ |
| $1$ | $-6.615737$ | $-6.103896$ |
| $2$ | $3.307869$ | $9.411765$ |
| $3$ | $-1.273237$ | $-10.685001$ |

**Hệ số** $S_k(x)=a_kx^2+b_kx+c_k$:

| $k$ | $[x_k;x_{k+1}]$ | $a_k$ | $b_k$ | $c_k$ |
|---:|---:|---:|---:|---:|
| $0$ | $[0;\ 0.5236]$ | $-0.488771$ | $0$ | $1$ |
| $1$ | $[0.5236;\ 1.0472]$ | $-5.340007$ | $5.080214$ | $-0.33$ |
| $2$ | $[1.0472;\ 1.5708]$ | $14.81633$ | $-37.135218$ | $21.774$ |
| $3$ | $[1.5708;\ 3.1416]$ | $-6.396984$ | $29.508531$ | $-30.568$ |

> **Kết luận.**
>
> $$
> \begin{aligned}
> S_{0}(x) &= -0.488771x^{2} + 1,\quad x\in[0;\ 0.5236] \\
> S_{1}(x) &= -5.340007x^{2} + 5.080214x - 0.33,\quad x\in[0.5236;\ 1.0472] \\
> S_{2}(x) &= 14.81633x^{2} - 37.135218x + 21.774,\quad x\in[1.0472;\ 1.5708] \\
> S_{3}(x) &= -6.396984x^{2} + 29.508531x - 30.568,\quad x\in[1.5708;\ 3.1416]
> \end{aligned}
> $$

### b) Spline cấp 3 với $S''(0)=-1$, $S''(3.1416)=1$

**Đề.** Đề ghi “$S''(0)=-1,\ S''(0)=1$” (lặp mốc 0); hiểu là $S''(0)=-1$, $S''(3.1416)=1$.

**Phương pháp** (spline cấp 3, Câu 20a). Ẩn $\sigma_k=S''(x_k)$; trơn cấp 1 tại các mốc trong (phương trình khung, Câu 20a) và 2 điều kiện biên cho hệ ba đường chéo, giải bằng truy đuổi; có $\sigma_k$ thì tính hệ số chính tắc của từng $S_k$.

**Lập hệ** theo $\sigma_k=S''(x_k)$: $\ell_i\sigma_{i-1}+d_i\sigma_i+u_i\sigma_{i+1}=r_i$, $i=0,\dots,4$:

- hàng $i=1,2,3$ (trơn tại $x_i$): $\ell_i=\dfrac{h_{i-1}}{6}$, $d_i=\dfrac{h_{i-1}+h_i}{3}$, $u_i=\dfrac{h_i}{6}$, $r_i=s_i-s_{i-1}$;
- hàng biên: $\sigma_0=-1$ ($d_0=1$, $u_0=0$, $r_0=-1$); $\sigma_4=1$ ($\ell_4=0$, $d_4=1$, $r_4=1$).

**Giải hệ bằng truy đuổi:**

$$
\begin{gathered}
P_0=-\frac{u_0}{d_0},\quad Q_0=\frac{r_0}{d_0};\qquad P_i=\frac{-u_i}{d_i+\ell_iP_{i-1}},\quad Q_i=\frac{r_i-\ell_iQ_{i-1}}{d_i+\ell_iP_{i-1}}\ \ (i=1,\dots,4);\\
\sigma_4=Q_4,\qquad \sigma_i=P_i\sigma_{i+1}+Q_i\ \ (i=3,\dots,0).
\end{gathered}
$$

| $i$ | $\ell_i$ | $d_i$ | $u_i$ | $r_i$ | $P_i$ | $Q_i$ | $\sigma_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ | $-1$ | $\boxed{-1}$ |
| $1$ | $0.087267$ | $0.349067$ | $0.087267$ | $-3.051948$ | $-0.25$ | $-8.493167$ | $\boxed{-13.252275}$ |
| $2$ | $0.087267$ | $0.349067$ | $0.087267$ | $4.961803$ | $-0.266667$ | $17.426962$ | $\boxed{19.036434}$ |
| $3$ | $0.087267$ | $0.698133$ | $0.2618$ | $-2.290553$ | $-0.387931$ | $-5.64759$ | $\boxed{-6.035521}$ |
| $4$ | $0$ | $1$ | $0$ | $1$ | $0$ | $1$ | $\boxed{1}$ |

**Hệ số chính tắc** $S_k(x)=a_kx^3+b_kx^2+c_kx+d_k$ trên $[x_k;x_{k+1}]$:

$$
\begin{gathered}
a_k=\frac{\sigma_{k+1}-\sigma_k}{6h_k},\qquad b_k=\frac{\sigma_kx_{k+1}-\sigma_{k+1}x_k}{2h_k},\qquad c_k=\frac{\sigma_{k+1}x_k^2-\sigma_kx_{k+1}^2}{2h_k}+s_k-\frac{(\sigma_{k+1}-\sigma_k)h_k}{6},\\
d_k=\frac{\sigma_kx_{k+1}^3-\sigma_{k+1}x_k^3}{6h_k}+\frac{y_kx_{k+1}-y_{k+1}x_k}{h_k}+\frac{(\sigma_{k+1}x_k-\sigma_kx_{k+1})h_k}{6}.
\end{gathered}
$$

| $k$ | $[x_k;x_{k+1}]$ | $a_k$ | $b_k$ | $c_k$ | $d_k$ |
|---:|---:|---:|---:|---:|---:|
| $0$ | $[0;\ 0.5236]$ | $-3.900011$ | $-0.5$ | $1.075095$ | $1$ |
| $1$ | $[0.5236;\ 1.0472]$ | $10.277791$ | $-22.770492$ | $12.735924$ | $-1.035203$ |
| $2$ | $[1.0472;\ 1.5708]$ | $-7.980633$ | $34.590173$ | $-47.332164$ | $19.932564$ |
| $3$ | $[1.5708;\ 3.1416]$ | $0.74649$ | $-6.535521$ | $17.268077$ | $-13.892122$ |

> **Kết luận.**
>
> $$
> \begin{aligned}
> S_{0}(x) &= -3.900011x^{3} - 0.5x^{2} + 1.075095x + 1,\quad x\in[0;\ 0.5236] \\
> S_{1}(x) &= 10.277791x^{3} - 22.770492x^{2} + 12.735924x - 1.035203,\quad x\in[0.5236;\ 1.0472] \\
> S_{2}(x) &= -7.980633x^{3} + 34.590173x^{2} - 47.332164x + 19.932564,\quad x\in[1.0472;\ 1.5708] \\
> S_{3}(x) &= 0.74649x^{3} - 6.535521x^{2} + 17.268077x - 13.892122,\quad x\in[1.5708;\ 3.1416]
> \end{aligned}
> $$

### c) Spline cấp 3 với $S'(0)=S'(3.1416)=0$

**Lập hệ:** hàng $i=1,2,3$ giữ nguyên ($\ell_i$, $d_i$, $u_i$, $r_i$ ở câu b); hàng biên đổi theo $S'$:

- $S'(0)=0$: $\dfrac{h_0}{3}\sigma_0+\dfrac{h_0}{6}\sigma_1=s_0-0$ ($d_0=\frac{h_0}{3}$, $u_0=\frac{h_0}{6}$, $r_0=s_0$);
- $S'(3.1416)=0$: $\dfrac{h_3}{6}\sigma_3+\dfrac{h_3}{3}\sigma_4=0-s_3$ ($\ell_4=\frac{h_3}{6}$, $d_4=\frac{h_3}{3}$, $r_4=-s_3$).

Truy đuổi và hệ số chính tắc theo công thức ở câu b:

| $i$ | $\ell_i$ | $d_i$ | $u_i$ | $r_i$ | $P_i$ | $Q_i$ | $\sigma_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0$ | $0$ | $0.174533$ | $0.087267$ | $-0.255921$ | $-0.5$ | $-1.466313$ | $\boxed{6.170296}$ |
| $1$ | $0.087267$ | $0.349067$ | $0.087267$ | $-3.051948$ | $-0.285714$ | $-9.573244$ | $\boxed{-15.273219}$ |
| $2$ | $0.087267$ | $0.349067$ | $0.087267$ | $4.961803$ | $-0.269231$ | $17.885319$ | $\boxed{19.949913}$ |
| $3$ | $0.087267$ | $0.698133$ | $0.2618$ | $-2.290553$ | $-0.38806$ | $-5.708754$ | $\boxed{-7.668492}$ |
| $4$ | $0.2618$ | $0.5236$ | $0$ | $0.636618$ | $0$ | $5.050094$ | $\boxed{5.050094}$ |

| $k$ | $[x_k;x_{k+1}]$ | $a_k$ | $b_k$ | $c_k$ | $d_k$ |
|---:|---:|---:|---:|---:|---:|
| $0$ | $[0;\ 0.5236]$ | $-6.825667$ | $3.085148$ | $0$ | $1$ |
| $1$ | $[0.5236;\ 1.0472]$ | $11.211845$ | $-25.248175$ | $14.835328$ | $-1.589259$ |
| $2$ | $[1.0472;\ 1.5708]$ | $-8.791191$ | $37.593361$ | $-50.972328$ | $21.382$ |
| $3$ | $[1.5708;\ 3.1416]$ | $1.349481$ | $-10.193539$ | $24.091334$ | $-17.921333$ |

> **Kết luận.**
>
> $$
> \begin{aligned}
> S_{0}(x) &= -6.825667x^{3} + 3.085148x^{2} + 1,\quad x\in[0;\ 0.5236] \\
> S_{1}(x) &= 11.211845x^{3} - 25.248175x^{2} + 14.835328x - 1.589259,\quad x\in[0.5236;\ 1.0472] \\
> S_{2}(x) &= -8.791191x^{3} + 37.593361x^{2} - 50.972328x + 21.382,\quad x\in[1.0472;\ 1.5708] \\
> S_{3}(x) &= 1.349481x^{3} - 10.193539x^{2} + 24.091334x - 17.921333,\quad x\in[1.5708;\ 3.1416]
> \end{aligned}
> $$

## Câu 22. Thuật toán phương pháp bình phương tối thiểu

### a) Hàm thực nghiệm với tập cơ sở $\{\varphi_j\}_{j=1}^m$ và sai số trung bình phương

**Thuật toán: Bình phương tối thiểu tuyến tính theo tham số**

- **Input:** vector $x$, $y$; cơ sở $\varphi_1,\dots,\varphi_m$.
- **Output:** vector hệ số $a=(a_1,\dots,a_m)$ của $g=\sum_ja_j\varphi_j$; sai số trung bình phương $\sigma$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Loại các điểm làm $\varphi_j(x_i)$ không xác định.<br> Đặt $n:=(\text{số điểm còn lại})$, đánh số lại $i=1,\dots,n$.<br> Nếu $n<m$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Ma trận cơ sở:** Khởi tạo ma trận $\Phi$ cỡ $n\times m$.<br> Lặp lồng $i=1,\dots,n$; $j=1,\dots,m$: tính $\Phi_{ij}:=\varphi_j(x_i)$.
- **Bước 2:** **Hệ chuẩn:** Khởi tạo ma trận $M$ cỡ $m\times m$ và vector $d$ có $m$ phần tử.<br> Lặp lồng $j=1,\dots,m$; $k=1,\dots,m$: tính $M_{jk}:=\sum_{i=1}^n\Phi_{ij}\Phi_{ik}$.<br> Lặp $j=1,\dots,m$: tính $d_j:=\sum_{i=1}^n\Phi_{ij}y_i$.
- **Bước 3:** **Giải hệ:** Giải hệ chuẩn $Ma=d$ bằng phân tích Cholesky $M=LL^{T}$ ($M$ đối xứng, xác định dương; $L$ tam giác dưới): giải $Lu=d$ (thế xuôi) rồi $L^{T}a=u$ (thế ngược).<br> Nếu không phân tích được ($M$ không xác định dương) thì báo “các hàm cơ sở phụ thuộc tuyến tính trên dữ liệu”, dừng thuật toán.
- **Bước 4:** **Sai số:** Tính $\sigma:=\sqrt{\frac1n\sum_{i=1}^n\big(\sum_ja_j\Phi_{ij}-y_i\big)^2}$.<br> Dừng thuật toán, trả về $a$ và $\sigma$.

### b) Dạng $y=a\,e^{b_1\varphi_1(x)+b_2\varphi_2(x)}$ và $y=a\,x^b$

**Thuật toán: Dạng mũ $y=a\,e^{b_1\varphi_1(x)+b_2\varphi_2(x)}$**

- **Input:** vector $x$, $y$; cơ sở $\varphi_1,\varphi_2$ (không phải hàm hằng).
- **Output:** $a$, $b_1$, $b_2$, lượng tịnh tiến $S_y$ và sai số trung bình phương $\sigma$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Loại các điểm làm $\varphi_1(x_i)$, $\varphi_2(x_i)$ không xác định.<br> Đặt $n:=(\text{số điểm còn lại})$, đánh số lại $i=1,\dots,n$.<br> Đặt $s:=1$ nếu số điểm $y_i>0$ không ít hơn số điểm $y_i<0$, ngược lại $s:=-1$ ($s$ là dấu của $a$).<br> Đặt $q:=(\text{số điểm có }s\,y_i\le0)$, $S_y:=0$.<br> Nếu $0<q\le0.1\,n$ thì loại $q$ điểm đó, đặt lại $n:=n-q$, đánh số lại $i=1,\dots,n$.<br> Nếu $q>0.1\,n$ thì đặt $S_y:=s\,\big(\lfloor\max_{s\,y_i\le0}|y_i|\rfloor+1\big)$ (mọi $s(y_i+S_y)>0$).<br> Nếu $n<3$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Đổi biến:** Lặp $i=1,\dots,n$: tính $z_i:=\ln\big(s(y_i+S_y)\big)$.
- **Bước 2:** **Bình phương tối thiểu:** Tìm $(c_0,c_1,c_2)$ theo câu a với dữ liệu $(x_i,z_i)$ và cơ sở $(1,\varphi_1,\varphi_2)$.
- **Bước 3:** **Trả biến, sai số:** Đặt $a:=s\,e^{c_0}$, $b_1:=c_1$, $b_2:=c_2$.<br> Tính $\sigma:=\sqrt{\frac1n\sum_i\big(a\,e^{b_1\varphi_1(x_i)+b_2\varphi_2(x_i)}-S_y-y_i\big)^2}$.<br> Dừng thuật toán, trả về $a$, $b_1$, $b_2$, $S_y$, $\sigma$.

**Thuật toán: Dạng luỹ thừa $y=a\,x^b$**

- **Input:** vector $x$, $y$.
- **Output:** $a$, $b$, lượng tịnh tiến $S_x$, $S_y$ và sai số trung bình phương $\sigma$.
- **Bước 0:** **Xử lý dữ liệu:** Nếu $x$, $y$ khác số phần tử thì báo lỗi, dừng thuật toán.<br> Đặt $n:=(\text{số điểm})$.<br> Đặt $q_x:=(\text{số điểm có }x_i\le0)$, $S_x:=0$.<br> Nếu $0<q_x\le0.1\,n$ thì loại $q_x$ điểm đó, đặt lại $n:=n-q_x$, đánh số lại $i=1,\dots,n$.<br> Nếu $q_x>0.1\,n$ thì đặt $S_x:=\lfloor|\min x|\rfloor+1$.<br> Đặt $s:=1$ nếu số điểm $y_i>0$ không ít hơn số điểm $y_i<0$, ngược lại $s:=-1$.<br> Đặt $q:=(\text{số điểm có }s\,y_i\le0)$, $S_y:=0$.<br> Nếu $0<q\le0.1\,n$ thì loại $q$ điểm đó, đặt lại $n:=n-q$, đánh số lại $i=1,\dots,n$.<br> Nếu $q>0.1\,n$ thì đặt $S_y:=s\,\big(\lfloor\max_{s\,y_i\le0}|y_i|\rfloor+1\big)$.<br> Nếu $n<2$ thì báo lỗi, dừng thuật toán.
- **Bước 1:** **Đổi biến:** Lặp $i=1,\dots,n$: tính $X_i:=\ln(x_i+S_x)$ và $z_i:=\ln\big(s(y_i+S_y)\big)$.
- **Bước 2:** **Bình phương tối thiểu:** Tìm $(c_0,c_1)$ theo câu a với dữ liệu $(X_i,z_i)$ và cơ sở $(1,X)$.
- **Bước 3:** **Trả biến, sai số:** Đặt $a:=s\,e^{c_0}$, $b:=c_1$.<br> Tính $\sigma:=\sqrt{\frac1n\sum_i\big(a(x_i+S_x)^b-S_y-y_i\big)^2}$.<br> Dừng thuật toán, trả về $a$, $b$, $S_x$, $S_y$, $\sigma$.

## Câu 23. Hàm thực nghiệm từ file dữ liệu

**Dữ liệu.** `data Câu 23.xlsx` có 4 bộ dữ liệu đặt cạnh nhau (“Câu a” … “Câu d”), mỗi bộ 60 cặp $(x_i,y_i)$; bộ c có mốc $x=2.63$ lặp lại với hai giá trị $y$ — giữ cả hai.

### a) $y=ax+\dfrac bx$

**Phương pháp.** Hàm cần tìm tuyến tính theo các tham số $a$, $b$ với hệ hàm cơ sở $\varphi_{1}(x)=x$, $\varphi_{2}(x)=\frac{1}{x}$:

$$
y=a\varphi_{1}(x)+b\varphi_{2}(x).
$$

Đặt hàm tổng bình phương sai lệch:

$$
S(a,b)=\sum_{i=1}^{n}\Big(ax_i+\frac{b}{x_i}-y_i\Big)^2\to\min.
$$

Từ điều kiện cực trị $\dfrac{\partial S}{\partial a}=0$, $\dfrac{\partial S}{\partial b}=0$, ta thu được hệ phương trình $(\Phi^T\Phi)\theta=\Phi^Ty$:

$$
\begin{bmatrix}\sum x_i^{2}&n\\n&\sum\frac{1}{x_i^{2}}\end{bmatrix}\begin{bmatrix}a\\b\end{bmatrix}=\begin{bmatrix}\sum x_iy_i\\\sum\frac{y_i}{x_i}\end{bmatrix}
$$

(lưu ý $\varphi_{1}(x_i)\varphi_{2}(x_i)=x_i\cdot\frac{1}{x_i}=1$).

**Tính toán.** Trên $n=60$ mốc ta có các tính toán:

$$
\begin{aligned}
\sum x_i^{2}&=414.464009, & \sum\frac{1}{x_i^{2}}&=15.291533, & \sum x_iy_i&=648.166038,\\
\sum\frac{y_i}{x_i}&=73.982568.
\end{aligned}
$$

Thay vào hệ phương trình chuẩn:

$$
\begin{bmatrix}414.464009&60\\60&15.291533\end{bmatrix}\begin{bmatrix}a\\b\end{bmatrix}=\begin{bmatrix}648.166038\\73.982568\end{bmatrix}.
$$

Giải hệ phương trình trên ta được:

$$
a=1.998874,\qquad b=-3.004924.
$$

Vậy hàm thực nghiệm cần tìm là:

$$
y=g(x)=1.998874x-\frac{3.004924}{x}.
$$

Sai số trung bình phương của hàm thực nghiệm:

$$
\sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(y_i-g(x_i)\big)^2}=0.0029.
$$

### b) $y=ax^2+b\cos x+c$

**Phương pháp.** Hàm cần tìm tuyến tính theo các tham số $a$, $b$, $c$ với hệ hàm cơ sở $\varphi_{1}(x)=x^{2}$, $\varphi_{2}(x)=\cos x$, $\varphi_{3}(x)=1$:

$$
y=a\varphi_{1}(x)+b\varphi_{2}(x)+c\varphi_{3}(x).
$$

Đặt hàm tổng bình phương sai lệch:

$$
S(a,b,c)=\sum_{i=1}^{n}\Big(ax_i^{2}+b\cos x_i+c-y_i\Big)^2\to\min.
$$

Từ điều kiện cực trị $\dfrac{\partial S}{\partial a}=0$, $\dfrac{\partial S}{\partial b}=0$, $\dfrac{\partial S}{\partial c}=0$, ta thu được hệ phương trình $(\Phi^T\Phi)\theta=\Phi^Ty$:

$$
\begin{bmatrix}\sum x_i^{4}&\sum x_i^{2}\cos x_i&\sum x_i^{2}\\\sum x_i^{2}\cos x_i&\sum \cos^2x_i&\sum \cos x_i\\\sum x_i^{2}&\sum \cos x_i&n\end{bmatrix}\begin{bmatrix}a\\b\\c\end{bmatrix}=\begin{bmatrix}\sum x_i^{2}y_i\\\sum y_i\cos x_i\\\sum y_i\end{bmatrix}
$$

**Tính toán.** Trên $n=60$ mốc ta có các tính toán:

$$
\begin{aligned}
\sum x_i^{4}&=4667.836041, & \sum x_i^{2}\cos x_i&=-338.04016, & \sum x_i^{2}&=448.53068,\\
\sum \cos^2x_i&=30.404524, & \sum \cos x_i&=-32.718948, & \sum x_i^{2}y_i&=10800.473623,\\
\sum y_i\cos x_i&=-800.163714, & \sum y_i&=1055.5006.
\end{aligned}
$$

Thay vào hệ phương trình chuẩn:

$$
\begin{bmatrix}4667.836041&-338.04016&448.53068\\-338.04016&30.404524&-32.718948\\448.53068&-32.718948&60\end{bmatrix}\begin{bmatrix}a\\b\\c\end{bmatrix}=\begin{bmatrix}10800.473623\\-800.163714\\1055.5006\end{bmatrix}.
$$

Giải hệ phương trình trên ta được:

$$
a=2.000101,\qquad b=-2.999001,\qquad c=1.004497.
$$

Vậy hàm thực nghiệm cần tìm là:

$$
y=g(x)=2.000101x^{2}-2.999001\,\cos x+1.004497.
$$

Sai số trung bình phương của hàm thực nghiệm:

$$
\sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(y_i-g(x_i)\big)^2}=0.002976.
$$

### c) $y=a\,e^{bx+cx^2}$

**Phương pháp.** Mọi $y_i>0$ nên $a>0$, lấy logarit tự nhiên hai vế:

$$
\begin{aligned}
y&=a\,e^{bx+cx^{2}}\\
\iff \ln y&=\ln a+\ln\Big(e^{bx+cx^{2}}\Big)\\
\iff \ln y&=\ln a+bx+cx^{2}.
\end{aligned}
$$

Đặt $Y=\ln y$, $A=\ln a$ ($\Longrightarrow a=e^A$) và hệ hàm cơ sở $\varphi_{0}(x)=1$, $\varphi_{1}(x)=x$, $\varphi_{2}(x)=x^{2}$. Ta đưa được về dạng tuyến tính theo các tham số $(A,b,c)$:

$$
Y=A\varphi_{0}(x)+b\varphi_{1}(x)+c\varphi_{2}(x).
$$

Đặt hàm tổng bình phương sai lệch:

$$
S(A,b,c)=\sum_{i=1}^{n}\Big(A+bx_i+cx_i^{2}-Y_i\Big)^2\to\min.
$$

Từ điều kiện cực trị $\dfrac{\partial S}{\partial A}=0$, $\dfrac{\partial S}{\partial b}=0$, $\dfrac{\partial S}{\partial c}=0$, ta thu được hệ phương trình $(\Phi^T\Phi)\theta=\Phi^TY$:

$$
\begin{bmatrix}n&\sum x_i&\sum x_i^{2}\\\sum x_i&\sum x_i^{2}&\sum x_i^{3}\\\sum x_i^{2}&\sum x_i^{3}&\sum x_i^{4}\end{bmatrix}\begin{bmatrix}A\\b\\c\end{bmatrix}=\begin{bmatrix}\sum Y_i\\\sum x_iY_i\\\sum x_i^{2}Y_i\end{bmatrix}
$$

**Tính toán.** Trên $n=60$ mốc ta có các tính toán:

$$
\begin{aligned}
\sum x_i&=147.209, & \sum x_i^{2}&=407.283913, & \sum x_i^{3}&=1231.34149,\\
\sum x_i^{4}&=3968.412286, & \sum Y_i&=-182.496393, & \sum x_iY_i&=-567.617587,\\
\sum x_i^{2}Y_i&=-1811.272985.
\end{aligned}
$$

Thay vào hệ phương trình chuẩn:

$$
\begin{bmatrix}60&147.209&407.283913\\147.209&407.283913&1231.34149\\407.283913&1231.34149&3968.412286\end{bmatrix}\begin{bmatrix}A\\b\\c\end{bmatrix}=\begin{bmatrix}-182.496393\\-567.617587\\-1811.272985\end{bmatrix}.
$$

Giải hệ phương trình trên ta được:

$$
A=8.146737\ \Longrightarrow\ a=e^A=3452.095718,\qquad b=-6.953435,\qquad c=0.865017.
$$

Vậy hàm thực nghiệm cần tìm là:

$$
y=g(x)=3452.095718\,e^{-6.953435x+0.865017x^{2}}.
$$

Sai số trung bình phương của hàm thực nghiệm (tính trên $y_i$ ban đầu):

$$
\sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(y_i-g(x_i)\big)^2}=1.117049.
$$

$\sigma$ lớn vì $22$ điểm có $|y|<0.01$ ($x\ge2.688$): ở đó sai lệch nhỏ của $y$ làm $\ln|y|$ lệch nhiều và chi phối hệ chuẩn.

### d) $y=a\,x^b$

**Phương pháp.** Mọi $x_i>0$. Mọi $y_i<0$ nên $a<0$, ta nhân hai vế với $-1$ rồi lấy logarit:

$$
\begin{aligned}
y&=a\,x^{b}\\
\iff -y&=(-a)\,x^{b}\\
\iff \ln(-y)&=\ln(-a)+\ln\big(x^{b}\big)\\
\iff \ln(-y)&=\ln(-a)+b\ln x.
\end{aligned}
$$

Đặt $Y=\ln(-y)$, $A=\ln(-a)$ ($\Longrightarrow a=-e^A$) và hệ hàm cơ sở $\varphi_{0}(x)=1$, $\varphi_{1}(x)=\ln x$. Ta đưa được về dạng tuyến tính theo các tham số $(A,b)$:

$$
Y=A\varphi_{0}(x)+b\varphi_{1}(x).
$$

Đặt hàm tổng bình phương sai lệch:

$$
S(A,b)=\sum_{i=1}^{n}\Big(A+b\ln x_i-Y_i\Big)^2\to\min.
$$

Từ điều kiện cực trị $\dfrac{\partial S}{\partial A}=0$, $\dfrac{\partial S}{\partial b}=0$, ta thu được hệ phương trình $(\Phi^T\Phi)\theta=\Phi^TY$:

$$
\begin{bmatrix}n&\sum \ln x_i\\\sum \ln x_i&\sum (\ln x_i)^2\end{bmatrix}\begin{bmatrix}A\\b\end{bmatrix}=\begin{bmatrix}\sum Y_i\\\sum Y_i\ln x_i\end{bmatrix}
$$

**Tính toán.** Trên $n=60$ mốc ta có các tính toán:

$$
\begin{aligned}
\sum \ln x_i&=51.083722, & \sum (\ln x_i)^2&=52.316043, & \sum Y_i&=93.674093,\\
\sum Y_i\ln x_i&=93.585132.
\end{aligned}
$$

Thay vào hệ phương trình chuẩn:

$$
\begin{bmatrix}60&51.083722\\51.083722&52.316043\end{bmatrix}\begin{bmatrix}A\\b\end{bmatrix}=\begin{bmatrix}93.674093\\93.585132\end{bmatrix}.
$$

Giải hệ phương trình trên ta được:

$$
A=0.226629\ \Longrightarrow\ a=-e^A=-1.254364,\qquad b=1.567551.
$$

Vậy hàm thực nghiệm cần tìm là:

$$
y=g(x)=-1.254364\,x^{1.567551}.
$$

Sai số trung bình phương của hàm thực nghiệm (tính trên $y_i$ ban đầu):

$$
\sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(y_i-g(x_i)\big)^2}=0.003595.
$$
