# 🏎️ RPi-WebBot: Real-Time IoT Rover

A Python-based robotic platform built on **Raspberry Pi**, featuring a web interface for remote control, live camera streaming, and dual-input support (Web GUI + Bluetooth Gamepad).

![Python](https://img.shields.io/badge/python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=flat-square&logo=raspberry-pi&logoColor=white)

---

## 🖼️ Preview

<p align="center">
<img width="474" height="633" alt="Zrzut ekranu 2026-03-28 o 17 01 07" src="https://github.com/user-attachments/assets/876b3d43-a3d3-46fc-b68d-7c855832fb53" />
</p>


---

## ✨ Features

* **Dual Control System** – Drive the robot via a responsive **Flask Web Interface** (featuring mobile-optimized touch controls, hold-to-drive logic, and dynamic obstacle alerts) or a **Bluetooth Gamepad** (e.g., PS4/Xbox Wireless Controller) using the `evdev` library.
* **Live Video Streaming** – Low-latency MJPEG stream from **Picamera2**, integrated directly into the web dashboard.
* **Smart Collision Avoidance** – Ultrasonic sensor (HC-SR04) integration that automatically interrupts "Forward" movement if an obstacle is detected within 30cm (Gamepad) or 20cm (Web).
* **Multi-threaded Architecture** – Separate threads for the Flask web server, Gamepad event polling, and Camera frame processing to ensure smooth operation.
* **Hardware Interface** – Direct GPIO control for L298N/L293D motor drivers and ultrasonic distance sensors.

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask (Web Server)
* **Frontend:** HTML5, CSS3, Vanilla JS (Mobile touch events, asynchronous Fetch API)
* **Hardware Control:** `RPi.GPIO` for motor & sensor signals
* **Camera:** `picamera2` with MJPEG encoding and `Condition`-based frame synchronization
* **Input:** `evdev` for Linux input device handling (Gamepad support)
* **Math/Logic:** Coordinate-to-vector calculation for joystick movement mapping

## 🔌 Hardware Setup

| Component | Pin (GPIO Board) |
|-----------|------------------|
| Motor A (IN1, IN2) | 8, 10 |
| Motor B (IN3, IN4) | 38, 40 |
| HC-SR04 Trigger | 16 |
| HC-SR04 Echo | 18 |
| Camera | CSI Ribbon Cable |

## 🚀 Quick Start

1. **Clone the repository**


2. **Install dependencies:**

       pip install flask evdev rpi.gpio

3. **Run the application:**

       sudo python3 main.py
       
   *Note: `sudo` may be required for GPIO/evdev access.*

4. **Access the interface:**
   Open `http://<your_pi_ip>:8080` in your browser.

## 🕹️ Gamepad Mapping

The robot automatically searches for a connected "Wireless Controller". 

* **Left Stick (Y-axis):** Forward / Backward
* **Left Stick (X-axis):** Left / Right rotation
* **Deadzone:** 60 units (to prevent stick drift)

## 🛡️ Safety Mechanisms

* **Hardware Cleanup:** Calls `GPIO.cleanup()` on exit to prevent pin damage.
* **Timeout Handling:** The ultrasonic sensor includes a timeout to prevent the script from hanging if no echo is received.
