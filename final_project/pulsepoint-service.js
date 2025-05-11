// pulsepoint-service.js
const { net } = require('electron');
const { URL } = require('url');

class PulsePointApi {
  constructor() {
    this.API_BASE = 'https://api.pulsepoint.org/v1/';
    this.API_ENDPOINT_INCIDENTS = 'incidents';
    this.API_ENDPOINT_INCIDENTS_QS = { both: 1 };
    
    this.API_KEY = 'igJdMg6LrVf1Z17c64AZyUbgbgaymdJsPN5VKGc';
    this.API_USERNAME = 'resp2022';
    this.API_PASSWORD = '4nzHt7zyEM';
  }

  async getIncidents(agencyId) {
    const params = { ...this.API_ENDPOINT_INCIDENTS_QS, agencyid: agencyId };
    return this._call(this.API_ENDPOINT_INCIDENTS, params);
  }

  _buildEndpointUrl(endpoint, params) {
    const endpointUrl = new URL(endpoint, this.API_BASE);
    
    endpointUrl.searchParams.append('apikey', this.API_KEY);
    
    for (const [key, value] of Object.entries(params)) {
      endpointUrl.searchParams.append(key, value);
    }
    
    return endpointUrl;
  }
  
  _buildEndpointHeader() {
    const authString = `${this.API_USERNAME}:${this.API_PASSWORD}`;
    
    return {
      'Authorization': `Basic ${Buffer.from(authString).toString('base64')}`
    };
  }

  _call(endpoint, params) {
    return new Promise((resolve, reject) => {
      const apiUrl = this._buildEndpointUrl(endpoint, params);
      console.log('Requesting URL:', apiUrl.toString());
      
      const request = net.request({
        method: 'GET',
        url: apiUrl.toString(),
        headers: this._buildEndpointHeader()
      });
      
      let responseData = '';
      
      request.on('response', (response) => {
        console.log('Response status:', response.statusCode);
        
        response.on('data', (chunk) => {
          responseData += chunk.toString();
        });
        
        response.on('end', () => {
          try {
            console.log('Raw response data (first 200 chars):', responseData.substring(0, 200) + '...');
            
            // Sometimes empty responses or non-JSON might come back
            if (!responseData || responseData.trim() === '') {
              console.log('Empty response received');
              resolve({ incidents: [] });
              return;
            }
            
            const data = JSON.parse(responseData);
            
            // Normalize the data structure to ensure we always have incidents as an array
            let normalizedData = data;
            
            if (!data.incidents) {
              // If no incidents property, wrap the whole response as the incidents array
              normalizedData = { incidents: Array.isArray(data) ? data : [data] };
            } else if (!Array.isArray(data.incidents)) {
              // If incidents exists but is not an array, convert it to array
              normalizedData.incidents = Object.values(data.incidents);
            }
            
            console.log('Normalized data structure:', 
              JSON.stringify({
                hasIncidents: 'incidents' in normalizedData,
                incidentsIsArray: Array.isArray(normalizedData.incidents),
                incidentsCount: normalizedData.incidents ? normalizedData.incidents.length : 0
              }, null, 2)
            );
            
            resolve(normalizedData);
          } catch (error) {
            console.error('Error parsing response:', error);
            console.error('Response that caused error:', responseData);
            reject(error);
          }
        });
      });
      
      request.on('error', (error) => {
        console.error('Request error:', error);
        reject(error);
      });
      
      request.end();
    });
  }
}

module.exports = PulsePointApi;