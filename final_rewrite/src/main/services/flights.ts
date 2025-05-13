class FlightsService {
  private API_ENDPOINT_AIRCRAFT = '/data/aircraft.json';

  private hostname: string;

  constructor(hostname: string) {
    this.hostname = hostname;
  }

  public async getAircrafts(): Promise<Response> {
    return this._call(this.API_ENDPOINT_AIRCRAFT);
  }

  private async _call(endpoint: string): Promise<Response> {
    const apiUrl = this._buildEndpointUrl(endpoint);

    const response = await fetch(apiUrl);

    return await response.json();
  }

  private _buildEndpointUrl(endpoint: string): URL {
    return new URL(endpoint, this.hostname);
  }
}

export default FlightsService;