<template>
  <div class="flex h-screen w-screen bg-gray-900 text-white">
    <!-- Left panel - Controls and Telemetry -->
    <div class="flex w-1/2 flex-col items-center justify-center p-8">
      <div class="w-full flex flex-col gap-8">
        <div class="w-full flex justify-center">
          <CarControlSteering :steering-direction="steeringDirection" />
        </div>
        <CarControlTelemetry :telemetryData="telemetryData" />
      </div>
    </div>

    <!-- Right panel - Video Feed -->
    <div class="flex w-1/2 items-center justify-center p-8">
      <CarControlVideo />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import CarControlSteering from "./CarControlSteering.vue";
import CarControlVideo from "./CarControlVideo.vue";
import CarControlTelemetry from "./CarControlTelemetry.vue";

interface SteeringDirection {
  up: boolean;
  left: boolean;
  down: boolean;
  right: boolean;
}

const steeringDirection = ref<SteeringDirection>({
  up: false,
  left: false,
  down: false,
  right: false,
});

const telemetryData = ref({
  distance: 0,
  speed: 0,
  time: 0,
});

const handleKeyDown = (e: KeyboardEvent) => {
  const key = e.key.toLowerCase();
  switch (key) {
    case "w":
      steeringDirection.value.up = true;
      break;
    case "a":
      steeringDirection.value.left = true;
      break;
    case "s":
      steeringDirection.value.down = true;
      break;
    case "d":
      steeringDirection.value.right = true;
      break;
  }
};

const handleKeyUp = (e: KeyboardEvent) => {
  const key = e.key.toLowerCase();
  switch (key) {
    case "w":
      steeringDirection.value.up = false;
      break;
    case "a":
      steeringDirection.value.left = false;
      break;
    case "s":
      steeringDirection.value.down = false;
      break;
    case "d":
      steeringDirection.value.right = false;
      break;
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
  window.removeEventListener("keyup", handleKeyUp);
});
</script>
