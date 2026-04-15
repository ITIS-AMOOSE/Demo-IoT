"""
subscriber_test.py - Subscribe và hiển thị dữ liệu MQTT
Dùng để test nhanh khi chưa có Node-RED.

Cách dùng:
  Pha 1 (open):  python subscriber_test.py
  Pha 2 (auth):  python subscriber_test.py --mode auth
  Pha 3 (TLS):   python subscriber_test.py --mode tls
"""

import json
import argparse
import ssl
import os

import paho.mqtt.client as mqtt

# ====== CẤU HÌNH ======
BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
MQTT_PORT = 1883
MQTTS_PORT = 8883
TOPIC = "iot/demo/data"

# Thông tin đăng nhập cho dashboard (chỉ đọc)
USERNAME = "dashboard"
PASSWORD = "dashboard123"

# Cert
CA_CERT = "certs/ca.crt"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[SUBSCRIBER] Kết nối thành công!")
        client.subscribe(TOPIC)
        print(f"[SUBSCRIBER] Đang lắng nghe topic: {TOPIC}")
        print(f"[SUBSCRIBER] Chờ dữ liệu... (Ctrl+C để dừng)\n")
    else:
        print(f"[SUBSCRIBER] Kết nối thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        print(f"[SUBSCRIBER] Nhận từ topic '{msg.topic}':")
        print(f"   Device ID   : {data.get('device_id', 'N/A')}")
        print(f"   Nhiệt độ   : {data.get('temperature', 'N/A')}°C")
        print(f"   Độ ẩm      : {data.get('humidity', 'N/A')}%")
        print(f"   Timestamp   : {data.get('timestamp', 'N/A')}")
        print()
    except json.JSONDecodeError:
        print(f"[SUBSCRIBER] Nhận payload không phải JSON: {msg.payload}")
    except Exception as e:
        print(f"[SUBSCRIBER] Lỗi xử lý message: {e}")


def main():
    parser = argparse.ArgumentParser(description="MQTT Subscriber Test")
    parser.add_argument(
        "--mode",
        choices=["open", "auth", "tls"],
        default="open",
        help="Chế độ: 'open' (Pha 1), 'auth' (Pha 2), 'tls' (Pha 3)",
    )
    args = parser.parse_args()

    client = mqtt.Client(client_id="subscriber-test")
    client.on_connect = on_connect
    client.on_message = on_message

    port = MQTT_PORT

    if args.mode in ("auth", "tls"):
        client.username_pw_set(USERNAME, PASSWORD)
        print(f"[SUBSCRIBER] Đăng nhập với user: {USERNAME}")

    if args.mode == "tls":
        port = MQTTS_PORT
        try:
            client.tls_set(
                ca_certs=CA_CERT,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
            )
            client.tls_insecure_set(True)
            print(f"[SUBSCRIBER] TLS được bật, CA cert: {CA_CERT}")
        except FileNotFoundError:
            print(f"[SUBSCRIBER] Lỗi: Không tìm thấy CA cert: {CA_CERT}")
            return
        except Exception as e:
            print(f"[SUBSCRIBER] Lỗi TLS: {e}")
            return

    try:
        print(f"[SUBSCRIBER] Kết nối tới {BROKER_HOST}:{port}...")
        client.connect(BROKER_HOST, port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[SUBSCRIBER] Lỗi: Không thể kết nối broker tại {BROKER_HOST}:{port}")
        return
    except Exception as e:
        print(f"[SUBSCRIBER] Lỗi: {e}")
        return

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[SUBSCRIBER] Đã dừng.")
        client.disconnect()


if __name__ == "__main__":
    main()
