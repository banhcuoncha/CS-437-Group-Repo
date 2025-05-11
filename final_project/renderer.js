let map, markerLayer;
const markerMap = new Map();
const cardMap = new Map();
// DOM elements
const statusEl = document.getElementById('status');
const fetchBtn = document.getElementById('fetchBtn');
const agencyInput = document.getElementById('agencyInput');
const incidentsContainer = document.getElementById('incidents');
const debugContent = document.getElementById('debugContent');
const debugToggle = document.getElementById('debugMode');
const debugPanel = document.getElementById('debugInfo');

// making use of the checked box Debug Mode
debugToggle.addEventListener('change', () => {
  debugPanel.style.display = debugToggle.checked ? 'block' : 'none';
});

// Display raw data
function displayRawData(data) {
  console.log('Raw data received:', data);
  
  // Always show the debug info for testing
  //document.getElementById('debugInfo').style.display = 'block';
  
  debugPanel.style.display = debugToggle.checked ? 'block' : 'none'

// Display the raw data structure
  const debugInfo = {
    dataType: typeof data,
    isArray: Array.isArray(data),
    hasIncidentsProperty: data && typeof data === 'object' && 'incidents' in data,
    incidentsCount: data && typeof data === 'object' && 'incidents' in data ? 
      (Array.isArray(data.incidents) ? data.incidents.length : 'Not an array') : 'N/A',
    rawData: JSON.stringify(data, null, 2)
  };
  
  debugContent.textContent = JSON.stringify(debugInfo, null, 2);
  
  // Clear old incidenet cards
  const cards = incidentsContainer.querySelectorAll('.incident-card, .loading, div');
  cards.forEach(el => el.remove());

  // // Clear existing content
  // incidentsContainer.innerHTML = '';
  
  // // Create a simple pre element to display the raw data
  // const rawDataElement = document.createElement('pre');
  // rawDataElement.style.whiteSpace = 'pre-wrap';
  // rawDataElement.style.overflow = 'auto';
  // rawDataElement.style.maxHeight = '500px';
  // rawDataElement.style.backgroundColor = '#f5f5f5';
  // rawDataElement.style.padding = '10px';
  // rawDataElement.style.borderRadius = '4px';
  
  // // Add the raw data
  // rawDataElement.textContent = JSON.stringify(data, null, 2);
  
  // // Add to DOM
  // incidentsContainer.appendChild(rawDataElement);
  
  // Also try to extract and display incidents in a simple format if they exist
  let incidents = [];
  
  if (Array.isArray(data?.incidents)) {
    incidents = data.incidents.flat(); // flatten nested arrays
  } else if (data && data.incidents && typeof data.incidents === 'object') {
    incidents = Object.values(data.incidents);
  }
  
  if (incidents.length > 0) {
    const incidentsCountEl = document.createElement('div');
    incidentsCountEl.textContent = `Found ${incidents.length} incidents`;
    incidentsCountEl.style.fontWeight = 'bold';
    incidentsCountEl.style.margin = '15px 0';
    incidentsContainer.appendChild(incidentsCountEl);
    incidentsReader(incidents)
  }
}

function incidentsReader(incidents) {

  if (markerLayer) {
    markerLayer.clearLayers();
  }
  incidents.forEach((incident) => {
    const lat = parseFloat(incident.Latitude);
    const lon = parseFloat(incident.Longitude);

    if (!isNaN(lat) && !isNaN(lon)) {
      const marker = L.marker([lat, lon])
      .bindPopup(`<strong>${incident.PulsePointIncidentCallType} (${incident.ID})</strong><br>${incident.MedicalEmergencyDisplayAddress}`)
      .on('click', () => {
        const card = cardMap.get(incident.ID);
        if (card) {
          // Remove highlight from any previous card
          document.querySelectorAll('.incident-card.highlighted').forEach(el => el.classList.remove('highlighted'));

          // Add highlight to this one
          card.classList.add('highlighted');

          // Scroll to it smoothly
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
      markerLayer.addLayer(marker);
      // Save marker to map with incidentID
      markerMap.set(incident.ID, marker);
      
    }
    const card = document.createElement('div');
    card.classList.add('incident-card');
    card.style.border = '1px solid #ccc';
    card.style.padding = '10px';
    card.style.marginBottom = '15px';
    card.style.borderRadius = '5px';
    card.style.backgroundColor = '#fff';
    

    const title = document.createElement('h4');
    title.textContent = `Incident: ${incident.PulsePointIncidentCallType || 'Unknown'} (${incident.ID})`;

    const address = document.createElement('p');
    address.innerHTML = `<strong>Address:</strong> ${incident.MedicalEmergencyDisplayAddress || 'N/A'}`;

    const received = document.createElement('p');
    received.innerHTML = `<strong>Received:</strong> ${new Date(incident.CallReceivedDateTime).toLocaleString()}`;

    const unitsList = document.createElement('ul');
    (incident.Unit || []).forEach(unit => {
      const li = document.createElement('li');
      li.textContent = `${unit.UnitID} - Status: ${unit.PulsePointDispatchStatus}${unit.UnitClearedDateTime ? ` (Cleared: ${new Date(unit.UnitClearedDateTime).toLocaleTimeString()})` : ''}`;
      unitsList.appendChild(li);
    });

    card.appendChild(title);
    card.appendChild(address);
    card.appendChild(received);
    if (unitsList.children.length > 0) {
      const unitLabel = document.createElement('p');
      unitLabel.innerHTML = '<strong>Units:</strong>';
      card.appendChild(unitLabel);
      card.appendChild(unitsList);
    }
    // Adding click listener so that the marker is highlighted when a card is clicked on
    card.addEventListener('click', () => {
      const marker = markerMap.get(incident.ID);
      if (marker) {
        marker.openPopup();
        map.setView(marker.getLatLng(), 15); // zoom to marker
      }
    });
    cardMap.set(incident.ID,card)
    incidentsContainer.appendChild(card);
  });

  
}

// Fetch incidents data
async function fetchIncidents() {
  try {
    statusEl.textContent = 'Fetching incidents...';
    const agencyId = agencyInput.value.trim();
    
    // Log what's being requested
    console.log(`Fetching incidents for agency ID: ${agencyId}`);
    
    // Call the API
    const data = await window.pulsePointAPI.getIncidents(agencyId);
    
    // Log what we got back
    console.log('API response received:', data);
    
    if (data.error) {
      statusEl.textContent = `Error: ${data.error}`;
      return;
    }
    
    // Display the raw data
    displayRawData(data);
    
    statusEl.textContent = `Last updated: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Error fetching incidents:', error);
    statusEl.textContent = `Error: ${error.message}`;
    
    // Display the error in the incidents container
    incidentsContainer.innerHTML = `
      <div style="color: red; padding: 20px;">
        <h3>Error Occurred</h3>
        <p>${error.message}</p>
        <pre>${error.stack}</pre>
      </div>
    `;
  }
}

// Initialize listeners
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Leaflet map
  map = L.map('map').setView([40.11, -88.27], 12); // Center on Champaign area

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  markerLayer = L.layerGroup().addTo(map);

  console.log('Test renderer initialized');
  
  // Force debug info to always be visible
  document.getElementById('debugInfo').style.display = 'block';
  debugContent.textContent = 'Waiting for data...';
  
  // Listen for fetch button clicks
  fetchBtn.addEventListener('click', fetchIncidents);
  
  // Listen for incident updates from main process
  if (window.pulsePointAPI && window.pulsePointAPI.onIncidentsUpdated) {
    window.pulsePointAPI.onIncidentsUpdated((data) => {
      console.log('Received update from main process:', data);
      displayRawData(data);
      statusEl.textContent = `Data received from main process: ${new Date().toLocaleString()}`;
    });
  } else {
    console.error('pulsePointAPI not found or missing onIncidentsUpdated method');
  }
  
  // Fetch incidents on start
  fetchIncidents();
});

// Clean up when window unloads
window.addEventListener('beforeunload', () => {
  if (window.pulsePointAPI && window.pulsePointAPI.removeIncidentsListener) {
    window.pulsePointAPI.removeIncidentsListener();
  }
});
