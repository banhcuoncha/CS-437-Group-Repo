import json
import threading
from typing import Optional

import asyncio
from ac_state import AutonomousCarState
import socketio

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import aiohttp_cors

import numpy as np
import cv2
from av import VideoFrame

class CameraStreamTrack(VideoStreamTrack):
    def __init__(self, state: AutonomousCarState):
        super().__init__()
        self.state = state
        
    async def recv(self):
        frame = self.state.video_read()

        if not isinstance(frame, np.ndarray):
            frame = np.zeros((640, 480, 3))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pts, time_base = await self.next_timestamp()
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

class AutonomousCarWeb(threading.Thread):
    def __init__(self, state: AutonomousCarState):
        super().__init__()

        self.state = state
        self.loop = asyncio.new_event_loop()

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

        self.webrtc_pcs = set()
        webrtc_route = self.app.router.add_post('/webrtc/offer', self._webrtc_handle_offer)
        self.cors.add(webrtc_route)
        
        self.app.on_shutdown.append(self._webrtc_cleanup())
        
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
        self.sio.attach(self.app)

        self.sio.on('connect', self._sio_on_connect)
        self.sio.on('disconnect', self._sio_on_disconnect)        

        self.sio.on('steering', self._sio_on_steering)

    def run(self):
        self.loop.create_task(self.setup())
        self.loop.create_task(self.send_telemetry())

        self.loop.run_forever()

    def __del__(self):
        self.loop.run_until_complete(self.app_runner.cleanup())

    async def setup(self, port=5174):
        await self.app_runner.setup()

        self.site = web.TCPSite(self.app_runner, port=port)
        await self.site.start()

        print(f'Web server started at port {port}')

    async def send_telemetry(self):
        while True:
            data = self.state.build_telemetry()

            await self.sio.emit('telemetry', data)
            await asyncio.sleep(0.5)

    async def _sio_on_connect(self, sid, environ):
        print('SocketIO Connected: ', sid)

    async def _sio_on_disconnect(self, sid):
        print('SocketIO Disconnected: ', sid)

    async def _sio_on_steering(self, sid, data):
        up, down, left, right = data['up'], data['down'], data['left'], data['right']
        q, e = data['q'], data['e']

        vert_dir = 0
        if up and not down:
            vert_dir = 1
        elif down and not up:
            vert_dir = -1
        
        horiz_dir = 0
        if right and not left:
            horiz_dir = 1
        elif left and not right:
            horiz_dir = -1

        pan_dir = 0
        if e and not q:
            pan_dir = 1
        elif q and not e:
            pan_dir = -1
        
        self.state.update_control(vert_dir, horiz_dir, pan_dir)

    async def _webrtc_handle_offer(self, request: web.Request):
        params = await request.json()
        offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

        pc = RTCPeerConnection()
        self.webrtc_pcs.add(pc)

        pc.addTrack(CameraStreamTrack(self.state))

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

# loop = asyncio.new_event_loop()
# ac_web = AutonomousCarWeb(loop)

# loop.create_task(ac_web.setup())

# async def loop_telemetry():
#     while True:
#         ac_web.emit_telemetry({'test': 'test'})
#         await asyncio.sleep(1)

# loop.create_task(loop_telemetry())

# loop.run_forever()
