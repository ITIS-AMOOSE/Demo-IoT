#!/bin/bash
# ================================================
# Tạo chứng chỉ tự ký (self-signed) cho demo TLS
# Chạy trong thư mục certs/
# Yêu cầu: OpenSSL đã cài
# ================================================

set -e

echo "========================================"
echo " Tạo chứng chỉ tự ký cho demo IoT TLS"
echo "========================================"
echo ""

# Kiểm tra OpenSSL
if ! command -v openssl &> /dev/null; then
    echo "[LỖI] Không tìm thấy OpenSSL!"
    echo "Cài đặt: sudo apt install openssl (Ubuntu) hoặc brew install openssl (macOS)"
    exit 1
fi

echo "[1/3] Tạo CA (Certificate Authority)..."
openssl req -new -x509 -days 365 -extensions v3_ca \
    -keyout ca.key -out ca.crt \
    -subj "/C=VN/ST=HCM/L=HCM/O=IoT-Demo/CN=Demo-CA" \
    -passout pass:capassword

echo "[OK] Đã tạo ca.key và ca.crt"
echo ""

echo "[2/3] Tạo Server Key và Certificate Signing Request..."
openssl req -new -nodes \
    -keyout server.key -out server.csr \
    -subj "/C=VN/ST=HCM/L=HCM/O=IoT-Demo/CN=localhost"

echo "[OK] Đã tạo server.key và server.csr"
echo ""

echo "[3/3] Ký Server Certificate bằng CA..."
openssl x509 -req -in server.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -days 365 -out server.crt \
    -passin pass:capassword

echo "[OK] Đã tạo server.crt"
echo ""

# Dọn file tạm
rm -f server.csr ca.srl

echo "========================================"
echo " HOÀN THÀNH! Các file đã tạo:"
echo "   ca.crt     - CA certificate (dùng cho client)"
echo "   ca.key     - CA private key (giữ bí mật)"
echo "   server.crt - Server certificate"
echo "   server.key - Server private key"
echo "========================================"
echo ""
echo "Tiếp theo:"
echo "  1. Cấu hình Mosquitto dùng mosquitto_tls.conf"
echo "  2. Client dùng ca.crt để verify server"
