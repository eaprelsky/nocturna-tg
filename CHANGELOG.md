# Changelog

All notable changes to Nocturna Telegram Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-22

### Added
- 🔗 **Webhook mode support** - Production-ready webhook implementation
- 🏥 Health check endpoint (`/health`) for monitoring
- 📚 Comprehensive webhook documentation:
  - Webhook setup guide with step-by-step instructions
  - Nginx configuration examples
  - SSL/Certbot integration guide
  - Quick commands cheatsheet
  - Deployment checklist
  - Troubleshooting guide

### Changed
- ⚡ **CRITICAL FIX**: Webhook timeout issue resolved
  - Webhook handler now uses asynchronous processing
  - Immediately returns 200 OK to Telegram
  - Commands processed in background without blocking
  - Prevents 504 Gateway Timeout errors
  - Eliminates message duplication loop
- 🔧 Increased Nginx proxy timeouts (10s → 60s) as safety measure
- 📦 Added `aiohttp` dependency for webhook HTTP server

### Configuration
- 🎛️ New environment variables for webhook mode:
  - `BOT_MODE` - polling (default) or webhook
  - `WEBHOOK_URL` - public HTTPS URL for webhook
  - `WEBHOOK_PATH` - webhook endpoint path
  - `WEBHOOK_PORT` - internal port for webhook server
  - `WEBHOOK_HOST` - host binding for webhook server
  - `WEBHOOK_SECRET` - secret token for webhook verification

### Infrastructure
- 🐳 Updated Docker Compose with port mapping for webhook
- 🌐 Nginx configuration template for production deployment
- 🔒 SSL/HTTPS support via Let's Encrypt integration
- 📊 Health check endpoint for uptime monitoring

### Documentation
- 📘 `docs/webhook-setup.md` - Detailed webhook setup guide
- 📋 `WEBHOOK_SETUP_QUICK.md` - Quick start (8 steps)
- ✅ `DEPLOYMENT_CHECKLIST.md` - Complete deployment checklist
- 🔧 `QUICK_COMMANDS.md` - Command reference cheatsheet
- 🐛 `WEBHOOK_TIMEOUT_FIX.md` - Timeout issue explanation and fix
- 🌐 `nginx-tg.nocturna.ru.conf` - Ready-to-use Nginx config

### Fixed
- 🐛 **Webhook 504 Gateway Timeout** causing infinite message loops
- 🔄 Proper async handling of long-running operations
- 🚀 Instant webhook response to Telegram API

### Technical Details
- Webhook handler uses `asyncio.create_task()` for non-blocking processing
- Telegram receives 200 OK immediately (< 1ms)
- Command processing continues in background
- Supports both polling (development) and webhook (production) modes
- Seamless mode switching via configuration

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

