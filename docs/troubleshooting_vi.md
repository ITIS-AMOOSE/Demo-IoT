# Xử lý lỗi thường gặp

## 1. Broker chưa chạy

**Triệu chứng:**
```
[SENSOR] Lỗi: Không thể kết nối tới broker tại localhost:1883
```

**Cách xử lý:**
- Kiểm tra Mosquitto đã chạy chưa: mở terminal mới chạy `mosquitto -c configs/mosquitto_open.conf -v`
- Nếu lệnh `mosquitto` không tìm thấy: thêm đường dẫn Mosquitto vào PATH
  - Windows: `C:\Program Files\mosquitto`
  - Hoặc chạy bằng đường dẫn đầy đủ: `"C:\Program Files\mosquitto\mosquitto.exe" -c configs/mosquitto_open.conf -v`

---

## 2. Port bị bận

**Triệu chứng:**
```
Error: Address already in use
```

**Cách xử lý:**
- Có một Mosquitto khác đang chạy, tắt nó trước:
  ```bash
  # Windows
  taskkill /IM mosquitto.exe /F

  # Linux/macOS
  sudo killall mosquitto
  ```
- Hoặc đổi port trong file config (ví dụ `listener 1884`)

---

## 3. Sai username/password (Pha 2)

**Triệu chứng:**
```
[SECURE SENSOR] Kết nối bị từ chối: sai username/password!
```

**Cách xử lý:**
1. Kiểm tra file `configs/passwords.txt` đã được tạo chưa
2. Tạo lại bằng lệnh:
   ```bash
   mosquitto_passwd -c configs/passwords.txt sensor
   # Nhập: sensor123
   mosquitto_passwd configs/passwords.txt dashboard
   # Nhập: dashboard123
   ```
3. Đảm bảo password trong code trùng với password đã tạo
4. Restart broker sau khi thay đổi password file

---

## 4. Lỗi ACL — publish bị drop

**Triệu chứng:**
- Sensor publish nhưng subscriber không nhận được

**Cách xử lý:**
- Kiểm tra file `configs/acl.txt`
- Đảm bảo user `sensor` có quyền `write` và user `dashboard` có quyền `read`
- Kiểm tra topic trong ACL trùng với topic trong code: `iot/demo/data`
- Xem log broker để biết message bị drop

---

## 5. Node-RED không nhận dữ liệu

**Triệu chứng:**
- Dashboard trống, không hiển thị nhiệt độ/độ ẩm

**Cách xử lý:**
1. Kiểm tra Node-RED đã **Deploy** flow chưa (nút đỏ góc trên phải)
2. Kiểm tra node MQTT broker đã kết nối (icon xanh dưới node)
3. Nếu icon đỏ: double-click node MQTT → kiểm tra server `localhost`, port `1883`
4. Pha 2/3: cần nhập username/password vào node MQTT broker
5. Kiểm tra `node-red-dashboard` đã cài chưa:
   ```bash
   cd %USERPROFILE%\.node-red
   npm install node-red-dashboard
   ```
6. Restart Node-RED sau khi cài dashboard

---

## 6. Lỗi cert TLS (Pha 3)

### 6.1 Không tìm thấy file cert
```
[SECURE SENSOR] Lỗi: Không tìm thấy file CA cert: certs/ca.crt
```
**Cách xử lý:** Chạy script tạo cert trước:
```bash
cd certs
generate_certs.bat   # Windows
cd ..
```

### 6.2 OpenSSL chưa cài
```
[LOI] Khong tim thay OpenSSL!
```
**Cách xử lý:**
- Windows: Tải tại https://slproweb.com/products/Win32OpenSSL.html
- Cài bản Win64 OpenSSL v3.x Light
- Thêm vào PATH: `C:\Program Files\OpenSSL-Win64\bin`

### 6.3 Broker không khởi động với TLS
```
Error: Unable to load server key file
```
**Cách xử lý:**
- Kiểm tra đường dẫn cert trong `configs/mosquitto_tls.conf` trùng với vị trí file
- Đảm bảo đã chạy `generate_certs.bat` trong thư mục `certs/`
- Thử chạy broker từ thư mục gốc dự án (cùng cấp với `certs/`)

### 6.4 SSL handshake thất bại
```
[ATTACKER] ❌ Lỗi SSL/TLS: ...
```
**Đây là kết quả ĐÚNG** — attacker không có credentials hợp lệ nên TLS handshake thất bại.

---

## 7. Wireshark không thấy gói MQTT

**Cách xử lý:**
1. Chọn đúng giao diện mạng:
   - **Windows:** chọn **Adapter for loopback traffic capture** hoặc **Npcap Loopback Adapter**
   - Nếu không thấy: cài lại Wireshark, chọn cài **Npcap** kèm option "Support raw 802.11 traffic"
2. Filter đúng:
   - Pha 1: `tcp.port == 1883` hoặc `mqtt`
   - Pha 3: `tcp.port == 8883` hoặc `tls`
3. Đảm bảo sensor đang chạy và publish dữ liệu
4. Thử tắt filter để xem tất cả traffic trước, rồi mới thêm filter

---

## 8. Lỗi import paho-mqtt

**Triệu chứng:**
```
ModuleNotFoundError: No module named 'paho'
```

**Cách xử lý:**
```bash
pip install paho-mqtt
# hoặc
pip install -r requirements.txt
```
Nếu dùng Python 3 trên Linux/macOS: `pip3 install paho-mqtt`

---

## 9. Sensor chạy nhưng subscriber không thấy gì

**Cách xử lý:**
1. Kiểm tra cả hai dùng cùng topic: `iot/demo/data`
2. Kiểm tra cả hai kết nối cùng broker (cùng host và port)
3. Chạy `subscriber_test.py` trước, rồi mới chạy `sensor.py`
4. Xem log broker: có hiển thị PUBLISH và SUBSCRIBE không

---

## 10. Windows Defender/Firewall chặn

**Triệu chứng:** Broker chạy nhưng client không kết nối được.

**Cách xử lý:**
1. Cho phép `mosquitto.exe` qua Windows Firewall:
   - Windows Settings → Update & Security → Windows Security → Firewall → Allow an app
   - Thêm `C:\Program Files\mosquitto\mosquitto.exe`
2. Hoặc tạm thời tắt firewall trong lúc demo (nhớ bật lại sau)
