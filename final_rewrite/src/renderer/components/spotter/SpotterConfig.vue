<template>
  <div class="flex items-center gap-3 flex-wrap">
    <div class="flex items-center">
      <label for="agencyId" class="mr-1">Agency ID:</label>
      <input
        type="text"
        id="agencyId"
        placeholder="Agency ID"

        :value="agencyId"
        @input="emit('update:agencyId', $event.target.value)"

        class="p-2 border border-gray-300 rounded"
      >
    </div>

    <div class="flex items-center">
      <input
        type="checkbox"
        id="autoRefresh"

        :checked="autoRefresh"
        @change="emit('update:autoRefresh', $event.target.checked)"

        class="mr-1"
      >
      <label for="autoRefresh" class="mr-1">Auto-refresh</label>
      <select
        :value="autoRefreshInterval"
        
        class="p-1 border border-gray-300 rounded"
      >
        <option
          v-for="option in autoRefreshOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  agencyId: {
    type: String,
    default: 'EMS1174'
  },
  autoRefresh: {
    type: Boolean,
    default: true
  },
  autoRefreshInterval: {
    type: Number,
    default: 60
  },
  autoRefreshOptions: {
    type: Array,
    default: () => [
      { value: 30, label: '30 seconds' },
      { value: 60, label: '1 minute' },
      { value: 300, label: '5 minutes' }
    ]
  }
});

const emits = defineEmits(['update:agencyId', 'update:autoRefresh', 'update:autoRefreshInterval']);


</script>