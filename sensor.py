"""
sensor.py - Giả lập cảm biến IoT (Pha 1: Không bảo mật)
Gửi dữ liệu nhiệt độ/độ ẩm lên MQTT broker qua kết nối anonymous.
"""

import json
import time
import random
import os
import socket
from datetime import datetime

import paho.mqtt.client as mqtt

# ====== CẤU HÌNH ======
BROKER_HOST = os.environ.get("BROKER_HOST", "localhost")
BROKER_PORT = int(os.environ.get("BROKER_PORT", "1883"))
TOPIC = "iot/demo/data"
DEVICE_ID = "sensor-01"
INTERVAL = 2  # Gửi mỗi 2 giây


def build_client_id():
    """
    Tạo client_id duy nhất để tránh đụng với sensor khác.
    Có thể override bằng biến môi trường MQTT_CLIENT_ID.
    """
    env_client_id = os.environ.get("MQTT_CLIENT_ID")
    if env_client_id:
        return env_client_id
    return f"{DEVICE_ID}-pub-{socket.gethostname()}-{os.getpid()}"


def generate_sensor_data():
    """Sinh dữ liệu cảm biến ngẫu nhiên trong khoảng hợp lý."""
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(24.0, 35.0), 1),
        "humidity": round(random.uniform(55.0, 85.0), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def on_connect(client, userdata, flags, rc):
    """Callback khi kết nối tới broker."""
    if rc == 0:
        print(f"[SENSOR] Kết nối thành công tới {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[SENSOR] Kết nối thất bại, mã lỗi: {rc}")


def on_publish(client, userdata, mid):
    """Callback khi publish thành công."""
    pass  # Log đã in ở vòng lặp chính


def on_disconnect(client, userdata, rc):
    """Callback khi mất kết nối."""
    if rc != 0:
        print(f"[SENSOR] Mất kết nối broker (rc={rc}), đang tự reconnect...")


def main():
    # Tạo MQTT client
    client = mqtt.Client(client_id=build_client_id())
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Kết nối tới broker
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    except ConnectionRefusedError:
        print(f"[SENSOR] Lỗi: Không thể kết nối tới broker tại {BROKER_HOST}:{BROKER_PORT}")
        print("[SENSOR] Hãy chắc chắn Mosquitto đang chạy.")
        return
    except Exception as e:
        print(f"[SENSOR] Lỗi kết nối: {e}")
        return

    client.loop_start()
    print(f"[SENSOR] Bắt đầu gửi dữ liệu lên topic '{TOPIC}' mỗi {INTERVAL} giây...")
    print("[SENSOR] Nhấn Ctrl+C để dừng.\n")

    try:
        while True:
            data = generate_sensor_data()
            payload = json.dumps(data, ensure_ascii=False)
            result = client.publish(TOPIC, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[SENSOR] Đã gửi: {payload}")
            else:
                print(f"[SENSOR] Gửi thất bại, mã lỗi: {result.rc}")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[SENSOR] Đã dừng gửi dữ liệu.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[SENSOR] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
