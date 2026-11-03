# LỜI GIẢI ĐỀ GIỮA KỲ MI3042 — 20251GKtest1

Ta có bảng dữ liệu gồm $N=104$ mốc cách đều $x_i=1+0.115\,i$ ($i=\overline{0,103}$, $x_i\in[1;\,12.845]$, bước lưới $h=0.115$) và các giá trị cho trước $\bar x=4.15$, $\bar y=-1.43$.

> *▹ Gợi ý ghi: file có dòng 107, 108 thiếu $x$ hoặc $y$ (đã bỏ, không cần ghi); không chép bảng số liệu.*

**a.** Do $102$ mốc mang dấu âm ($y_i<0\Longrightarrow a<0$), ta nhân hai vế với $-1$ rồi lấy logarit:

$$
\begin{aligned}
y&=a\,e^{bx+\frac{c}{x}}\\
\iff -y&=(-a)\,e^{bx+\frac{c}{x}}\\
\iff \ln(-y)&=\ln(-a)+\ln\Big(e^{bx+\frac{c}{x}}\Big)\\
\iff \ln(-y)&=\ln(-a)+bx+\frac{c}{x}.
\end{aligned}
$$

Đặt $Y=\ln(-y)$, $A=\ln(-a)$ ($\Longrightarrow a=-e^A$) và hệ hàm cơ sở $\varphi_{0}(x)=1$, $\varphi_{1}(x)=x$, $\varphi_{2}(x)=\frac{1}{x}$. Ta đưa được về dạng tuyến tính theo các tham số $(A,b,c)$:

$$
Y=A\varphi_{0}(x)+b\varphi_{1}(x)+c\varphi_{2}(x).
$$

Đặt hàm tổng bình phương sai lệch:

$$
S(A,b,c)=\sum_{i=1}^{n}\Big(A+bx_i+\frac{c}{x_i}-Y_i\Big)^2\to\min.
$$

Từ điều kiện cực trị $\dfrac{\partial S}{\partial A}=0$, $\dfrac{\partial S}{\partial b}=0$, $\dfrac{\partial S}{\partial c}=0$, ta thu được hệ phương trình $(\Phi^T\Phi)\theta=\Phi^TY$:

$$
\begin{bmatrix}n&\sum x_i&\sum\frac{1}{x_i}\\\sum x_i&\sum x_i^{2}&n\\\sum\frac{1}{x_i}&n&\sum\frac{1}{x_i^{2}}\end{bmatrix}\begin{bmatrix}A\\b\\c\end{bmatrix}=\begin{bmatrix}\sum Y_i\\\sum x_iY_i\\\sum\frac{Y_i}{x_i}\end{bmatrix}
$$

(lưu ý $\varphi_{1}(x_i)\varphi_{2}(x_i)=x_i\cdot\frac{1}{x_i}=1$).
Trong $104$ mốc dữ liệu có $2$ mốc cuối dương $y_{102}=0.0169$, $y_{103}=0.0091$ nên không lấy logarit, loại bỏ.
Trên $n=102$ mốc ta có các tính toán:

$$
\begin{aligned}
\sum x_i&=694.365, & \sum\frac{1}{x_i}&=22.591638, & \sum x_i^{2}&=5896.316975,\\
\sum\frac{1}{x_i^{2}}&=8.52859, & \sum Y_i&=-103.195072, & \sum x_iY_i&=-1107.65705,\\
\sum\frac{Y_i}{x_i}&=-3.786516.
\end{aligned}
$$

> *▹ Gợi ý ghi: ghi đủ các tổng (đều dùng trong hệ chuẩn), không lập bảng từng điểm.*

Thay vào hệ phương trình chuẩn:

$$
\begin{bmatrix}102&694.365&22.591638\\694.365&5896.316975&102\\22.591638&102&8.52859\end{bmatrix}\begin{bmatrix}A\\b\\c\end{bmatrix}=\begin{bmatrix}-103.195072\\-1107.65705\\-3.786516\end{bmatrix}.
$$

Giải hệ phương trình trên ta được:

$$
A=0.868465\ \Longrightarrow\ a=-e^A=-2.383249,\qquad b=-0.30595,\qquad c=0.914613.
$$

Vậy hàm thực nghiệm cần tìm là:

$$
y=g(x)=-2.383249\,e^{-0.30595x+\frac{0.914613}{x}}.
$$

Sai số trung bình phương của hàm thực nghiệm:

$$
\sigma=\sqrt{\frac1n\sum_{i=1}^{n}\big(y_i-g(x_i)\big)^2}=0.111911.
$$

**b.**

**Thuật toán: Lặp giải $f(x)=\bar y$ trên lưới mốc cách đều**

- **Input:** mốc cách đều $x_i$, $y_i$ ($i=0,\dots,n$), bước $h$; $\bar y$; số mốc nội suy $m$; sai số $\varepsilon$; số lần lặp tối đa $N$.
- **Output:** các nghiệm gần đúng $\bar x$ của $f(x)=\bar y$.
- **B1:** **Tìm khoảng cách ly:** lặp $i=0,\dots,n-1$:<br>&emsp;&emsp; nếu $y_i=\bar y$ thì $x_i$ là nghiệm;<br>&emsp;&emsp; nếu $(y_i-\bar y)(y_{i+1}-\bar y)<0$ thì $(x_i,x_{i+1})$ là khoảng cách ly.
- **B2:** **Lặp trên từng khoảng** $(x_k,x_{k+1})$:
  - **a)** **Chọn hướng, mốc gốc:** nếu $k+m-1\le n$ thì Newton tiến, $s:=k$, mốc $x_k,\dots,x_{k+m-1}$; ngược lại Newton lùi, $s:=k+1$, mốc $x_{k+2-m},\dots,x_{k+1}$.
  - **b)** **Sai phân:** lập bảng sai phân của $m$ mốc; $d_j:=\Delta^jy_k$ (tiến) hoặc $d_j:=\nabla^jy_{k+1}$ (lùi), $j=0,\dots,m-1$.
  - **c)** **Hàm lặp:** với $t=\frac{x-x_s}{h}$, $\varphi(t):=\dfrac{\bar y-d_0}{d_1}-\sum_{j=2}^{m-1}\dfrac{d_j}{j!\,d_1}\,t(t\mp1)\cdots\big(t\mp(j-1)\big)$ (dấu $-$ khi tiến, $+$ khi lùi).
  - **d)** **Lặp:** $t_0:=\dfrac{\bar y-d_0}{d_1}$, $t_{l+1}:=\varphi(t_l)$ đến khi $h\,|t_{l+1}-t_l|<\varepsilon$; quá $N$ lần thì báo “không hội tụ”.
  - **e)** **Nghiệm:** nếu $t^*\in[0;1]$ (tiến) hoặc $t^*\in[-1;0]$ (lùi) thì $\bar x:=x_s+t^*h$; ngược lại bỏ khoảng này.
- **B3:** **Trả về** các nghiệm.

> *▹ Gợi ý ghi: đề yêu cầu viết thuật toán: ghi đủ B1–B3.*

Từ dữ liệu đã cho là mốc cách đều tăng dần, với $\bar y=-1.43$, phương trình $f(x)=-1.43$ có duy nhất $1$ khoảng cách ly nghiệm là $[x_{13},x_{14}]=[2.495;\,2.61]$ (vì $y_{13}=-1.5127<-1.43<y_{14}=-1.3977$). Áp dụng thuật toán với $m=3$ mốc, $\varepsilon=10^{-6}$ (Dữ liệu có nhiễu ($|\Delta^5y_{13}|=0.7185>\Delta y_{13}=0.115$), lặp với 6 mốc hội tụ rất chậm ($|\varphi'|\approx0.86$) nên dùng $m=3$.):
Newton tiến với $3$ mốc $x_{13},\dots,x_{15}$, $t=\dfrac{x-2.495}{0.115}$; $y_{13}=-1.5127$, $\Delta y_{13}=0.1150$, $\Delta^{2}y_{13}=-0.0987$:

$$
\varphi(t) = 0.71913 + 0.42913t(t-1)
$$

$$
\begin{gathered}
t_{0}=0.71913,\ t_{1}=0.632454,\ t_{2}=0.619377,\ \dots,\ t_{6}=0.617803,\\
\Longrightarrow\ t^*=t_{6}\in[0;1],\quad \bar x=x_{13}+t^*h=2.495+0.617803\cdot0.115=2.566047.
\end{gathered}
$$

> *▹ Gợi ý ghi: dãy lặp chỉ cần ghi $t_0,t_1,t_2,\dots,t$ cuối.*

Kết quả như sau:

| $\text{Nghiệm}$ | $\text{Khoảng cách ly}$ | $\text{Mốc sử dụng}$ | $\text{Phương pháp áp dụng}$ | $\text{Kết quả }x^*$ |
|:---:|:---:|:---:|:---:|:---:|
| $x^*$ | $[2.495;\ 2.61]$ | $[2.495;\ 2.725]$ | $\text{Newton tiến (từ }x_{13}=2.495)$ | $2.566047$ |

**c.** Mốc gần $\bar x=4.15$ nhất là $x_{27}=4.105$ (với bước $h=0.115$). Chọn tâm $x_0=4.105$ và trích xuất $7$ mốc đối xứng ứng với chỉ số gốc $i\in\{24,\dots,30\}$ (đánh số lại $-3..3$):

| $i$ | $-3$ | $-2$ | $-1$ | $0$ | $1$ | $2$ | $3$ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $\text{chỉ số gốc}$ | $24$ | $25$ | $26$ | $27$ | $28$ | $29$ | $30$ |
| $x_i$ | $3.76$ | $3.875$ | $3.99$ | $4.105$ | $4.22$ | $4.335$ | $4.45$ |
| $y_i$ | $-0.9384$ | $-0.8979$ | $-0.811$ | $-0.8056$ | $-0.7548$ | $-0.7416$ | $-0.7049$ |

Bảng sai phân trung tâm:

| $i$ | $x_i$ | $y_i$ | $\Delta y_i$ | $\Delta^{2}y_i$ | $\Delta^{3}y_i$ | $\Delta^{4}y_i$ | $\Delta^{5}y_i$ | $\Delta^{6}y_i$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $-3$ | $3.76$ | $-0.9384$ | $0.0405$ | $0.0464$ | $-0.1279$ | $0.2548$ | $\boxed{-0.4647}$ | $\boxed{0.8187}$ |
| $-2$ | $3.875$ | $-0.8979$ | $0.0869$ | $-0.0815$ | $\boxed{0.1269}$ | $\boxed{-0.2099}$ | $\boxed{0.3540}$ | |
| $-1$ | $3.99$ | $-0.8110$ | $\boxed{0.0054}$ | $\boxed{0.0454}$ | $\boxed{-0.0830}$ | $0.1441$ | | |
| $0$ | $4.105$ | $\boxed{-0.8056}$ | $\boxed{0.0508}$ | $-0.0376$ | $0.0611$ | | | |
| $1$ | $4.22$ | $-0.7548$ | $0.0132$ | $0.0235$ | | | | |
| $2$ | $4.335$ | $-0.7416$ | $0.0367$ | | | | | |
| $3$ | $4.45$ | $-0.7049$ | | | | | | |

> *▹ Gợi ý ghi: ghi đủ bảng, khoanh các ô dùng trong công thức.*

Đặt biến chuẩn hoá $t=\dfrac{x-4.105}{0.115}$. Công thức nội suy Stirling bậc $6$ có dạng:

$$
\begin{aligned}
P_{6}(t) &= y_{0} +\dfrac{\Delta y_{-1} + \Delta y_{0}}{2}t +\dfrac{\Delta^{2}y_{-1}}{2!}t^2 +\dfrac{\Delta^{3}y_{-2} + \Delta^{3}y_{-1}}{2\cdot3!}t(t^2-1) +\dfrac{\Delta^{4}y_{-2}}{4!}t^2(t^2-1) +\cdots \\
 &= -0.8056 +\dfrac{0.0054+0.0508}{2}t +\dfrac{0.0454}{2!}t^2 \\
&\quad +\dfrac{0.1269-0.0830}{2\cdot3!}t(t^2-1) +\dfrac{-0.2099}{4!}t^2(t^2-1) +\cdots \\
 &= -0.8056 +0.0281t +0.0227t^2 +0.003658t(t^2-1) -0.008746t^2(t^2-1) +\cdots
\end{aligned}
$$

Vector hệ số theo thứ tự các cơ sở là

$$
c = \bigl(-0.8056;\ 0.0281;\ 0.0227;\ 0.003658;\ -0.008746;\ -0.000461;\ 0.001137\bigr)
$$

Khai triển các tích cơ sở theo luỹ thừa của $t$ ta có bảng nhân:

| | $t^{6}$ | $t^{5}$ | $t^{4}$ | $t^{3}$ | $t^{2}$ | $t$ | $1$ |
|:---|---:|---:|---:|---:|---:|---:|---:|
| $1$ | $0$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ |
| $t$ | $0$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ |
| $t^2$ | $0$ | $0$ | $0$ | $0$ | $1$ | $0$ | $0$ |
| $t(t^2-1)$ | $0$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ |
| $t^2(t^2-1)$ | $0$ | $0$ | $1$ | $0$ | $-1$ | $0$ | $0$ |
| $t(t^2-1)(t^2-4)$ | $0$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ |
| $t^2(t^2-1)(t^2-4)$ | $1$ | $0$ | $-5$ | $0$ | $4$ | $0$ | $0$ |

> *▹ Gợi ý ghi: các ô $0$ phía trên có thể để trống.*

Nhân từng hàng của bảng nhân với hệ số $c_k$ tương ứng rồi cộng theo cột, ta được dạng chính tắc:

$$
P_{6}(t) = 0.001137t^{6} - 0.000461t^{5} - 0.014431t^{4} + 0.005965t^{3} + 0.035994t^{2} + 0.022597t - 0.8056
$$

Tại $\bar x=4.15$, ta có $\bar t=\dfrac{4.15-4.105}{0.115}=\dfrac{9}{23}\approx0.391304$. Tính $P_6(\bar t)$ và $P_6'(\bar t)$ bằng sơ đồ Horner chia lặp:

$$
f(4.15)\approx P_6(\bar t)=-0.791228,\qquad \frac{dP_6}{dt}\bigg|_{t=\bar t}=0.050056.
$$

Đạo hàm theo biến gốc $x$:

$$
f'(4.15)\approx\frac{1}{h}\,\frac{dP_6}{dt}\bigg|_{t=\bar t}=\frac{0.050056}{0.115}=0.435267.
$$
