// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld('pulsepointService', {
  getIncidents: (agencyId: string) => ipcRenderer.invoke('pulsepoint:get-incidents', agencyId)
});

contextBridge.exposeInMainWorld('flightsService', {
  getAircrafts: () => ipcRenderer.invoke('flights:get-aircrafts')
});