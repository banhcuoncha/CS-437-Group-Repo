<template>
  <div class="flex flex-col w-full gap-2">
    <div class="w-full rounded-lg bg-gray-800 p-6">
      <h2 class="mb-4 text-xl font-bold">Telemetry Data</h2>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span>Battery:</span>
          <span class="font-mono">{{ (telemetryData.battery*100).toFixed(0) }}%</span>
        </div>
        <div class="flex justify-between">
          <span>Moving:</span>
          <span class="font-mono">{{ telemetryData.moving ? 'Yes' : 'No' }}</span>
        </div>
        <div class="flex justify-between">
          <span>Turning:</span>
          <span class="font-mono">{{ getTurningStatus() }} ({{ telemetryData.turning_angle.toFixed(0) }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TelemetryData {
  turning_angle: number;
  battery: number;
  moving: boolean;
}

const props = defineProps<{
  telemetryData: TelemetryData;
}>();

const getTurningStatus = () => {
  if (props.telemetryData.turning_angle < 0) {
    return 'Left';
  } else if (props.telemetryData.turning_angle > 0) {
    return 'Right';
  } else {
    return 'Forward';
  }
}
</script>
