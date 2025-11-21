# Installation Guide

This guide will help you set up the Nocturna SaaS Backend development environment.

## Prerequisites

- Python 3.11
- Conda package manager
- PostgreSQL 14+
- Redis 6+
- Clickhouse 22+
- Nocturna Calculations service (already deployed)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/eaprelsky/nocturna-saas-backend.git
cd nocturna-saas-backend
```

### 2. Create Conda Environment

```bash
make setup
conda activate nocturna-backend
```

This will create a new conda environment named `nocturna-backend` with Python 3.11.

### 3. Install Dependencies

```bash
make install
```

This will install all required Python packages:
- FastAPI and Uvicorn for the web server
- SQLAlchemy and Alembic for database operations
- Redis and Clickhouse drivers
- Pydantic for data validation
- Testing tools (pytest, pytest-asyncio, pytest-cov)
- And other dependencies

### 4. Configure Environment

```bash
make setup-env
```

This will:
1. Ask for the path to your Nocturna Calculations `.env` file
2. Configure database connections (PostgreSQL, Redis, Clickhouse)
3. Set up integration with Nocturna Calculations service
4. Configure LLM service (if needed)
5. Create separate configurations for development and testing

The script will create two files:
- `.env` - Development environment configuration
- `.env.test` - Test environment configuration

### 5. Set Up Test Environment

```bash
make setup-test-env
```

This will:
1. Create test databases and schemas
2. Configure test environment variables
3. Set up test data

## Environment Configuration

### Database Configuration

The backend uses three databases:

1. **PostgreSQL**
   - Main database for user data, charts, and interpretations
   - Uses separate schema from Nocturna Calculations
   - Development: `nocturna_saas` database, `nocturna_saas` schema
   - Testing: `nocturna_test` database, `nocturna_saas_test` schema

2. **Redis**
   - Used for caching and session management
   - Development: DB 1
   - Testing: DB 1

3. **Clickhouse**
   - Used for analytics and logging
   - Development: `nocturna_saas` database
   - Testing: `nocturna_saas_test` database

### Integration with Nocturna Calculations

The backend integrates with Nocturna Calculations service:

- Uses the same PostgreSQL instance but different schemas
- Uses the same Redis instance but different databases
- Communicates via HTTP/WebSocket
- Default configuration:
  - Host: localhost
  - HTTP Port: 8000
  - WebSocket Port: 8001

### LLM Configuration

The backend supports multiple LLM providers:

1. **OpenAI**
   - Default provider
   - Requires OpenAI API key
   - Default model: gpt-4

2. **Anthropic**
   - Alternative provider
   - Requires Anthropic API key
   - Default model: claude-3-opus

3. **DeepSeek**
   - Alternative provider
   - Requires DeepSeek API key
   - Default model: deepseek-chat

4. **Local LLM**
   - For local deployment
   - Requires local LLM server URL

## Development Commands

```bash
# Start development server
make run

# Run all tests
make test

# Run tests with coverage
make test-cov

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests in watch mode
make test-watch

# Clean up environment
make clean
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify schema exists

2. **Redis Connection Issues**
   - Ensure Redis is running
   - Check Redis configuration in `.env`
   - Verify Redis DB number

3. **Clickhouse Connection Issues**
   - Ensure Clickhouse is running
   - Check Clickhouse configuration in `.env`
   - Verify database exists

4. **Nocturna Calculations Integration Issues**
   - Ensure Nocturna Calculations service is running
   - Check service URL in `.env`
   - Verify service token is valid

5. **LLM Service Issues**
   - Check API keys in `.env`
   - Verify LLM provider configuration
   - Check network connectivity

### Getting Help

If you encounter any issues:
1. Check the error messages
2. Review the configuration files
3. Check the service logs
4. Open an issue on GitHub 