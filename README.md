<div align="center">
  <h1>🤖 WebRTC Telepresence Robot Controller</h1>
  <p>An ultra-low-latency, mobile-responsive WebRTC &amp; WebSocket control suite for Raspberry Pi telepresence robots.</p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&amp;logo=python&amp;logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/WebRTC-WHEP-333333?style=for-the-badge&amp;logo=webrtc&amp;logoColor=white" alt="WebRTC" />
    <img src="https://img.shields.io/badge/aiohttp-AsyncIO-2C5BB4?style=for-the-badge" alt="aiohttp" />
    <img src="https://img.shields.io/badge/Open%20Source-Yes-success?style=for-the-badge" alt="Open Source" />
    <img src="https://img.shields.io/badge/License-Non--Commercial-red?style=for-the-badge" alt="License" />
  </p>
</div>

<hr />

<h2>🌟 Key Features</h2>
<ul>
  <li>📹 <strong>Full 4:3 Uncropped Sensor Feed:</strong> Configured for native <code>1280x960 @ 30fps</code> camera capture to maximize vertical ground visibility ahead of the robot.</li>
  <li>🚀 <strong>Embedded MediaMTX Subprocess:</strong> The Python backend automatically manages, launches, and monitors the MediaMTX binary—no separate terminal processes required.</li>
  <li>⚡ <strong>Ultra-Low Latency Video &amp; Audio:</strong> Hardware-accelerated WebRTC (WHEP) video streaming and bidirectional WebSocket audio.</li>
  <li>📱 <strong>Mobile Dual-Thumb Cockpit UI:</strong> Touch-first joystick tracks with dynamic viewport notch handling (<code>dvh</code>) and custom landscape/portrait views.</li>
  <li>🔒 <strong>Single-Client Lockout:</strong> Hardware safety enforcement ensuring only one active driver can control the robot at a time.</li>
  <li>📡 <strong>10Hz Telemetry &amp; Safety Watchdog:</strong> Continuous WebSocket heartbeat loop that automatically halts motors if signal is lost.</li>
</ul>

<hr />

<h2>🛠 Hardware &amp; Architecture</h2>

<h3>Bill of Materials (BOM) &amp; Components</h3>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: rgba(255,255,255,0.05);">
      <th>Component</th>
      <th>Description</th>
      <th>Qty</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Main Controller</strong></td>
      <td>Raspberry Pi (4, 5, or Zero 2W) running Raspberry Pi OS (hosts web backend &amp; video server)</td>
      <td>1</td>
    </tr>
    <tr>
      <td><strong>Motor Controller</strong></td>
      <td>ESP32 Microcontroller (handles low-level PWM actuation &amp; hardware telemetry)</td>
      <td>1</td>
    </tr>
    <tr>
      <td><strong>Camera Module</strong></td>
      <td>Raspberry Pi Camera Module (Wide-angle recommended, capturing 1280x960 @ 30fps)</td>
      <td>1</td>
    </tr>
    <tr>
      <td><strong>Motor Driver</strong></td>
      <td>H-Bridge / DC Motor Driver Board connected to ESP32 PWM pins</td>
      <td>1</td>
    </tr>
    <tr>
      <td><strong>Power Monitoring</strong></td>
      <td>Voltage and current sensor modules wired to ESP32 analog/I2C inputs</td>
      <td>1 set</td>
    </tr>
    <tr>
      <td><strong>Power Supply</strong></td>
      <td>LiPo / Li-ion Battery pack with power distribution board</td>
      <td>1</td>
    </tr>
    <tr>
      <td><strong>Chassis</strong></td>
      <td>Telepresence / differential drive robot chassis and motors</td>
      <td>1 set</td>
    </tr>
  </tbody>
</table>

<h3>ESP32 Architecture &amp; Telemetry Bridge</h3>
<p>The system utilizes a hybrid controller topology:</p>
<ul>
  <li><strong>Motor Control Pipeline:</strong> The Raspberry Pi receives high-level user commands from the web UI and forwards motor vectors to the <strong>ESP32</strong>. The ESP32 translates these into precise hardware PWM signals for the motor driver.</li>
  <li><strong>Hardware Telemetry:</strong> The ESP32 continuously monitors battery charge percentage, voltage levels, and current draw, transmitting these telemetry metrics back upstream to the Raspberry Pi for dashboard integration.</li>
</ul>

<h3>Circuit Diagram &amp; Robot Photos</h3>
<p><em>[Insert schematic diagram here outlining Pi-to-ESP32 communication, motor driver wiring, and sensor integration.]</em></p>
<p><em>[Insert photos of the physical robot chassis and internal electronics bay here.]</em></p>

<hr />

<h2>📋 To Implement (Pending Hardware Integration)</h2>
<ul>
  <li><strong>ESP32-Pi Serial/UART Protocol:</strong> Finalize bi-directional packet framing over serial/USB to stream throttle/steering commands down and receive battery voltage/current metrics up.</li>
  <li><strong>GPIO &amp; Sensor Wiring:</strong> Complete physical assembly and circuit integration between the Raspberry Pi, ESP32, motor drivers, and power monitoring sensors.</li>
  <li><strong>Dashboard Telemetry Binding:</strong> Wire incoming battery charge, voltage, and current feedback payloads from the ESP32 backend into the web UI telemetry view.</li>
  <li><strong>Fail-Safe Watchdog Tuning:</strong> Calibrate the ESP32-side safety timeout to immediately cut motor power if communication from the Raspberry Pi is interrupted.</li>
</ul>

<hr />

<h2>📁 Repository Structure</h2>
<pre><code>├── app.py                  # Main entrypoint (launches MediaMTX &amp; HTTP/WS server)
├── config.py               # Application configuration parameters
├── mediamtx                # MediaMTX executable binary for Pi architecture
├── mediamtx.yml            # MediaMTX camera and streaming configuration
├── requirements.txt        # Minimal Python dependencies
├── LICENSE                 # Non-Commercial License (PolyForm Noncommercial 1.0.0)
├── THIRD_PARTY_LICENSES.md # MediaMTX and third-party attributions
├── index.html              # Mobile/Desktop Web Cockpit UI
├── robot/
│   ├── audio.py            # Audio streaming module
│   ├── state.py            # Robot state management
│   ├── watchdog.py         # Safety watchdog and heartbeat monitor
│   ├── webrtc.py           # WebRTC / WHEP stream handler
│   └── websocket.py        # Async Python WebSocket handler &amp; safety lock
└── static/
    ├── css/
    │   └── style.css       # Responsive touch layout &amp; viewport CSS
    └── js/
        ├── script.js       # Touch joystick UI logic
        ├── webrtc.js       # WHEP video &amp; WebSocket audio client
        └── websocket.js    # Telemetry connection &amp; heartbeat loop</code></pre>

<hr />

<h2>🚀 Installation &amp; Setup</h2>

<h3>1. Prerequisites</h3>
<ul>
  <li><strong>Hardware:</strong> Raspberry Pi (3B+, 4, 5, or Zero 2W) running Raspberry Pi OS.</li>
  <li><strong>Camera:</strong> Raspberry Pi Camera Module connected and enabled.</li>
  <li><strong>MediaMTX Binary:</strong> Ensure the <code>mediamtx</code> binary matching your Raspberry Pi architecture (e.g., <code>linux_arm64</code> or <code>linux_armv7</code>) is placed in the repository root directory and made executable:
    <pre><code>chmod +x mediamtx</code></pre>
  </li>
</ul>

<hr />

<h3>2. Install Dependencies</h3>
<ol>
  <li>
    Clone the repository to your Raspberry Pi:
    <pre><code>git clone https://github.com/YOUR_USERNAME/telepresence-robot.git
cd telepresence-robot</code></pre>
  </li>
  <li>
    Re-create a clean virtual environment and activate it:
    <pre><code>python3 -m venv venv
source venv/bin/activate</code></pre>
  </li>
  <li>
    Install required packages:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
</ol>

<hr />

<h3>3. Execution</h3>
<p>Run the main application script:</p>
<pre><code>python3 app.py</code></pre>

<blockquote>
  <p><strong>Note:</strong> Executing <code>app.py</code> automatically initializes and manages the background MediaMTX instance, starts the WebSockets control pipeline, and serves the browser UI.</p>
</blockquote>

<p>Once running, access the controller from any smartphone or computer on the same network:</p>
<pre><code>http://&lt;RASPBERRY_PI_IP&gt;:8080</code></pre>

<hr />

<h2>🤖 AI Assistance Disclaimer</h2>
<p>Portions of this codebase, documentation, and interface layout were developed with the assistance of artificial intelligence (AI) tools. The architecture, implementation, and logic have been reviewed and tested for use in this telepresence robot control system.</p>

<hr />

<h2>📜 License &amp; Usage Rights</h2>
<p>This project is licensed under the <strong>PolyForm Noncommercial License 1.0.0</strong>.</p>
<ul>
  <li><strong>Non-Commercial Use Only:</strong> You are free to view, modify, and run this code for personal, educational, or research purposes.</li>
  <li><strong>Commercial Restriction:</strong> Any commercial use, monetization, or incorporation into paid products/services is strictly prohibited.</li>
</ul>
<p>See the full text in the <a href="LICENSE.md">LICENSE</a> file. Third-party software licenses are acknowledged in <a href="THIRD_PARTY_LICENSES.md">THIRD_PARTY_LICENSES.md</a>.</p>
