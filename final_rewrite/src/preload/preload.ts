// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld('pulsepointService', {
  getIncidents: (agencyId: string) => ipcRenderer.invoke('pulsepoint:get-incidents', agencyId)
});

contextBridge.exposeInMainWorld('flightsService', {
  getAircrafts: () => ipcRenderer.invoke('flights:get-aircrafts')
});

contextBridge.exposeInMainWorld('gpsService', {
  onUpdate: (callback: (event: Electron.IpcRendererEvent, data: { lat: number; lon: number }) => void) =>
    ipcRenderer.on('gps-data-update', callback),
  onError: (callback: (event: Electron.IpcRendererEvent, error: string) => void) =>
    ipcRenderer.on('gps-data-error', callback),
  removeAllListeners: () => { // Important for component unmount
    ipcRenderer.removeAllListeners('gps-data-update');
    ipcRenderer.removeAllListeners('gps-data-error');
  }
});