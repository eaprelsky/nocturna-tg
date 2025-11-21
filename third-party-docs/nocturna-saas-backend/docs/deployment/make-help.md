# Make Commands Documentation

This document describes the available make commands for the Nocturna SaaS Backend project.

## Basic Commands

### Environment Setup
```bash
make setup
```
Creates a conda environment and installs all dependencies. This is the first command you should run when setting up the project.

### Install Dependencies
```bash
make install
```
Updates the conda environment and installs all Python dependencies from requirements.txt.

### Run Development Server
```bash
make run
```
Starts the FastAPI development server on port 8081 with auto-reload enabled.

### Run Tests
```bash
make test
```
Sets up test infrastructure and runs all tests with coverage reporting.

### Clean Environment
```bash
make clean
```
Removes the conda environment and cleans up all build artifacts.

## Detailed Commands

### Environment Management
- `make setup` - Create conda environment with Python 3.11 and install dependencies
- `make setup-env` - Set up environment configuration files
- `make install` - Update conda environment and install/update dependencies
- `make clean` - Remove conda environment completely

### Testing Commands
- `make test` - Run all tests with coverage (includes test environment setup)
- `make test-cov` - Run tests with detailed coverage report (HTML + terminal)
- `make test-unit` - Run only unit tests
- `make test-integration` - Run only integration tests
- `make test-watch` - Run tests in watch mode (re-runs on file changes)
- `make setup-test-env` - Set up test databases and infrastructure
- `make setup-test-infra` - Complete test infrastructure setup

### Service Management

#### Redis Commands
- `make redis-start` - Start Redis server
- `make redis-stop` - Stop Redis server
- `make redis-cli` - Connect to Redis CLI
- `make redis-flush` - Flush all Redis data

#### ClickHouse Commands
- `make clickhouse-start` - Start ClickHouse server
- `make clickhouse-stop` - Stop ClickHouse server
- `make clickhouse-status` - Check ClickHouse server status
- `make clickhouse-install` - Install ClickHouse server

### Utility Commands
- `make generate-env` - Generate .env file with secure random values
- `make setup-dev` - Set up development environment
- `make check-services` - Check and install required system services
- `make help` - Show all available commands with descriptions

## Environment Variables

The Makefile uses the following variables:
- `ENV_NAME` - Conda environment name (default: nocturna-saas)
- `CONDA_PYTHON` - Path to Python in conda environment
- `CONDA_PIP` - Path to pip in conda environment

## Directory Structure

The Makefile assumes the following project structure:
- `src/` - Application source code
- `tests/` - Test files
- `scripts/` - Setup and utility scripts
- `environment.yml` - Conda environment specification
- `requirements.txt` - Python package dependencies
- `alembic/` - Database migrations

## Prerequisites

Before running make commands, ensure you have:
1. **Conda** installed (Miniconda or Anaconda)
2. **PostgreSQL** 14+ installed and running
3. **Redis** 6+ installed
4. **ClickHouse** 22+ (will be installed automatically if missing)

## Quick Start

1. **First-time setup:**
   ```bash
   make setup
   conda activate nocturna-saas
   ```

2. **Daily development:**
   ```bash
   conda activate nocturna-saas
   make run
   ```

3. **Run tests:**
   ```bash
   make test
   ```

4. **Update dependencies:**
   ```bash
   make install
   ```

## Common Usage Patterns

### Setting Up Development Environment
```bash
# Clone repository
git clone <repo-url>
cd nocturna-saas-backend

# Initial setup
make setup
conda activate nocturna-saas

# Generate environment configuration
make generate-env

# Set up test infrastructure
make setup-test-infra

# Start development server
make run
```

### Testing Workflow
```bash
# Run all tests
make test

# Run tests with detailed coverage
make test-cov

# Run only unit tests (faster)
make test-unit

# Watch mode for TDD
make test-watch
```

### Service Management
```bash
# Start required services
make redis-start
make clickhouse-start

# Check service status
make check-services

# Stop services when done
make redis-stop
make clickhouse-stop
```

## Troubleshooting

### Common Issues

1. **Conda environment not found**
   - Run `make setup` to create the environment
   - Ensure conda is in your PATH

2. **Permission errors with services**
   - Services require sudo on Linux: `sudo make redis-start`
   - On macOS, use brew services instead

3. **PostgreSQL connection errors**
   - Ensure PostgreSQL is running
   - Check connection parameters in .env file
   - Run `make setup-test-env` to create test database

4. **Test failures**
   - Run `make setup-test-infra` to ensure test environment is ready
   - Check if all services are running

### Environment Variables Issues

If tests fail with configuration errors:
```bash
# Regenerate environment file
make generate-env

# Check environment setup
make setup-env
```

### Database Issues

If database-related tests fail:
```bash
# Reset test environment
make setup-test-env

# Or completely clean and start over
make clean
make setup
make setup-test-infra
```

## Development Best Practices

1. **Always activate conda environment:**
   ```bash
   conda activate nocturna-saas
   ```

2. **Run tests before committing:**
   ```bash
   make test
   ```

3. **Keep dependencies updated:**
   ```bash
   make install
   ```

4. **Use watch mode during development:**
   ```bash
   make test-watch
   ```

5. **Generate fresh .env for new environments:**
   ```bash
   make generate-env
   ```

## CI/CD Integration

For continuous integration, use this sequence:
```bash
make setup
conda activate nocturna-saas
make setup-test-infra
make test
```

## Contributing

When adding new make commands:
1. Add the command to the Makefile
2. Add `.PHONY` target if it doesn't create files
3. Document the command in this file
4. Add help text in the Makefile's help target
5. Test on different platforms (Linux/macOS/Windows with WSL) 