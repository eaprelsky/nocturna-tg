# API Documentation

## Overview

The Nocturna SaaS Backend provides REST API endpoints for astrological calculations, chart management, user authentication, and subscription services.

## Base URLs

- **Main API**: `http://localhost:8081`
- **Authentication**: `http://localhost:8081/api/auth`
- **API v1**: `http://localhost:8081/api/v1`

## Authentication

### JWT Authentication

Most API endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Register & Login

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "is_verified": false,
    "credits": 0,
    "weekly_credits": 0,
    "language": "en",
    "timezone": "UTC"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## Astrological Calculations

### Birth Chart
```http
POST /api/v1/calculations/birth-chart
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "planets": [...],
        "houses": [...],
        "aspects": [...]
    }
}
```

### Secondary Progressions
```http
POST /api/v1/calculations/progressions
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC",
    "comparison_date": "2024-01-01",
    "comparison_time": "12:00:00"
}
```

### Transits
```http
POST /api/v1/calculations/transits
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

### Synastry (Compatibility)
```http
POST /api/v1/calculations/synastry
Authorization: Bearer <token>
Content-Type: application/json

{
    "person1_request": {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "timezone": "UTC"
    },
    "person2_request": {
        "birth_date": "1992-05-15",
        "birth_time": "14:30:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "UTC"
    }
}
```

### Advanced Calculations

#### Aspects
```http
POST /api/v1/calculations/aspects
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

#### Houses
```http
POST /api/v1/calculations/houses
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

#### Fixed Stars
```http
POST /api/v1/calculations/fixed-stars
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

#### Arabic Parts
```http
POST /api/v1/calculations/arabic-parts
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

#### Planetary Dignities
```http
POST /api/v1/calculations/dignities
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

## Chart Management

### List User Charts
```http
GET /api/v1/charts/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "charts": [
        {
            "id": 1,
            "name": "My Birth Chart",
            "user_id": 1,
            "chart_data": {...},
            "is_public": false,
            "created_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "size": 50
}
```

### Calculate and Save Chart
```http
POST /api/v1/charts/calculate
Authorization: Bearer <token>
Content-Type: application/json

{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
}
```

## Subscription Management

### Get User Subscriptions
```http
GET /api/v1/subscriptions/
Authorization: Bearer <token>
```

**Response:**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "plan_id": 1,
        "status": "active",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-02-01T00:00:00Z",
        "auto_renew": true
    }
]
```

### Get Available Plans
```http
GET /api/v1/subscriptions/plans/
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Basic Plan",
        "description": "Basic astrological features",
        "price_rub": 999.0,
        "price_usd": 12.99,
        "duration_days": 30,
        "credits_per_month": 100,
        "is_active": true
    }
]
```

### Create Subscription
```http
POST /api/v1/subscriptions/
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": 1,
    "plan_id": 1,
    "auto_renew": true
}
```

## Error Responses

### Error Format
```json
{
    "status": "error",
    "error": "Detailed error message",
    "code": "ERROR_CODE"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (data validation error)
- `500` - Internal Server Error

## API Testing

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8081/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123456"}'
```

**Login:**
```bash
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123456"}'
```

**Calculate Chart:**
```bash
curl -X POST http://localhost:8081/api/v1/calculations/birth-chart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-01",
    "birth_time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "UTC"
  }'
```

## Rate Limiting

- **Requests per minute**: 100
- **Window size**: 60 seconds
- **Excluded paths**: `/docs`, `/health`, static files

## API Documentation

- **Interactive Docs**: http://localhost:8081/docs
- **OpenAPI Schema**: http://localhost:8081/openapi.json
- **ReDoc**: http://localhost:8081/redoc 