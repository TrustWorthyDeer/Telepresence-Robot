let controlWS = null;
let heartbeatInterval = null;
const telemetryDiv = document.getElementById('telemetry');

const connectOverlay = document.getElementById('connectOverlay');
const controlsPanel = document.getElementById('controlsPanel');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

connectBtn.addEventListener('click', connectRobot);
disconnectBtn.addEventListener('click', disconnectRobot);

function connectRobot() {
  telemetryDiv.innerText = 'Telemetry: Connecting...';

  controlWS = new WebSocket(`ws://${window.location.host}/ws/control`);

  controlWS.onopen = () => {
    console.log('[WS Control] Connected');

    // Toggle UI
    connectOverlay.classList.add('hidden');
    controlsPanel.classList.remove('hidden');
    disconnectBtn.classList.remove('hidden');

    requestAnimationFrame(() => {
      if (typeof renderControls === 'function') renderControls();
    });

    // Start WebRTC stream
    startWebRTC();

    // Heartbeat loop (100ms)
    heartbeatInterval = setInterval(sendControls, 100);
  };

  controlWS.onmessage = (event) => {
    const robotState = JSON.parse(event.data);
    // Sync UI with initial state received from Python server
    if (typeof updateStateFromServer === 'function') {
      updateStateFromServer(robotState);
    }
    if (telemetryDiv) {
      telemetryDiv.innerText = `Thr: ${robotState.throttle.toFixed(2)} | Str: ${robotState.steering.toFixed(2)}`;
    }
  };

  controlWS.onclose = (event) => {
    if (event.code === 1006 || event.wasClean === false) {
      alert(
        'Connection failed. Another client may already be controlling the robot.',
      );
    }
    disconnectRobot();
  };
}

function disconnectRobot() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }

  if (controlWS) {
    controlWS.onclose = null;
    controlWS.close();
    controlWS = null;
  }

  // Stop WebRTC stream
  stopWebRTC();

  // Reset controls & toggle UI
  if (typeof resetControls === 'function') resetControls();
  connectOverlay.classList.remove('hidden');
  controlsPanel.classList.add('hidden');
  disconnectBtn.classList.add('hidden');
  if (telemetryDiv) telemetryDiv.innerText = 'Telemetry: Disconnected';
}

function sendControls() {
  if (controlWS && controlWS.readyState === WebSocket.OPEN) {
    const payload = {
      throttle: throttle,
      steering: steering,
      headlights: headlights,
      floodlights: floodlights,
    };
    controlWS.send(JSON.stringify(payload));
  }
}
