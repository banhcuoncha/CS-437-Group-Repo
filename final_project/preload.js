// window.addEventListener('DOMContentLoaded', () => {
//     const replaceText = (selector, text) => {
//       const element = document.getElementById(selector)
//       if (element) element.innerText = text
//     }
  
//     for (const dependency of ['chrome', 'node', 'electron']) {
//       replaceText(`${dependency}-version`, process.versions[dependency])
//     }
//   })
// preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'pulsePointAPI', 
  {
    getIncidents: (agencyId) => ipcRenderer.invoke('get-incidents', agencyId),
    onIncidentsUpdated: (callback) => {
      ipcRenderer.on('incidents-updated', (event, data) => callback(data));
    },
    removeIncidentsListener: () => {
      ipcRenderer.removeAllListeners('incidents-updated');
    }
  }
);