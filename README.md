# 🏭 Industrial IoT Digital Twin: Smart Generator

![Project Status](https://img.shields.io/badge/Status-Active-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Node-RED](https://img.shields.io/badge/Node--RED-Edge-red?style=flat-square)
![Ubidots](https://img.shields.io/badge/Cloud-Ubidots-orange?style=flat-square)
![Security](https://img.shields.io/badge/Security-TLS%20v1.2-lock?style=flat-square)

## 📖 Overview

This project implements a secure, bi-directional **Industrial IoT Digital Twin** for a heavy 3-Phase Generator. It was developed for the **IoT & Cloud Computing** course (Fall 2025) to fulfill two key requirements:
1.  **Technical Implementation:** A complete Edge-to-Cloud data pipeline.
2.  **Comparative Study:** Demonstrating an architecture that bridges Data Visualization (Ubidots) and Edge Management concepts (simulated via Node-RED).

Instead of simple random data, this project uses a **Physics Engine** to simulate thermal inertia, voltage sag, and fluid dynamics. The data is processed by an **Intelligent Edge Gateway (Node-RED)** before being securely transmitted to the **Ubidots Cloud** via **MQTTS (TLS)**.

### 🎯 Key Features
* **Physics-Based Simulation:** Simulates RPM, Voltage, Power Factor, and Oil Pressure based on real mechanical laws using Python.
* **Intelligent Edge:** Node-RED gateway performs local anomaly detection (e.g., *Critical Oil Leak* when RPM > 500 and Pressure < 2.0 Bar) before transmission.
* **Zero-Trust Security:** All cloud traffic is encrypted using **TLS v1.2 on Port 8883**.
* **Cloud Analytics:** Ubidots calculates "Synthetic Variables" (Revenue €, Torque Nm) from raw telemetry.
* **Active Control (Downlink):** Remote "Emergency Stop" switch capable of shutting down the local physics engine in <1 second.

---

## 🏗 Architecture

The system follows a 3-Tier "Edge-to-Cloud" Architecture:

```mermaid
graph LR
    subgraph "Device Layer (OT)"
    A[Python Physics Engine] -- JSON / MQTT :1883 --> B[Local Broker]
    end

    subgraph "Edge Layer (IT)"
    B -- MQTT --> C[Node-RED Gateway]
    C -- Edge AI Logic --> C
    end

    subgraph "Cloud Layer"
    C -- MQTTS / TLS :8883 --> D[Ubidots Platform]
    D -- Downlink CMD --> C
    C -- Control Signal --> A
    end