import json
from typing import Optional

import asyncio
import socketio

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import aiohttp_cors

import numpy as np
import cv2
from av import VideoFrame

class VideoCamera:
    def __init__(self, device_id=0):
        self.camera = cv2.VideoCapture(device_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    def __del__(self):
        self.camera.release()
        
    def get_frame(self):
        success, frame = self.camera.read()
        if not success:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        return frame

class CameraStreamTrack(VideoStreamTrack):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        
    async def recv(self):
        frame = self.camera.get_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pts, time_base = await self.next_timestamp()
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

class AutonomousCarWeb:
    def __init__(self, loop):
        self.loop = loop

        self.app = web.Application()
        self.app_runner = web.AppRunner(self.app)
        self.site: Optional[web.TCPSite] = None

        self.cors = aiohttp_cors.setup(self.app, defaults={
            '*': aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers='*',
                    allow_headers='*',
            )
        })

        self.camera = self._webrtc_setup_camera()

        self.webrtc_pcs = set()
        webrtc_route = self.app.router.add_post('/webrtc/offer', self._webrtc_handle_offer)
        self.cors.add(webrtc_route)
        
        self.app.on_shutdown.append(self._webrtc_cleanup())
        
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
        self.sio.attach(self.app)

        self.sio.on('connect', self._sio_on_connect)
        self.sio.on('disconnect', self._sio_on_disconnect)

    def __del__(self):
        self.loop.run_until_complete(self.app_runner.cleanup())

    async def setup(self, host='0.0.0.0', port=5174):
        await self.app_runner.setup()

        self.site = web.TCPSite(self.app_runner, host, port)
        await self.site.start()

        print(f'Web server started at http://{host}:{port}')

    def emit_telemetry(self, data: dict[str, any]):
        self.loop.create_task(self.sio.emit('telemetry', data))

    async def _sio_on_connect(self, sid, environ):
        print('SocketIO Connected: ', sid)

    async def _sio_on_disconnect(self, sid):
        print('SocketIO Disconnected: ', sid)

    def _webrtc_setup_camera(self):
        return VideoCamera(1)

    async def _webrtc_handle_offer(self, request: web.Request):
        params = await request.json()
        offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

        pc = RTCPeerConnection()
        self.webrtc_pcs.add(pc)

        pc.addTrack(CameraStreamTrack(self.camera))

        self._webrtc_setup_pc(pc)

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return web.Response(
            content_type='application/json',
            text=json.dumps({
                'sdp': pc.localDescription.sdp,
                'type': pc.localDescription.type
            })
        )
    
    def _webrtc_setup_pc(self, pc: RTCPeerConnection):
        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            if pc.iceConnectionState in ["failed", "closed"]:
                await pc.close()
                self.webrtc_pcs.discard(pc)
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if pc.connectionState in ["failed", "closed"]:
                await pc.close()
                self.webrtc_pcs.discard(pc)

    async def _webrtc_cleanup(self):
        await asyncio.gather(*[pc.close() for pc in self.webrtc_pcs])
        self.webrtc_pcs.clear()

loop = asyncio.new_event_loop()
ac_web = AutonomousCarWeb(loop)

loop.create_task(ac_web.setup())

async def loop_telemetry():
    while True:
        ac_web.emit_telemetry({'test': 'test'})
        await asyncio.sleep(1)

loop.create_task(loop_telemetry())

loop.run_forever()
