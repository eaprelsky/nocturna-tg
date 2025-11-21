# Deployment Guide

## Overview

This guide explains how to deploy the Nocturna SaaS Backend service in different environments using Conda-based setup and modern containerization.

## Prerequisites

- **Python 3.11** (managed via Conda)
- **Conda** (Miniconda or Anaconda)
- **Docker and Docker Compose** (recommended for production)
- **PostgreSQL 14+**
- **Redis 6+**
- **ClickHouse 22+**
- **Nocturna Calculations Server** (external dependency)

## Deployment Options

### 1. Docker Deployment (Recommended for Production)

#### Quick Docker Setup

1. **Clone the repository:**
```bash
git clone https://github.com/eaprelsky/nocturna-saas-backend.git
cd nocturna-saas-backend
```

2. **Configure environment:**
```bash
# Generate secure environment file
make generate-env

# Edit configuration as needed
nano .env
```

3. **Build and start services:**
```bash
docker-compose up -d
```

4. **Check service status:**
```bash
docker-compose ps
docker-compose logs backend
```

5. **Run migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

#### Docker Environment Variables

Key variables for Docker deployment:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/nocturna

# Services
REDIS_HOST=redis
REDIS_PORT=6379
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123

# External Services
CALCULATION_SERVER_REST_URL=http://nocturna-calculations:8000
NOCTURNA_SERVICE_TOKEN=your-service-token

# Security
JWT_SECRET_KEY=generated-secure-key
SECRET_KEY=generated-secret-key

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### 2. Direct Deployment (Development/Staging)

#### System Setup

1. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 postgresql redis-server

# CentOS/RHEL
sudo yum install -y python3 postgresql-server redis
```

2. **Install Conda:**
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

#### Application Deployment

1. **Clone and setup:**
```bash
git clone https://github.com/eaprelsky/nocturna-saas-backend.git
cd nocturna-saas-backend

# Create environment and install dependencies
make setup
conda activate nocturna-saas
```

2. **Configure environment:**
```bash
# Generate secure configuration
make generate-env

# Edit for production
nano .env
```

3. **Set up database:**
```bash
# Create production database
sudo -u postgres createdb nocturna_production

# Run migrations
alembic upgrade head
```

4. **Start services:**
```bash
# Start system services
sudo systemctl start postgresql
sudo systemctl start redis-server

# Start application
make run
```

### 3. Production Deployment with systemd

#### Create systemd service

1. **Create service file:**
```bash
sudo nano /etc/systemd/system/nocturna-backend.service
```

```ini
[Unit]
Description=Nocturna SaaS Backend
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=nocturna
Group=nocturna
WorkingDirectory=/opt/nocturna-saas-backend
Environment=PATH=/opt/miniconda3/envs/nocturna-saas/bin
ExecStart=/opt/miniconda3/envs/nocturna-saas/bin/uvicorn src.main:app --host 0.0.0.0 --port 8081
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2. **Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable nocturna-backend
sudo systemctl start nocturna-backend
sudo systemctl status nocturna-backend
```

## Environment Configuration

### Production Environment Variables

```env
# Application
APP_NAME=Nocturna SaaS Backend
DEBUG=false
ENVIRONMENT=production
PROJECT_HOST=yourdomain.com
PROJECT_PORT=8081

# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/nocturna_production

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
SECRET_KEY=your-super-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
CALCULATION_SERVER_REST_URL=https://calculations.yourdomain.com
NOCTURNA_SERVICE_TOKEN=your-production-service-token

# Services
REDIS_HOST=localhost
REDIS_PORT=6379
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123

# CORS
CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]

# Monitoring
LOG_LEVEL=INFO
```

### Security Configuration

1. **Generate secure secrets:**
```bash
# Use the built-in generator
make generate-env

# Or generate manually
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **File permissions:**
```bash
chmod 600 .env
chown nocturna:nocturna .env
```

3. **Database security:**
```bash
# Create dedicated database user
sudo -u postgres psql -c "CREATE USER nocturna_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nocturna_production TO nocturna_user;"
```

## Reverse Proxy Setup

### Nginx Configuration

1. **Install Nginx:**
```bash
sudo apt-get install nginx
```

2. **Create site configuration:**
```bash
sudo nano /etc/nginx/sites-available/nocturna-backend
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Static files (if any)
    location /static/ {
        alias /opt/nocturna-saas-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8081/health;
    }
}
```

3. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/nocturna-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Database Setup

### PostgreSQL Production Setup

1. **Install and configure:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Secure installation
sudo -u postgres psql
\password postgres
```

2. **Create production database:**
```sql
CREATE DATABASE nocturna_production;
CREATE USER nocturna_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nocturna_production TO nocturna_user;
ALTER DATABASE nocturna_production OWNER TO nocturna_user;
```

3. **Configure PostgreSQL:**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Key settings for production:
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

4. **Run migrations:**
```bash
cd /opt/nocturna-saas-backend
conda activate nocturna-saas
alembic upgrade head
```

### Redis Production Setup

1. **Configure Redis:**
```bash
sudo nano /etc/redis/redis.conf
```

```conf
# Security
bind 127.0.0.1
requirepass your_redis_password

# Persistence
save 900 1
save 300 10
save 60 10000

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru
```

2. **Start Redis:**
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## Monitoring and Logging

### Application Monitoring

1. **Health check endpoint:**
```bash
curl https://api.yourdomain.com/health
```

2. **Log monitoring:**
```bash
# Application logs
journalctl -u nocturna-backend -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

3. **System monitoring:**
```bash
# Resource usage
htop
iotop
df -h

# Service status
systemctl status nocturna-backend
systemctl status postgresql
systemctl status redis-server
systemctl status nginx
```

### Log Configuration

1. **Application logging:**
```bash
# Configure log level in .env
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

2. **Log rotation:**
```bash
sudo nano /etc/logrotate.d/nocturna-backend
```

```
/var/log/nocturna-backend/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 nocturna nocturna
    postrotate
        systemctl reload nocturna-backend
    endscript
}
```

## Backup and Recovery

### Database Backup

1. **Automated backup script:**
```bash
#!/bin/bash
# /opt/scripts/backup-nocturna.sh

BACKUP_DIR="/opt/backups/nocturna"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="nocturna_production"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Remove backups older than 7 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

2. **Schedule with cron:**
```bash
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup-nocturna.sh
```

### Application Backup

```bash
#!/bin/bash
# Backup application files and configuration

tar -czf /opt/backups/nocturna/app_backup_$(date +%Y%m%d).tar.gz \
    /opt/nocturna-saas-backend \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc"
```

## Scaling Considerations

### Horizontal Scaling

1. **Load balancer configuration:**
```nginx
upstream nocturna_backend {
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}

server {
    location / {
        proxy_pass http://nocturna_backend;
    }
}
```

2. **Multiple instances:**
```bash
# Start multiple instances on different ports
uvicorn src.main:app --host 0.0.0.0 --port 8081 &
uvicorn src.main:app --host 0.0.0.0 --port 8082 &
uvicorn src.main:app --host 0.0.0.0 --port 8083 &
```

### Database Scaling

1. **Connection pooling:**
```python
# In database configuration
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db?max_size=20&max_overflow=0"
```

2. **Read replicas:**
```python
# Configure read/write splitting in application
MASTER_DATABASE_URL = "postgresql+asyncpg://..."
REPLICA_DATABASE_URL = "postgresql+asyncpg://..."
```

## Security Checklist

- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure strong passwords and secrets
- [ ] Implement rate limiting
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Secure file permissions
- [ ] Monitor access logs
- [ ] Implement backup encryption
- [ ] Configure CORS properly

## Troubleshooting

### Common Issues

1. **Service won't start:**
```bash
# Check logs
journalctl -u nocturna-backend --since "1 hour ago"

# Check configuration
conda activate nocturna-saas
python -c "from src.core.config import settings; print(settings.DATABASE_URL)"
```

2. **Database connection errors:**
```bash
# Test connection
psql -h localhost -U nocturna_user -d nocturna_production

# Check PostgreSQL status
sudo systemctl status postgresql
```

3. **Memory issues:**
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head

# Adjust service limits
sudo systemctl edit nocturna-backend
```

4. **Performance issues:**
```bash
# Profile application
pip install py-spy
py-spy top --pid $(pgrep -f uvicorn)

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
``` 