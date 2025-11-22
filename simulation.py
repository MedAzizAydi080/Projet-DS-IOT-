import time
import random
import json
import paho.mqtt.client as mqtt
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.columns import Columns 

# --- CONFIGURATION ---
LOCAL_BROKER = "localhost"
LOCAL_PORT = 1883
TOPIC_TELEMETRY = "factory/generator/telemetry"
TOPIC_CONTROL = "factory/generator/control"

class HeavyGenerator:
    def __init__(self):
        # --- MOTION ---
        self.rpm = 0.0
        self.target_rpm = 1800.0 # Standard 60Hz Gen Speed
        self.vibration = 0.02
        
        # --- ELECTRICAL ---
        self.voltage_l1 = 220.0
        self.current_l1 = 0.0
        self.power_factor = 0.85
        self.power_output = 0.0 # kW
        
        # --- FLUIDS ---
        self.oil_pressure = 0.0 # Bar
        
        # --- STATE ---
        self.health = 100.0
        self.status = "STARTING"

    def update(self):
        # 1. RPM Inertia
        self.rpm += (self.target_rpm - self.rpm) * 0.02
        
        # 2. Electrical Physics
        base_load = 150.0 
        if self.rpm > 1000:
            self.current_l1 = base_load + random.uniform(-5, 5)
        else:
            self.current_l1 = 0
            
        self.voltage_l1 = 220.0 - (self.current_l1 * 0.01) + random.uniform(-0.5, 0.5)
        self.power_output = (self.voltage_l1 * self.current_l1 * self.power_factor) / 1000.0
        
        # 3. Fluid Physics
        self.oil_pressure = (self.rpm / 1800.0) * 5.5 + random.uniform(-0.1, 0.1)
        
        # 4. Vibration
        health_factor = (100 - self.health) / 10.0
        self.vibration = (self.rpm / 8000.0) + (random.uniform(0, 0.02) * health_factor)
        
        # 5. Random Degradation
        if self.status == "RUNNING" and random.random() > 0.99:
            self.health -= 0.2

    def emergency_brake(self):
        self.target_rpm = 0
        self.status = "EMERGENCY STOP"

# --- MQTT CALLBACKS ---
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        # Check for "1" (Ubidots) or "BRAKE"
        if "1" in payload or "BRAKE" in payload:
            gen.emergency_brake()
    except:
        pass

# --- VISUALIZATION ---
def generate_dashboard(gen):
    # ELECTRICAL TABLE
    elec_table = Table(title="⚡ ELECTRICAL OUTPUT", expand=True, border_style="yellow")
    elec_table.add_column("Metric")
    elec_table.add_column("Value")
    elec_table.add_row("Voltage L1", f"{gen.voltage_l1:.1f} V")
    elec_table.add_row("Current L1", f"{gen.current_l1:.1f} A")
    elec_table.add_row("Power", f"[bold yellow]{gen.power_output:.2f} kW[/]")

    # MECHANICAL TABLE
    mech_table = Table(title="⚙️ MECHANICAL / FLUIDS", expand=True, border_style="blue")
    mech_table.add_column("Metric")
    mech_table.add_column("Value")
    mech_table.add_row("RPM", f"{int(gen.rpm)}")
    mech_table.add_row("Vibration", f"{gen.vibration:.3f} G")
    mech_table.add_row("Oil Pressure", f"{gen.oil_pressure:.2f} Bar")
    mech_table.add_row("Health", f"[green]{gen.health:.1f}%[/]")
    
    status_color = "green" if gen.status == "RUNNING" else "red blink"
    
    return Group(
        Panel(f"STATUS: [{status_color}]{gen.status}[/{status_color}]", style="bold white"),
        Columns([Panel(elec_table), Panel(mech_table)])
    )

# --- MAIN LOOP ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message

try:
    client.connect(LOCAL_BROKER, LOCAL_PORT, 60)
    client.subscribe(TOPIC_CONTROL)
    
    # --- FIX ADDED HERE ---
    # Force the broker to forget the old "Emergency" signal on startup
    client.publish(TOPIC_CONTROL, "0", retain=True)
    # ----------------------
    
    client.loop_start()
except:
    print("Error connecting to Mosquitto. Is it running?")
    exit()

gen = HeavyGenerator()
gen.status = "RUNNING"

with Live(generate_dashboard(gen), refresh_per_second=4) as live:
    while True:
        gen.update()
        
        payload = {
            "rpm": int(gen.rpm),
            "vibration": round(gen.vibration, 4),
            "voltage": round(gen.voltage_l1, 1),
            "current": round(gen.current_l1, 1),
            "power": round(gen.power_output, 2),
            "oil_pressure": round(gen.oil_pressure, 2),
            "health": round(gen.health, 1),
            "status": gen.status
        }
        
        client.publish(TOPIC_TELEMETRY, json.dumps(payload))
        live.update(generate_dashboard(gen))
        time.sleep(0.25)