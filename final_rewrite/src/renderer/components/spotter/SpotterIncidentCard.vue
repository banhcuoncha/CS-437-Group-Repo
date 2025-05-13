<template>
  <div
    :class="[
      'p-3 rounded transition-all duration-200 cursor-pointer border',
      isHighlighted
        ? 'bg-blue-50 shadow-md border-blue-300'
        : 'bg-white shadow hover:shadow-md border-gray-200'
    ]"
    @click="$emit('highlight', incident.ID)"
  >
    <div class="flex justify-between">
      <h3 class="font-medium text-blue-600 text-sm">{{ incident.PulsePointIncidentCallType }}</h3>
      <span class="text-sm text-gray-500">{{ formatDate(incident.CallReceivedDateTime) }}</span>
    </div>
    <div class="flex justify-between text-sm text-gray-700 mt-1 mb-2">
      <span class="truncate" :title="incident.MedicalEmergencyDisplayAddress">
        {{ incident.MedicalEmergencyDisplayAddress }}
      </span>
      <span class="ml-2 text-gray-500 whitespace-nowrap">ID: {{ incident.ID }}</span>
    </div>

    <div v-if="incident.Unit?.length" class="mt-2">
      <p class="text-xs font-semibold uppercase text-gray-500 mb-0.5">Responding Units</p>
      <ul class="space-y-1 border-t border-gray-100 pt-1">
        <li
          v-for="unit in incident.Unit"
          :key="unit.UnitID"
          class="flex text-xs py-0.5"
        >
          <span
            class="px-1.5 py-0.5 rounded text-xs font-medium mr-2"
            :class="unit.UnitClearedDateTime ? 'bg-gray-100 text-gray-600' : 'bg-green-100 text-green-800'"
          >
            {{ unit.UnitID }}
          </span>
          <span
            :class="unit.UnitClearedDateTime ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ unit.PulsePointDispatchStatus }}
          </span>
          <span
            v-if="unit.UnitClearedDateTime"
            class="ml-auto italic text-gray-500"
          >
            {{ formatDate(unit.UnitClearedDateTime, true) }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  incident: any;
  isHighlighted?: boolean;
}>();

defineEmits<{
  (e: 'highlight', incidentId: string): void;
}>();

function formatDate(dateString: string, time = false): string {
  const date = new Date(dateString);

  return time ? date.toLocaleTimeString() : date.toLocaleDateString();
}
</script>
