<template>
  <div class="aspect-video w-full rounded-lg bg-gray-800 overflow-hidden">
    <video
      ref="videoRef"
      class="h-full w-full object-cover"
      autoplay
      playsinline
      muted
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const videoRef = ref<HTMLVideoElement | null>(null);
const stream = ref<MediaStream | null>(null);

const startVideoStream = async () => {
  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 }
      }
    });
    
    stream.value = mediaStream;
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream;
    }
  } catch (error) {
    console.error('Error accessing video stream:', error);
  }
};

onMounted(() => {
  startVideoStream();
});

onUnmounted(() => {
  // Clean up the video stream
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
  }
});
</script>
