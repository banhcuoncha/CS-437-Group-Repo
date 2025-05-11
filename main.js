// main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const PulsePointApi = require('./pulsepoint-service');

let mainWindow;
const pulsePointApi = new PulsePointApi();

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
  
  // Open DevTools for debugging (optional)
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// Handle API calls from renderer process
ipcMain.handle('get-incidents', async (event, agencyId) => {
  try {
    const incidents = await pulsePointApi.getIncidents(agencyId || 'EMS1174');
    // Log structure to help debug
    console.log('API Response Structure:', JSON.stringify({
      dataType: typeof incidents,
      isArray: Array.isArray(incidents),
      hasIncidentsProperty: incidents && typeof incidents === 'object' && 'incidents' in incidents,
      incidentsType: incidents && typeof incidents === 'object' && 'incidents' in incidents ? 
        typeof incidents.incidents : 'N/A',
      isIncidentsArray: incidents && typeof incidents === 'object' && 'incidents' in incidents ? 
        Array.isArray(incidents.incidents) : false,
      keys: incidents && typeof incidents === 'object' ? Object.keys(incidents) : []
    }, null, 2));
    
    return incidents;
  } catch (error) {
    console.error('Error fetching incidents:', error);
    return { error: error.message };
  }
});

// Initialize data when app starts
async function initializeData() {
  try {
    const incidents = await pulsePointApi.getIncidents('EMS1174');
    
    // Log a more detailed view of the data structure for debugging
    console.log('API Response Raw Data Sample:');
    if (incidents && typeof incidents === 'object') {
      // Sample just a small part of the data to avoid flooding the console
      const keys = Object.keys(incidents);
      console.log('Top-level keys:', keys);
      
      if (incidents.incidents) {
        if (Array.isArray(incidents.incidents)) {
          console.log(`Found ${incidents.incidents.length} incidents in array`);
          if (incidents.incidents.length > 0) {
            console.log('First incident sample:', incidents.incidents[0]);
          }
        } else if (typeof incidents.incidents === 'object') {
          const incidentKeys = Object.keys(incidents.incidents);
          console.log(`Found incidents object with ${incidentKeys.length} keys`);
          if (incidentKeys.length > 0) {
            console.log('First incident sample:', incidents.incidents[incidentKeys[0]]);
          }
        }
      } else {
        // Check if the top-level properties might be incidents
        const firstValue = incidents[keys[0]];
        if (typeof firstValue === 'object' && firstValue !== null) {
          console.log('First potential incident sample:', firstValue);
        }
      }
    }
    
    console.log(`Processed data structure, sending to renderer`);
    if (mainWindow) {
      mainWindow.webContents.send('incidents-updated', incidents);
    }
  } catch (error) {
    console.error('Failed to initialize data:', error);
  }
}

app.whenReady().then(() => {
  setTimeout(initializeData, 1000); // Initialize after window is ready
});