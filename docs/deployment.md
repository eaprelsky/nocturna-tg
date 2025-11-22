# Развертывание в production

Руководство по развертыванию Nocturna Telegram Bot в продакшен окружение.

## Содержание

- [Предварительные требования](#предварительные-требования)
- [Вариант 1: Docker (рекомендуется)](#вариант-1-docker-рекомендуется)
- [Вариант 2: Традиционное развертывание](#вариант-2-традиционное-развертывание)
- [Настройка переменных окружения](#настройка-переменных-окружения)
- [Мониторинг и логи](#мониторинг-и-логи)
- [Обновление и backup](#обновление-и-backup)
- [Troubleshooting](#troubleshooting)

---

## Предварительные требования

### Системные требования

- **ОС**: Linux (Ubuntu 20.04+, Debian 11+) или Windows Server
- **RAM**: минимум 512MB, рекомендуется 1GB
- **CPU**: 1 core минимум, 2 cores рекомендуется
- **Диск**: 2GB свободного пространства
- **Интернет**: стабильное подключение

### Зависимости

- **Docker** 20.10+ и **Docker Compose** 1.29+ (для Docker варианта)
- **Python** 3.11+ (для традиционного варианта)
- **Git** для клонирования репозитория
- **Доступ к серверу** Nocturna Calculations API

### Внешние сервисы

1. **Telegram Bot Token** - получить у [@BotFather](https://t.me/botfather)
2. **Nocturna Calculations API** - должен быть запущен и доступен
3. **Service Token** - создать через `scripts/create_remote_token.py`
4. **OpenRouter API** (опционально) - для LLM интерпретаций

---

## Вариант 1: Docker (рекомендуется)

Самый простой и надежный способ развертывания.

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/your-org/nocturna-tg.git
cd nocturna-tg
```

### Шаг 2: Настройка переменных окружения

```bash
cp .env.example .env
nano .env  # или vim, code и т.д.
```

Заполните обязательные переменные:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_bot_name

# Если Nocturna API на том же сервере - используйте localhost
NOCTURNA_API_URL=http://localhost:8000/api
# Если на другом сервере - используйте его адрес
# NOCTURNA_API_URL=http://your-nocturna-server:8000/api

NOCTURNA_SERVICE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Опциональные переменные (оставьте пустыми если не используете)
CHART_SERVICE_URL=
CHART_SERVICE_API_KEY=
OPENROUTER_API_KEY=

LOG_LEVEL=INFO
```

> **Важно:** Docker Compose использует `network_mode: host`, поэтому бот может обращаться к сервисам на `localhost` напрямую.

### Шаг 3: Запуск через Docker Compose

```bash
docker-compose up -d
```

Проверка статуса:

```bash
docker-compose ps
docker-compose logs -f nocturna-bot
```

### Шаг 4: Проверка работы

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Попробуйте `/transit`

### Управление контейнером

```bash
# Остановка
docker-compose stop

# Рестарт
docker-compose restart

# Остановка и удаление
docker-compose down

# Просмотр логов
docker-compose logs -f

# Обновление образа
docker-compose pull
docker-compose up -d
```

---

## Вариант 2: Традиционное развертывание

Развертывание без Docker (например, на VPS).

### Шаг 1: Подготовка системы

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### Шаг 2: Создание пользователя для бота

```bash
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

### Шаг 3: Клонирование и установка

```bash
git clone https://github.com/your-org/nocturna-tg.git
cd nocturna-tg

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных

```bash
cp .env.example .env
nano .env
```

### Шаг 5: Создание systemd сервиса

Создайте файл `/etc/systemd/system/nocturna-bot.service`:

```ini
[Unit]
Description=Nocturna Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/nocturna-tg
Environment="PATH=/home/botuser/nocturna-tg/venv/bin"
ExecStart=/home/botuser/nocturna-tg/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nocturna-bot
sudo systemctl start nocturna-bot
```

Проверка статуса:

```bash
sudo systemctl status nocturna-bot
sudo journalctl -u nocturna-bot -f
```

---

## Настройка переменных окружения

### Обязательные переменные

```env
# Telegram
TELEGRAM_BOT_TOKEN=<ваш токен от BotFather>
TELEGRAM_BOT_USERNAME=<имя бота без @>

# Nocturna API
NOCTURNA_API_URL=http://your-server:8000/api
NOCTURNA_SERVICE_TOKEN=<service token>

# Логирование
LOG_LEVEL=INFO
```

### Опциональные переменные

```env
# LLM интерпретации (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-haiku-4.5

# Chart Service (если используется)
CHART_SERVICE_URL=http://chart-service:3000
CHART_SERVICE_API_KEY=<api ключ>
```

### Создание Service Token

Если у вас еще нет service token:

```bash
# Локально или на сервере
python scripts/create_remote_token.py \
  https://your-nocturna-server.com/api \
  admin@example.com \
  your_password \
  365  # дней действия
```

Скопируйте полученный токен в `.env`

---

## Мониторинг и логи

### Просмотр логов

**Docker:**
```bash
docker-compose logs -f nocturna-bot
```

**Systemd:**
```bash
sudo journalctl -u nocturna-bot -f
```

**Файлы логов:**
```bash
tail -f logs/nocturna-bot.log
```

### Уровни логирования

Установите в `.env`:

```env
LOG_LEVEL=DEBUG   # Подробные логи для отладки
LOG_LEVEL=INFO    # Стандартный уровень (рекомендуется)
LOG_LEVEL=WARNING # Только предупреждения и ошибки
LOG_LEVEL=ERROR   # Только ошибки
```

### Мониторинг здоровья

Создайте скрипт проверки:

```bash
#!/bin/bash
# check_bot.sh

if docker ps | grep -q nocturna-telegram-bot; then
    echo "Bot is running"
    exit 0
else
    echo "Bot is not running! Restarting..."
    docker-compose restart nocturna-bot
    exit 1
fi
```

Добавьте в cron для автоматической проверки:

```bash
*/5 * * * * /home/botuser/check_bot.sh >> /var/log/bot-check.log 2>&1
```

---

## Обновление и backup

### Обновление бота

**Docker вариант:**

```bash
cd /path/to/nocturna-tg
git pull origin master
docker-compose build
docker-compose up -d
```

**Традиционный вариант:**

```bash
cd /home/botuser/nocturna-tg
git pull origin master
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart nocturna-bot
```

### Backup конфигурации

Регулярно сохраняйте:

```bash
# Backup .env файла
cp .env .env.backup.$(date +%Y%m%d)

# Backup логов
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Копирование на другой сервер
scp .env.backup.* user@backup-server:/backups/nocturna/
```

### Откат к предыдущей версии

```bash
git log --oneline  # Посмотреть коммиты
git checkout <commit-hash>
docker-compose up -d --build
```

---

## Troubleshooting

### Бот не запускается

**Проблема:** Ошибка при старте

**Решение:**
1. Проверьте логи: `docker-compose logs nocturna-bot`
2. Убедитесь, что все переменные в `.env` заполнены
3. Проверьте токен: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"`

### Бот не отвечает на команды

**Проблема:** Бот онлайн, но не реагирует

**Решение:**
1. Проверьте доступность Nocturna API
2. Проверьте срок действия service token
3. Посмотрите логи на ошибки API

```bash
# Проверка API
curl http://your-server:8000/api/health

# Проверка токена
python scripts/check_token.py
```

### Ошибки подключения к API

**Проблема:** `Connection refused` или `Timeout`

**Решение:**
1. Убедитесь, что Nocturna Calculations API запущен
2. Проверьте URL в `.env`
3. Проверьте файрволл и сетевые правила

```bash
# Проверка доступности
curl -v http://your-server:8000/api/health

# Проверка из контейнера
docker-compose exec nocturna-bot curl http://nocturna-calculations:8000/health
```

### Высокое использование памяти

**Проблема:** Контейнер использует много RAM

**Решение:**
1. Установите лимиты в `docker-compose.yml`
2. Проверьте логи на утечки памяти
3. Перезапустите контейнер

```bash
# Мониторинг ресурсов
docker stats nocturna-telegram-bot

# Рестарт с очисткой
docker-compose down
docker-compose up -d
```

### LLM интерпретации не работают

**Проблема:** Бот показывает данные, но без интерпретации

**Решение:**
1. Проверьте наличие `OPENROUTER_API_KEY` в `.env`
2. Проверьте баланс на OpenRouter
3. Проверьте логи на ошибки API

```bash
# Тест OpenRouter API
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## Безопасность

### Рекомендации

1. **Не храните .env в Git** - файл уже в `.gitignore`
2. **Используйте сильные пароли** для admin аккаунта
3. **Регулярно обновляйте service token** (каждые 90 дней)
4. **Настройте файрволл** - разрешите только нужные порты
5. **Используйте HTTPS** для API серверов
6. **Включите 2FA** для доступа к серверу

### Настройка файрволла (UFW)

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # Nocturna API (если на том же сервере)
sudo ufw status
```

---

## Масштабирование

### Несколько инстансов бота

Telegram bot API поддерживает только один активный инстанс на токен. Для высокой доступности используйте:

1. **Мониторинг и автоматический рестарт**
2. **Backup сервер** в режиме standby
3. **Kubernetes** для оркестрации (advanced)

### Горизонтальное масштабирование API

Если Nocturna API перегружен:

1. Запустите несколько инстансов API
2. Используйте Load Balancer (nginx, HAProxy)
3. Настройте бота на использование LB endpoint

---

## Дополнительные ресурсы

- [Установка](installation.md) - детальная инструкция по установке
- [Быстрый старт](quickstart.md) - быстрое начало работы
- [Интеграция с LLM](llm-integration.md) - настройка OpenRouter
- [Token Refresh Flow](token-refresh-flow.md) - управление токенами

---

**Документация обновлена:** 2025-11-21  
**Версия:** 1.0.0

