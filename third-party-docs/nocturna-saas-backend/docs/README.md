# Nocturna SaaS Backend Documentation

## Overview
This is the backend service for Nocturna SaaS platform. It provides a comprehensive REST API for astrological calculations, user management, and subscription services, integrating with the external Nocturna Calculations service.

## Key Features
- **Complete Astrological API**: Birth charts, progressions, transits, synastry, aspects, houses, fixed stars, and more
- **Modern Architecture**: FastAPI with synchronous design, no WebSocket dependencies
- **Secure Authentication**: JWT-based authentication with role-based access control
- **Subscription Management**: Full subscription and billing capabilities
- **Professional Tools**: Advanced astrological calculations via external calculation server

## Technology Stack
- **Framework**: FastAPI (Python 3.11)
- **Environment**: Conda-based dependency management
- **Database**: PostgreSQL 14+ with SQLAlchemy
- **Caching**: Redis 6+
- **Analytics**: ClickHouse 22+
- **Communication**: REST API only (WebSocket removed)

## Documentation Structure

### Quick Start
- [Installation Guide](installation/README.md) - Set up development environment with Conda
- [Development Guide](development/README.md) - Development workflow and best practices
- [Deployment Guide](deployment/README.md) - Production deployment with Docker/systemd

### API Reference
- [REST API Documentation](api/README.md) - Complete API reference with examples
- [OpenAPI Specification](api/openapi.yaml) - Machine-readable API spec
- [Postman Collection](api/postman_collection.json) - Ready-to-use API tests

### Architecture
- [Architectural Constraints](architecture_constraints.md) - REST-only communication principles
- [System Architecture](architecture/system-architecture.md) - Overall system design
- Database Schema Documentation
- Integration Patterns

### Development
- [Setup Guide](development/README.md) - Complete development environment setup
- [Make Commands](deployment/make-help.md) - All available Makefile commands
- [Development Workflow](development/README.md) - TDD, testing, and code quality
- [Git Workflow](deployment/git-help.md) - Version control best practices

### Deployment
- [Production Deployment](deployment/README.md) - Complete production setup guide
- Environment Configuration
- Docker Containerization
- Monitoring & Logging
- Security Best Practices

### Integration
- External Services Integration
- Nocturna Calculations Server Communication
- Authentication & Authorization
- Error Handling Patterns

## Available API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Astrological Calculations
- `POST /api/v1/calculations/birth-chart` - Calculate natal chart
- `POST /api/v1/calculations/progressions` - Secondary progressions
- `POST /api/v1/calculations/transits` - Transit calculations
- `POST /api/v1/calculations/synastry` - Compatibility analysis
- `POST /api/v1/calculations/aspects` - Planetary aspects
- `POST /api/v1/calculations/houses` - House cusps
- `POST /api/v1/calculations/fixed-stars` - Fixed star positions
- `POST /api/v1/calculations/arabic-parts` - Arabic parts/lots
- `POST /api/v1/calculations/dignities` - Planetary dignities

### Chart Management
- `GET /api/v1/charts/` - List user's saved charts
- `POST /api/v1/charts/calculate` - Calculate and save chart

### Subscription Management
- `GET /api/v1/subscriptions/` - User subscriptions
- `GET /api/v1/subscriptions/plans/` - Available subscription plans
- `POST /api/v1/subscriptions/` - Create new subscription

## Getting Started

### 1. Quick Setup
```bash
# Clone repository
git clone https://github.com/eaprelsky/nocturna-saas-backend.git
cd nocturna-saas-backend

# Create conda environment and install dependencies
make setup
conda activate nocturna-saas

# Generate secure configuration
make generate-env

# Set up test infrastructure
make setup-test-infra

# Start development server
make run
```

### 2. Development Workflow
```bash
# Daily development
conda activate nocturna-saas
make run                 # Start server
make test                # Run tests
make test-watch         # Watch mode for TDD
```

### 3. API Testing
- **Interactive Docs**: http://localhost:8081/docs
- **Health Check**: http://localhost:8081/health
- **API Root**: http://localhost:8081/api

## Architecture Principles

### REST-Only Communication
The system uses **REST API exclusively** for all communication. WebSocket support has been completely removed in favor of a simpler, more maintainable synchronous architecture.

### External Calculations
**All astrological calculations** are performed by the external Nocturna Calculations server. This backend handles only business logic, data management, and API orchestration.

### Modern Python Stack
- **Conda Environment Management**: Reliable, reproducible environments
- **Synchronous Design**: Simplified codebase without async complexity
- **Type Safety**: Full mypy type checking
- **Testing**: Comprehensive test suite with 99%+ coverage

## Key Changes from Previous Versions

### ✅ Completed Modernization
- **Removed WebSocket dependencies** - Now REST API only
- **Eliminated async/await patterns** - Synchronous throughout
- **Migrated from Poetry to Conda** - Better environment management
- **Standardized URL patterns** - All APIs under `/api/v1/` prefix
- **Unified schema structure** - Consistent request/response formats

### 🆕 New Features
- **Extended calculation endpoints** - 8 new astrological calculation types
- **Subscription management** - Complete billing and subscription system
- **Enhanced security** - Modern JWT authentication with proper middleware
- **Improved testing** - Comprehensive test infrastructure

## External Dependencies

### Required Services
1. **PostgreSQL 14+** - Main database
2. **Redis 6+** - Caching and sessions
3. **ClickHouse 22+** - Analytics (auto-installed)
4. **Nocturna Calculations Server** - External calculation service (port 8000)

### Service Communication
```
Frontend → Nocturna SaaS Backend → Nocturna Calculations Server
         ↓
    PostgreSQL/Redis/ClickHouse
```

## Support and Contribution

### Documentation Updates
This documentation has been **completely updated** to reflect:
- ✅ Current REST-only architecture
- ✅ Conda-based development workflow  
- ✅ All new API endpoints
- ✅ Modern deployment practices
- ✅ Actual Makefile commands

### Getting Help
1. Check the relevant documentation section
2. Review API documentation at `/docs`
3. Run `make help` for available commands
4. Check the troubleshooting sections in deployment guides

### Contributing
1. Follow the [Development Guide](development/README.md)
2. Use [Make Commands](deployment/make-help.md) for all operations
3. Ensure tests pass: `make test`
4. Follow conventional commit guidelines

## API Documentation Access

- **Local Development**: http://localhost:8081/docs
- **OpenAPI Schema**: http://localhost:8081/openapi.json
- **ReDoc Format**: http://localhost:8081/redoc

The documentation is automatically generated and always up-to-date with the current codebase. 