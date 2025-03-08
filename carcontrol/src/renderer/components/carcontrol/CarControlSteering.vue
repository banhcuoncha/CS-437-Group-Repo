<template>
  <div 
    class="grid grid-cols-3 gap-2"
    @keydown="handleKeyDown"
    @keyup="handleKeyUp"
    tabindex="0"
  >
    <!-- Empty cell -->
    <div></div>
    <!-- Up key (W) -->
    <div
      :class="[
        'flex h-16 w-16 items-center justify-center rounded border-2 font-bold',
        steeringDirection.up ? 'border-blue-400 bg-blue-600' : 'border-gray-600',
      ]"
    >
      W
    </div>
    <!-- Empty cell -->
    <div></div>
    <!-- Left key (A) -->
    <div
      :class="[
        'flex h-16 w-16 items-center justify-center rounded border-2 font-bold',
        steeringDirection.left ? 'border-blue-400 bg-blue-600' : 'border-gray-600',
      ]"
    >
      A
    </div>
    <!-- Down key (S) -->
    <div
      :class="[
        'flex h-16 w-16 items-center justify-center rounded border-2 font-bold',
        steeringDirection.down ? 'border-blue-400 bg-blue-600' : 'border-gray-600',
      ]"
    >
      S
    </div>
    <!-- Right key (D) -->
    <div
      :class="[
        'flex h-16 w-16 items-center justify-center rounded border-2 font-bold',
        steeringDirection.right ? 'border-blue-400 bg-blue-600' : 'border-gray-600',
      ]"
    >
      D
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface SteeringDirection {
  up: boolean;
  left: boolean;
  down: boolean;
  right: boolean;
}

const props = defineProps<{
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'steeringChange', direction: SteeringDirection): void;
}>();

const steeringDirection = ref<SteeringDirection>({
  up: false,
  left: false,
  down: false,
  right: false,
});

const resetSteering = () => {
  steeringDirection.value = {
    up: false,
    left: false,
    down: false,
    right: false,
  };
  emit('steeringChange', steeringDirection.value);
};

const handleKeyDown = (e: KeyboardEvent) => {
  if (props.disabled) return;
  
  const key = e.key.toLowerCase();
  let changed = false;

  switch (key) {
    case "w":
      if (!steeringDirection.value.up) {
        steeringDirection.value.up = true;
        changed = true;
      }
      break;
    case "a":
      if (!steeringDirection.value.left) {
        steeringDirection.value.left = true;
        changed = true;
      }
      break;
    case "s":
      if (!steeringDirection.value.down) {
        steeringDirection.value.down = true;
        changed = true;
      }
      break;
    case "d":
      if (!steeringDirection.value.right) {
        steeringDirection.value.right = true;
        changed = true;
      }
      break;
  }

  if (changed) {
    emit('steeringChange', steeringDirection.value);
  }
};

const handleKeyUp = (e: KeyboardEvent) => {
  if (props.disabled) return;
  
  const key = e.key.toLowerCase();
  let changed = false;

  switch (key) {
    case "w":
      if (steeringDirection.value.up) {
        steeringDirection.value.up = false;
        changed = true;
      }
      break;
    case "a":
      if (steeringDirection.value.left) {
        steeringDirection.value.left = false;
        changed = true;
      }
      break;
    case "s":
      if (steeringDirection.value.down) {
        steeringDirection.value.down = false;
        changed = true;
      }
      break;
    case "d":
      if (steeringDirection.value.right) {
        steeringDirection.value.right = false;
        changed = true;
      }
      break;
  }

  if (changed) {
    emit('steeringChange', steeringDirection.value);
  }
};

defineExpose({
  resetSteering
});
</script>
