#!/usr/bin/env python3
import socket, subprocess, json, platform, shutil, time

SERVER_IP = input("Server IP: ").strip()
PORT = 5001
INTERVAL = 60  # seconds

def bytes_to_gb(b):
    return round(b / (1024**3), 2)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP not found"

def get_battery():
    try:
        out = subprocess.check_output(
            ["termux-battery-status"], text=True, timeout=5
        )
        return json.loads(out)
    except:
        return {"error": "battery unavailable"}

def get_ram():
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail_kb = int(line.split()[1])
        mem["total_gb"] = bytes_to_gb(total_kb * 1024)
        mem["avail_gb"] = bytes_to_gb(avail_kb * 1024)
        mem["used_percent"] = round((total_kb - avail_kb) / total_kb * 100, 2)
    except:
        mem["error"] = "RAM info unavailable"
    return mem

def get_storage(path="/"):
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "total_gb": bytes_to_gb(total),
            "used_gb": bytes_to_gb(used),
            "free_gb": bytes_to_gb(free),
            "used_percent": round((used / total) * 100, 2)
        }
    except:
        return {"error": "storage info unavailable"}

def get_location():
    try:
        out = subprocess.check_output(
            ["termux-location", "-p", "network", "-r", "once"],
            text=True, timeout=10
        )
        data = json.loads(out)
        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "accuracy": data.get("accuracy")
        }
    except:
        return {"error": "location unavailable"}

def get_device_info():
    return {
        "device_name": platform.node(),
        "android_version": platform.release()
    }

while True:
    try:
        payload = {
            "ip": get_ip(),
            "device_info": get_device_info(),
            "location": get_location(),
            "battery": get_battery(),
            "ram": get_ram(),
            "storage": get_storage("/")
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        s.sendall((json.dumps(payload) + "\n").encode())
        s.close()
        print(f"📤 Data sent: {json.dumps(payload, indent=2)}")

    except Exception as e:
        print("❌ Error sending data:", e)

    time.sleep(INTERVAL)