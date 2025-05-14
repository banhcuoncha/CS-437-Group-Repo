<template>
  <div class="mx-auto p-5 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-semibold text-gray-600 mb-4">PulsePoint Incidents</h1>

    <div class="space-y-4 mb-5">
      <SpotterConfig
        v-model:agencyId="agencyId"
        v-model:autoRefresh="autoRefresh"
        v-model:autoRefreshInterval="autoRefreshInterval"

        v-model:autoRefreshOptions="autoRefreshOptions"
      />

      <div class="flex items-center gap-4">
        <button
          @click="fetchIncidents"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Fetch Incidents
        </button>

        <button
          @click="setMapLocationToCurrent"
          class = "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          To Current Location
        </button>
        <span class="italic text-gray-600">{{ status }}</span>
      </div>
    </div>

    <SpotterMap class="mb-5" ref="map" :markers="markers" :currentPosition="currentPosition"/>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="flex flex-col h-full">
        <h2 class="text-xl font-semibold text-gray-600 mb-4">Incidents ({{ incidents.length }})</h2>
        <div v-if="incidents.length === 0" class="text-center py-8 text-gray-600">
          No incidents loaded yet.
        </div>
        <div class="overflow-y-auto h-[calc(100vh-350px)] pr-2">
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-3">
            <SpotterIncidentCard
              v-for="incident in incidents"
              :key="incident.ID"
              :incident="incident"
              :is-highlighted="getIncidentMarkerId(incident.ID) === highlightedMarkerId"
              @highlight="highlightMarker(getIncidentMarkerId(incident.ID))"
            />
          </div>
        </div>
      </div>

      <div class="flex flex-col h-full">
        <h2 class="text-xl font-semibold text-gray-600 mb-4">Aircrafts ({{ flights.length }})</h2>
        <div v-if="flights.length === 0" class="text-center py-8 text-gray-600">
          No flights spotted yet.
        </div>
        <div class="overflow-y-auto h-[calc(100vh-350px)] pr-2">
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-3">
            <SpotterFlightCard
              v-for="flight in flights"
              :key="flight.hex"
              :flight="flight"
              :is-highlighted="getFlightMarkerId(flight.hex) === highlightedMarkerId"
              @highlight="highlightMarker(getFlightMarkerId(flight.hex))"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Dummy coordinates - Remove this when you can -- Neil
const currentPosition = ref<{ lat: number; lon: number }>({
  lat: 40.10301,
  lon: -88.22494
});
// new function to center on current location
function setMapLocationToCurrent() {
  map.value?.centerOnCurrent?.()
}

import { computed, onMounted, reactive, ref, watch } from 'vue';

import SpotterConfig from './SpotterConfig.vue';
import SpotterMap from './SpotterMap.vue';
import SpotterIncidentCard from './SpotterIncidentCard.vue';
import SpotterFlightCard from './SpotterFlightCard.vue';

const defaultAgencyId = 'EMS1174';
const defaultAutoRefresh = true;
const defaultAutoRefreshInterval = 30;

const defaultStatus = 'Not yet updated.';

const agencyId = ref(defaultAgencyId);
const autoRefresh = ref(defaultAutoRefresh);
const autoRefreshInterval = ref(defaultAutoRefreshInterval);
const autoRefreshOptions = ref([
  { value: '30', label: '30 seconds' },
  { value: '60', label: '1 minute' },
  { value: '300', label: '5 minutes' }
]);

const status = ref(defaultStatus);

const autoRefreshEvent = ref<ReturnType<typeof setInterval> | null>(null);

const incidents = ref<any[]>([]);
const flights = ref<any[]>([]);

const markers = reactive(new Map());

const map = ref<InstanceType<typeof SpotterMap> | null>(null);

const highlightedMarkerId = ref<string | null>(null);

const incidentIndex = computed<Record<string, number>>(() => Object.fromEntries(
  incidents.value.map((incident, i) => [incident.ID, i])
));

watch(() => incidents, (newIncidents, oldIncidents) => {
  const newIncidentIds = new Set(newIncidents.value.map(incident => getIncidentMarkerId(incident.ID)));

  if (oldIncidents && oldIncidents.value) {
    for (const incident of oldIncidents.value) {
      if (!incident) continue;

      const id = getIncidentMarkerId(incident.ID);
      if (!newIncidentIds.has(id)) markers.delete(id);
    }

    for (const incident of incidents.value) {
      const id = getIncidentMarkerId(incident.ID);

      let marker = markers.get(id);

      const lat = parseFloat(incident.Latitude);
      const lon = parseFloat(incident.Longitude);

      if (isNaN(lat) || isNaN(lon)) continue;

      if (!marker) {
        marker = {
          id,
          type: 'incident',
          data: L.marker([lat, lon])
        };

        markers.set(id, marker);
      }

      marker.data.bindPopup(`<strong>${incident.PulsePointIncidentCallType} (${incident.ID})</strong><br>${incident.MedicalEmergencyDisplayAddress}`);

      marker.data.on('popupopen', () => {
        highlightedMarkerId.value = id;
      });

      marker.data.on('popupclose', () => {
        if (highlightedMarkerId.value === id) highlightedMarkerId.value = null;
      });
    }
  }
}, { deep: true, immediate: true });

watch(() => flights, (newFlights, oldFlights) => {
  const newFlightIds = new Set(newFlights.value.map(flight => getFlightMarkerId(flight.hex)));

  if (oldFlights && oldFlights.value) {
    for (const flight of oldFlights.value) {
      if (!flight) continue;

      const id = getFlightMarkerId(flight.hex);
      if (!newFlightIds.has(id)) markers.delete(id);
    }

    for (const flight of flights.value) {
      const id = getFlightMarkerId(flight.hex);

      let marker = markers.get(id);

      if (!marker) {
        marker = {
          id,
          type: 'flight',
          data: L.marker([flight.lat, flight.lon])
        };

        markers.set(id, marker);
      }

      marker.data.setLatLng([flight.lat, flight.lon]);

      marker.data.bindPopup(`<strong>${flight.flight || 'Unknown Flight [' + flight.hex + ']'} (${flight.hex})</strong><br>${flight.lat}, ${flight.lon}`);

      marker.data.on('popupopen', () => {
        highlightedMarkerId.value = id;
      });

      marker.data.on('popupclose', () => {
        if (highlightedMarkerId.value === id) highlightedMarkerId.value = null;
      });
    }
  }
}, { deep: true, immediate: true });

watch(() => [autoRefresh, autoRefreshInterval], () => {
  if (autoRefreshEvent.value) clearInterval(autoRefreshEvent.value);

  if (autoRefresh.value) {
    autoRefreshEvent.value = setInterval(() => {
      fetchIncidents();
    }, autoRefreshInterval.value * 1000);
  }
}, { deep: true, immediate: true });

function highlightMarker(markerId: string) {
  const marker = markers.get(markerId);
  if (!marker) return;

  if (highlightedMarkerId.value === markerId) {
    highlightedMarkerId.value = null;
    
    map.value?.unhighlightMarker(marker.data);
  } else {
    highlightedMarkerId.value = markerId;

    map.value?.highlightMarker(marker.data);
  }
}

function getIncidentMarkerId(id: string) {
  return `incidents-${id}`;
}

function getFlightMarkerId(id: string) {
  return `flights-${id}`;
}

async function fetchIncidents() {
  const data = await window.pulsepointService.getIncidents(agencyId.value);

  if (data.error) {
    status.value = `Error: ${data.error}`;
    return;
  }

  incidents.value = data.incidents.recent || [];
  status.value = `Last updated: ${new Date().toLocaleString()}`;
}

async function fetchAircrafts() {
  const data = await window.flightsService.getAircrafts();

  if (data.error) {
    status.value = `Error: ${data.error}`;
    return;
  }

  console.log(data.aircraft);

  flights.value = data.aircraft;
}

onMounted(() => {
  fetchIncidents();

  setInterval(() => {
    fetchAircrafts();
  }, 1000);
});
</script>
