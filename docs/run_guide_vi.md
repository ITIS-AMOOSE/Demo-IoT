# Hướng dẫn chạy demo từng bước

## Yêu cầu phần mềm

| Phần mềm | Phiên bản | Link tải |
|-----------|----------|----------|
| Python | 3.8+ | https://www.python.org/downloads/ |
| Mosquitto | 2.x | https://mosquitto.org/download/ |
| Node.js | 14+ | https://nodejs.org/ |
| Node-RED | 3.x | `npm install -g node-red` |
| OpenSSL | 3.x | https://slproweb.com/products/Win32OpenSSL.html |
| Wireshark | 4.x | https://www.wireshark.org/download.html |

## Bước 0: Cài đặt

### 0.1 Cài Python dependencies
```bash
cd iot-security-demo
pip install -r requirements.txt
```

### 0.2 Cài Mosquitto (Windows)
1. Tải installer từ https://mosquitto.org/download/
2. Chạy installer, cài vào `C:\Program Files\mosquitto`
3. Thêm `C:\Program Files\mosquitto` vào PATH
4. Kiểm tra: mở CMD gõ `mosquitto -h`

### 0.3 Cài Node-RED
```bash
npm install -g node-red
```

### 0.4 Cài Wireshark
1. Tải từ https://www.wireshark.org/download.html
2. Cài đặt, chọn cài thêm Npcap khi được hỏi

---

## Pha 1: Không bảo mật

> **Mục tiêu:** Sensor gửi dữ liệu, attacker chèn dữ liệu giả thành công, Wireshark đọc được payload.

### Bước 1.1: Chạy broker mở
Mở **Terminal 1**:
```bash
mosquitto -c configs/mosquitto_open.conf -v
```
Kết quả mong đợi: Mosquitto khởi động, hiển thị `mosquitto version X.X.X running`.

### Bước 1.2: Chạy sensor
Mở **Terminal 2**:
```bash
python sensor.py
```
Kết quả: Mỗi 2 giây in ra dữ liệu JSON đã gửi.

### Bước 1.3: Chạy subscriber (tùy chọn)
Mở **Terminal 3**:
```bash
python subscriber_test.py
```
Kết quả: Hiển thị dữ liệu nhận từ sensor.

### Bước 1.4: Chạy Node-RED dashboard
Mở **Terminal 4**:
```bash
node-red
```
- Mở http://localhost:1880
- Import flow từ `node_red/flow-export.json` (xem `node_red/README.md`)
- Xem dashboard tại http://localhost:1880/ui

### Bước 1.5: Chạy attacker
Mở **Terminal 5**:
```bash
python attacker.py
```
Kết quả: Dashboard hiển thị dữ liệu bất thường (nhiệt độ 80-120°C) từ `attacker-fake`.

### Bước 1.6: Quan sát Wireshark
1. Mở Wireshark → chọn giao diện **Loopback** (hoặc **Adapter for loopback traffic capture**)
2. Filter: `tcp.port == 1883`
3. Tìm gói MQTT PUBLISH → xem payload JSON rõ ràng

📸 **Chụp ảnh:** Dashboard bình thường, dashboard bị tấn công, Wireshark thấy payload.

**Dừng tất cả bằng Ctrl+C.**

---

## Pha 2: Bảo mật cơ bản (Auth + ACL)

> **Mục tiêu:** Chỉ user hợp lệ mới kết nối và publish/subscribe được.

### Bước 2.1: Tạo file password
```bash
mosquitto_passwd -c configs/passwords.txt sensor
```
Nhập password: `sensor123` (gõ 2 lần)

```bash
mosquitto_passwd configs/passwords.txt dashboard
```
Nhập password: `dashboard123` (gõ 2 lần)

### Bước 2.2: Chạy broker auth
Mở **Terminal 1**:
```bash
mosquitto -c configs/mosquitto_auth.conf -v
```

### Bước 2.3: Chạy secure sensor
Mở **Terminal 2**:
```bash
python secure_sensor.py --mode auth
```
Kết quả: Kết nối thành công, publish dữ liệu bình thường.

### Bước 2.4: Chạy subscriber
Mở **Terminal 3**:
```bash
python subscriber_test.py --mode auth
```

### Bước 2.5: Chạy secure attacker
Mở **Terminal 4**:
```bash
python secure_attacker.py --mode auth
```
Kết quả: **Kết nối bị từ chối!** Log hiển thị lỗi xác thực.

📸 **Chụp ảnh:** Log sensor thành công, log attacker bị từ chối.

**Dừng tất cả bằng Ctrl+C.**

---

## Pha 3: Bảo mật nâng cao (TLS)

> **Mục tiêu:** Dữ liệu được mã hóa, Wireshark không đọc được nội dung.

### Bước 3.1: Tạo chứng chỉ TLS
```bash
cd certs
generate_certs.bat
cd ..
```
(Linux/macOS: `chmod +x certs/generate_certs.sh && cd certs && ./generate_certs.sh && cd ..`)

### Bước 3.2: Tạo file password (nếu chưa có)
Giống Bước 2.1.

### Bước 3.3: Chạy broker TLS
Mở **Terminal 1**:
```bash
mosquitto -c configs/mosquitto_tls.conf -v
```

### Bước 3.4: Chạy secure sensor (TLS)
Mở **Terminal 2**:
```bash
python secure_sensor.py --mode tls
```
Kết quả: Kết nối TLS thành công, publish mã hóa.

### Bước 3.5: Chạy subscriber (TLS)
Mở **Terminal 3**:
```bash
python subscriber_test.py --mode tls
```

### Bước 3.6: Chạy attacker (TLS)
Mở **Terminal 4**:
```bash
python secure_attacker.py --mode tls
```
Kết quả: **Tấn công thất bại!** Sai credentials qua TLS.

### Bước 3.7: Quan sát Wireshark
1. Mở Wireshark → chọn **Loopback**
2. Filter: `tcp.port == 8883`
3. Quan sát: payload **KHÔNG còn đọc được** dạng JSON, chỉ thấy dữ liệu mã hóa TLS

📸 **Chụp ảnh:** Log sensor TLS, Wireshark chỉ thấy dữ liệu mã hóa.

---

## Kiểm tra kết quả

| Kiểm tra | Pha 1 | Pha 2 | Pha 3 |
|----------|-------|-------|-------|
| Sensor gửi dữ liệu? | ✅ | ✅ | ✅ |
| Subscriber nhận dữ liệu? | ✅ | ✅ | ✅ |
| Attacker gửi được? | ✅ (nguy hiểm!) | ❌ Bị chặn | ❌ Bị chặn |
| Wireshark đọc payload? | ✅ Đọc rõ | ✅ Đọc rõ | ❌ Mã hóa |
| Dashboard hoạt động? | ✅ | ✅ | ✅ |
