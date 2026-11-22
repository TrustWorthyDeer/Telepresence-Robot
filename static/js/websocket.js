let controlWS = null;
let heartbeatInterval = null;
let serverClockOffset = null;
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
    serverClockOffset = null;
    controlWS.send(JSON.stringify({
      type: 'clock_sync',
      client_time: performance.now() / 1000,
    }));

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
    if (robotState.type === 'clock_sync') {
      const receivedAt = performance.now() / 1000;
      serverClockOffset =
        robotState.server_time -
        (robotState.client_time + receivedAt) / 2;
      return;
    }

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
  serverClockOffset = null;

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
  if (
    controlWS &&
    controlWS.readyState === WebSocket.OPEN &&
    serverClockOffset !== null
  ) {
    const payload = {
      throttle: throttle,
      steering: steering,
      headlights: headlights,
      floodlights: floodlights,
      sent_at: performance.now() / 1000 + serverClockOffset,
    };
    controlWS.send(JSON.stringify(payload));
  }
}
