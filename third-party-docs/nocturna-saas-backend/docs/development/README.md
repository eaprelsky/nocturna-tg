# Development Guide

This guide explains how to develop the Nocturna SaaS Backend.

## Development Environment

### Prerequisites

- **Python 3.11** (managed via Conda)
- **Conda** (Miniconda or Anaconda)
- **PostgreSQL 14+**
- **Redis 6+**
- **ClickHouse 22+** (auto-installed if missing)
- **Nocturna Calculations Server** (running on port 8000)

### Setup Options

#### Recommended Setup (Conda + Make)

1. **Install Conda:**
```bash
# Download and install Miniconda (if not already installed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

2. **Clone the repository:**
```bash
git clone https://github.com/eaprelsky/nocturna-saas-backend.git
cd nocturna-saas-backend
```

3. **Initial setup:**
```bash
# Create conda environment and install dependencies
make setup

# Activate environment
conda activate nocturna-saas

# Generate environment configuration
make generate-env
```

4. **Set up test infrastructure:**
```bash
# Set up databases and test environment
make setup-test-infra
```

5. **Start development server:**
```bash
make run
```

#### Manual Setup (Alternative)

If you prefer manual setup:

1. **Create conda environment:**
```bash
conda env create -f environment.yml
conda activate nocturna-saas
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up database:**
```bash
# Create test database
python scripts/setup_test_env.py

# Run migrations
alembic upgrade head
```

## Development Workflow

### Daily Development

1. **Activate environment:**
```bash
conda activate nocturna-saas
```

2. **Start services (if not running):**
```bash
make redis-start
make clickhouse-start
# PostgreSQL should be running as system service
```

3. **Start development server:**
```bash
make run
```

The server will start on `http://localhost:8081` with auto-reload enabled.

### Testing

#### Run All Tests
```bash
make test
```

#### Test Development Workflow
```bash
# Unit tests only (faster)
make test-unit

# Integration tests
make test-integration

# Watch mode (re-runs on changes)
make test-watch

# Coverage report
make test-cov
```

#### Test Environment Setup
```bash
# Reset test environment if needed
make setup-test-env
```

### Code Quality

#### Linting and Formatting
The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run quality checks:
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

#### Pre-commit Hooks
Set up pre-commit hooks to run checks automatically:
```bash
pip install pre-commit
pre-commit install
```

### Database Management

#### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check current migration
alembic current

# Migration history
alembic history
```

#### Database Reset
```bash
# Reset development database
alembic downgrade base
alembic upgrade head

# Reset test database
make setup-test-env
```

### API Development

#### Interactive API Documentation
- **Swagger UI**: http://localhost:8081/docs
- **ReDoc**: http://localhost:8081/redoc
- **OpenAPI Schema**: http://localhost:8081/openapi.json

#### Testing API Endpoints
```bash
# Test authentication
curl -X POST http://localhost:8081/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123456"}'

# Test calculations
curl -X POST http://localhost:8081/api/v1/calculations/birth-chart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"birth_date": "1990-01-01", "birth_time": "12:00:00", "latitude": 55.7, "longitude": 37.6, "timezone": "UTC"}'
```

## Project Structure

```
nocturna-saas-backend/
├── src/                    # Application source code
│   ├── api/               # API endpoints (deprecated)
│   ├── core/              # Core configuration and utilities
│   ├── models/            # SQLAlchemy models
│   ├── routers/           # FastAPI routers
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic services
│   └── main.py           # Application entry point
├── tests/                 # Test files
│   ├── api/              # API tests
│   ├── core/             # Core functionality tests
│   ├── integration/      # Integration tests
│   ├── models/           # Model tests
│   ├── repositories/     # Repository tests
│   ├── routers/          # Router tests
│   └── services/         # Service tests
├── alembic/              # Database migrations
├── scripts/              # Setup and utility scripts
├── docs/                 # Documentation
├── environment.yml       # Conda environment specification
├── requirements.txt      # Python dependencies
├── Makefile             # Development commands
└── .env                 # Environment configuration
```

## Environment Configuration

### Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nocturna

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
CALCULATION_SERVER_REST_URL=http://localhost:8000
NOCTURNA_SERVICE_TOKEN=your-service-token

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
```

### Generate Configuration
```bash
# Generate secure .env file
make generate-env
```

## External Dependencies

### Nocturna Calculations Server

The application requires the Nocturna Calculations Server to be running:

1. **Start the calculation server** (port 8000)
2. **Configure service token** in `.env` file
3. **Test connection**:
```bash
curl http://localhost:8000/health
```

### Database Services

#### PostgreSQL Setup
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS
```

#### Redis Setup
```bash
# Install and start via Makefile
make redis-start

# Or manually
sudo apt-get install redis-server  # Linux
brew install redis                 # macOS
```

#### ClickHouse Setup
```bash
# Auto-install via Makefile
make clickhouse-install
make clickhouse-start

# Check status
make clickhouse-status
```

## Debugging

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG make run

# Run with debugger
python -m debugpy --listen 5678 --wait-for-client -m uvicorn src.main:app --reload
```

### Common Issues

1. **Import errors**: Ensure conda environment is activated
2. **Database connection**: Check PostgreSQL is running and credentials are correct
3. **Calculation errors**: Verify Nocturna Calculations Server is running
4. **Test failures**: Run `make setup-test-infra` to reset test environment

### Logging

Application logs include:
- **Request/Response** logging
- **Database** query logging
- **External service** communication
- **Error** tracking with stack traces

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Performance

### Monitoring
- **Health check**: `/health`
- **Metrics**: Available via logging
- **Database queries**: SQLAlchemy logging enabled in debug mode

### Optimization Tips
1. Use async endpoints where appropriate
2. Implement proper caching strategies
3. Monitor database query performance
4. Use connection pooling for external services

## Deployment Preparation

Before deploying:
1. Run full test suite: `make test`
2. Check code quality: `flake8`, `mypy`
3. Verify all services are properly configured
4. Test with production-like data
5. Review security settings 