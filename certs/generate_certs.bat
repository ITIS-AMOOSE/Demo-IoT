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

REM Tim OpenSSL: PATH, hoac cac thu muc cai thuong gap (Shining Light Win64, v1.x–4.x)
set "OPENSSL_CMD=openssl"
where openssl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" (
        set "OPENSSL_CMD=C:\Program Files\OpenSSL-Win64\bin\openssl.exe"
    ) else if exist "C:\Program Files\OpenSSL\bin\openssl.exe" (
        set "OPENSSL_CMD=C:\Program Files\OpenSSL\bin\openssl.exe"
    ) else if exist "C:\OpenSSL-Win64\bin\openssl.exe" (
        set "OPENSSL_CMD=C:\OpenSSL-Win64\bin\openssl.exe"
    ) else (
        echo [LOI] Khong tim thay OpenSSL!
        echo   - Hay them OpenSSL-Win64\bin vao PATH, hoac
        echo   - Cai tu: https://slproweb.com/products/Win32OpenSSL.html
        echo Goi y PowerShell: $env:Path += ";C:\Program Files\OpenSSL-Win64\bin"
        pause
        exit /b 1
    )
    echo Dang dung: %OPENSSL_CMD%
)

echo [1/3] Tao CA (Certificate Authority)...
"%OPENSSL_CMD%" req -new -x509 -days 365 -extensions v3_ca ^
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
"%OPENSSL_CMD%" req -new -nodes ^
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
"%OPENSSL_CMD%" x509 -req -in server.csr ^
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
