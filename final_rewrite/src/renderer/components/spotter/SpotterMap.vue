<template>
  <div :id="mapId" class="h-96 w-full rounded border border-gray-300"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, shallowRef, useId, watch } from 'vue';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const mapId = useId();
const map = shallowRef<L.Map | null>(null);

const props = defineProps({
  markers: {
    type: Object,
    default: () => [],
    validator: value => value instanceof Map
  }
});

defineExpose({
  highlightMarker,
  unhighlightMarker
});

const baseMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

const layers = ref<Record<string, L.LayerGroup>>({
  incident: L.layerGroup(),
  flight: L.layerGroup()
});

watch(() => props.markers, (markers, oldMarkers) => {
  if (oldMarkers) {
    for (const [markerId, marker] of oldMarkers) {
      if (!marker || markers.has(marker.id)) continue;

      layers.value[marker.type].removeLayer(marker.data);
    }
  }

  for (const [markerId, marker] of markers) {
    if (oldMarkers && layers.value[marker.type].hasLayer(marker.data)) continue;

    layers.value[marker.type].addLayer(marker.data);
  }
}, { deep: true, immediate: true });

function highlightMarker(marker: any) {
  marker.openPopup();
  map.value?.setView(marker.getLatLng(), 10);
}

function unhighlightMarker(marker: any) {
  marker.closePopup();
}

function initMap() {
  map.value = L.map(mapId, {
    center: [40.11, -88.27],
    zoom: 12,
    layers: [baseMap, ...Object.values(layers.value)]
  });

  L.control.layers({}, {
    'Incidents': layers.value.incident,
    'Flights': layers.value.flight
  }).addTo(map.value);
}

onMounted(() => {
  initMap();
});

onUnmounted(() => {
  if (map.value) {
    map.value.off();
    map.value.remove();
    map.value = null;
  }
});
</script>

<style>
@import 'leaflet/dist/leaflet.css';

.leaflet-container {
  font-family: inherit;
}

.leaflet-popup-content {
  margin: 10px;
}
</style>