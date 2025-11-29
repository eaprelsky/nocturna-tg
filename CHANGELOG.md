# Changelog

All notable changes to Nocturna Telegram Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-24

### Added - Personal Transits Feature
- 🌟 **Biwheel Transit Charts** - Personal transit visualization
  - Inner wheel: User's natal chart
  - Outer wheel: Current transit positions
  - Aspect lines showing natal-to-transit interactions
- 🔮 **`/my_transit` command** - Personal transit analysis
  - Calculates transits to user's natal chart
  - Shows aspects between natal and current planetary positions
  - LLM-powered personalized interpretation
- 📊 **Database Integration** - Persistent user data storage
  - SQLAlchemy ORM with Alembic migrations
  - Stores natal chart data per user
  - `/natal` command to save birth data
  - `/my_natal` command to view saved chart
- 🎨 **Chart Service Integration** - Visual chart rendering
  - Integration with nocturna-image service
  - Biwheel chart rendering endpoint
  - Aspect configuration (natal-to-transit only)
  - Graceful fallback to text-only mode

### Changed
- ⚡ **Enhanced Chart Service Client** (`src/api/chart_service_client.py`)
  - Added `render_transit_chart()` method for biwheel charts
  - Added `render_natal_chart()` method for single charts
- 📈 **Enhanced Services**
  - `ChartService`: Added `generate_personal_transit_chart()` method
  - `InterpretationService`: Added `interpret_personal_transits()` method
  - `PersonalTransitService`: Returns natal houses for biwheel rendering
- 🔧 **API Client Fixes**
  - Fixed synastry endpoint parameter (`target_chart_id` not `second_chart_id`)
  - Improved error handling and logging
  - Re-enabled personal transits after API fix

### Fixed
- 🐛 **Synastry Endpoint** - nocturna-calculations API fully implemented
  - `calculate_synastry_chart()` method now available
  - Fixed parameter name mismatch in documentation
  - Personal transits feature re-enabled
- 🔍 **Birth Data Validation** - Fixed incorrect chart_id check
  - Removed check for `chart_id` field (always None with caching)
  - Proper validation of birth data presence

### Infrastructure
- 🗄️ **Database Setup**
  - Alembic migration system
  - Initial tables: users, birth_data
  - Automatic schema migrations
- 📦 **New Dependencies**
  - `sqlalchemy` - ORM
  - `alembic` - Database migrations
  - `asyncpg` - Async PostgreSQL support (optional)

### Documentation
- 📘 Created comprehensive feature documentation:
  - `docs/features/biwheel-transit-charts.md` - Biwheel implementation guide
  - `docs/features/biwheel-transit-implementation.md` - Quick reference
- 📝 Updated API integration docs
- 🔗 Added Chart Service API references

## [1.0.1] - 2025-11-22

### Added
- 🔗 **Webhook mode support** - Production-ready webhook implementation
- 🏥 Health check endpoint (`/health`) for monitoring
- 📚 Comprehensive webhook documentation

### Changed
- ⚡ **CRITICAL FIX**: Webhook timeout issue resolved
  - Webhook handler now uses asynchronous processing
  - Immediately returns 200 OK to Telegram
  - Commands processed in background without blocking
- 🔧 Increased Nginx proxy timeouts (10s → 60s) as safety measure
- 📦 Added `aiohttp` dependency for webhook HTTP server

### Configuration
- 🎛️ New environment variables for webhook mode:
  - `BOT_MODE` - polling (default) or webhook
  - `WEBHOOK_URL`, `WEBHOOK_PATH`, `WEBHOOK_PORT`, `WEBHOOK_HOST`, `WEBHOOK_SECRET`

### Documentation
- 📘 `docs/webhook-setup.md` - Detailed webhook setup guide
- 🌐 `nginx-tg.nocturna.ru.conf` - Ready-to-use Nginx config

### Fixed
- 🐛 **Webhook 504 Gateway Timeout** causing infinite message loops
- 🔄 Proper async handling of long-running operations

## [1.0.0] - 2025-11-21

### Added
- 🎉 **Initial Release** - Production-ready Telegram bot for astrological analysis
- 🌟 Real-time planetary positions via Nocturna Calculations API
- 🔮 Transit analysis with planetary aspects
- 🤖 LLM-powered interpretations via OpenRouter (Claude Haiku 4.5)
- 📊 Chart rendering support (integration ready for Chart Service)
- 🇷🇺 Russian language interface with Russian formatter
- 🐳 Docker containerization for easy deployment
- 📚 Comprehensive documentation:
  - Installation guide
  - Quick start guide
  - LLM integration guide
  - Chart service requirements
  - Deployment documentation
- 🏗️ Clean architecture:
  - Separation of concerns (API clients, services, bot handlers)
  - SOLID principles implementation
  - OOP design patterns
- ⚙️ Configuration management via environment variables
- 📝 Structured logging with configurable log levels

### Bot Commands
- `/start` - Welcome message and bot introduction
- `/transit` - Current planetary transits with interpretation
- `/help` - Command reference and usage guide

### Infrastructure
- Docker support with multi-stage builds
- Docker Compose for orchestration
- Health checks and resource limits
- Makefile for development automation
- Git workflow with conventional commits

### Dependencies
- Python 3.11+
- python-telegram-bot 21.7+
- Pydantic 2.9+ for configuration management
- Integration with external services:
  - Nocturna Calculations API
  - OpenRouter (optional)
  - Chart Service (optional, coming soon)

### Documentation
- README with quick start instructions
- Installation guide for Conda environment
- LLM integration documentation
- Architecture overview
- API integration guides

### Security
- Environment-based configuration
- Service token authentication
- No sensitive data in repository
- Docker security best practices

---

## [Unreleased]

### Planned Features
- 📅 Natal chart storage per user
- 💑 Synastry (relationship compatibility) analysis
- 📈 Progress tracking and personal transit notifications
- 🎨 Chart visualization (when Chart Service is ready)
- 🌍 Multi-language support (English, other languages)
- 📊 User analytics and usage statistics
- 🔔 Daily/weekly horoscope subscriptions
- 🎯 Personalized transit alerts
- 📖 Extended astrological interpretations
- 🗄️ Database integration for persistent storage

---

## Version History

### Pre-release Development
- **2025-11-17** - Initial chart service integration tests
- **2025-11-09** - LLM integration with OpenRouter
- **2025-11** - Project initialization and core architecture

---

## Migration Guide

### From Development to v1.0.0

1. **Update Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in required values (bot token, API URLs)
   - Add optional OpenRouter API key for interpretations

2. **Docker Deployment**
   ```bash
   docker-compose up -d
   ```

3. **Traditional Deployment**
   ```bash
   conda activate nocturna-tg
   python -m src.main
   ```

---

## Support

For issues, questions, or contributions:
- Check documentation in `/docs` folder
- Review troubleshooting guides
- Contact project maintainers

---

**Note**: This is the first production release. Future updates will follow semantic versioning.

