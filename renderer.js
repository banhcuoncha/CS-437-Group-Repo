// DOM elements
const statusEl = document.getElementById('status');
const fetchBtn = document.getElementById('fetchBtn');
const agencyInput = document.getElementById('agencyInput');
const incidentsContainer = document.getElementById('incidents');
const debugContent = document.getElementById('debugContent');

// Display raw data
function displayRawData(data) {
  console.log('Raw data received:', data);
  
  // Always show the debug info for testing
  document.getElementById('debugInfo').style.display = 'block';
  
// Display the raw data structure
//   const debugInfo = {
//     dataType: typeof data,
//     isArray: Array.isArray(data),
//     hasIncidentsProperty: data && typeof data === 'object' && 'incidents' in data,
//     incidentsCount: data && typeof data === 'object' && 'incidents' in data ? 
//       (Array.isArray(data.incidents) ? data.incidents.length : 'Not an array') : 'N/A',
//     rawData: JSON.stringify(data, null, 2)
//   };
  
  debugContent.textContent = JSON.stringify(debugInfo, null, 2);
  
  // Clear existing content
  incidentsContainer.innerHTML = '';
  
  // Create a simple pre element to display the raw data
  const rawDataElement = document.createElement('pre');
  rawDataElement.style.whiteSpace = 'pre-wrap';
  rawDataElement.style.overflow = 'auto';
  rawDataElement.style.maxHeight = '500px';
  rawDataElement.style.backgroundColor = '#f5f5f5';
  rawDataElement.style.padding = '10px';
  rawDataElement.style.borderRadius = '4px';
  
  // Add the raw data
  rawDataElement.textContent = JSON.stringify(data, null, 2);
  
  // Add to DOM
  incidentsContainer.appendChild(rawDataElement);
  
  // Also try to extract and display incidents in a simple format if they exist
  let incidents = [];
  
  if (Array.isArray(data)) {
    incidents = data;
  } else if (data && data.incidents && Array.isArray(data.incidents)) {
    incidents = data.incidents;
  } else if (data && data.incidents && typeof data.incidents === 'object') {
    incidents = Object.values(data.incidents);
  }
  
  if (incidents.length > 0) {
    const incidentsCountEl = document.createElement('div');
    incidentsCountEl.textContent = `Found ${incidents.length} incidents`;
    incidentsCountEl.style.fontWeight = 'bold';
    incidentsCountEl.style.margin = '15px 0';
    incidentsContainer.appendChild(incidentsCountEl);
    
  }
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
