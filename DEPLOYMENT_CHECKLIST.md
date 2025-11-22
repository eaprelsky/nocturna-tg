# Deployment Checklist - Webhook Mode

Чеклист для развертывания Nocturna Telegram Bot в webhook режиме на tg.nocturna.ru

## ✅ Pre-deployment

- [ ] Домен tg.nocturna.ru указывает на IP сервера
- [ ] Docker и Docker Compose установлены
- [ ] Nginx установлен
- [ ] Порты 80 и 443 открыты в firewall
- [ ] Бот зарегистрирован через @BotFather
- [ ] Получен TELEGRAM_BOT_TOKEN

## ✅ Configuration Files

### 1. `.env` файл

Создайте `.env` в корне проекта:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_BOT_USERNAME=your_bot_name

# Webhook mode
BOT_MODE=webhook
WEBHOOK_URL=https://tg.nocturna.ru
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080
WEBHOOK_HOST=0.0.0.0
WEBHOOK_SECRET=$(openssl rand -hex 32)  # Сгенерируйте новый!

# APIs
NOCTURNA_API_URL=http://localhost:8000/api
NOCTURNA_SERVICE_TOKEN=your_service_token
NOCTURNA_IMAGE_SERVICE_TOKEN=your_image_token

# Optional
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-haiku-4.5

# Settings
LOG_LEVEL=INFO
TIMEZONE=Europe/Moscow
```

### 2. `docker-compose.yml`

Проверьте, что порты раскомментированы:

```yaml
ports:
  - "8080:8080"
```

И закомментирован network_mode:

```yaml
# network_mode: host
```

## ✅ Nginx Configuration

### Шаг 1: Создать базовый конфиг

```bash
sudo cp nginx-tg.nocturna.ru.conf /etc/nginx/sites-available/nocturna-tg
sudo ln -s /etc/nginx/sites-available/nocturna-tg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 2: Установить SSL

```bash
sudo certbot --nginx -d tg.nocturna.ru
```

### Шаг 3: Раскомментировать HTTPS блок

Откройте `/etc/nginx/sites-available/nocturna-tg` и раскомментируйте весь блок `server { listen 443 ssl http2; ... }`

```bash
sudo nano /etc/nginx/sites-available/nocturna-tg
# Раскомментируйте HTTPS блок
sudo nginx -t
sudo systemctl reload nginx
```

## ✅ Docker Deployment

### Шаг 1: Пересоберите образ

```bash
cd /path/to/nocturna-tg
docker-compose build
```

### Шаг 2: Запустите контейнер

```bash
docker-compose up -d
```

### Шаг 3: Проверьте логи

```bash
docker-compose logs -f nocturna-bot
```

Ожидаемый вывод:
```
INFO - Loading configuration...
INFO - Starting bot in WEBHOOK mode...
INFO - Webhook URL: https://tg.nocturna.ru/webhook
INFO - Listening on 0.0.0.0:8080
INFO - Webhook server started successfully
```

## ✅ Verification

### 1. Health Check

```bash
curl https://tg.nocturna.ru/health
```

Ожидается:
```json
{"status": "healthy", "service": "nocturna-telegram-bot"}
```

### 2. Webhook Info

```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

Ожидается:
```json
{
  "ok": true,
  "result": {
    "url": "https://tg.nocturna.ru/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

### 3. Test Bot

Отправьте боту в Telegram:
```
/start
```

### 4. Monitor Logs

```bash
# Bot logs
docker-compose logs -f nocturna-bot

# Nginx access logs
sudo tail -f /var/log/nginx/tg.nocturna.ru_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/tg.nocturna.ru_error.log
```

## ✅ Security Checks

- [ ] WEBHOOK_SECRET установлен и имеет минимум 32 символа
- [ ] SSL сертификат валидный (проверьте через браузер)
- [ ] Только необходимые порты открыты (80, 443, SSH)
- [ ] Firewall настроен (ufw/iptables)
- [ ] Логи ротируются
- [ ] Автообновление сертификата работает (`certbot renew --dry-run`)

## ✅ Monitoring Setup

### Systemd Service (optional)

Для автозапуска при перезагрузке убедитесь, что Docker настроен на autostart:

```bash
sudo systemctl enable docker
```

### Log Rotation

Проверьте, что логи ротируются:

```bash
sudo cat /etc/logrotate.d/nginx
```

### Alerts (optional)

Настройте мониторинг:
- Uptime monitoring для https://tg.nocturna.ru/health
- Alert при падении контейнера
- Alert при истечении SSL сертификата

## 🔄 Rollback Plan

Если что-то пошло не так:

```bash
# 1. Остановить контейнер
docker-compose down

# 2. Удалить webhook
curl "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"

# 3. Переключиться на polling
# Измените в .env: BOT_MODE=polling

# 4. Закомментировать ports в docker-compose.yml
# 5. Раскомментировать network_mode: host

# 6. Перезапустить
docker-compose up -d
```

## 📝 Post-Deployment

- [ ] Документировать все изменения
- [ ] Обновить CHANGELOG.md
- [ ] Создать backup конфигурации
- [ ] Протестировать все команды бота
- [ ] Уведомить пользователей (если есть)

## 🛠️ Maintenance

### Обновление бота

```bash
git pull origin master
docker-compose build
docker-compose up -d
```

### Обновление SSL сертификата

Certbot обновляет автоматически, но можно проверить:

```bash
sudo certbot renew --dry-run
```

### Просмотр логов

```bash
# Последние 100 строк
docker-compose logs --tail=100 nocturna-bot

# Real-time
docker-compose logs -f nocturna-bot

# С временными метками
docker-compose logs -t nocturna-bot
```

### Рестарт без даунтайма

```bash
docker-compose restart nocturna-bot
```

## 📞 Support

- Документация: [docs/webhook-setup.md](docs/webhook-setup.md)
- Быстрый старт: [WEBHOOK_SETUP_QUICK.md](WEBHOOK_SETUP_QUICK.md)
- Troubleshooting: [docs/deployment.md](docs/deployment.md)

---

**Дата последнего обновления:** 2025-11-22  
**Версия:** 1.0

