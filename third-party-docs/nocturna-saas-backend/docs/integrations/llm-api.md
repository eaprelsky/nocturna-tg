# Nocturna LLM API

This document describes the LLM (Large Language Model) API integration in Nocturna, which provides astrological interpretations and daily energy readings.

## Overview

The LLM API is a FastAPI-based service that provides:
- **Daily Energy Interpretations**: Get daily astrological energy readings
- **Chart Interpretations**: Generate detailed interpretations of natal charts
- **LLM Status**: Check the status and configuration of the LLM service

## API Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configured via environment variables
- **Frontend Proxy**: `/api` (proxied by Vite to localhost:8000)

## Authentication

All endpoints require OAuth2 Bearer token authentication.

```typescript
// AuthService automatically handles token refresh
const accessToken = await AuthService.getAccessToken();
```

## LLM Endpoints

### Daily Energy Interpretation

```typescript
// Get daily energy interpretation
const request = {
  chart_data: {
    // Natal chart data
  },
  location: {
    latitude: 55.7558,
    longitude: 37.6176,
    city: 'Moscow'
  },
  language: 'ru', // or 'en'
  style: 'modern', // or 'traditional'
  include_timings: true // optional
};

const response = await fetch('/llm/daily-interpretation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify(request)
});

const interpretation = await response.json();
// Returns: DailyEnergyInterpretation
```

### Chart Interpretation

```typescript
// Get chart interpretation
const request = {
  chart_data: {
    // Natal chart data
  },
  language: 'ru', // or 'en'
  style: 'modern', // or 'traditional'
  sections: ['overview', 'planets', 'houses', 'aspects', 'synthesis'] // optional
};

const response = await fetch('/llm/chart-interpretation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify(request)
});

const interpretation = await response.json();
// Returns: ChartInterpretation
```

### LLM Status

```typescript
// Check LLM status
const response = await fetch('/llm/status', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const status = await response.json();
// Returns: { configured: boolean; provider: string; model: string; message: string }
```

## Response Types

### DailyEnergyInterpretation

```typescript
interface DailyEnergyInterpretation {
  id: string;
  date: string;
  timestamp: string;
  language: string;
  sections: {
    overview: {
      title: string;
      summary: string;
      mood: string;
      intensity: number;
      keyThemes: string[];
      dominantPlanets: string[];
      challengingAspects: string[];
      supportiveAspects: string[];
    };
    energies: Array<{
      name: string;
      description: string;
      influence: 'positive' | 'negative' | 'neutral';
      intensity: number;
      timeframe: string;
      keywords: string[];
      planetarySource: string;
    }>;
    recommendations: Array<{
      category: string;
      title: string;
      description: string;
      priority: 'high' | 'medium' | 'low';
      timeframe: string;
      icon: string;
    }>;
    timing: {
      bestHours: string[];
      challengingHours: string[];
      moonPhase: string;
    };
  };
  metadata: {
    provider: string;
    model: string;
    tokensUsed: number;
    generationTime: number;
    quality: number;
    version: string;
  };
}
```

### ChartInterpretation

```typescript
interface ChartInterpretation {
  id: string;
  chartId: string;
  timestamp: string;
  language: string;
  sections: {
    overview: OverviewInterpretation;
    planets: PlanetInterpretation[];
    houses: HouseInterpretation[];
    aspects: AspectInterpretation[];
    synthesis: SynthesisInterpretation;
  };
  metadata: {
    provider: string;
    model: string;
    tokensUsed: number;
    generationTime: number;
    quality: number;
    version: string;
  };
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body:

```typescript
interface ErrorResponse {
  code: string;
  message: string;
  details?: any;
}
```

Common error codes:
- `LLM_NOT_CONFIGURED`: LLM service is not properly configured
- `LLM_ERROR`: General LLM service error
- `INVALID_REQUEST`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Authentication failed
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per hour per user
- 1000 requests per hour per IP address

Rate limit headers are included in the response:
- `X-RateLimit-Limit`: Maximum requests per period
- `X-RateLimit-Remaining`: Remaining requests in current period
- `X-RateLimit-Reset`: Time when the rate limit resets

## Best Practices

1. **Caching**: Cache interpretations for the same day/location to reduce API calls
2. **Error Handling**: Implement proper error handling and retry logic
3. **Rate Limiting**: Monitor rate limit headers and implement backoff strategy
4. **Language Support**: Use appropriate language codes ('ru' or 'en')
5. **Style Selection**: Choose interpretation style based on user preferences 