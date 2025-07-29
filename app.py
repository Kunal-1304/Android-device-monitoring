from flask import Flask, render_template, jsonify, request
import socket, threading, json, datetime
import pywhatkit as kit
import datetime as dt

app = Flask(__name__)

PORT = 5001
WHATSAPP_NUM = "+91XXXXXXXXXX"  # your number here

LIMITS = {
    "battery": 20,
    "ram_used": 85,
    "storage_used": 90
}

latest_data = {}
alerts_log = []
latest_data_lock = threading.Lock()
alerts_lock = threading.Lock()

def check_alerts(data, addr):
    alerts = []
    
    bat = data.get("battery", {}).get("percentage")
    if bat and bat < LIMITS["battery"]:
        alerts.append(f"🔋 Battery low: {bat}%")

    ram = data.get("ram", {}).get("used_percent")
    if ram and ram > LIMITS["ram_used"]:
        alerts.append(f"🧠 RAM high: {ram}%")

    storage = data.get("full_storage", {}).get("used_percent")
    if storage and storage > LIMITS["storage_used"]:
        alerts.append(f"💾 Storage full: {storage}%")

    return alerts

def handle_client(conn, addr):
    with conn:
        try:
            data_raw = conn.recv(4096).decode().strip()
            data = json.loads(data_raw)
            
            timestamp = datetime.datetime.now().isoformat()
            print(f"\n[{timestamp}] Got data from {addr}")

            global latest_data
            with latest_data_lock:
                latest_data = data.copy()
                latest_data['last_updated'] = timestamp

            # check for problems
            alerts = check_alerts(data, addr)
            for alert in alerts:
                msg = f"{timestamp} | {addr} | {alert}"
                with alerts_lock:
                    alerts_log.append(msg)
                print(f"ALERT: {msg}")

                # send whatsapp msg
                try:
                    device_name = data.get("device_id", f"Device-{addr[0]}")
                    
                    whatsapp_text = f"""🚨 Alert from {device_name}
{alert}
Time: {timestamp.split('T')[0]} {timestamp.split('T')[1][:8]}
Check device now!"""

                    now = dt.datetime.now()
                    send_hour = now.hour
                    send_min = now.minute + 1

                    kit.sendwhatmsg(WHATSAPP_NUM, whatsapp_text, send_hour, send_min, 
                                  wait_time=8, tab_close=True)
                    print("WhatsApp sent")
                    
                except Exception as e:
                    print(f"WhatsApp failed: {e}")

        except json.JSONDecodeError:
            print(f"Bad JSON from {addr}")
        except Exception as e:
            print(f"Client error: {e}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()
    print(f"Server running on port {PORT}")

    while True:
        try:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
        except:
            pass

@app.route("/")
def home():
    with latest_data_lock:
        data = latest_data.copy()
    with alerts_lock:
        recent = alerts_log[-10:]
    return render_template("index.html", active_page="dashboard", data=data, alerts=recent)

@app.route("/devices")
def devices():
    with latest_data_lock:
        data = latest_data.copy()
    return render_template("devices.html", active_page="devices", data=data)

@app.route("/logs")
def logs():
    with alerts_lock:
        all_logs = alerts_log.copy()
    return render_template("logs.html", active_page="logs", alerts=all_logs)

@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings", thresholds=LIMITS)

@app.route("/data")
def get_data():
    with latest_data_lock:
        data = latest_data.copy()
    with alerts_lock:
        recent = alerts_log[-10:]
    
    return jsonify({
        "data": data,
        "alerts": recent,
        "status": "ok"
    })

@app.route("/update_limits", methods=['POST'])
def update_limits():
    global LIMITS
    try:
        new_limits = request.get_json()
        if new_limits:
            for k, v in new_limits.items():
                if k in LIMITS:
                    LIMITS[k] = int(v)
            return jsonify({"status": "ok", "limits": LIMITS})
        return jsonify({"status": "error"})
    except:
        return jsonify({"status": "error"})

if __name__ == "__main__":
    print("Starting monitoring system...")
    
    # start socket server
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # start web app
    app.run(debug=False, host='0.0.0.0', port=5000)
