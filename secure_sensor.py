"""
secure_sensor.py - Cảm biến IoT có bảo mật (Pha 2 & Pha 3)
Hỗ trợ:
  - Pha 2: Username/password authentication
  - Pha 3: TLS encryption + authentication

Cách dùng:
  Pha 2 (auth):  python secure_sensor.py --mode auth
  Pha 3 (TLS):   python secure_sensor.py --mode tls
"""

import json
import time
import random
import argparse
import ssl
import os
from datetime import datetime

import paho.mqtt.client as mqtt

# ====== CẤU HÌNH ======
BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
MQTT_PORT = int(os.environ.get("BROKER_PORT", "1883"))           # Port cho Pha 2 (auth)
MQTTS_PORT = int(os.environ.get("BROKER_TLS_PORT", "8883"))      # Port cho Pha 3 (TLS)
TOPIC = "iot/demo/data"
DEVICE_ID = "sensor-01"
INTERVAL = 2

# Thông tin đăng nhập (phải trùng với password_file của Mosquitto)
USERNAME = "sensor"
PASSWORD = "sensor123"

# Đường dẫn cert cho TLS (Pha 3)
CA_CERT = "certs/ca.crt"


def generate_sensor_data():
    """Sinh dữ liệu cảm biến ngẫu nhiên."""
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(24.0, 35.0), 1),
        "humidity": round(random.uniform(55.0, 85.0), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def on_connect(client, userdata, flags, rc):
    mode = userdata.get("mode", "unknown")
    if rc == 0:
        print(f"[SECURE SENSOR] Kết nối thành công! (chế độ: {mode})")
    elif rc == 5:
        print(f"[SECURE SENSOR] Kết nối bị từ chối: sai username/password!")
    else:
        print(f"[SECURE SENSOR] Kết nối thất bại, mã lỗi: {rc}")
        # Mã lỗi phổ biến:
        # 1 = sai protocol, 2 = client ID không hợp lệ,
        # 4 = sai username/password, 5 = không được phép


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[SECURE SENSOR] Mất kết nối bất ngờ, mã: {rc}")


def main():
    parser = argparse.ArgumentParser(description="Secure IoT Sensor")
    parser.add_argument(
        "--mode",
        choices=["auth", "tls"],
        default="auth",
        help="Chế độ bảo mật: 'auth' (Pha 2) hoặc 'tls' (Pha 3)",
    )
    args = parser.parse_args()

    # Tạo client với userdata chứa mode
    client = mqtt.Client(
        client_id=f"{DEVICE_ID}-secure",
        userdata={"mode": args.mode},
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Đặt username/password
    client.username_pw_set(USERNAME, PASSWORD)
    print(f"[SECURE SENSOR] Đăng nhập với user: {USERNAME}")

    # Cấu hình TLS nếu ở Pha 3
    if args.mode == "tls":
        port = MQTTS_PORT
        try:
            client.tls_set(
                ca_certs=CA_CERT,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
            )
            # Tắt kiểm tra hostname vì dùng cert tự ký cho demo
            client.tls_insecure_set(True)
            print(f"[SECURE SENSOR] TLS được bật, CA cert: {CA_CERT}")
        except FileNotFoundError:
            print(f"[SECURE SENSOR] Lỗi: Không tìm thấy file CA cert: {CA_CERT}")
            print("[SECURE SENSOR] Hãy chạy script tạo cert trước (xem certs/README.md)")
            return
        except Exception as e:
            print(f"[SECURE SENSOR] Lỗi cấu hình TLS: {e}")
            return
    else:
        port = MQTT_PORT

    # Kết nối
    try:
        print(f"[SECURE SENSOR] Đang kết nối tới {BROKER_HOST}:{port}...")
        client.connect(BROKER_HOST, port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[SECURE SENSOR] Lỗi: Broker không chấp nhận kết nối tại port {port}")
        return
    except Exception as e:
        print(f"[SECURE SENSOR] Lỗi kết nối: {e}")
        return

    client.loop_start()
    time.sleep(1)  # Đợi callback on_connect

    print(f"[SECURE SENSOR] Gửi dữ liệu lên '{TOPIC}' mỗi {INTERVAL} giây...")
    print("[SECURE SENSOR] Nhấn Ctrl+C để dừng.\n")

    try:
        while True:
            data = generate_sensor_data()
            payload = json.dumps(data, ensure_ascii=False)
            result = client.publish(TOPIC, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[SECURE SENSOR] Đã gửi: {payload}")
            else:
                print(f"[SECURE SENSOR] Gửi thất bại, mã lỗi: {result.rc}")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[SECURE SENSOR] Đã dừng.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
