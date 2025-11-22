# Quick Commands Cheatsheet

Шпаргалка с основными командами для работы с Nocturna Telegram Bot в webhook режиме.

## 🚀 Первоначальная настройка

```bash
# Клонировать репозиторий
git clone <repo-url>
cd nocturna-tg

# Создать .env файл
cp .env.polling.example .env  # для локальной разработки
# или
nano .env  # создать вручную для webhook

# Сгенерировать webhook secret
openssl rand -hex 32

# Пересобрать Docker образ
docker-compose build
```

## 🔧 Nginx

```bash
# Установить конфиг
sudo cp nginx-tg.nocturna.ru.conf /etc/nginx/sites-available/nocturna-tg
sudo ln -s /etc/nginx/sites-available/nocturna-tg /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезагрузить Nginx
sudo systemctl reload nginx

# Просмотр логов
sudo tail -f /var/log/nginx/tg.nocturna.ru_access.log
sudo tail -f /var/log/nginx/tg.nocturna.ru_error.log
```

## 🔒 SSL (Certbot)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d tg.nocturna.ru

# Проверить автообновление
sudo certbot renew --dry-run

# Список сертификатов
sudo certbot certificates

# Принудительное обновление
sudo certbot renew
```

## 🐳 Docker

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Рестарт
docker-compose restart nocturna-bot

# Пересборка и запуск
docker-compose up -d --build

# Логи (последние 100 строк)
docker-compose logs --tail=100 nocturna-bot

# Логи (real-time)
docker-compose logs -f nocturna-bot

# Логи с временными метками
docker-compose logs -t nocturna-bot

# Статус контейнеров
docker-compose ps

# Вход в контейнер
docker-compose exec nocturna-bot bash

# Удалить контейнеры и volumes
docker-compose down -v
```

## 🤖 Telegram Bot API

```bash
# Заменить YOUR_BOT_TOKEN на реальный токен

# Информация о webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"

# Установить webhook вручную
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -d "url=https://tg.nocturna.ru/webhook" \
  -d "secret_token=YOUR_SECRET"

# Удалить webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"

# Информация о боте
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getMe"

# Получить обновления (только в polling режиме)
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates"
```

## ✅ Проверка работы

```bash
# Health check
curl https://tg.nocturna.ru/health

# Проверить, что порт открыт
sudo netstat -tlnp | grep 8080

# Проверить Docker сеть
docker network ls
docker network inspect nocturna-tg_default

# Проверить, что бот слушает порт
docker-compose exec nocturna-bot netstat -tlnp

# Проверить SSL сертификат
openssl s_client -connect tg.nocturna.ru:443 -servername tg.nocturna.ru
```

## 🔄 Переключение режимов

### Polling → Webhook

```bash
# 1. Обновить .env
nano .env
# Изменить: BOT_MODE=webhook

# 2. Обновить docker-compose.yml
# Закомментировать: network_mode: host
# Раскомментировать: ports: - "8080:8080"

# 3. Перезапустить
docker-compose restart nocturna-bot

# 4. Проверить
curl https://tg.nocturna.ru/health
```

### Webhook → Polling

```bash
# 1. Удалить webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"

# 2. Обновить .env
nano .env
# Изменить: BOT_MODE=polling

# 3. Обновить docker-compose.yml
# Раскомментировать: network_mode: host
# Закомментировать: ports

# 4. Перезапустить
docker-compose restart nocturna-bot
```

## 🐛 Отладка

```bash
# Проверить переменные окружения в контейнере
docker-compose exec nocturna-bot env | grep BOT_MODE
docker-compose exec nocturna-bot env | grep WEBHOOK

# Проверить, что бот запущен
docker-compose ps

# Проверить последние ошибки
docker-compose logs --tail=50 nocturna-bot | grep ERROR

# Проверить последние предупреждения
docker-compose logs --tail=50 nocturna-bot | grep WARNING

# Полная очистка и перезапуск
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Проверка DNS
nslookup tg.nocturna.ru
dig tg.nocturna.ru

# Проверка портов
sudo ufw status
sudo iptables -L -n
```

## 📊 Мониторинг

```bash
# Использование ресурсов
docker stats nocturna-telegram-bot

# Размер образов
docker images | grep nocturna

# Размер контейнеров
docker ps -s

# Дисковое пространство
df -h

# Использование памяти
free -h

# Процессы в контейнере
docker-compose top nocturna-bot
```

## 🧹 Очистка

```bash
# Удалить неиспользуемые образы
docker image prune

# Удалить неиспользуемые контейнеры
docker container prune

# Удалить все (осторожно!)
docker system prune -a

# Очистить логи Docker
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'
```

## 🔐 Безопасность

```bash
# Проверить открытые порты
sudo netstat -tulpn | grep LISTEN

# Проверить UFW
sudo ufw status verbose

# Включить UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Проверить fail2ban (если установлен)
sudo fail2ban-client status

# Обновить пакеты
sudo apt update && sudo apt upgrade -y
```

## 📝 Обслуживание

```bash
# Обновить код
git pull origin master

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Пересобрать и перезапустить
docker-compose up -d --build

# Создать backup .env
cp .env .env.backup.$(date +%Y%m%d)

# Создать backup конфигурации Nginx
sudo cp /etc/nginx/sites-available/nocturna-tg /etc/nginx/sites-available/nocturna-tg.backup.$(date +%Y%m%d)

# Ротация логов вручную
sudo logrotate -f /etc/logrotate.d/nginx
```

## 🆘 Аварийное восстановление

```bash
# 1. Остановить всё
docker-compose down
sudo systemctl stop nginx

# 2. Проверить конфигурации
sudo nginx -t
docker-compose config

# 3. Откатить изменения
git reset --hard HEAD^

# 4. Восстановить из backup
cp .env.backup.20251122 .env

# 5. Запустить заново
sudo systemctl start nginx
docker-compose up -d

# 6. Переключиться на polling если нужно
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"
# Изменить BOT_MODE=polling в .env
docker-compose restart nocturna-bot
```

---

**Совет:** Сохраните этот файл в закладках для быстрого доступа к командам!

