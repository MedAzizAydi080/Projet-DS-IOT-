# 🚀 Run & Operations Guide

This guide explains how to install, run, control, and troubleshoot the Industrial IoT Digital Twin (Heavy Generator) project.

---
## 1. Prerequisites
- Python 3.10+
- Mosquitto (or any MQTT broker) on `localhost:1883`
- Node-RED running (http://localhost:1880)
- Ubidots account + API token (MQTT username for `industrial.api.ubidots.com:8883`)
- (Optional) Docker (for Mosquitto), `mosquitto-clients` tools

---
## 2. Clone & Python Environment
```bash
git clone <repo-url>
cd iot-ds
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---
## 3. Start Core Services
### A. Mosquitto (System Install)
```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```
### B. Mosquitto (Docker Alternative)
```bash
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto
```
### C. Node-RED
```bash
node-red
```
Access UI at: http://localhost:1880

---
## 4. Import Node-RED Flow
1. Open Node-RED UI
2. Menu (☰) > Import > Upload `flows.json`
3. Edit MQTT Out node targeting Ubidots:
   - Host: `industrial.api.ubidots.com`
   - Port: `8883`
   - Username: your Ubidots token
   - Password: (blank unless required)
   - Enable TLS
4. Deploy

---
## 5. Run the Simulation
```bash
source venv/bin/activate  # if not already
python simulation.py
```
Publishes ~4 Hz telemetry to `factory/generator/telemetry`.
Subscribes to `factory/generator/control` for emergency brake.
Displays a Rich dashboard (electrical + mechanical panels).

---
## 6. Emergency Brake / Control
Trigger via Ubidots downlink variable (mapped to `/v1.6/devices/heavy-generator/emergency-brake/lv`) or manually:
```bash
mosquitto_pub -h localhost -t factory/generator/control -m BRAKE
```
Any payload containing `1` or exactly `BRAKE` invokes `emergency_brake()`.

---
## 7. Topics Summary
| Topic | Direction | Purpose |
|-------|-----------|---------|
| `factory/generator/telemetry` | Python → Node-RED | Raw local telemetry |
| `/v1.6/devices/heavy-generator` | Node-RED → Ubidots | Enriched (alerts added) |
| `/v1.6/devices/heavy-generator/emergency-brake/lv` | Ubidots → Node-RED | Cloud control variable |
| `factory/generator/control` | Node-RED → Python | Brake command |

---
## 8. Edge Alert Logic (Node-RED Function)
| Condition | Alert |
|-----------|-------|
| vibration > 0.8 | CRITICAL VIBRATION |
| oil_pressure < 2.0 AND rpm > 500 | LOW OIL PRESSURE |
| voltage > 240 OR voltage < 200 | VOLTAGE UNSTABLE |
| otherwise | NORMAL |

---
## 9. Customization
- Physics tuning: edit `target_rpm`, degradation probability, add new metrics in `simulation.py`.
- Alert thresholds: modify Node-RED Function node.
- Add synthetic variables in Ubidots (e.g., torque, cost, efficiency).

---
## 10. Troubleshooting
| Symptom | Resolution |
|---------|------------|
| "Error connecting to Mosquitto" | Ensure broker running (`systemctl status mosquitto`) or Docker container healthy. |
| No telemetry in Node-RED | Check MQTT In topic; add Debug node. |
| No cloud data | Verify token, TLS enabled, port 8883 accessible. |
| Brake not working | Payload must contain `1` or `BRAKE`. |
| Vibration always high | Health degraded; restart simulation to reset. |
| Ubidots variables missing | Confirm device name matches topics. |

---
## 11. Security Notes
- Local link (1883) plaintext: enable TLS for production.
- Cloud leg already uses MQTTS (TLS).
- Avoid committing tokens; use environment vars or Node-RED credential store.

---
## 12. Project Files
```
flows.json        # Node-RED flow (ingest + processing + forward + control relay)
requirements.txt  # Python dependencies
simulation.py     # Physics simulation + MQTT publisher + control listener
RUN_GUIDE.md      # This run & operations guide
README.md         # High-level overview & architecture
venv/             # Virtual environment (after creation)
```

---
## 13. Next Enhancements
- docker-compose stack (Mosquitto + Node-RED + simulation)
- Prometheus exporter
- Temperature model + cooling curve
- Webhook/email alerts for critical states

---
## 14. Clean Exit
Stop with Ctrl+C. After brake, RPM target set to zero; loop continues publishing until you terminate.

---
Happy experimenting! ⚙️
