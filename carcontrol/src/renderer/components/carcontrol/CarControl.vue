<template>
  <div class="flex flex-col h-screen w-screen bg-gray-900 text-white">
    <div class="flex flex-1">
      <!-- Left panel - Controls and Telemetry -->
      <div class="flex w-1/2 flex-col items-center justify-center p-8">
        <div class="w-full flex flex-col gap-8">
          <div class="w-full flex justify-center">
            <CarControlSteering 
              ref="steeringRef"
              :disabled="remoteInputFocused"
              @steering-change="handleSteeringChange" 
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
        class="flex-1 rounded-lg px-4 py-3 bg-gray-900 text-white border border-gray-700 focus:border-blue-500 focus:outline-none"
        @focus="handleInputFocus"
        @blur="remoteInputFocused = false"
      />
      <button 
        @click="toggleConnection"
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
import { ref } from "vue";
import CarControlSteering from "./CarControlSteering.vue";
import CarControlVideo from "./CarControlVideo.vue";
import CarControlTelemetry from "./CarControlTelemetry.vue";

interface SteeringDirection {
  up: boolean;
  left: boolean;
  down: boolean;
  right: boolean;
}

const steeringRef = ref<InstanceType<typeof CarControlSteering> | null>(null);

const telemetryData = ref({
  distance: 0,
  speed: 0,
  time: 0,
});

const remoteHost = ref('http://localhost:5174');
const remoteConnected = ref(false);
const remoteInputFocused = ref(false);

const handleInputFocus = () => {
  remoteInputFocused.value = true;
  steeringRef.value?.resetSteering();
};

const toggleConnection = () => {
  remoteConnected.value = !remoteConnected.value;
};

const handleSteeringChange = (direction: SteeringDirection) => {
  // Handle the steering change event here
  console.log('Steering changed:', direction);
  // You can send this to your backend or handle it however needed
};
</script>
