# Hướng dẫn cài đặt Node-RED Dashboard

## 1. Cài đặt Node-RED

### Yêu cầu
- Node.js 14+ (tải tại https://nodejs.org/)

### Cài Node-RED
```bash
npm install -g node-red
```

### Khởi chạy
```bash
node-red
```

Mở trình duyệt: http://localhost:1880

## 2. Cài module Dashboard

Trong giao diện Node-RED:
1. Click **Menu** (☰) → **Manage palette**
2. Tab **Install** → tìm `node-red-dashboard`
3. Click **Install**

Hoặc qua dòng lệnh:
```bash
cd %USERPROFILE%\.node-red
npm install node-red-dashboard
```

Khởi động lại Node-RED sau khi cài.

## 3. Import Flow

1. Mở Node-RED: http://localhost:1880
2. Click **Menu** (☰) → **Import**
3. Chọn tab **Clipboard**
4. Copy nội dung file `flow-export.json` và paste vào
5. Click **Import**
6. Click **Deploy** (nút đỏ góc trên phải)

## 4. Xem Dashboard

Mở trình duyệt: http://localhost:1880/ui

## 5. Cấu hình cho Pha 2 & 3

### Pha 2 (Auth)
1. Double-click node **Mosquitto Local** (MQTT broker)
2. Tab **Security** → nhập Username: `dashboard`, Password: `dashboard123`
3. Click **Update** → **Deploy**

### Pha 3 (TLS)
1. Double-click node **Mosquitto Local**
2. Đổi Port thành `8883`
3. Tab **Security** → nhập Username/Password
4. Tick **Enable secure (SSL/TLS) connection**
5. Click biểu tượng bút chì bên cạnh TLS Configuration
6. Upload `ca.crt` vào CA Certificate
7. Click **Update** → **Deploy**

## Lưu ý

- Dashboard tự động cập nhật khi có dữ liệu mới từ sensor
- Nếu không thấy dữ liệu, kiểm tra Mosquitto đang chạy và sensor đang publish
- Xem `docs/troubleshooting_vi.md` nếu gặp lỗi
