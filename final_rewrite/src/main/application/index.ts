import path from "node:path";

import { app, BrowserWindow, ipcMain } from "electron";
import started from "electron-squirrel-startup";

import PulsePointService from "../services/pulsepoint";
import FlightsService from "../services/flights";
import GpsService from "../services/gps";

export default class Spotter {
  private app: Electron.App;

  private mainWindow: BrowserWindow;

  private pulsepointService: PulsePointService;
  private flightsService: FlightsService;
  private gpsService: GpsService;

  constructor() {
    this.app = app;

    // Handle creating/removing shortcuts on Windows when installing/uninstalling.
    if (started) {
      app.quit();
    }

    // This method will be called when Electron has finished
    // initialization and is ready to create browser windows.
    // Some APIs can only be used after this event occurs.
    app.whenReady().then(() => {
      this.initializeServices();

      this.createWindow();

      // Start GpsService AFTER mainWindow is created and assigned
      if (this.mainWindow) {
        this.gpsService.start(this.mainWindow); // Pass the created mainWindow
      } else {
        console.error("mainWindow is not available to start GpsService.");
      }
      
    });

    // Quit when all windows are closed, except on macOS. There, it's common
    // for applications and their menu bar to stay active until the user quits
    // explicitly with Cmd + Q.
    app.on("window-all-closed", () => {
      if (process.platform !== "darwin") {
        app.quit();
      }
    });

    app.on("activate", () => {
      // On OS X it's common to re-create a window in the app when the
      // dock icon is clicked and there are no other windows open.
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });

    // In this file you can include the rest of your app's specific main process
    // code. You can also put them in separate files and import them here.

    this.pulsepointService = new PulsePointService();
    this.flightsService = new FlightsService("http://localhost:8080");
    this.gpsService = new GpsService();

    ipcMain.handle("pulsepoint:get-incidents", async (event, agencyId) => {
      return await this.pulsepointService.getIncidents(agencyId);
    });

    ipcMain.handle("flights:get-aircrafts", async (event) => {
      return await this.flightsService.getAircrafts();
    });
  }

  private initializeServices() {
    return;
  }

  private createWindow() {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
      width: 1000,
      height: 800,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, "preload.js"),
      },
    });

    // and load the index.html of the app.
    if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
      mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
    } else {
      mainWindow.loadFile(
        path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`),
      );
    }

    // Open the DevTools.
    mainWindow.webContents.openDevTools();

    this.mainWindow = mainWindow;
  }
}
