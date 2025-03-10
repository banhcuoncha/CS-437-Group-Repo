<template>
  <div class="flex flex-col w-full gap-2">
    <div class="w-full rounded-lg bg-gray-800 p-6">
      <h2 class="mb-4 text-xl font-bold">Telemetry Data</h2>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span>Forward:</span>
          <span class="font-mono">{{ telemetryData.forward ? 'Yes' : 'No' }}</span>
        </div>
        <div class="flex justify-between">
          <span>Camera Direction:</span>
          <span class="font-mono">{{ telemetryData.camera_dir.toFixed(0) }}</span>
        </div>
        <div class="flex justify-between">
          <span>Car Direction:</span>
          <span class="font-mono">{{ getTurningStatus() }} ({{ telemetryData.car_dir.toFixed(0) }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TelemetryData {
  car_dir: number;
  camera_dir: number;
  forward: boolean;
}

const props = defineProps<{
  telemetryData: TelemetryData;
}>();

const getTurningStatus = () => {
  if (props.telemetryData.car_dir < 0) {
    return 'Left';
  } else if (props.telemetryData.car_dir > 0) {
    return 'Right';
  } else {
    return 'Forward';
  }
}
</script>
