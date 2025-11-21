# Docker Production Deployment

## Quick Start

### 1. Prepare Environment Variables

Create a `.env` file with production settings:

```bash
# Generate secure environment file
make generate-env

# Edit for production
nano .env
```

**Required production variables:**

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-random-key>
JWT_SECRET_KEY=<generate-secure-random-key>
FIRST_SUPERUSER=<admin-email>
FIRST_SUPERUSER_PASSWORD=<secure-password>
CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
DATABASE_URL=postgresql+psycopg2://user:password@postgres:5432/nocturna
CALCULATION_SERVER_REST_URL=http://nocturna-calculations:8000
```

### 2. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 3. Run Database Migrations

```bash
# Run migrations
docker-compose exec app alembic upgrade head
```

### 4. Verify Deployment

```bash
# Check health
curl http://localhost:8081/health

# Check API docs
curl http://localhost:8081/docs
```

## Service Configuration

### Application Service

- **Image**: Built from Dockerfile
- **Port**: 8081
- **Health Check**: `/health` endpoint
- **Workers**: 4 (configurable via Dockerfile)

### Database Services

- **PostgreSQL**: Port 5432, data persisted in volume
- **Redis**: Port 6379, data persisted in volume
- **ClickHouse**: Ports 9000, 8123, data persisted in volume

## Environment Variables

All services use environment variables from `.env` file. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `ENVIRONMENT` | Environment name (production) | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | Yes |
| `FIRST_SUPERUSER` | Admin user email | Yes |
| `FIRST_SUPERUSER_PASSWORD` | Admin user password | Yes |

## Production Configuration Validation

The application validates production configuration on startup:

- ✅ `DEBUG` must be `false`
- ✅ `SECRET_KEY` and `JWT_SECRET_KEY` must be set and secure
- ✅ `DATABASE_URL` must use PostgreSQL (not SQLite)
- ✅ `CORS_ORIGINS` must be explicitly configured (no `*`)
- ✅ `FIRST_SUPERUSER` and password must be set

If validation fails, the application will **not start** in production mode.

## Scaling

### Horizontal Scaling

To scale the application service:

```bash
# Scale to 3 instances
docker-compose up -d --scale app=3
```

**Note**: Ensure your load balancer (e.g., nginx) is configured to distribute traffic.

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring

### Health Checks

All services have health checks configured:

- **App**: `curl http://localhost:8081/health`
- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`
- **ClickHouse**: HTTP ping

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

## Backup

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U nocturna nocturna > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U nocturna nocturna < backup_20240101.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v nocturna-saas-backend_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Troubleshooting

### Service Won't Start

1. Check logs: `docker-compose logs app`
2. Verify environment variables: `docker-compose config`
3. Check production validation errors in logs

### Database Connection Errors

1. Ensure PostgreSQL is healthy: `docker-compose ps postgres`
2. Check DATABASE_URL format
3. Verify network connectivity: `docker-compose exec app ping postgres`

### CORS Errors

1. Verify `CORS_ORIGINS` is set correctly (JSON array format)
2. Check that origins don't contain `*` in production
3. Review application logs for CORS warnings

## Security Checklist

- [ ] All secrets are set and secure (not default values)
- [ ] CORS origins are explicitly configured
- [ ] Database passwords are strong
- [ ] Redis password is set (optional but recommended)
- [ ] HTTPS is configured via reverse proxy (nginx)
- [ ] Firewall rules are configured
- [ ] Regular security updates are applied
- [ ] Logs are monitored for suspicious activity

