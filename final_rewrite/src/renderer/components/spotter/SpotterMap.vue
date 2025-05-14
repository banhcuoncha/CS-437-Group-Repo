<template>
  <div :id="mapId" class="h-96 w-full rounded border border-gray-300"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, shallowRef, useId, watch } from 'vue';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { PropType } from 'vue';
//import planeUrl from '../icons/aircraft.png';
const mapId = useId();
const map = shallowRef<L.Map | null>(null);
const currentMarker = shallowRef<L.CircleMarker | null>(null);

// plane icon
// const planeIcon = L.icon({
//   iconUrl: planeUrl,
//   iconSize: [32,32],
//   iconAnchor: [16,16],
//   popupAnchor: [0,-16],
// })
const props = defineProps({
  markers: {
    type: Object,
    default: () => new Map(),
    //validator: value => value instanceof Map
  },
  currentPosition: {
    type: Object as PropType<{ lat: number; lon: number }>,
    default: () => ({ lat: 40.103, lon: -88.224 }),
    validator: (v: any) =>
      v != null &&
      typeof v.lat === 'number' &&
      typeof v.lon === 'number'
  }
  
});

defineExpose({
  highlightMarker,
  unhighlightMarker,
  map,
  centerOnCurrent
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

// New watch block for curPos
watch(
  () => props.currentPosition,
  (pos) => {
    if (!map.value) return;
    // remove old one
    if (currentMarker.value) {
      map.value.removeLayer(currentMarker.value);
      currentMarker.value = null;
    }
    // add new one
    if (pos && typeof pos.lat === 'number' && typeof pos.lon === 'number') {
      
      currentMarker.value = L.circleMarker([pos.lat, pos.lon], {
        radius: 8
      }).addTo(map.value);

    }
  },
  { immediate: true }
);

function centerOnCurrent() {
  const pos = props.currentPosition;
  if (map.value && pos) {
    map.value.setView([pos.lat, pos.lon], 20);
  }
}


function updateCurrentMarker(pos: { lat: number; lon: number } | null) {
  if (!map.value) return;
  // remove old
  if (currentMarker.value) {
    map.value.removeLayer(currentMarker.value);
    currentMarker.value = null;
  }
  // add new
  if (pos) {
    const m = L.circleMarker([pos.lat, pos.lon], { radius: 8 })
      .addTo(map.value);
    currentMarker.value = m;
  }
}
function highlightMarker(marker: any) {
  marker.openPopup();
  map.value?.setView(marker.getLatLng(), 10);
}

function unhighlightMarker(marker: any) {
  marker.closePopup();
}

function initMap() {
  map.value = L.map(mapId, {
    center: [props.currentPosition.lat, props.currentPosition.lon],
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
  updateCurrentMarker(props.currentPosition);
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