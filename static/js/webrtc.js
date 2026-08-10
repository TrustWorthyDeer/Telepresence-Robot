let pcVideo = null;
let pcAudio = null;

async function startWebRTC() {
  const videoElement = document.getElementById('background-video');
  const audioElement = document.getElementById('audioElement');
  const statusDiv = document.getElementById('status');

  // 1. Video (WHEP)
  try {
    statusDiv.innerText = 'Status: Connecting Video...';
    pcVideo = new RTCPeerConnection();
    pcVideo.addTransceiver('video', { direction: 'recvonly' });

    pcVideo.ontrack = (event) => {
      videoElement.srcObject = event.streams[0];
    };

    const videoOffer = await pcVideo.createOffer();
    await pcVideo.setLocalDescription(videoOffer);

    const response = await fetch(
      `http://${window.location.hostname}:8889/cam/whep`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/sdp' },
        body: videoOffer.sdp,
      },
    );

    if (response.ok) {
      const videoAnswerSdp = await response.text();
      await pcVideo.setRemoteDescription({
        type: 'answer',
        sdp: videoAnswerSdp,
      });
    }
  } catch (err) {
    console.error('Video streaming error:', err);
  }

  // 2. Audio (WebSocket)
  try {
    statusDiv.innerText = 'Status: Connecting Audio...';
    const localStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false,
    });

    pcAudio = new RTCPeerConnection();
    pcAudio.addTransceiver('audio', { direction: 'sendrecv' });

    localStream
      .getTracks()
      .forEach((track) => pcAudio.addTrack(track, localStream));
    pcAudio.ontrack = (event) => {
      audioElement.srcObject = event.streams[0];
    };

    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = async () => {
      const audioOffer = await pcAudio.createOffer();
      await pcAudio.setLocalDescription(audioOffer);
      ws.send(
        JSON.stringify({ type: 'offer', sdp: pcAudio.localDescription.sdp }),
      );
    };

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'answer') {
        await pcAudio.setRemoteDescription(
          new RTCSessionDescription({ type: data.type, sdp: data.sdp }),
        );
        statusDiv.innerText = 'Status: Connected';
      }
    };
  } catch (err) {
    console.error('Audio streaming error:', err);
    statusDiv.innerText = 'Status: Connected (Video Only)';
  }
}

function stopWebRTC() {
  if (pcVideo) {
    pcVideo.close();
    pcVideo = null;
  }
  if (pcAudio) {
    pcAudio.close();
    pcAudio = null;
  }
  document.getElementById('background-video').srcObject = null;
  document.getElementById('status').innerText = 'Status: Disconnected';
}
