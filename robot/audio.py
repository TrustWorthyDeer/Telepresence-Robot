import asyncio
import fractions
import pyaudio
import av
from aiortc import MediaStreamTrack

# Audio configuration constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 960

# Shared PyAudio instance
p = pyaudio.PyAudio()

class I2SMicTrack(MediaStreamTrack):
    # Captures audio from the I2S microphone to send to the browser.
    kind = "audio"
    
    def __init__(self):
        super().__init__()
        self.stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                             input=True, frames_per_buffer=CHUNK)
        self.pts = 0

    async def recv(self):
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.stream.read, CHUNK, False)
        
        frame = av.AudioFrame(format='s16', layout='mono', samples=CHUNK)
        frame.sample_rate = RATE
        frame.planes[0].update(data)
        frame.pts = self.pts
        frame.time_base = fractions.Fraction(1, RATE)
        self.pts += CHUNK
        return frame

async def play_browser_audio(track):
    # Receives audio from the browser and plays it on the I2S amplifier.
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    output=True, frames_per_buffer=CHUNK)
    while True:
        try:
            frame = await track.recv()
            data = frame.to_ndarray().tobytes()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, stream.write, data)
        except Exception as e:
            print("Browser audio track closed.")
            break

def cleanup_audio():
    # Terminates the PyAudio instance cleanly.
    p.terminate()