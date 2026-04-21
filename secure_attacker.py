"""
secure_attacker.py - Giả lập tấn công khi broker đã bảo mật (Pha 2 & Pha 3)
Minh họa việc attacker bị từ chối khi:
  - Pha 2: Sai username/password hoặc không có quyền publish
  - Pha 3: Không có cert TLS hợp lệ

Cách dùng:
  Pha 2: python secure_attacker.py --mode auth
  Pha 3: python secure_attacker.py --mode tls
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
MQTT_PORT = int(os.environ.get("BROKER_PORT", "1883"))
MQTTS_PORT = int(os.environ.get("BROKER_TLS_PORT", "8883"))
TOPIC = "iot/demo/data"

# Attacker dùng thông tin đăng nhập SAI
WRONG_USERNAME = "hacker"
WRONG_PASSWORD = "wrongpass"

# Attacker không có CA cert hợp lệ
FAKE_CA_CERT = "certs/ca.crt"  # Có file nhưng sai credentials


def generate_fake_data():
    return {
        "device_id": "attacker-fake",
        "temperature": round(random.uniform(80.0, 120.0), 1),
        "humidity": round(random.uniform(0.0, 10.0), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def on_connect(client, userdata, flags, rc):
    mode = userdata.get("mode", "unknown")
    if rc == 0:
        print(f"[ATTACKER] Kết nối thành công (chế độ: {mode})")
        print("[ATTACKER] Đang thử publish dữ liệu giả...")
    elif rc == 4 or rc == 5:
        print(f"[ATTACKER] ❌ BỊ TỪ CHỐI! Sai username/password (mã lỗi: {rc})")
        print("[ATTACKER] → Broker đã bảo mật, attacker không thể kết nối!")
    else:
        print(f"[ATTACKER] ❌ Kết nối thất bại, mã lỗi: {rc}")


def on_publish(client, userdata, mid):
    print(f"[ATTACKER] ⚠️  Publish có vẻ thành công (mid={mid})")
    print("[ATTACKER]    Nhưng nếu ACL được cấu hình, broker sẽ âm thầm drop message.")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[ATTACKER] Bị ngắt kết nối bởi broker (mã: {rc})")


def main():
    parser = argparse.ArgumentParser(description="Secure Attacker Simulation")
    parser.add_argument(
        "--mode",
        choices=["auth", "tls"],
        default="auth",
        help="Chế độ tấn công: 'auth' (Pha 2) hoặc 'tls' (Pha 3)",
    )
    args = parser.parse_args()

    client = mqtt.Client(
        client_id="attacker-secure",
        userdata={"mode": args.mode},
    )
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Attacker dùng credentials SAI
    client.username_pw_set(WRONG_USERNAME, WRONG_PASSWORD)
    print(f"[ATTACKER] Thử đăng nhập với user SAI: {WRONG_USERNAME}")

    if args.mode == "tls":
        port = MQTTS_PORT
        print(f"[ATTACKER] Thử kết nối TLS tới port {port}...")
        try:
            # Attacker có thể có CA cert (download được) nhưng sai credentials
            client.tls_set(
                ca_certs=FAKE_CA_CERT,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
            )
            client.tls_insecure_set(True)
        except FileNotFoundError:
            print(f"[ATTACKER] Không tìm thấy CA cert: {FAKE_CA_CERT}")
            print("[ATTACKER] → Attacker không có cert → không thể kết nối TLS!")
            return
        except Exception as e:
            print(f"[ATTACKER] Lỗi TLS: {e}")
            return
    else:
        port = MQTT_PORT

    # Thử kết nối
    try:
        print(f"[ATTACKER] Đang thử kết nối tới {BROKER_HOST}:{port}...")
        client.connect(BROKER_HOST, port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[ATTACKER] ❌ Broker từ chối kết nối tại port {port}!")
        print("[ATTACKER] → Tấn công thất bại: broker đã được bảo mật.")
        return
    except ssl.SSLError as e:
        print(f"[ATTACKER] ❌ Lỗi SSL/TLS: {e}")
        print("[ATTACKER] → Tấn công thất bại: không qua được TLS handshake!")
        return
    except Exception as e:
        print(f"[ATTACKER] ❌ Lỗi: {e}")
        return

    client.loop_start()
    time.sleep(2)  # Đợi kết quả on_connect

    # Thử publish vài bản tin
    print(f"\n[ATTACKER] Thử gửi 3 bản tin giả vào topic '{TOPIC}'...")
    for i in range(1, 4):
        data = generate_fake_data()
        payload = json.dumps(data, ensure_ascii=False)
        result = client.publish(TOPIC, payload)
        print(f"[ATTACKER] Lần {i}: publish rc={result.rc} - {payload}")
        time.sleep(2)

    print("\n[ATTACKER] Kết thúc thử tấn công.")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
