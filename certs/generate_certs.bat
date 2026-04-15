@echo off
REM ================================================
REM Tạo chứng chỉ tự ký (self-signed) cho demo TLS
REM Chạy trong thư mục certs/
REM Yêu cầu: OpenSSL đã cài và có trong PATH
REM ================================================

echo ========================================
echo  Tao chung chi tu ky cho demo IoT TLS
echo ========================================
echo.

REM Kiểm tra OpenSSL
where openssl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [LOI] Khong tim thay OpenSSL!
    echo Hay cai OpenSSL va them vao PATH.
    echo Download tai: https://slproweb.com/products/Win32OpenSSL.html
    pause
    exit /b 1
)

echo [1/3] Tao CA (Certificate Authority)...
openssl req -new -x509 -days 365 -extensions v3_ca ^
    -keyout ca.key -out ca.crt ^
    -subj "/C=VN/ST=HCM/L=HCM/O=IoT-Demo/CN=Demo-CA" ^
    -passout pass:capassword

if %ERRORLEVEL% neq 0 (
    echo [LOI] Tao CA that bai!
    pause
    exit /b 1
)
echo [OK] Da tao ca.key va ca.crt
echo.

echo [2/3] Tao Server Key va Certificate Signing Request...
openssl req -new -nodes ^
    -keyout server.key -out server.csr ^
    -subj "/C=VN/ST=HCM/L=HCM/O=IoT-Demo/CN=localhost"

if %ERRORLEVEL% neq 0 (
    echo [LOI] Tao server key that bai!
    pause
    exit /b 1
)
echo [OK] Da tao server.key va server.csr
echo.

echo [3/3] Ky Server Certificate bang CA...
openssl x509 -req -in server.csr ^
    -CA ca.crt -CAkey ca.key -CAcreateserial ^
    -days 365 -out server.crt ^
    -passin pass:capassword

if %ERRORLEVEL% neq 0 (
    echo [LOI] Ky certificate that bai!
    pause
    exit /b 1
)
echo [OK] Da tao server.crt
echo.

REM Dọn file tạm
del /q server.csr 2>nul
del /q ca.srl 2>nul

echo ========================================
echo  HOAN THANH! Cac file da tao:
echo    ca.crt     - CA certificate (dung cho client)
echo    ca.key     - CA private key (giu bi mat)
echo    server.crt - Server certificate
echo    server.key - Server private key
echo ========================================
echo.
echo Tiep theo:
echo   1. Cau hinh Mosquitto dung mosquitto_tls.conf
echo   2. Client dung ca.crt de verify server
echo.
pause
