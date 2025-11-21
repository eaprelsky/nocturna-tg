# Changelog

All notable changes to Nocturna Telegram Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

