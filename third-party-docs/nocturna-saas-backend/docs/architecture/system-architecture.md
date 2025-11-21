# System Architecture

## Overview
The Nocturna SaaS Backend is designed as a modular, scalable service that integrates with the Nocturna Calculations service for astrological computations. The system follows a clean architecture approach with clear separation of concerns.

## Core Components

### 1. API Layer
- FastAPI-based REST API
- WebSocket support for real-time features
- Request validation using Pydantic models
- OpenAPI documentation

### 2. Domain Layer
- Business logic and domain models
- Service interfaces
- Domain events
- Value objects

### 3. Application Layer
- Use cases implementation
- Command/Query handlers
- Application services
- DTOs (Data Transfer Objects)

### 4. Infrastructure Layer
- Database access (PostgreSQL)
- External service integration (Nocturna Calculations)
- Caching (Redis)
- Message queue (RabbitMQ)
- File storage

### 5. Cross-Cutting Concerns
- Authentication & Authorization
- Logging
- Error handling
- Monitoring
- Caching strategy

## Integration with Nocturna Calculations

### Communication Pattern
- REST API calls for synchronous operations
- WebSocket for real-time updates
- Event-driven architecture for async operations

### Key Integration Points
1. Astrological Calculations
   - Birth chart generation
   - Transit calculations
   - Aspect analysis
   - House system calculations

2. Geocoding
   - Location search
   - Timezone calculations
   - Coordinates validation

## Database Schema

### Core Entities
1. Users
   - Authentication info
   - Profile data
   - Subscription status

2. Charts
   - Birth data
   - Calculation results
   - User associations

3. Subscriptions
   - Plan details
   - Billing info
   - Usage tracking

4. Sessions
   - User sessions
   - API tokens
   - WebSocket connections

## Security Architecture

### Authentication
- JWT-based authentication
- OAuth2 for third-party integration
- Session management

### Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- API key management

### Data Protection
- Encryption at rest
- Secure communication (TLS)
- Data sanitization

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Database sharding strategy
- Cache distribution

### Performance Optimization
- Response caching
- Database indexing
- Query optimization
- Connection pooling

## Monitoring & Observability

### Metrics
- API performance
- Resource utilization
- Business metrics
- Error rates

### Logging
- Structured logging
- Log aggregation
- Error tracking

### Alerting
- Performance thresholds
- Error rate monitoring
- Resource utilization alerts

## Deployment Architecture

### Containerization
- Docker-based deployment
- Kubernetes orchestration
- Service mesh integration

### Environment Strategy
- Development
- Staging
- Production
- Feature environments

## Future Considerations

### Planned Features
- Multi-tenant support
- Advanced analytics
- Machine learning integration
- Mobile API optimization

### Technical Debt Management
- Code quality metrics
- Performance benchmarks
- Security audits
- Documentation updates 