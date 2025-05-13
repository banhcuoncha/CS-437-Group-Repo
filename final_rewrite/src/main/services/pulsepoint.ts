const { URL } = require('url');

class PulsePointService {
  private API_BASE = 'https://api.pulsepoint.org/v1/';

  private API_ENDPOINT_INCIDENTS = 'incidents';
  private API_ENDPOINT_INCIDENTS_QS = { both: 1 };

  private API_KEY = 'igJdMg6LrVf1Z17c64AZyUbgbgaymdJsPN5VKGc';
  private API_USERNAME = 'resp2022';
  private API_PASSWORD = '4nzHt7zyEM';

  public async getIncidents(agencyId: string): Promise<Response> {
    const params = { ...this.API_ENDPOINT_INCIDENTS_QS, agencyid: agencyId };
    return this._call(this.API_ENDPOINT_INCIDENTS, params);
  }

  private async _call(endpoint: string, params: Record<string, any>): Promise<Response> {
    const apiUrl = this._buildEndpointUrl(endpoint, params);

    const response = await fetch(apiUrl, {
      headers: {
        ...this._buildEndpointHeader()
      }
    });

    return await response.json();
  }

  private _buildEndpointUrl(endpoint: string, params: Record<string, any>): URL {
    const endpointUrl = new URL(endpoint, this.API_BASE);

    endpointUrl.searchParams.append('apikey', this.API_KEY);

    for (const [key, value] of Object.entries(params)) {
      endpointUrl.searchParams.append(key, value);
    }

    return endpointUrl;
  }

  private _buildEndpointHeader(): Record<string, string> {
    const authString = `${this.API_USERNAME}:${this.API_PASSWORD}`;

    return {
      'Authorization': `Basic ${Buffer.from(authString).toString('base64')}`
    };
  }
}

export default PulsePointService;