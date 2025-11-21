# Architecture Guide

This document describes the architecture of the Nocturna SaaS Backend.

## Overview

The Nocturna SaaS Backend is a FastAPI-based service that provides:
- User management
- Chart calculations and storage
- Astrological interpretations
- Integration with LLM services
- Analytics and logging

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  FastAPI App    │────▶│  Services       │────▶│  External       │
│                 │     │                 │     │  Services       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                        ▲
        │                        │                        │
        ▼                        ▼                        │
┌─────────────────┐     ┌─────────────────┐               │
│                 │     │                 │               │
│  API Endpoints  │     │  Repositories   │───────────────┘
│                 │     │                 │
└─────────────────┘     └─────────────────┘
        │                        │
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Models         │     │  Database       │
│                 │     │                 │
└─────────────────┘     └─────────────────┘
```

## Components

### 1. FastAPI Application

The main application is built using FastAPI and provides:
- REST API endpoints
- WebSocket support
- Authentication and authorization
- Request validation
- Response serialization

### 2. Services

Core business logic is implemented in services:

1. **UserService**
   - User management
   - Authentication
   - Authorization

2. **ChartService**
   - Chart calculations
   - Chart storage
   - Chart validation

3. **InterpretationService**
   - Astrological interpretations
   - LLM integration
   - Response formatting

4. **LLMService**
   - Multiple LLM provider support
   - Prompt management
   - Response handling

### 3. Repositories

Data access layer:

1. **UserRepository**
   - User data operations
   - Profile management

2. **ChartRepository**
   - Chart storage
   - Chart retrieval
   - Chart updates

3. **InterpretationRepository**
   - Interpretation storage
   - History tracking

### 4. Models

Data models using SQLAlchemy:

1. **User**
   - User information
   - Authentication data
   - Preferences

2. **Chart**
   - Chart data
   - Calculation parameters
   - Metadata

3. **Interpretation**
   - Interpretation text
   - Chart reference
   - Timestamps

### 5. External Services

Integration with external services:

1. **Nocturna Calculations**
   - Chart calculations
   - Astronomical data
   - WebSocket communication

2. **LLM Providers**
   - OpenAI
   - Anthropic
   - DeepSeek
   - Local LLM

## Database Architecture

### PostgreSQL

Main database for:
- User data
- Charts
- Interpretations
- System configuration

Schema:
```
nocturna_saas/
├── users/
├── charts/
├── interpretations/
└── system/
```

### Redis

Used for:
- Session management
- Caching
- Rate limiting
- Real-time updates

Configuration:
- Development: DB 1
- Testing: DB 1
- Production: DB 2

### Clickhouse

Used for:
- Analytics
- Logging
- Performance metrics
- Usage statistics

Tables:
```
nocturna_saas/
├── events/
├── metrics/
└── logs/
```

## Security

### Authentication

- JWT-based authentication
- Token refresh mechanism
- Session management

### Authorization

- Role-based access control
- Permission management
- Resource ownership

### Data Protection

- Input validation
- Output sanitization
- SQL injection prevention
- XSS protection

## Error Handling

### Error Types

1. **ValidationError**
   - Input validation
   - Data format
   - Required fields

2. **AuthenticationError**
   - Invalid credentials
   - Expired tokens
   - Missing permissions

3. **BusinessError**
   - Business logic violations
   - Invalid operations
   - Resource conflicts

4. **ExternalServiceError**
   - Service unavailability
   - Communication errors
   - Timeout handling

### Error Response Format

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {
            "field": "Additional error details"
        }
    }
}
```

## Logging

### Log Levels

1. **DEBUG**
   - Detailed information
   - Development only

2. **INFO**
   - General information
   - Normal operations

3. **WARNING**
   - Potential issues
   - Non-critical errors

4. **ERROR**
   - Error conditions
   - Failed operations

5. **CRITICAL**
   - System failures
   - Security issues

### Log Format

```json
{
    "timestamp": "ISO-8601",
    "level": "LOG_LEVEL",
    "service": "SERVICE_NAME",
    "message": "Log message",
    "context": {
        "request_id": "UUID",
        "user_id": "UUID",
        "additional": "context"
    }
}
```

## Performance

### Caching Strategy

1. **Redis Cache**
   - User sessions
   - Chart data
   - LLM responses

2. **In-Memory Cache**
   - Configuration
   - Static data
   - Lookup tables

### Optimization

1. **Database**
   - Indexes
   - Query optimization
   - Connection pooling

2. **API**
   - Response compression
   - Pagination
   - Field selection

3. **External Services**
   - Connection pooling
   - Timeout handling
   - Retry mechanism

## Deployment

### Requirements

1. **Hardware**
   - CPU: 2+ cores
   - RAM: 4+ GB
   - Storage: 20+ GB

2. **Software**
   - Python 3.11
   - PostgreSQL 14+
   - Redis 6+
   - Clickhouse 22+

### Configuration

1. **Environment Variables**
   - Database credentials
   - Service URLs
   - API keys
   - Feature flags

2. **Service Configuration**
   - Ports
   - Timeouts
   - Limits
   - Logging

### Scaling

1. **Horizontal Scaling**
   - Multiple instances
   - Load balancing
   - Session sharing

2. **Vertical Scaling**
   - Resource allocation
   - Connection limits
   - Cache size

## Monitoring

### Metrics

1. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

2. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Cache hit rate

3. **Business Metrics**
   - Active users
   - Chart calculations
   - Interpretations
   - API usage

### Alerts

1. **System Alerts**
   - Resource usage
   - Service health
   - Error rates

2. **Business Alerts**
   - Usage spikes
   - Error patterns
   - Performance issues

## Development

### Code Organization

```
src/
├── api/           # API endpoints
├── core/          # Core functionality
├── models/        # Data models
├── repositories/  # Data access
├── services/      # Business logic
└── utils/         # Utilities
```

### Testing

1. **Unit Tests**
   - Individual components
   - Mocked dependencies

2. **Integration Tests**
   - Component interaction
   - External services

3. **API Tests**
   - Endpoint testing
   - Request/response

### Documentation

1. **Code Documentation**
   - Docstrings
   - Type hints
   - Comments

2. **API Documentation**
   - OpenAPI/Swagger
   - Endpoint descriptions
   - Request/response examples

3. **Architecture Documentation**
   - System design
   - Component interaction
   - Deployment guide 