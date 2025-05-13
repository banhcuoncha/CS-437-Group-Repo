<template>
  <div
    :class="[
      'p-3 rounded transition-all duration-200 cursor-pointer border',
      isHighlighted
        ? 'bg-blue-50 shadow-md border-blue-300'
        : 'bg-white shadow hover:shadow-md border-gray-200'
    ]"
    @click="$emit('highlight', flight.hex)"
  >
    <h3 class="font-medium text-blue-600 text-sm">{{ flight.flight || 'Unknown Flight [' + flight.hex + ']' }}</h3>

    <div class="mt-2">
      <p class="text-xs font-semibold uppercase text-gray-500 mb-0.5">Flight Details</p>
      <div class="border-t border-gray-100 pt-1">
        <div class="flex flex-wrap gap-x-3 gap-y-1">
          <div class="flex items-center text-xs py-0.5">
            <span class="px-1.5 py-0.5 rounded text-xs font-medium mr-1 bg-green-100 text-green-800">ALT</span>
            <span class="text-gray-600">{{ flight.altitude.toLocaleString() }} ft</span>
          </div>
          <div class="flex items-center text-xs py-0.5">
            <span class="px-1.5 py-0.5 rounded text-xs font-medium mr-1 bg-green-100 text-green-800">SPD</span>
            <span class="text-gray-600">{{ flight.speed }} kts</span>
          </div>
          <div class="flex items-center text-xs py-0.5">
            <span class="px-1.5 py-0.5 rounded text-xs font-medium mr-1 bg-green-100 text-green-800">TRK</span>
            <span class="text-gray-600">{{ flight.track }}°</span>
          </div>
          <div class="flex items-center text-xs py-0.5">
            <span class="px-1.5 py-0.5 rounded text-xs font-medium mr-1 bg-green-100 text-green-800">RSSI</span>
            <span class="text-gray-600">{{ flight.rssi }} dBm</span>
          </div>
          <div class="flex items-center text-xs py-0.5">
            <span class="px-1.5 py-0.5 rounded text-xs font-medium mr-1 bg-green-100 text-green-800">TYPE</span>
            <span class="text-gray-600">{{ flight.type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Flight {
  altitude: number;
  flight: string;
  hex: string;
  lat: number;
  lon: number;
  messages: number;
  rssi: number;
  seen: number;
  seen_pos: number;
  speed: number;
  track: number;
  type: string;
}

const props = defineProps<{
  flight: Flight;
  isHighlighted?: boolean;
}>();

defineEmits<{
  (e: 'highlight', flightId: string): void;
}>();

</script>
