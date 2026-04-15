# Hướng dẫn tạo chứng chỉ TLS cho demo

## Yêu cầu

Cần cài **OpenSSL** trước khi chạy script.

### Windows
- Tải tại: https://slproweb.com/products/Win32OpenSSL.html
- Cài bản **Win64 OpenSSL v3.x Light**
- Thêm `C:\Program Files\OpenSSL-Win64\bin` vào biến môi trường PATH
- Kiểm tra: mở CMD gõ `openssl version`

### Linux (Ubuntu/Debian)
```bash
sudo apt install openssl
```

### macOS
```bash
brew install openssl
```

## Cách chạy

### Windows
```cmd
cd certs
generate_certs.bat
```

### Linux / macOS
```bash
cd certs
chmod +x generate_certs.sh
./generate_certs.sh
```

## Kết quả

Sau khi chạy xong, thư mục `certs/` sẽ có:

| File | Mô tả |
|------|--------|
| `ca.crt` | Certificate của CA (dùng cho client để verify server) |
| `ca.key` | Private key của CA (giữ bí mật) |
| `server.crt` | Certificate của server (dùng cho Mosquitto) |
| `server.key` | Private key của server (dùng cho Mosquitto) |

## Sử dụng

1. Cấu hình Mosquitto dùng file `configs/mosquitto_tls.conf`
2. Sensor dùng `ca.crt` để xác thực server (xem `secure_sensor.py --mode tls`)
3. Subscriber dùng `ca.crt` tương tự (xem `subscriber_test.py --mode tls`)

## Lưu ý

- Cert tự ký **chỉ dùng cho demo**, không dùng trong production
- Cert có hiệu lực 365 ngày
- Nếu gặp lỗi, xem `docs/troubleshooting_vi.md`
