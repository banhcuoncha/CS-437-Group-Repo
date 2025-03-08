<template>
  <div class="flex flex-col w-full gap-2">
    <div class="aspect-video w-full rounded-lg bg-gray-800 overflow-hidden">
      <video
        ref="videoRef"
        class="h-full w-full object-cover"
        autoplay
        playsinline
        muted
      />
    </div>
    <input
      v-model="remoteHost"
      type="text"
      placeholder="Remote Host URL"
      class="w-full rounded-lg px-4 py-3 bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none"
    />
    <button 
      @click="connectionState === 'connected' ? stopStream() : startStream()"
      :disabled="connectionState === 'connecting'"
      class="w-full rounded-lg px-4 py-3 font-semibold transition-colors duration-200"
      :class="{
        'bg-green-500 hover:bg-green-600': connectionState === 'disconnected',
        'bg-red-500 hover:bg-red-600': connectionState === 'connected',
        'bg-yellow-500 cursor-not-allowed': connectionState === 'connecting'
      }"
    >
      {{ 
        connectionState === 'connecting' 
          ? 'Connecting...' 
          : (connectionState === 'connected' ? 'Disconnect' : 'Connect') 
      }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

type ConnectionState = 'disconnected' | 'connecting' | 'connected';

const videoRef = ref<HTMLVideoElement | null>(null);
const peerConnection = ref<RTCPeerConnection | null>(null);
const connectionState = ref<ConnectionState>('disconnected');
const remoteHost = ref('http://localhost:5174');

const startStream = async () => {
  try {
    connectionState.value = 'connecting';

    const configuration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    };

    peerConnection.value = new RTCPeerConnection(configuration);
    const pc = peerConnection.value;

    pc.addEventListener('track', (event) => {
      console.log('Received track');
      if (event.track.kind === 'video' && videoRef.value) {
        videoRef.value.srcObject = event.streams[0];
      }
    });

    pc.addEventListener('iceconnectionstatechange', () => {
      console.log(`ICE connection state: ${pc.iceConnectionState}`);
      if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
        connectionState.value = 'connected';
      } else if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'closed') {
        connectionState.value = 'disconnected';
        stopStream();
      }
    });

    pc.addEventListener('connectionstatechange', () => {
      console.log(`Connection state: ${pc.connectionState}`);
    });

    const dataChannel = pc.createDataChannel('chat');
    dataChannel.onopen = () => console.log('Data channel is open');
    dataChannel.onclose = () => console.log('Data channel is closed');

    const offer = await pc.createOffer({
      offerToReceiveVideo: true,
      offerToReceiveAudio: false
    });

    await pc.setLocalDescription(offer);

    const response = await fetch(`${remoteHost.value}/offer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sdp: pc.localDescription?.sdp,
        type: pc.localDescription?.type
      })
    });

    const answer = await response.json();
    await pc.setRemoteDescription(new RTCSessionDescription(answer));

    console.log('WebRTC connection established');

  } catch (error) {
    console.error('Error starting stream:', error);
    connectionState.value = 'disconnected';
  }
};

const stopStream = async () => {
  if (peerConnection.value) {
    peerConnection.value.close();
    peerConnection.value = null;
  }

  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  
  connectionState.value = 'disconnected';
};

onUnmounted(() => {
  if (peerConnection.value) {
    peerConnection.value.close();
  }
});
</script>
