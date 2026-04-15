# Kịch bản thuyết trình demo

## Giới thiệu (2 phút)

> "Dự án của nhóm em demo về **Bảo mật dữ liệu trong hệ thống IoT**. Chúng em sẽ minh họa 3 mức độ bảo mật khác nhau và cho thấy tại sao việc bảo mật IoT là rất quan trọng."

> "Kiến trúc demo gồm: một chương trình Python giả lập cảm biến IoT, gửi dữ liệu qua giao thức MQTT tới broker Mosquitto, và hiển thị trên dashboard Node-RED. Ngoài ra có chương trình giả lập attacker để tấn công."

📸 **Slide minh họa:** Sơ đồ kiến trúc (Sensor → Mosquitto → Dashboard, Attacker → Mosquitto)

---

## Pha 1: Không bảo mật (3 phút)

### Lời nói:
> "Đầu tiên, chúng em cho broker chạy ở chế độ mở — bất kỳ ai cũng kết nối được mà không cần xác thực."

### Thao tác:
1. Chạy `mosquitto -c configs/mosquitto_open.conf -v`
2. Chạy `python sensor.py` — chỉ dashboard dữ liệu bình thường
3. Mở Node-RED dashboard — cho xem giao diện
4. Chạy `python attacker.py` — cho xem dữ liệu giả xuất hiện

### Lời nói:
> "Như các bạn thấy, attacker gửi được dữ liệu giả với nhiệt độ 80-120°C vào cùng topic. Dashboard hiển thị dữ liệu sai mà không hề phát hiện."

> "Dùng Wireshark, chúng ta có thể đọc được toàn bộ nội dung JSON truyền qua mạng."

📸 **Chụp ảnh cho báo cáo:**
- Dashboard bình thường (gauge nhiệt độ 24-35°C)
- Dashboard bị tấn công (gauge nhảy lên 80-120°C)
- Wireshark: packet MQTT PUBLISH, thấy rõ payload JSON

---

## Pha 2: Bảo mật cơ bản (3 phút)

### Lời nói:
> "Bây giờ chúng em bật bảo mật cơ bản: yêu cầu username/password và phân quyền topic bằng ACL."

### Thao tác:
1. Dừng broker cũ
2. Chạy `mosquitto -c configs/mosquitto_auth.conf -v`
3. Chạy `python secure_sensor.py --mode auth` — kết nối thành công
4. Chạy `python secure_attacker.py --mode auth` — kết nối thất bại

### Lời nói:
> "Sensor dùng đúng username/password nên kết nối và publish bình thường. Attacker dùng sai credentials nên bị broker từ chối ngay."

> "ACL cũng phân quyền rõ: sensor chỉ được write, dashboard chỉ được read. Kể cả nếu attacker đoán đúng mật khẩu nhưng không có quyền write trên topic, message cũng bị drop."

📸 **Chụp ảnh cho báo cáo:**
- Log secure_sensor kết nối thành công
- Log secure_attacker bị từ chối (mã lỗi 5)
- Log broker hiện attempt bị chặn

---

## Pha 3: Bảo mật nâng cao (3 phút)

### Lời nói:
> "Cuối cùng, chúng em thêm mã hóa TLS. Toàn bộ dữ liệu truyền giữa sensor và broker được mã hóa, tương tự HTTPS."

### Thao tác:
1. Dừng broker cũ
2. Chạy `mosquitto -c configs/mosquitto_tls.conf -v`
3. Chạy `python secure_sensor.py --mode tls` — kết nối TLS thành công
4. Chạy `python secure_attacker.py --mode tls` — thất bại
5. Mở Wireshark filter `tcp.port == 8883` — payload mã hóa

### Lời nói:
> "Ở pha này, kể cả nếu ai đó bắt được gói tin trên mạng, họ cũng không đọc được nội dung vì đã được mã hóa TLS."

> "So sánh Wireshark pha 1 và pha 3: pha 1 thấy rõ JSON, pha 3 chỉ thấy dữ liệu mã hóa."

📸 **Chụp ảnh cho báo cáo:**
- Log sensor TLS thành công
- Wireshark pha 3: dữ liệu mã hóa, không đọc được JSON
- So sánh side-by-side Wireshark pha 1 vs pha 3

---

## Tổng kết (2 phút)

### Lời nói:
> "Tóm lại, chúng em đã demo 3 mức bảo mật:"

> "Pha 1 — không bảo mật: ai cũng gửi được, đọc được. Pha 2 — auth + ACL: chỉ user hợp lệ mới truy cập được. Pha 3 — TLS: dữ liệu mã hóa hoàn toàn."

Hiển thị bảng đánh giá:

| Tiêu chí | Pha 1 | Pha 2 | Pha 3 |
|----------|:-----:|:-----:|:-----:|
| Tính bí mật | ❌ | ❌ | ✅ |
| Tính toàn vẹn | ❌ | ⚠️ | ✅ |
| Xác thực nguồn gửi | ❌ | ✅ | ✅ |
| Chống giả mạo | ❌ | ✅ | ✅ |

> "Trong thực tế, hệ thống IoT cần ít nhất mức bảo mật pha 3 để đảm bảo an toàn. Cảm ơn thầy/cô và các bạn đã lắng nghe."

---

## Ghi chú cho người thuyết trình

- **Thời lượng tổng:** khoảng 13-15 phút
- **Chuẩn bị trước:** chạy thử 1 lần để đảm bảo không lỗi
- **Mẹo:** mở sẵn các terminal, chỉ cần nhấn Enter để chạy
- **Nếu lỗi:** xem `troubleshooting_vi.md`, giải thích lỗi là phần của demo
- **Câu hỏi thường gặp:**
  - "Sao không dùng thiết bị thật?" → Giải thích: sinh viên không có hardware, Python giả lập tương đương
  - "TLS có phải SSL không?" → TLS là phiên bản mới hơn của SSL, nguyên lý tương tự
