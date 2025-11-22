# Webhook Setup Guide

This guide explains how to set up the Nocturna Telegram Bot in webhook mode for production deployment.

## 📋 Table of Contents

- [Webhook vs Polling](#webhook-vs-polling)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Docker Setup](#docker-setup)
- [Nginx Configuration](#nginx-configuration)
- [SSL Certificate](#ssl-certificate)
- [Starting the Bot](#starting-the-bot)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Webhook vs Polling

### Polling Mode (Development)
- ✅ Bot actively requests updates from Telegram
- ✅ No external access required
- ✅ Works behind NAT/firewall
- ❌ Less efficient for high-traffic bots
- ❌ Slight delay in receiving updates

### Webhook Mode (Production)
- ✅ Telegram sends updates directly to your server
- ✅ More efficient and scalable
- ✅ Instant update delivery
- ❌ Requires HTTPS with valid certificate
- ❌ Requires public domain/IP

## Prerequisites

- Domain name (e.g., `tg.nocturna.ru`)
- Server with public IP address
- Docker and Docker Compose installed
- Nginx installed
- Port 80 and 443 accessible

## Configuration

### 1. Update Environment Variables

Add webhook configuration to your `.env` file:

```bash
# Bot mode
BOT_MODE=webhook

# Webhook settings
WEBHOOK_URL=https://tg.nocturna.ru
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080
WEBHOOK_HOST=0.0.0.0

# Optional: Secret token for webhook verification
WEBHOOK_SECRET=your_random_secret_here_min_32_chars
```

**Security Note:** Generate a strong random secret for `WEBHOOK_SECRET`:
```bash
openssl rand -hex 32
```

### 2. Update Docker Compose

Edit `docker-compose.yml` to expose the webhook port:

```yaml
services:
  nocturna-bot:
    # ... other settings ...
    
    environment:
      # ... other variables ...
      - BOT_MODE=webhook
      - WEBHOOK_URL=https://tg.nocturna.ru
      - WEBHOOK_PATH=/webhook
      - WEBHOOK_PORT=8080
      - WEBHOOK_SECRET=${WEBHOOK_SECRET}
    
    # Comment out network_mode when using webhook
    # network_mode: host
    
    # Expose webhook port
    ports:
      - "8080:8080"
```

## Docker Setup

### 1. Rebuild the Container

```bash
# Stop existing container
docker-compose down

# Rebuild with new dependencies (aiohttp)
docker-compose build

# Start in webhook mode
docker-compose up -d
```

### 2. Check Logs

```bash
docker-compose logs -f nocturna-bot
```

You should see:
```
INFO - Starting bot in WEBHOOK mode...
INFO - Webhook URL: https://tg.nocturna.ru/webhook
INFO - Listening on 0.0.0.0:8080
INFO - Webhook server started successfully
```

## Nginx Configuration

### 1. Create Nginx Config

Copy the example configuration:

```bash
sudo cp docs/nginx-config-example.conf /etc/nginx/sites-available/nocturna-tg
```

Or create manually at `/etc/nginx/sites-available/nocturna-tg`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name tg.nocturna.ru;

    # Logs
    access_log /var/log/nginx/tg.nocturna.ru_access.log;
    error_log /var/log/nginx/tg.nocturna.ru_error.log;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
```

### 2. Enable the Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/nocturna-tg /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## SSL Certificate

### Install Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### Obtain Certificate

```bash
sudo certbot --nginx -d tg.nocturna.ru
```

Certbot will:
1. Verify domain ownership
2. Obtain SSL certificate
3. Automatically configure Nginx for HTTPS
4. Set up auto-renewal

### Verify Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

### Manual Nginx HTTPS Configuration

After certbot, your Nginx config should look like:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tg.nocturna.ru;

    # SSL certificates (managed by certbot)
    ssl_certificate /etc/letsencrypt/live/tg.nocturna.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tg.nocturna.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Telegram webhook endpoint
    location /webhook {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Telegram webhook requirements
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8080;
        access_log off;
    }

    # Deny all other requests
    location / {
        return 404;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name tg.nocturna.ru;
    return 301 https://$server_name$request_uri;
}
```

## Starting the Bot

### 1. Start the Service

```bash
docker-compose up -d
```

### 2. Check Webhook Status

```bash
# Check bot logs
docker-compose logs -f nocturna-bot

# Check health endpoint
curl https://tg.nocturna.ru/health
```

Expected response:
```json
{
    "status": "healthy",
    "service": "nocturna-telegram-bot"
}
```

## Verification

### 1. Test the Bot

Send a message to your bot on Telegram:
```
/start
```

### 2. Check Webhook Info

Get webhook information from Telegram:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

Expected response:
```json
{
    "ok": true,
    "result": {
        "url": "https://tg.nocturna.ru/webhook",
        "has_custom_certificate": false,
        "pending_update_count": 0,
        "max_connections": 40
    }
}
```

### 3. Monitor Logs

```bash
# Bot logs
docker-compose logs -f nocturna-bot

# Nginx logs
sudo tail -f /var/log/nginx/tg.nocturna.ru_access.log
```

## Troubleshooting

### Bot Not Receiving Updates

**Check webhook URL:**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**Delete old webhook (if needed):**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

**Restart bot:**
```bash
docker-compose restart nocturna-bot
```

### SSL Certificate Errors

**Verify certificate:**
```bash
sudo certbot certificates
```

**Renew certificate:**
```bash
sudo certbot renew
```

**Check Nginx configuration:**
```bash
sudo nginx -t
```

### Connection Refused

**Check if bot is listening:**
```bash
sudo netstat -tlnp | grep 8080
```

**Check Docker container:**
```bash
docker-compose ps
docker-compose logs nocturna-bot
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Webhook Secret Mismatch

**Check logs for:**
```
WARNING - Invalid webhook secret token
```

**Solution:** Ensure `WEBHOOK_SECRET` in `.env` matches the one configured in the bot.

## Switching Back to Polling

If you need to switch back to polling mode:

### 1. Update `.env`
```bash
BOT_MODE=polling
```

### 2. Delete Webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

### 3. Restart Bot
```bash
docker-compose restart nocturna-bot
```

### 4. Update Docker Compose (optional)
Uncomment `network_mode: host` and comment out `ports` in `docker-compose.yml`.

## Local Development

For local development, always use polling mode:

```bash
# .env (local)
BOT_MODE=polling

# Run without Docker
make run

# Or with Docker
docker-compose up
```

This allows you to debug without needing a public domain or SSL certificate.

## Security Best Practices

1. **Use WEBHOOK_SECRET**: Always set a strong random secret
2. **Restrict IPs**: Consider limiting access to Telegram IP ranges in Nginx
3. **Monitor logs**: Regularly check for suspicious activity
4. **Keep dependencies updated**: Run `docker-compose build` periodically
5. **Use firewall**: Only expose necessary ports (80, 443, SSH)

## Additional Resources

- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/webhooks)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Need help?** Check [troubleshooting.md](troubleshooting.md) or open an issue on GitHub.

