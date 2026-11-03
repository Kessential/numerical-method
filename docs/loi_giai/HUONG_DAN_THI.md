# Hướng dẫn thi giữa kỳ (data 20261GKtest1 / 20261GKtest2)

## 1. Chạy

Mở terminal VS Code ở thư mục `numerical-method`, gõ:

```
.venv\Scripts\python.exe docs\loi_giai\sinh_loi_giai.py gk
```

Chương trình hỏi lần lượt, **Enter = dùng giá trị trong `[ ]`**:

| Câu hỏi | Trả lời |
|---|---|
| File dữ liệu đề | `1` nếu làm **Đề 1** (`20261GKtest1.rar`), `2` nếu **Đề 2** (`20261GKtest2.rar`) |
| Mật khẩu file nén | gõ mật khẩu ghi trên đề (sai thì được nhập lại, tối đa 3 lần) |
| — | Đọc khối **DOC FILE**: số mốc, $h$, $\bar x$, $\bar y$, các ô ngoài bảng → đối chiếu với đề |
| Tên file lời giải | Enter |
| Dạng câu a, b, c… | chọn số theo bảng mục 2; hết câu thì **Enter** |
| Định dạng | `3` (Markdown + PDF) |

Kết quả: **`docs/loi_giai/giua_ky_20261GKtest1.pdf`** (hoặc `.md`). Chép vào bài, **bỏ các dòng "▹ Gợi ý ghi"**. Cuối terminal có mục `KET QUA` để đối chiếu nhanh.

## 2. Đề hỏi gì → chọn dạng nào

| Số | Dạng (bảng sổ tay) | Trả lời tiếp |
|---|---|---|
| `1` | Định thức Vandermonde, tính duy nhất nội suy (câu 1) | cách lấy mốc*, … |
| `2` | Đa thức Chebyshev $T_n$: truy hồi, bậc, hệ số đầu (câu 2) | $n$ |
| `3` | $n$ mốc tối ưu trên $[a,b]$ (câu 3) | $n$, $a$, $b$ |
| `4` | Horner: $P(c)$, chia $(x-c)$, đạo hàm cấp $k$ (câu 4) | hệ số $P$ từ bậc cao (vd `3 0 -2 -1`), các $c$, $k$ |
| `5` | Nhân $P(x)(x-c)$ hoặc tích $w(x)=\prod(x-x_k)$ (câu 5) | `1` nhân / `2` tích (+ cách lấy mốc*) |
| `6` | Lagrange, $f(\bar x)$ (câu 6–7) | cách lấy mốc*, $\bar x$, $k$ |
| `7` | Newton tiến / lùi, $f(\bar x)$, đạo hàm (câu 8–11; mốc cách đều → sai phân, không đều → tỷ sai phân, tự chọn) | cách lấy mốc*, $\bar x$, $k$, chiều `t`/`l` |
| `8` | **Stirling** $m$ mốc (câu 13, 16) | $\bar x$: Enter; $m$ (vd `7`, `9`); $k$: `1` |
| `9` | **Bessel** $m$ mốc (câu 14, 17) | $\bar x$: Enter; $m$ (vd `8`); $k$: `1` |
| `10` | Khoảng đơn điệu, khoảng cách ly của $f(x)=\bar y$ (câu 18a, b) | $\bar y$ |
| `11` | Giải $f(x)=\bar y$ bằng **hàm ngược** (câu 18c, 19a) | $\bar y$; $m$ (`6`); ghi thuật toán `c`/`k` |
| `12` | Giải $f(x)=\bar y$ bằng **phương pháp lặp** (câu 18d, 19b) | $\bar y$; $m$ (`4`, lỗi "không hội tụ / ngoài khoảng" thì `3`); $\varepsilon$, $N$: Enter; thuật toán `c`; ghi chú: Enter |
| `13` | **Spline** bậc 1, 2, 3 + điều kiện biên (câu 20–21) | bậc $p$; cách lấy mốc*; điều kiện biên, vd `S''(x0) = 0; S''(xn) = 0`, `S'(x0) = 0` |
| `14` | **Bình phương tối thiểu**, sai số (câu 22–23) | dạng hàm + cơ sở (bảng dưới) |

\* **Cách lấy mốc**: `1` trích $m$ mốc gần $\bar x$ (bảng dài của đề), `2` theo chỉ số gốc (vd `10-17`), `3` cả bảng (bảng nhỏ), `4` nhập tay $x_i$, $y_i$ (đề cho bảng riêng).

Gauss I / Gauss II đã bỏ khỏi menu.

**Bình phương tối thiểu (dạng `14`):**

| Hàm cần tìm | Dạng | Cơ sở |
|---|---|---|
| $y=ae^{bx+\frac cx}$ | `2` | `x; 1/x` |
| $y=ae^{bx^2+\frac cx}$ | `2` | `x^2; 1/x` |
| $y=ae^{bx+cx^2}$ | `2` | `x; x^2` |
| $y=ax+\frac bx$ | `1` | `x; 1/x` |
| $y=ax^2+b\cos x+c$ | `1` | `x^2; cos x; 1` |
| $y=ax+b$ | `1` | `x; 1` |
| $y=ax^b$ | `3` | — |

Đề cho $\bar x$, $\bar y$ khác với file (hoặc file không có) → gõ số đó thay vì Enter.

## 3. Sửa một tham số rồi chạy lại

Mọi câu trả lời được lưu vào `data/giua_ky_20261GKtest1_tra_loi.txt` (mỗi câu hỏi 1 dòng `#` + 1 dòng trả lời). Sửa dòng cần đổi (vd số mốc $m$) rồi chạy:

```
.venv\Scripts\python.exe docs\loi_giai\sinh_loi_giai.py gk data\giua_ky_20261GKtest1_tra_loi.txt
```

## 4. Chạy thử trước (đề 2025)

```
.venv\Scripts\python.exe docs\loi_giai\sinh_loi_giai.py gk data\giua_ky_20251_tra_loi.txt
```

→ `docs/loi_giai/giua_ky_20251.pdf`, khớp đáp án đề 1 năm 2025 (a = `14`, b = `12`, c = `8`).

## 5. Gặp lỗi

- **Sai mật khẩu**: nhập lại; 3 lần sai thì chạy lại lệnh.
- **"can moc cach deu"**: dữ liệu không cách đều → Stirling / Bessel / lặp không dùng được; dùng hàm ngược (`11`), Lagrange (`6`) hoặc Newton (`7`, tự dùng tỷ sai phân).
- **Không thấy $\bar x$ / $\bar y$**: gõ tay giá trị trên đề.
- **Spline bậc 4**: chạy script riêng `.venv\Scripts\python.exe interpolation\spline.py data\de_20261\20261GKtest1.xlsx`.
