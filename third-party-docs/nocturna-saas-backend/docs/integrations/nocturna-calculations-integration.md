# Nocturna Calculations API Integration

This document describes the complete integration with the [nocturna-calculations](https://github.com/eaprelsky/nocturna-calculations) API, which provides comprehensive astrological calculations using Swiss Ephemeris.

## Overview

The nocturna-calculations API is a FastAPI-based service that provides:
- **Authentication**: OAuth2 with JWT tokens
- **Chart Management**: Create, store, and manage astrological charts
- **Direct Calculations**: Calculate planetary positions, aspects, houses without storing charts
- **Advanced Calculations**: Fixed stars, Arabic parts, dignities, harmonics, progressions, and more
- **Chart-based Calculations**: Perform calculations on stored charts
- **Admin Functions**: User management and service token administration

## API Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configured via environment variables
- **Frontend Proxy**: `/api` (proxied by Vite to localhost:8000)

## Authentication

All endpoints except `/health` require OAuth2 Bearer token authentication.

### Service Token Authentication (Current Implementation)

The current implementation uses a service token for authentication:

```typescript
// AuthService automatically handles token refresh
const accessToken = await AuthService.getAccessToken();
```

### User Authentication (Available for Future Implementation)

```typescript
// Register new user
await ChartApiService.register({
  email: 'user@example.com',
  username: 'username',
  password: 'password',
  first_name: 'John',
  last_name: 'Doe'
});

// Login user
const tokens = await ChartApiService.login('username', 'password');

// Refresh token
const newTokens = await ChartApiService.refreshToken(refreshToken);

// Logout
await ChartApiService.logout(refreshToken);

// Get current user info
const user = await ChartApiService.getCurrentUser();
```

## Chart Endpoints

### Natal Chart Calculation (Primary Method)

```typescript
import { ChartApiService } from '../services/ChartApiService';

// Calculate natal chart directly
const chartRequest: ChartRequest = {
  datetime: {
    date: '1990-01-01',
    time: '12:00'
  },
  location: {
    latitude: 55.7558,
    longitude: 37.6176,
    city: 'Moscow',
    timezone: 'Europe/Moscow'
  },
  options: {
    house_system: 'placidus',
    orb: 8
  }
};

const natalChart = await ChartApiService.calculateNatalChart(chartRequest);
// Returns: { chart_id, planets, houses, aspects }
```

### Chart Storage and Management

```typescript
// Create and store a chart
const chartData = {
  date: '1990-01-01T12:00:00Z',
  latitude: 55.7558,
  longitude: 37.6176,
  timezone: 'Europe/Moscow',
  config: {
    house_system: 'placidus',
    aspects: ['conjunction', 'opposition', 'trine', 'square', 'sextile'],
    orbs: { conjunction: 8, opposition: 8, trine: 6, square: 6, sextile: 4 }
  }
};

const chart = await ChartApiService.createChart(chartData);

// List user's charts
const charts = await ChartApiService.listCharts(0, 20);

// Get specific chart
const chart = await ChartApiService.getChart(chartId);

// Update chart
const updatedChart = await ChartApiService.updateChart(chartId, updateData);

// Delete chart
await ChartApiService.deleteChart(chartId);
```

## Direct Calculation Endpoints

These endpoints perform calculations without storing charts:

### Planetary Positions

```typescript
const request = {
  date: '1990-01-01',
  time: '12:00',
  latitude: 55.7558,
  longitude: 37.6176,
  timezone: 'Europe/Moscow',
  planets: ['sun', 'moon', 'mercury', 'venus', 'mars'], // optional
  house_system: 'placidus' // optional
};

const result = await ChartApiService.calculatePlanetaryPositions(request);
// Returns: { positions: PlanetaryPosition[] }
```

### Aspects

```typescript
const result = await ChartApiService.calculateAspects(request);
// Returns: { aspects: Aspect[] }
```

### Houses

```typescript
const result = await ChartApiService.calculateHouses(request);
// Returns: { houses: House[] }
```

## Advanced Calculation Endpoints

### Fixed Stars

```typescript
const fixedStars = await ChartApiService.calculateFixedStars(chartId, {
  magnitude_limit: 3.0,
  orb: 1.0
});
```

### Arabic Parts

```typescript
const arabicParts = await ChartApiService.calculateArabicParts(chartId, {
  parts: ['fortune', 'spirit', 'love'] // optional
});
```

### Planetary Dignities

```typescript
const dignities = await ChartApiService.calculateDignities(chartId);
```

### Antiscia Points

```typescript
const antiscia = await ChartApiService.calculateAntiscia(chartId);
```

### Declinations

```typescript
const declinations = await ChartApiService.calculateDeclinations(chartId);
```

### Harmonic Charts

```typescript
const harmonics = await ChartApiService.calculateHarmonics(chartId, {
  harmonics: [4, 7, 9] // which harmonics to calculate
});
```

### Chart Rectification

```typescript
const rectification = await ChartApiService.calculateRectification(chartId, {
  events: [
    { description: 'Marriage', date: '2010-06-15T14:30:00Z' },
    { description: 'Job change', date: '2015-03-20T09:00:00Z' }
  ]
});
```

### Primary Directions

```typescript
const directions = await ChartApiService.calculatePrimaryDirections(chartId, {
  year: 2024,
  method: 'placidus' // or 'regiomontanus'
});
```

### Secondary Progressions

```typescript
const progressions = await ChartApiService.calculateSecondaryProgressions(chartId, {
  progression_date: '2024-01-01'
});
```

## Chart-Based Calculations

These endpoints perform calculations on stored charts:

```typescript
// All chart-based calculations follow the same pattern:
const chartId = 'your-chart-id';
const parameters = { /* calculation-specific parameters */ };

// Planetary positions for stored chart
const positions = await ChartApiService.calculateChartPlanetaryPositions(chartId, parameters);

// Aspects for stored chart
const aspects = await ChartApiService.calculateChartAspects(chartId, parameters);

// Houses for stored chart
const houses = await ChartApiService.calculateChartHouses(chartId, parameters);

// Advanced calculations for stored chart
const fixedStars = await ChartApiService.calculateChartFixedStars(chartId, parameters);
const arabicParts = await ChartApiService.calculateChartArabicParts(chartId, parameters);
const dignities = await ChartApiService.calculateChartDignities(chartId, parameters);
const antiscia = await ChartApiService.calculateChartAntiscia(chartId, parameters);
const declinations = await ChartApiService.calculateChartDeclinations(chartId, parameters);
const harmonics = await ChartApiService.calculateChartHarmonics(chartId, parameters);
const rectification = await ChartApiService.calculateChartRectification(chartId, parameters);

// Relationship and timing calculations
const synastry = await ChartApiService.calculateChartSynastry(chartId, {
  second_chart_id: 'other-chart-id'
});

const progressions = await ChartApiService.calculateChartProgressions(chartId, {
  progression_date: '2024-01-01'
});

const directions = await ChartApiService.calculateChartDirections(chartId, {
  direction_date: '2024-01-01'
});

const returns = await ChartApiService.calculateChartReturns(chartId, {
  return_type: 'solar', // or 'lunar'
  year: 2024
});

const eclipses = await ChartApiService.calculateChartEclipses(chartId, {
  start_date: '2024-01-01',
  end_date: '2024-12-31'
});

const ingresses = await ChartApiService.calculateChartIngresses(chartId, {
  planet: 'sun',
  start_date: '2024-01-01',
  end_date: '2024-12-31'
});
```

## Data Types

### PlanetaryPosition

```typescript
interface PlanetaryPosition {
  planet: string;
  longitude: number;
  latitude: number;
  distance: number;
  speed: number;
  is_retrograde: boolean;
  house?: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
}
```

### House

```typescript
interface House {
  number: number;
  longitude: number;
  latitude: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
}
```

### Aspect

```typescript
interface Aspect {
  planet1: string;
  planet2: string;
  aspect_type: string;
  orb: number;
  applying: boolean;
  exact_time?: string;
}
```

## Admin Functions

### Service Token Management

```typescript
// Verify admin access
const isAdmin = await ChartApiService.verifyAdminAccess();

// Get registration settings
const settings = await ChartApiService.getRegistrationSettings();

// List service tokens (admin only)
const tokens = await ChartApiService.listServiceTokens();

// Create service token (admin only)
const newToken = await ChartApiService.createServiceToken({
  days: 30,
  scope: 'calculations',
  eternal: false
});

// Revoke service token (admin only)
await ChartApiService.revokeServiceToken(tokenId);

// Refresh service token
const refreshedToken = await ChartApiService.refreshServiceToken();
```

## Utility Functions

### Health Check

```typescript
const isHealthy = await ChartApiService.healthCheck();
```

### LLM Integration Helpers

```typescript
// Get all available calculation methods
const methods = ChartApiService.getAvailableCalculations();

// Get API documentation for LLM
const docs = ChartApiService.getApiDocumentation();
```

## Error Handling

The service includes comprehensive error handling:

```typescript
try {
  const chart = await ChartApiService.calculateNatalChart(chartRequest);
} catch (error) {
  if (error.response?.status === 401) {
    // Authentication error - token will be automatically refreshed
    console.log('Authentication error, retrying...');
  } else if (error.response?.status === 422) {
    // Validation error
    console.error('Invalid request data:', error.response.data);
  } else {
    // Other errors
    console.error('Calculation failed:', error.message);
  }
}
```

## Legacy Compatibility

The service maintains compatibility with existing code:

```typescript
// Legacy transit calculation
const transits = await ChartApiService.calculateTransits(natalChart, '2024-01-01T12:00:00Z');

// Legacy midpoint calculation (placeholder)
const midpoints = await ChartApiService.calculateMidpoints(planets);

// Legacy geocoding (if available)
const locations = await ChartApiService.geocodeCity('Moscow');
const location = await ChartApiService.reverseGeocode(55.7558, 37.6176);
```

## LLM Integration

The nocturna-calculations API is designed to work seamlessly with the LLM service for astrological interpretations. The LLM service provides:

1. **Daily Energy Interpretations**: Get daily astrological energy readings
2. **Chart Interpretations**: Generate detailed interpretations of natal charts
3. **LLM Status**: Check the status and configuration of the LLM service

For detailed documentation on the LLM API, see [LLM API Documentation](llm-api.md).

### Integration Example

```typescript
// Get daily energy interpretation
const dailyEnergy = await ChartApiService.getDailyEnergy({
  chart_data: natalChart,
  location: {
    latitude: 55.7558,
    longitude: 37.6176,
    city: 'Moscow'
  },
  language: 'ru',
  style: 'modern'
});

// Get chart interpretation
const chartInterpretation = await ChartApiService.getChartInterpretation({
  chart_data: natalChart,
  language: 'ru',
  style: 'modern',
  sections: ['overview', 'planets', 'houses', 'aspects', 'synthesis']
});

// Check LLM status
const llmStatus = await ChartApiService.checkLLMStatus();
```

The LLM service is designed to provide high-quality astrological interpretations with:
1. **Multiple Languages**: Support for Russian and English
2. **Interpretation Styles**: Modern and traditional approaches
3. **Detailed Sections**: Overview, planets, houses, aspects, and synthesis
4. **Daily Energy**: Timely and relevant daily astrological guidance
5. **Error Handling**: Robust error handling for reliable LLM interactions

## Configuration

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_NOCTURNA_SERVICE_TOKEN=your-service-token

# Development
VITE_DEV_MODE=true
```

### Vite Proxy Configuration

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
});
```

## Testing

```typescript
// Test API connectivity
const isHealthy = await ChartApiService.healthCheck();
console.log('API Status:', isHealthy ? 'Healthy' : 'Unhealthy');

// Test authentication
try {
  const user = await ChartApiService.getCurrentUser();
  console.log('Authentication successful:', user);
} catch (error) {
  console.error('Authentication failed:', error);
}

// Test calculation
try {
  const chart = await ChartApiService.calculateNatalChart(testChartRequest);
  console.log('Calculation successful:', chart.chart_id);
} catch (error) {
  console.error('Calculation failed:', error);
}
```

## Best Practices

1. **Always check health status** before making calculations
2. **Handle authentication errors gracefully** - the service auto-retries once
3. **Use appropriate calculation methods** - direct calculations for one-off requests, chart-based for repeated calculations
4. **Cache chart IDs** when performing multiple calculations on the same chart
5. **Implement proper error handling** for all API calls
6. **Use TypeScript types** for better development experience and error prevention

## Troubleshooting

### Common Issues

1. **404 Errors**: Ensure nocturna-calculations service is running on localhost:8000
2. **401 Errors**: Check service token validity and authentication configuration
3. **422 Errors**: Validate request data format and required fields
4. **Timeout Errors**: Increase timeout for complex calculations

### Debug Mode

Enable debug logging:

```typescript
// Enable detailed logging
console.log('API Request:', method, url, data);
console.log('API Response:', response.status, response.data);
```

This integration provides complete access to the nocturna-calculations API and is ready for future LLM integration where AI models can programmatically access all astrological calculation capabilities. 