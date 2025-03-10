<template>
  <div class="flex flex-col h-screen w-screen bg-gray-900 text-white">
    <div class="flex flex-1">
      <!-- Left panel - Controls and Telemetry -->
      <div class="flex w-1/2 flex-col items-center justify-center p-8">
        <div class="w-full flex flex-col gap-8">
          <div class="w-full flex justify-center">
            <CarControlSteering 
              @steeringChange="handleSteeringUpdate" 
            />
          </div>
          <CarControlTelemetry :telemetryData="telemetryData" />
        </div>
      </div>

      <!-- Right panel - Video Feed -->
      <div class="flex w-1/2 items-center justify-center p-8">
        <CarControlVideo :remoteHost="remoteHost" :remoteConnected="remoteConnected" />
      </div>
    </div>

    <!-- Bottom bar with remote host input and connect button -->
    <div class="w-full p-4 bg-gray-800 flex gap-4">
      <input
        v-model="remoteHost"
        type="text"
        :disabled="remoteConnected"
        class="flex-1 rounded-lg px-4 py-3 bg-gray-900 text-white border border-gray-700 focus:border-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <button 
        @click="remoteConnected ? disconnectRemote() : connectRemote()"
        class="rounded-lg px-6 py-3 font-semibold transition-colors duration-200"
        :class="{
          'bg-green-500 hover:bg-green-600': !remoteConnected,
          'bg-red-500 hover:bg-red-600': remoteConnected
        }"
      >
        {{ remoteConnected ? 'Disconnect' : 'Connect' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import CarControlSteering, { SteeringDirection } from "./CarControlSteering.vue";
import CarControlVideo from "./CarControlVideo.vue";
import CarControlTelemetry, { TelemetryData } from "./CarControlTelemetry.vue";

import { io, Socket } from "socket.io-client";

const socket = ref<Socket | null>(null);

const telemetryData = ref<TelemetryData | null>({
  car_dir: 0,
  camera_dir: 0,
  forward: false
});

const remoteHost = ref('http://localhost:5174');
const remoteConnected = ref(false);

const handleTelemetryUpdate = (data: TelemetryData) => {
  console.log('Received telemetry');
  telemetryData.value = data;
};

const handleSteeringUpdate = (direction: SteeringDirection) => {
  console.log('Steering changed:', direction);

  if (socket.value) {
    socket.value.emit('steering', direction);
  }
};

watch(socket, () => {
  if (!socket.value) {
    remoteConnected.value = false;
    return;
  }

  socket.value.on('telemetry', handleTelemetryUpdate);

  socket.value.on('connect', () => {
    console.log('Connected to socket server');
    remoteConnected.value = true;
  });

  socket.value.on('disconnect', () => {
    console.log('Disconnected from socket server');
    socket.value = null;
  });

  socket.value.on('connect_error', (error) => {
    console.error('Connection error:', error);
    socket.value = null;
  });
});

const disconnectRemote = () => {
  if (socket.value) {
    socket.value.disconnect();
    socket.value = null;
  }
}

const connectRemote = () => {
  disconnectRemote();

  try {
    socket.value = io(remoteHost.value, {
      reconnectionAttempts: 2
    });
  } catch (error) {
    console.error('Failed to create socket connection:', error);
  }
}
</script>
