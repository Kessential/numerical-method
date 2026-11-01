# Phương pháp số MI3042 — quy tắc làm việc

Dự án học môn **Phương pháp số (MI3042)**: viết thuật toán + code Python chạy thuật toán cho từng mục trong đề cương. Trả lời và viết tài liệu bằng **tiếng Việt**, ký hiệu theo slide ($x_i, y_i, h, n, P_n, R_n, w_{n+1}$…).

Đề cương (`slide_example/MI3042_Phương pháp số 26072025.pdf`):
- **Ch.1 Xấp xỉ hàm số:** bài toán nội suy, mốc tối ưu, Horner, Lagrange, Newton (mốc bất kỳ / cách đều), trung tâm (Gauss I-II, Stirling, Bessel), nội suy ngược, spline, bình phương tối thiểu.
- **Ch.2 Đạo hàm & tích phân số:** công thức 2 điểm, 3 điểm, k điểm; trung điểm, hình thang, Simpson, Newton–Cotes.
- **Ch.3 PTVP thường:** Euler hiện/ẩn, hình thang, Runge–Kutta, Adams (Bashforth, Moulton, dự báo–hiệu chỉnh), sai phân (bài toán biên, giá trị riêng).

Slide hiện có: `slide_example/13…19_*.pdf`; slide các chương sau sẽ được thêm vào cùng thư mục.

## 0. Cấu trúc thư mục

```
slide_example/             # slide, đề cương, bài tập, đề thi — CHỈ ĐỌC, không sửa
docs/thuat_toan/<ten>.md   # mỗi thuật toán (nhóm thuật toán) 1 file markdown riêng
docs/loi_giai/             # lời giải LaTeX (xelatex) câu 3-23: mau_loi_giai.tex (văn bản, chỗ <<khoa>>)
                           #   + sinh_loi_giai.py (gọi hàm trong interpolation/ để điền số) -> loi_giai_bai_tap.tex/.pdf
interpolation/             # Ch.1: horner, moc_toi_uu, lagrange, newton, trung_tam,
                           #       noi_suy_nguoc, spline, binh_phuong_toi_thieu
derivative_integral/       # Ch.2: dao_ham_so, trung_diem, hinh_thang, simpson, newton_cotes
ode/                       # Ch.3: euler, runge_kutta, adams, sai_phan
data/                      # dữ liệu mẫu để chạy thử, luôn có cả bộ "bẩn"
```

- Tên `.md` trùng tên `.py`: `docs/thuat_toan/newton.md` ↔ `interpolation/newton.py`.
- Chương mới → thêm thư mục/dòng tương ứng vào bảng trên.
- **Không** làm LaTeX hay lời giải bài tập dạng văn bản (người dùng tự chép vào vở) trừ khi được yêu cầu.
- Lời giải LaTeX đã yêu cầu: quy tắc sửa / build / trình bày ở `docs/loi_giai/CLAUDE.md` (tự nạp khi đọc file trong `docs/loi_giai/`).

## 1. Quy trình cho mỗi chủ đề

1. Đọc slide: `pdftotext -enc UTF-8 -layout "<file>.pdf" -` + mục tương ứng trong đề cương / `BaitapPPS_2026.pdf`.
2. **Kiểm tra lại slide — slide có thể sai.** Tự suy dẫn lại công thức và kiểm bằng số: đa thức bậc ≤ n phải được nội suy chính xác; tích phân/đạo hàm so với nghiệm giải tích; bậc sai số khi giảm h; đối chiếu với numpy. Chỗ sai hoặc khác quy ước ghi trong file `.md`:
   `> Ghi chú: slide <file> tr.<n> ghi ..., đúng là ... vì ...`
3. Viết `docs/thuat_toan/<ten>.md` → cài `<chuong>/<ten>.py` → chạy với dữ liệu trong `data/` (cả bộ sạch và bộ bẩn) → đối chiếu với numpy.

## 2. Viết thuật toán (file `.md`)

Mẫu chuẩn: `docs/thuat_toan/horner.md`, `docs/thuat_toan/moc_toi_uu.md`.

- **Khung:** `# <Tên nhóm>` → `## <số>. <Tên thuật toán>` → **Input** (kiểu, miền giá trị, ε, N) → **Output** (kèm tính chất, ví dụ thứ tự sắp xếp) → **Bước 0 — Xử lý dữ liệu** → **Bước 1, 2, …** với bước con **2.1, 2.2** → dừng / trả về. Thuật toán lặp luôn có bước **"Không hội tụ"** khi hết N lần lặp.
- **Ngắn gọn, đủ, logic:** mỗi bước 1–2 dòng, có tên ngắn ("Khởi tạo", "Chuẩn hoá", "Xuống thang"…); gán bằng `:=`; chỉ dùng biến đã định nghĩa ở bước trước; rẽ nhánh ghi rõ `TH1/TH2`; vòng lặp ghi rõ chỉ số chạy và điều kiện dừng; công thức dài đặt trong `$$…$$`.
- Dùng lại thuật toán khác bằng tham chiếu (`mục 2, horner.md`), không chép lại.
- Tiêu đề file chỉ ghi **tên thuật toán** (không ghi số câu / tuần bài tập). **Không** viết phần "xây dựng / suy dẫn công thức" — chỉ viết thuật toán.
- Thuật toán có nhiều biến thể (vd Horner chia / Horner nhân): viết từng biến thể thành một mục, kèm bảng **"Chọn biến thể theo mục đích"** (mục đích → biến thể → chi phí). Code cho người dùng chọn mục đích rồi tự dùng biến thể rẻ nhất, gộp các mục dùng chung một phép tính.
- **Bước 0 — Xử lý dữ liệu là bắt buộc** (dữ liệu đề cho không sạch). Chọn các mục phù hợp với thuật toán:
  - Chuẩn hoá: dấu trừ Unicode `−` `–` (copy từ PDF) → `-`; dấu phẩy thập phân → dấu chấm; bỏ khoảng trắng / ký tự lạ; ô rỗng, ô chữ → loại.
  - Loại NaN, ±∞; báo số dòng bị loại và lý do.
  - Mốc trùng: cùng y → giữ 1; khác y chênh $\le10^{-3}\max(1,\max|y|)$ → lấy trung bình; chênh lớn hơn → hỏi giữ giá trị đầu / sau / trung bình / dừng (Enter hoặc file trả lời = giữ đầu), báo số dòng và lựa chọn. Bình phương tối thiểu giữ mọi điểm.
  - Sắp tăng theo x; kiểm tra các mốc phân biệt.
  - Kiểm tra cách đều: $|x_{i+1}-x_i-h|\le\delta h$ → chọn công thức mốc cách đều hay mốc bất kỳ.
  - Điều kiện riêng của phương pháp: đủ số mốc; n chẵn (Simpson); $\bar y\in[\min y,\max y]$ và khoảng đơn điệu (nội suy ngược); $\bar x$ ngoài $[x_0,x_n]$ → cảnh báo ngoại suy; ma trận suy biến (BPTT); $h>0$; tham số nguyên dương…
  - Không thoả → dừng, thông báo lỗi rõ ràng.

## 3. Trình bày phần tính toán — in sẵn trong output của code

Người dùng chép output vào vở, nên **output của script phải là lời giải hoàn chỉnh**, theo thứ tự:

```
XU LY DU LIEU   -> CHI IN KHI DU LIEU BAN / LOI: du lieu goc, cai gi bi loai/gop/sua va vi sao, du lieu sach
CONG THUC       -> chi cong thuc chung chua gan voi bang nao (bo khoi nay khi moi cong thuc da ghi tren bang)
TINH TOAN       -> cac buoc/bang/lan lap (thay so); cong thuc ghi ngay tren bang dung no
KET QUA         -> ket qua cuoi (+ danh gia sai so neu co cong thuc sai so)
KIEM TRA        -> tu kiem tra (P(x_i) vs y_i, phan du, so voi numpy...)
```

- Dữ liệu sạch → **không in** khối XU LY DU LIEU. Không có khối "PHUONG PHAP".
- Tiêu đề mỗi trường hợp (vd `n = 9 moc toi uu tren [-1, 1]`) in 1 dòng, **không** kẻ thanh ngang `=====` trên/dưới.
- Kết quả là đa thức hoặc nhiều giá trị → in **dạng vector** `[v0, v1, ...]`, hàm trả về `numpy` array.
- **Quy ước đa thức:** $P_n(x)=a_nx^n+\dots+a_1x+a_0$ — **chỉ số = số mũ** ($a_i$ là hệ số của $x^i$). Vector hệ số nhập và in **từ bậc cao xuống thấp** $(a_n,\dots,a_0)$, vd $3x^3-2x-1$ → `3 0 -2 -1`. Trong code, đảo vector thành `A[i] = a_i` để viết công thức đúng chỉ số như file `.md`.

- **Bố cục theo lời giải PDF** (`docs/loi_giai/loi_giai_bai_tap.pdf`):
  - Công thức (công thức lặp của bảng) ghi ngay trên bảng dùng nó.
  - Ô (tỷ) sai phân được chọn in trong `[ ]`.
  - Bảng tích khoanh ma trận A (cột `|`); hệ số in `C = (tên từng thành phần) = (số)`, đa thức in `P_n = C.A = [...]`.
  - Trích xuất mốc: bảng quá trình rồi bảng ngang các mốc đã đánh số lại (`i`, `x_i`, `y_i`).
  - Không in bảng đổi biến $t\to x$ (vẫn in $P(x)$ ở KET QUA).
- **Lặp:** in lần lặp **1, 2, áp chót và cuối**, giữa in `...`; tổng số lần ≤ 4 thì in hết.
- **Bảng** (Horner, sai phân, tỷ sai phân, RK, spline, mốc…): **in toàn bộ**, không cắt.
- Trong chat chỉ tóm tắt kết quả + lệnh chạy; không tính tay số liệu.

## 4. Code Python

Mẫu chuẩn: `interpolation/horner.py`, `interpolation/moc_toi_uu.py`. Phong cách tham khảo: repo `D:\Project\numerical-analysis` (`interpolation/lagrange.py`, `matrix/gauss/gauss_seidel.py`).

- **Mỗi file `.py` độc lập** (copy sang máy thi là chạy, chỉ cần numpy; không import chéo giữa các file). Cấu trúc:
  1. docstring đầu file: tên thuật toán, input, cách chạy, file `.md` tương ứng;
  2. `# ===== CAC HAM CONG CU =====`: đọc số / làm sạch dữ liệu, in bảng, in đa thức;
  3. `# ===== THUAT TOAN =====`: hàm tổng quát, comment `# Buoc 2.1 — ...` khớp từng bước trong `.md`;
  4. `# ===== CHUONG TRINH CHINH =====`: `main()` + `if __name__ == "__main__":`.
- Hàm thuật toán là bản **tổng quát** (không gắn số liệu của một câu); tham số `verbose=True` để in quá trình; trả về kết quả (tuple/dict) để kiểm tra.
- **Nhập liệu:** đọc file (csv/txt; xlsx qua pandas nếu có) từ đối số dòng lệnh, nếu không có thì `input()` với giá trị mặc định ghi dạng `(VD [...])` (Enter hoặc EOF → dùng VD). Menu nhiều lựa chọn in mỗi lựa chọn 1 dòng (chỉ khi nhập từ bàn phím). Dấu phân tách là khoảng trắng hoặc `;`; dấu `,` giữa hai chữ số hiểu là dấu thập phân. Bọc `try/except` khi mở file, file rỗng, sai kích thước, sai kiểu.
- **In:** chữ **không dấu** (tránh lỗi mã hoá console), theo khối ở mục 3. Số tính ra in qua `fmt`: tối đa 6 chữ số thập phân, bỏ số 0 thừa, $|v|<10^{-4}$ in dạng e (`9.14e-04`), $|v|<10^{-12}$ in thành 0 (riêng đánh giá sai số dùng `fmt(E, nho=0)` để không mất số rất nhỏ). Số liệu đề cho giữ nguyên (`.10g`); sai phân của số liệu cách đều giữ đúng số chữ số thập phân của dữ liệu (`0.0008739`).
- **Đọc file bảng** (6 script đọc bảng): tự nhận `.csv` / `.xlsx` / `.txt` dạng bảng; in khối `DOC FILE` (cột x, y, dòng, ô bị bỏ) để xác nhận; $\bar x$, $\bar y$ có trong file làm giá trị mặc định (Enter = đồng ý); nhiều sheet có số liệu → menu chọn sheet; số dòng báo lỗi là số dòng gốc trong file; file chỉ có y → hỏi cách sinh x (cách đều, Chebyshev giảm dần theo công thức cos, hoặc tăng dần).
- **BPTT:** giải hệ chuẩn $Ma=d$ bằng Cholesky; hiệu chỉnh Gauss–Newton ẩn, chỉ chạy khi có cờ `--gn`. Đầu `main()` gọi `sys.stdout.reconfigure(errors="backslashreplace")` để in dữ liệu gốc có ký tự lạ không bị crash. Công thức có luỹ thừa / giai thừa lớn tính qua `log`/`math.lgamma` để không tràn số; kiểm tra trên lưới thì nhân dần từng thừa số, không tạo mảng 2 chiều lớn.
- Chọn lần lặp cần in khi biết trước tổng số N: `k <= 2 or k >= N - 1`; khi chưa biết N (lặp tới hội tụ): lưu 2 lần đầu + `deque(maxlen=2)` cho 2 lần cuối rồi in sau vòng lặp.
- Chạy: `python interpolation/<ten>.py [data/<file>]`.

## 5. Kiểm tra trước khi báo xong

- Chạy script với ca của đề bài + ít nhất 1 bộ dữ liệu bẩn trong `data/`.
- Đối chiếu kết quả với numpy (vd `np.polyval`, `np.polyder`, `np.polyfit`, `np.trapezoid`) hoặc nghiệm giải tích.
- Báo cho người dùng các chỗ slide sai/khác quy ước đã phát hiện.
