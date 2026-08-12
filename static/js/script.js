const throttleThumb = document.getElementById('throttle');
const steeringThumb = document.getElementById('steering');
const throttleTrack = throttleThumb.parentElement;
const steeringTrack = steeringThumb.parentElement;

let throttle = 0;
let steering = 0;

let headlights = false;
let floodlights = false;

function renderControls() {
  // ---------- Throttle ----------
  const tRect = throttleTrack.getBoundingClientRect();
  const thumbHeight = throttleThumb.offsetHeight;
  const throttleTravel = tRect.height - thumbHeight;
  const throttleY = ((1 - throttle) / 2) * throttleTravel;
  throttleThumb.style.left = '50%';
  throttleThumb.style.top = `${throttleY + thumbHeight / 2}px`;

  // ---------- Steering ----------
  const sRect = steeringTrack.getBoundingClientRect();
  const thumbWidth = steeringThumb.offsetWidth;
  const steeringTravel = sRect.width - thumbWidth;
  const steeringX = ((steering + 1) / 2) * steeringTravel;
  steeringThumb.style.left = `${steeringX + thumbWidth / 2}px`;
  steeringThumb.style.top = '50%';
}

/* THROTTLE */
throttleTrack.addEventListener('pointerdown', startThrottle);

function startThrottle(e) {
  throttleTrack.setPointerCapture(e.pointerId);
  updateThrottle(e);
  throttleTrack.addEventListener('pointermove', updateThrottle);
  throttleTrack.addEventListener('pointerup', stopThrottle);
  throttleTrack.addEventListener('pointercancel', stopThrottle);
}

function updateThrottle(e) {
  const rect = throttleTrack.getBoundingClientRect();
  const thumbHalf = throttleThumb.offsetHeight / 2;

  let y = e.clientY - rect.top;
  y = Math.max(thumbHalf, Math.min(rect.height - thumbHalf, y));

  const travel = rect.height - throttleThumb.offsetHeight;

  let value = 1 - ((y - thumbHalf) / travel) * 2;
  throttle = value;

  renderControls();
  sendControls();
}

function stopThrottle(e) {
  throttleTrack.releasePointerCapture(e.pointerId);
  throttleTrack.removeEventListener('pointermove', updateThrottle);
  throttleTrack.removeEventListener('pointerup', stopThrottle);
  throttleTrack.removeEventListener('pointercancel', stopThrottle);

  // Magnetic spring back to zero
  throttle = 0;
  renderControls();
  sendControls();
}

/* STEERING */
steeringTrack.addEventListener('pointerdown', startSteering);

function startSteering(e) {
  steeringTrack.setPointerCapture(e.pointerId);
  updateSteering(e);
  steeringTrack.addEventListener('pointermove', updateSteering);
  steeringTrack.addEventListener('pointerup', stopSteering);
  steeringTrack.addEventListener('pointercancel', stopSteering);
}

function updateSteering(e) {
  const rect = steeringTrack.getBoundingClientRect();
  const thumbHalf = steeringThumb.offsetWidth / 2;

  let x = e.clientX - rect.left;
  x = Math.max(thumbHalf, Math.min(rect.width - thumbHalf, x));

  const travel = rect.width - steeringThumb.offsetWidth;

  let value = ((x - thumbHalf) / travel) * 2 - 1;
  steering = value;

  renderControls();
  sendControls();
}

function stopSteering(e) {
  steeringTrack.releasePointerCapture(e.pointerId);
  steeringTrack.removeEventListener('pointermove', updateSteering);
  steeringTrack.removeEventListener('pointerup', stopSteering);
  steeringTrack.removeEventListener('pointercancel', stopSteering);

  steering = 0;
  renderControls();
  sendControls();
}

/* UTILITIES */
function resetControls() {
  throttle = 0;
  steering = 0;
  renderControls();
  sendControls();
}

window.addEventListener('resize', renderControls);

renderControls();

function toggleHeadlights() {
  headlights = !headlights;
  document.getElementById('lightsBtn').classList.toggle('active', headlights);
  sendControls();
}

function toggleFloodlights() {
  floodlights = !floodlights;
  document.getElementById('floodBtn').classList.toggle('active', floodlights);
  sendControls();
}

document.getElementById('stopBtn').addEventListener('click', resetControls);

document
  .getElementById('lightsBtn')
  .addEventListener('click', toggleHeadlights);

document
  .getElementById('floodBtn')
  .addEventListener('click', toggleFloodlights);

function updateStateFromServer(state) {
  if (state.throttle !== undefined) throttle = state.throttle;
  if (state.steering !== undefined) steering = state.steering;
  if (state.headlights !== undefined) {
    headlights = state.headlights;
    const lightsBtn = document.getElementById('lightsBtn');
    if (lightsBtn) lightsBtn.classList.toggle('active', headlights);
  }
  if (state.floodlights !== undefined) {
    floodlights = state.floodlights;
    const floodBtn = document.getElementById('floodBtn');
    if (floodBtn) floodBtn.classList.toggle('active', floodlights);
  }
  renderControls();
}
