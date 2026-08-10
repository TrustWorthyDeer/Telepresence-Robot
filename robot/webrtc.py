import json
import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
# from audio import I2SMicTrack, play_browser_audio

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    pc = RTCPeerConnection()

    # Listen for incoming tracks (Browser -> Pi)
    # @pc.on("track")
    # def on_track(track):
    #     if track.kind == "audio":
    #         print("Browser microphone connected!")
    #         asyncio.create_task(play_browser_audio(track))

    # Handle Signaling Handshake
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            
            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                
                await ws.send_json({
                    "type": "answer",
                    "sdp": pc.localDescription.sdp
                })

    await pc.close()
    return ws