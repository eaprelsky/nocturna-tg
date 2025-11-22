# Быстрая настройка Webhook режима

Краткая инструкция по переводу бота в webhook режим для production.

## 1. Обновите зависимости

```bash
# Локально (если используете)
pip install -r requirements.txt

# Docker (пересоберите образ)
docker-compose build
```

## 2. Настройте переменные окружения

Добавьте в `.env`:

```bash
# Режим работы
BOT_MODE=webhook

# Webhook настройки
WEBHOOK_URL=https://tg.nocturna.ru
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080
WEBHOOK_HOST=0.0.0.0

# Секретный токен (сгенерируйте новый)
WEBHOOK_SECRET=$(openssl rand -hex 32)
```

## 3. Обновите Docker Compose

В `docker-compose.yml` закомментируйте `network_mode: host` и раскомментируйте `ports`:

```yaml
# network_mode: host  # Закомментируйте

ports:  # Раскомментируйте
  - "8080:8080"
```

## 4. Настройте Nginx

Скопируйте конфиг:

```bash
sudo cp docs/nginx-config-example.conf /etc/nginx/sites-available/nocturna-tg
sudo ln -s /etc/nginx/sites-available/nocturna-tg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 5. Установите SSL сертификат

```bash
sudo certbot --nginx -d tg.nocturna.ru
```

## 6. Раскомментируйте HTTPS секцию в Nginx

После установки SSL раскомментируйте в `/etc/nginx/sites-available/nocturna-tg`:

```nginx
server {
    listen 443 ssl http2;
    # ... весь блок HTTPS
}
```

Перезагрузите Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Запустите бота

```bash
docker-compose up -d
```

## 8. Проверьте работу

```bash
# Проверьте логи
docker-compose logs -f nocturna-bot

# Должны увидеть:
# INFO - Starting bot in WEBHOOK mode...
# INFO - Webhook URL: https://tg.nocturna.ru/webhook
# INFO - Webhook server started successfully

# Проверьте health endpoint
curl https://tg.nocturna.ru/health

# Проверьте webhook статус
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

## Возврат к Polling режиму

Если нужно вернуться к локальной отладке:

```bash
# Измените в .env
BOT_MODE=polling

# Удалите webhook
curl "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"

# Перезапустите бота
docker-compose restart nocturna-bot
```

## Полная документация

См. [docs/webhook-setup.md](docs/webhook-setup.md) для детальной информации.

---

**Важно:** Webhook требует:
- ✅ HTTPS (не HTTP)
- ✅ Валидный SSL сертификат
- ✅ Публичный домен
- ✅ Порт 80/443 доступны

Для локальной разработки всегда используйте `BOT_MODE=polling`.

