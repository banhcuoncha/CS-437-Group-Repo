import asyncio
import json
import cv2
import argparse
import logging
import numpy as np
import socketio
from aiohttp import web
from aiohttp.web import middleware
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')

@middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Video source - either webcam or a video file
class VideoCamera:
    def __init__(self, device_id=0):
        self.camera = cv2.VideoCapture(device_id)
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    def __del__(self):
        self.camera.release()
        
    def get_frame(self):
        success, frame = self.camera.read()
        if not success:
            return None
        return frame

# Custom video track that sends frames from our camera
class CameraStreamTrack(VideoStreamTrack):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        
    async def recv(self):
        frame = self.camera.get_frame()
        
        if frame is None:
            # If camera failed to capture a frame, provide a blank one
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
        # Convert to RGB for VideoFrame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pts, time_base = await self.next_timestamp()
        
        # Create VideoFrame from numpy array
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

# Store active peer connections
pcs = set()

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    logging.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    logging.info(f"Message from {sid}: {data}")
    # Echo the message back
    await sio.emit('message', data, room=sid)

async def offer(request):
    """Handle WebRTC offer from client"""
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    # Create a video source
    camera = VideoCamera(1)  # 0 is usually the default webcam
    video_track = CameraStreamTrack(camera)
    
    # Add video track to peer connection
    pc.addTrack(video_track)
    
    # Handle ICE connection state
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logging.info(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed" or pc.iceConnectionState == "closed":
            await pc.close()
            pcs.discard(pc)
    
    # Handle peer connection closure
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logging.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)
    
    # Set the remote description (client's offer)
    await pc.setRemoteDescription(offer)
    
    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )

async def on_shutdown(app):
    """Close all peer connections when shutting down"""
    # Close all peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC video streaming server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5174, help="Port for HTTP server (default: 5173)")
    args = parser.parse_args()
    
    # Create web application with CORS middleware
    app = web.Application(middlewares=[cors_middleware])
    
    # Attach Socket.IO to the app
    sio.attach(app)
    
    # Add shutdown handler
    app.on_shutdown.append(on_shutdown)
    
    # Add only the /offer endpoint
    app.router.add_post("/offer", offer)
    
    # Add OPTIONS handler for CORS preflight requests
    async def options_handler(request):
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    app.router.add_route('OPTIONS', '/{tail:.*}', options_handler)
    
    # Start server
    web.run_app(app, host=args.host, port=args.port)
