# Feature: Biwheel Transit Charts

**Date:** 2025-11-24  
**Status:** ✅ Implemented  
**Feature:** Personal transit charts with biwheel visualization

## Overview

Команда `/my_transit` теперь показывает полноценную биколесную карту транзитов:
- **Внутреннее кольцо:** Натальная карта пользователя
- **Внешнее кольцо:** Текущие транзитные позиции планет
- **Аспекты:** Связи между натальными и транзитными планетами

## Implementation

### Chart Service API

Используется эндпоинт nocturna-image сервиса:
```
POST /api/v1/chart/render/transit
```

### Request Structure

```json
{
  "natal": {
    "planets": { /* 10 планет */ },
    "houses": [ /* 12 домов */ ]
  },
  "transit": {
    "planets": { /* 10 планет */ },
    "datetime": "2025-11-24T13:37:05Z"
  },
  "aspectSettings": {
    "natal": { "enabled": false },
    "transit": { "enabled": false },
    "natalToTransit": {
      "enabled": true,
      "orb": 3
    }
  }
}
```

## Architecture

### 1. Data Flow

```
User → /my_transit
  ↓
BotHandlers.my_transit_command()
  ↓
PersonalTransitService.calculate_personal_transits()
  ├── Recreates natal chart in API
  ├── Creates transit chart in API  
  ├── Calculates synastry (aspects)
  └── Returns: natal_positions, natal_houses, transit_positions, transit_aspects
  ↓
ChartService.generate_personal_transit_chart()
  ↓
ChartServiceClient.render_transit_chart()
  ↓
POST /api/v1/chart/render/transit
  ↓
Returns: Biwheel PNG image
```

### 2. Code Components

**ChartServiceClient** (`src/api/chart_service_client.py`)
- `render_transit_chart()` - Makes API call to Chart Service

**ChartService** (`src/services/chart_service.py`)
- `generate_personal_transit_chart()` - Prepares data and calls client

**PersonalTransitService** (`src/services/personal_transit_service.py`)
- `calculate_personal_transits()` - Calculates transit data
- Returns both natal and transit data for rendering

**BotHandlers** (`src/bot/handlers.py`)
- `my_transit_command()` - Orchestrates the flow
- Handles chart image + LLM interpretation

## Features

### Visual
- ✅ Biwheel chart (natal + transits)
- ✅ Aspect lines between wheels
- ✅ Retrograde planet indicators
- ✅ House cusps from natal chart
- ✅ 1000x1000 high-quality PNG

### Aspects Configuration
- ✅ Only natal-to-transit aspects shown
- ✅ Orb: 3 degrees (tight aspects)
- ✅ Types: Conjunction, Opposition, Trine, Square, Sextile

### Interpretation
- ✅ LLM-generated personalized interpretation
- ✅ Addresses user with "ты" (second person)
- ✅ Practical advice and recommendations

## Usage

User command:
```
/my_transit
```

Bot response:
1. ⏳ Status message
2. 🌟 Biwheel chart image
3. 📖 Personalized interpretation

## Configuration

### Chart Service Settings

In `.env`:
```env
CHART_SERVICE_URL=http://localhost:3000
CHART_SERVICE_API_KEY=your_api_key_here
CHART_SERVICE_TIMEOUT=60
```

### Aspect Settings

Hardcoded in `ChartServiceClient.render_transit_chart()`:
```python
"aspectSettings": {
    "natal": {"enabled": False},
    "transit": {"enabled": False},
    "natalToTransit": {
        "enabled": True,
        "orb": 3,
        "types": {
            "conjunction": {"enabled": True},
            "opposition": {"enabled": True},
            "trine": {"enabled": True},
            "square": {"enabled": True},
            "sextile": {"enabled": True}
        }
    }
}
```

## Fallback Behavior

If Chart Service unavailable:
1. Falls back to text-only report
2. Shows list of aspects
3. Still provides LLM interpretation

## Testing

### Manual Test
```bash
# In Telegram bot
/natal  # First, set up natal chart
/my_transit  # Then request transit chart
```

### Expected Output
- Biwheel chart image showing natal (inner) and transit (outer)
- Aspect lines connecting planets
- Interpretation text message

## Dependencies

**Required:**
- Nocturna Calculations API (for calculations)
- User natal chart saved in database

**Optional (with graceful fallback):**
- Chart Service (for biwheel visualization)
- OpenRouter LLM (for interpretation)

## Performance

- Chart rendering: ~1-2 seconds
- LLM interpretation: ~2-3 seconds
- Total response time: ~3-5 seconds

## Future Enhancements

Potential improvements:
- [ ] Cache transit charts for performance
- [ ] Allow user to select aspect orb
- [ ] Add minor aspects (quintile, biquintile, etc.)
- [ ] Support different house systems
- [ ] Add transit timeline (past/future)

## Documentation

- Full API docs: [Chart Service API](../../third-party-docs/nocturna-image/docs/API.md)
- Biwheel details: [Biwheel Charts](../../third-party-docs/nocturna-image/docs/BIWHEEL_CHARTS.md)
- Changelog: [My Transit Enhanced](../changelogs/my-transit-enhanced.md)

## Notes

- Biwheel functionality powered by [nocturna-wheel](https://github.com/eaprelsky/nocturna-wheel) library
- Chart Service must be running and accessible
- Transit datetime is converted to ISO format (YYYY-MM-DDTHH:MM:SSZ)

