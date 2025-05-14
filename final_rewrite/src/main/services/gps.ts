// src/main/services/gpsService.ts
import { BrowserWindow } from 'electron';
const Gpsd = require('node-gpsd-client'); // Use the working import syntax here

interface GpsPosition {
  lat: number;
  lon: number;
  
}

export class GpsService {
  private client: any; // Consider defining a proper type if unofficial types are not good
  private mainWindow: BrowserWindow | null = null;

  constructor() {
    this.client = new Gpsd({
      port: 2947, // Default gpsd port
      hostname: 'localhost', // Default gpsd hostname
      parse: true,
      // logger: { // Optional: if you want to see its internal logs
      //   info: console.log,
      //   warn: console.warn,
      //   error: console.error,
      // },
    });

    this.client.on('connected', () => {
      console.log('GPSD Service: Connected to gpsd');
      this.client.watch({ class: 'WATCH', json: true, scaled: true });
    });

    this.client.on('error', (err: Error) => {
      console.error(`GPSD Service: Error - ${err.message}`);
      if (this.mainWindow) {
        this.mainWindow.webContents.send('gps-data-error', err.message);
      }
    });

    this.client.on('TPV', (tpvData: any) => {
      // console.log('GPSD Service: TPV Data received', tpvData);
      if (tpvData.lat !== undefined && tpvData.lon !== undefined) {
        const position: GpsPosition = {
          lat: tpvData.lat,
          lon: tpvData.lon,
        };
        if (this.mainWindow) {
          this.mainWindow.webContents.send('gps-data-update', position);
        }
      }
    });
  }

  public start(mainWindow: BrowserWindow): void {
    this.mainWindow = mainWindow;
    console.log('GPSD Service: Starting and attempting to connect...');
    this.client.connect();
  }

  public stop(): void {
    if (this.client) {
      this.client.unwatch();
      this.client.disconnect();
      console.log('GPSD Service: Disconnected');
    }
  }
}

export default GpsService;