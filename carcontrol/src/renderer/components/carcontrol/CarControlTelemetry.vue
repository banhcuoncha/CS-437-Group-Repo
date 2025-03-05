<template>
  <div class="w-64 rounded-lg bg-gray-800 p-6">
    <h2 class="mb-4 text-xl font-bold">Telemetry Data</h2>
    <div class="space-y-2">
      <div class="flex justify-between">
        <span>Distance Travelled:</span>
        <span class="font-mono">{{ telemetryData.distance }} m</span>
      </div>
      <div class="flex justify-between">
        <span>Current Speed:</span>
        <span class="font-mono">{{ telemetryData.speed }} km/h</span>
      </div>
      <div class="flex justify-between">
        <span>Time Elapsed:</span>
        <span class="font-mono">{{ telemetryData.time }} s</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TelemetryData {
  distance: number;
  speed: number;
  time: number;
}

defineProps<{
  telemetryData: TelemetryData;
}>();
</script>