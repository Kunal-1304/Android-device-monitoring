from flask import Flask, render_template, jsonify, request, url_for
import socket, threading, json, datetime
import pywhatkit as kit
import datetime as dt

app = Flask(__name__)

PORT = 5001

THRESHOLDS = {
    "battery": 40,
    "ram_used": 80,
    "storage_used": 90
}

# Shared global state
latest_data = {}
alerts_log = []

# Locks to ensure thread safety
latest_data_lock = threading.Lock()
alerts_lock = threading.Lock()

# --- Alert Checker ---
def check_alerts(data, addr):
    alerts = []

    # Battery check
    bat = data.get("battery", {}).get("percentage")
    if isinstance(bat, (int, float)) and bat < THRESHOLDS["battery"]:
        alerts.append(f"🔋 Battery level is critically low: {bat}%")

    # RAM check
    ram_used = data.get("ram", {}).get("used_percent")
    if isinstance(ram_used, (int, float)) and ram_used > THRESHOLDS["ram_used"]:
        alerts.append(f"🧠 High RAM usage detected: {ram_used}%")

    # Storage check
    stor_used = data.get("full_storage", {}).get("used_percent")
    if isinstance(stor_used, (int, float)) and stor_used > THRESHOLDS["storage_used"]:
        alerts.append(f"💾 High storage usage detected: {stor_used}%")

    return alerts

# --- Socket Client Handler ---
def handle_client(conn, addr):
    with conn:
        try:
            text = conn.recv(4096).decode().strip()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"[{addr}] ⚠ Invalid JSON: {text}")
                return

            ts = datetime.datetime.now().isoformat()
            print(f"\n[{ts}] Data from {addr}:\n{json.dumps(data, indent=2)}")

            # Thread-safe update of latest_data
            global latest_data
            with latest_data_lock:
                latest_data = data.copy()
                latest_data['last_updated'] = ts  # Add timestamp
            print(f"in client thread: latest_data: {latest_data}")

            # Check for alerts
            alerts = check_alerts(data, addr)
            for a in alerts:
                alert_message = f"{ts} | {addr} | {a}"
                with alerts_lock:
                    alerts_log.append(alert_message)
                print(f"❗ ALERT: {alert_message}")

                # --- WhatsApp Alert ---
                try:
                    # Use device_id from data if available, else fallback to IP
                    device_id = data.get("device_id", f"Device-{addr[0]}")
                    emoji = a.split()[0]
                    message_text = a.split(":", 1)[1].strip()

                    whatsapp_message = (
                        f"{emoji} *System Alert*\n"
                        f"Device ID: `{device_id}`\n"
                        f"{message_text}.\n"
                        f"Please take necessary action immediately to avoid disruption.\n"
                        f"— Monitoring System"
                    )

                    now = dt.datetime.now()
                    hour = now.hour
                    minute = now.minute + 1

                    kit.sendwhatmsg(
                        "+917219371901",  # 🔁 Replace with your WhatsApp number
                        whatsapp_message,
                        hour,
                        minute,
                        wait_time=10,
                        tab_close=True
                    )
                    print("📲 WhatsApp alert sent.")
                    
                except Exception as e:
                    print(f"❌ Failed to send WhatsApp alert: {e}")

        except Exception as e:
            print(f"Error handling client {addr}: {e}")

# --- Start Socket Server ---
def start_socket_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", PORT))
        s.listen()
        print(f"🚀 Socket server listening on port {PORT}")

        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
    except Exception as e:
        print(f"Error starting socket server: {e}")

# --- Flask Routes ---
@app.route("/")
def index():
    with latest_data_lock:
        data_copy = latest_data.copy()
    with alerts_lock:
        recent_alerts = alerts_log[-10:]
    return render_template("index.html", active_page="dashboard", data=data_copy, alerts=recent_alerts)

@app.route("/devices")
def devices():
    with latest_data_lock:
        data_copy = latest_data.copy()
    return render_template("devices.html", active_page="devices", data=data_copy)

@app.route("/logs")
def logs():
    with alerts_lock:
        log_copy = alerts_log.copy()
    return render_template("logs.html", active_page="logs", alerts=log_copy)

@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings", thresholds=THRESHOLDS)

@app.route("/data")
def get_data():
    with latest_data_lock:
        data_copy = latest_data.copy()
    with alerts_lock:
        recent_alerts = alerts_log[-10:]
    print("in /data route: latest_data:", data_copy)
    return jsonify({
        "data": data_copy,
        "alerts": recent_alerts,
        "status": "success"
    })

@app.route("/update_thresholds", methods=['POST'])
def update_thresholds():
    global THRESHOLDS
    try:
        data = request.get_json()
        if data:
            THRESHOLDS.update(data)
            return jsonify({"status": "success", "thresholds": THRESHOLDS})
        return jsonify({"status": "error", "message": "No data provided"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- Entry Point ---
if __name__ == "__main__":
    threading.Thread(target=start_socket_server, daemon=True).start()
    app.run(debug=False, port=5000, use_reloader=False)
