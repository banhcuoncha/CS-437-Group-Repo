<template>
  <div class="grid grid-cols-3 gap-2">
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
defineProps<{
  steeringDirection: {
    up: boolean;
    left: boolean;
    down: boolean;
    right: boolean;
  };
}>();
</script>
