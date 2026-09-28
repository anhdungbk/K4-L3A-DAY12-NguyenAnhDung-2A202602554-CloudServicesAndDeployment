# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Mỗi câu bên dưới đã được trả lời bằng ghi chú quan sát từ lúc làm bài.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: ..........................  Mã học viên: ..........................

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Khi deploy lên Render, nếu quên khai báo `AGENT_API_KEY` thì Settings sẽ báo lỗi ngay lúc app khởi động và deployment fail thay vì mở một API public với khóa `changeme`. Với khóa mặc định, người khác có thể đoán được khóa đó rồi gọi `/ask`, còn tôi chỉ phát hiện sau khi service đã chạy và có thể đã bị dùng sai.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Khi chạy test CP3 tôi nhận được log: `{"event":"ask_completed","level":"info","timestamp":"2026-09-28T08:34:21.299549+00:00","user_id":"sv-test","tokens_in":3,"tokens_out":37,"cost_usd":2.265e-05}`. Tôi có thể lọc riêng các request của `sv-test` để điều tra, và cộng/truy vấn `cost_usd` hay token theo thời gian để cảnh báo chi phí. Một chuỗi `print` tự do không có trường cố định nên khó lọc và tổng hợp tự động.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | Chưa đo được: Docker daemon trên máy chưa chạy |
| Multi-stage | Chưa đo được: Docker daemon trên máy chưa chạy |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Tôi chưa thể build để ghi số MB thật vì Docker Desktop/daemon không hoạt động trên máy. Về thành phần, image một stage thường giữ lại pip cache, công cụ build và các file trung gian; runtime của tôi chỉ copy dependencies đã cài từ `builder` và mã nguồn `app`, `utils`, nên các phần build đó không đi theo image cuối.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi chỉ sửa `app/main.py`, các layer base image, `COPY requirements.txt` và `RUN pip install` vẫn được cache. Docker chạy lại layer copy source và các layer sau nó. Nếu `COPY . .` đặt trước `pip install`, thay đổi một ký tự trong source làm cache của layer đó mất hiệu lực, nên `pip install` cũng phải chạy lại dù requirements không đổi.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗi trong app có thể cho kẻ tấn công thực thi lệnh trong container. Nếu process chạy root, lệnh đó có quyền root trong container và có thể tận dụng một cấu hình mount sai hoặc lỗ hổng container runtime để tác động tới host. `USER appuser` với UID 10001 làm process ứng dụng không có quyền root ngay từ đầu, nên khi bị chiếm nó chỉ có quyền của user thường và bị giảm khả năng sửa hệ thống hoặc đọc file nhạy cảm.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Có thể gửi 20 request trong khoảng 2 giây: 10 request ở cuối phút, ví dụ 10:00:59, sau đó thêm 10 request ngay đầu phút kế tiếp, 10:01:01. Bộ đếm reset tại giây 00 nên mỗi nhóm vẫn dưới 10/phút, trong khi sliding window 60 giây thấy đủ 20 request và chặn từ request thứ 11.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn tốc độ gọi trong 60 giây, còn cost guard giới hạn tổng tiền của một user theo tháng. Một request có prompt/response rất dài có thể vẫn dưới 10 request/phút nên rate limit cho qua, nhưng nếu chi phí làm vượt ngân sách tháng thì cost guard chặn. Ngược lại, nhiều request rất rẻ gửi dồn trong vài giây có thể ngân sách vẫn còn nhưng rate limit chặn với 429.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu endpoint duy nhất kiểm tra Redis, Redis mất kết nối thì cả ba container đều trả 503. Load balancer đánh dấu từng container không khỏe, ngừng gửi traffic và có thể restart chúng. Sau đó Redis vẫn đang lỗi nên container vừa lên lại tiếp tục fail health check; kết quả là cả cụm bị churn dù process Python vẫn sống. Tách `/health` giúp process vẫn 200, còn `/ready` 503 chỉ ngăn request mới vào instance chưa sẵn sàng.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Với Redis chung, response của request đầu có `history_length` là 0; sau khi lưu user và assistant, request kế tiếp với cùng user thấy 2, kể cả khi được chuyển sang instance khác. Nếu dùng dict Python, mỗi agent có dict riêng: request vào instance chưa từng phục vụ user sẽ lại thấy 0, còn instance đã phục vụ user thì có thể thấy 2 hoặc lớn hơn. Vì vậy history_length sẽ nhảy thất thường theo instance nhận request.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi tôi gặp khi chạy local trước khi deploy là Uvicorn dừng ở startup với `NotImplementedError: TODO (CP4): cài đặt install`, xuất phát từ `lifecycle.install()` trong lifespan. Tôi xác định nguyên nhân qua traceback chỉ đến `app/lifecycle.py`, rồi cài đặt đăng ký SIGTERM/SIGINT và lưu/chuyển tiếp handler cũ. Sau đó Uvicorn khởi động được, và service Render trả 200 cho `/health` và `/ready`.
