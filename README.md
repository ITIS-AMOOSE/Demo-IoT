# 🔐 Demo Bảo mật Dữ liệu trong Hệ thống IoT

## Mục tiêu

Demo minh họa 3 mức độ bảo mật trong hệ thống IoT, chạy hoàn toàn trên laptop, không cần phần cứng thật.

| Pha | Mô tả | Kết quả |
|-----|--------|---------|
| **Pha 1** | Không bảo mật | Attacker chèn dữ liệu giả thành công |
| **Pha 2** | Auth + ACL | Attacker bị từ chối kết nối |
| **Pha 3** | TLS + Auth | Dữ liệu mã hóa, attacker thất bại |

## Kiến trúc hệ thống

```
┌─────────────┐     MQTT      ┌───────────────┐     MQTT      ┌──────────────┐
│  sensor.py  │ ──publish──→  │   Mosquitto   │ ──subscribe── │   Node-RED   │
│ (Cảm biến)  │               │   (Broker)    │               │ (Dashboard)  │
└─────────────┘               └───────────────┘               └──────────────┘
                                     ↑
                              ┌──────┴──────┐
                              │ attacker.py │
                              │  (Tấn công)  │
                              └─────────────┘
```

**Luồng dữ liệu:**
1. `sensor.py` giả lập cảm biến, gửi nhiệt độ/độ ẩm lên broker
2. Mosquitto nhận và chuyển tiếp dữ liệu
3. Node-RED subscribe và hiển thị trên dashboard
4. `attacker.py` thử chèn dữ liệu giả vào cùng topic

## Công nghệ sử dụng

- **Python 3** + `paho-mqtt` — giả lập cảm biến và tấn công
- **Eclipse Mosquitto** — MQTT broker
- **Node-RED** + `node-red-dashboard` — dashboard hiển thị
- **OpenSSL** — tạo chứng chỉ TLS
- **Wireshark** — quan sát gói tin mạng

## Cấu trúc dự án

```
iot-security-demo/
├── README.md                    ← Bạn đang đọc file này
├── requirements.txt             ← Thư viện Python
├── sensor.py                    ← Cảm biến IoT (Pha 1)
├── attacker.py                  ← Tấn công giả mạo (Pha 1)
├── secure_sensor.py             ← Cảm biến có bảo mật (Pha 2 & 3)
├── secure_attacker.py           ← Tấn công khi đã bảo mật (Pha 2 & 3)
├── subscriber_test.py           ← Test subscriber nhanh
├── configs/
│   ├── mosquitto_open.conf      ← Config broker mở (Pha 1)
│   ├── mosquitto_auth.conf      ← Config broker auth (Pha 2)
│   ├── mosquitto_tls.conf       ← Config broker TLS (Pha 3)
│   ├── acl.txt                  ← Phân quyền topic
│   └── passwords.example.txt   ← Mẫu username/password
├── certs/
│   ├── generate_certs.bat       ← Tạo cert (Windows)
│   ├── generate_certs.sh        ← Tạo cert (Linux/macOS)
│   └── README.md                ← Hướng dẫn tạo cert
├── node_red/
│   ├── flow-export.json         ← Flow Node-RED import sẵn
│   └── README.md                ← Hướng dẫn cài Node-RED
├── screenshots/                 ← Ảnh chụp cho báo cáo
└── docs/
    ├── run_guide_vi.md          ← Hướng dẫn chạy từng bước
    ├── demo_script_vi.md        ← Kịch bản thuyết trình
    └── troubleshooting_vi.md    ← Xử lý lỗi thường gặp
```

## 🚀 Cách chạy nhanh (Docker)

> **Yêu cầu duy nhất:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) + [Wireshark](https://www.wireshark.org/download.html) + Python 3 (chỉ để chạy sensor local cho Wireshark).
>
> Cài Python dependency: `pip install paho-mqtt==1.6.1`

### Chạy đồng thời cả 3 pha (1 lệnh cho demo)

> Dùng khi bạn muốn mở demo và show ngay 3 mức bảo mật cùng lúc, không cần đổi profile qua lại.
>
> Không chạy thêm `python sensor.py` hoặc `python attacker.py` local khi dùng cách này để tránh chạy trùng publisher.

```powershell
# Nếu demo Pha 3 (TLS), nhớ tạo cert trước (chạy 1 lần)
cd certs
.\generate_certs.bat
cd ..

# Chạy cả 3 pha cùng lúc
docker compose -f docker-compose.demo.yml up --build
```

Các cổng broker khi chạy đồng thời:
- **Pha 1 (Open):** `localhost:1883`
- **Pha 2 (Auth):** `localhost:1884`
- **Pha 3 (TLS):** `localhost:8883`

Wireshark filter gợi ý:
- Pha 1: `tcp.port == 1883`
- Pha 2: `tcp.port == 1884`
- Pha 3: `tcp.port == 8883 && tls`

Dừng demo đồng thời:
```powershell
docker compose -f docker-compose.demo.yml down
```

---

### Pha 1 — Không bảo mật

> Khuyến nghị demo ổn định: chỉ chạy `mosquitto` + `nodered` bằng Docker,
> còn `sensor/attacker` chạy local để Wireshark bắt gói loopback rõ ràng.

**Terminal 1: Khởi động broker + dashboard**
```powershell
docker compose --profile pha1 up --build mosquitto nodered
```

**Terminal 2: Chạy sensor local (để Wireshark bắt được gói tin)**
```powershell
python sensor.py
```

**Terminal 3: Chạy attacker local**
```powershell
python attacker.py
```

**Dashboard:** http://localhost:1880/ui — thấy dữ liệu cảm biến + dữ liệu giả từ attacker.

**🦈 Wireshark:**
1. Mở Wireshark → chọn **Adapter for loopback traffic capture** (KHÔNG phải Ethernet)
2. Filter: `mqtt`
3. Tìm gói **Publish Message** → xem payload JSON rõ ràng
4. Tìm gói **Connect Command** → thấy `User Name Flag: Not set` (không xác thực)
5. 📸 Chụp ảnh làm bằng chứng: **dữ liệu truyền không mã hóa**

Dừng: `Ctrl+C` ở terminal local, rồi `docker compose --profile pha1 down`

---

### Pha 2 — Auth + ACL

**Terminal 1: Khởi động broker + dashboard với Auth**
```powershell
$env:MOSQUITTO_CONFIG="mosquitto_auth.conf"; docker compose --profile pha2 up --build mosquitto nodered
```

**Terminal 2: Chạy secure sensor local (có username/password)**
```powershell
python secure_sensor.py --mode auth
```
→ ✅ `Kết nối thành công!` + gửi dữ liệu bình thường

**Terminal 3: Chạy attacker local (thử tấn công)**
```powershell
python secure_attacker.py --mode auth
```
→ ❌ `Broker từ chối kết nối!` → Tấn công thất bại

**Dashboard:** http://localhost:1880/ui — chỉ hiển thị dữ liệu từ sensor hợp lệ.

**🦈 Wireshark:**
1. Filter: `mqtt`
2. Tìm gói **Connect Command** → thấy `User Name Flag: Set` + `Password Flag: Set`
3. Tìm gói **Publish Message** → payload JSON **vẫn đọc rõ** (Auth không mã hóa dữ liệu!)
4. 📸 Chụp ảnh: **có xác thực nhưng dữ liệu vẫn truyền rõ trên mạng**

Dừng: `Ctrl+C` ở terminal local, rồi `docker compose --profile pha2 down`

---

### Pha 3 — TLS

```powershell
# Tạo cert (chạy 1 lần duy nhất)
cd certs
.\generate_certs.bat
cd ..
```

> ⚠️ **Lưu ý Windows (PowerShell):**
> - Nếu báo `openssl is not recognized`:
>   - Cài OpenSSL (free): `winget install -e --id ShiningLight.OpenSSL.Light`
>   - Thêm PATH tạm thời: `$env:Path += ";C:\Program Files\OpenSSL-Win64\bin"`
>   - Kiểm tra: `openssl version`
> - Nếu báo `Can't open "ca.crt" for writing, Permission denied`:
>   - Dừng các tiến trình đang dùng cert (`Ctrl+C`, `docker compose --profile pha3 down`)
>   - Mở PowerShell quyền Administrator và chạy lại `.\generate_certs.bat`
> - Nếu bạn đang ở sẵn thư mục `certs`, **không chạy lại** `cd certs`.

**Terminal 1: Khởi động broker TLS + dashboard TLS**
```powershell
$env:MOSQUITTO_CONFIG="mosquitto_tls.conf"; docker compose --profile pha3 up --build mosquitto nodered-tls
```

**Terminal 2: Chạy secure sensor TLS local**
```powershell
python secure_sensor.py --mode tls
```
→ ✅ Kết nối TLS thành công + gửi dữ liệu mã hóa

**Terminal 3: Chạy attacker TLS local**
```powershell
python secure_attacker.py --mode tls
```
→ ❌ Sai credentials (và/hoặc không có cert hợp lệ) → Tấn công thất bại

**🦈 Wireshark:**
1. Filter: `tcp.port == 8883`
2. Chỉ thấy **TLS encrypted** → KHÔNG đọc được payload
3. 📸 Chụp ảnh: **dữ liệu hoàn toàn được mã hóa**

Dừng: `Ctrl+C` ở terminal local, rồi `docker compose --profile pha3 down`

---

### So sánh Wireshark 3 pha (cho báo cáo)

| Pha | Xác thực | Payload trên Wireshark | Kết luận |
|-----|----------|----------------------|----------|
| 1 | ❌ Không | Đọc rõ JSON | Ai cũng đọc được |
| 2 | ✅ Auth+ACL | **Vẫn đọc rõ** JSON | Auth chặn truy cập, không mã hóa |
| 3 | ✅ Auth+TLS | 🔒 Mã hóa TLS | An toàn toàn diện |

### Xem log Docker

```powershell
docker compose --profile pha2 logs -f secure-sensor-auth
docker compose --profile pha2 logs -f secure-attacker-auth
```

---

<details>
<summary>📖 <b>Cách chạy thủ công (không dùng Docker)</b></summary>

Xem hướng dẫn chi tiết: [docs/run_guide_vi.md](docs/run_guide_vi.md)

Cần cài: Python 3, Mosquitto, Node-RED, OpenSSL, Wireshark.

```bash
pip install -r requirements.txt
mosquitto -c configs/mosquitto_open.conf -v   # Terminal 1
python sensor.py                               # Terminal 2
python subscriber_test.py                      # Terminal 3
python attacker.py                             # Terminal 4
```

</details>

## Mô tả 3 pha bảo mật

### Pha 1: Không bảo mật
- Broker chấp nhận mọi kết nối (anonymous)
- Bất kỳ ai cũng publish được vào topic
- Wireshark đọc được payload JSON rõ ràng
- **Nguy cơ:** giả mạo dữ liệu, đọc trộm, không xác thực

### Pha 2: Bảo mật cơ bản (Auth + ACL)
- Broker yêu cầu username/password
- ACL phân quyền: sensor chỉ write, dashboard chỉ read
- Attacker không có credentials → bị từ chối
- **Cải thiện:** xác thực nguồn gửi, phân quyền truy cập

### Pha 3: Bảo mật nâng cao (TLS + Auth)
- Kết nối mã hóa TLS (port 8883)
- Client dùng CA cert để verify server
- Wireshark không đọc được nội dung payload
- **Cải thiện:** bảo mật truyền tải, chống nghe lén

## Bảng đánh giá trước/sau bảo mật

| Tiêu chí | Pha 1 (Mở) | Pha 2 (Auth) | Pha 3 (TLS) |
|----------|:-----------:|:------------:|:------------:|
| **Tính bí mật** | ❌ Payload đọc được | ❌ Payload đọc được | ✅ Mã hóa TLS |
| **Tính toàn vẹn** | ❌ Ai cũng sửa được | ⚠️ Chỉ user hợp lệ | ✅ TLS + Auth |
| **Xác thực nguồn gửi** | ❌ Không xác thực | ✅ Username/password | ✅ Username + TLS |
| **Chống giả mạo** | ❌ Dễ giả mạo | ✅ ACL phân quyền | ✅ ACL + mã hóa |
| **Mở rộng bảo mật** | ❌ | ⚠️ Cơ bản | ✅ Có thể thêm client cert |

## Ảnh nên chụp cho báo cáo

1. 📊 Dashboard Node-RED khi nhận dữ liệu bình thường
2. ⚠️ Dashboard khi bị attacker chèn dữ liệu giả (nhiệt độ bất thường)
3. 🔍 Wireshark ở Pha 1: thấy payload JSON rõ ràng
4. 🔒 Log attacker bị từ chối ở Pha 2
5. 🔐 Wireshark ở Pha 3: payload bị mã hóa
6. ✅ Log sensor kết nối TLS thành công

## Thuật ngữ

| Thuật ngữ | Giải thích |
|-----------|-----------|
| **MQTT** | Giao thức truyền tin nhẹ, phổ biến trong IoT |
| **Broker** | Server trung gian nhận và chuyển tiếp message |
| **Publish** | Gửi dữ liệu lên broker |
| **Subscribe** | Đăng ký nhận dữ liệu từ broker |
| **Topic** | "Kênh" dữ liệu, ví dụ `iot/demo/data` |
| **TLS** | Giao thức mã hóa kết nối (giống HTTPS) |
| **ACL** | Access Control List - danh sách phân quyền |
| **Dashboard** | Bảng hiển thị dữ liệu trực quan |

## Tài liệu liên quan

- [Hướng dẫn chạy chi tiết](docs/run_guide_vi.md)
- [Kịch bản thuyết trình](docs/demo_script_vi.md)
- [Xử lý lỗi thường gặp](docs/troubleshooting_vi.md)
- [Hướng dẫn tạo cert TLS](certs/README.md)
- [Hướng dẫn Node-RED](node_red/README.md)
