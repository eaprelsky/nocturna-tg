# Docker Deployment - Важные заметки

## Архитектура развертывания

Бот предназначен для работы с **внешними сервисами**, которые уже запущены на вашем сервере или в сети:

- **Nocturna Calculations API** - должен быть запущен отдельно
- **Chart Service** (опционально) - должен быть запущен отдельно
- **OpenRouter** - внешний облачный сервис

Docker Compose файл **НЕ поднимает** эти сервисы автоматически - он только запускает сам бот.

## Network Mode: Host

Бот использует `network_mode: host`, что означает:

✅ **Преимущества:**
- Прямой доступ к `localhost` сервисам
- Нет необходимости в bridge network
- Проще конфигурация для локальных сервисов
- Меньше накладных расходов

⚠️ **Особенности:**
- Все порты контейнера доступны на хосте
- Работает только на Linux (Windows/Mac имеют ограничения)
- Не работает с `networks` секцией в compose

## Конфигурация .env

### Вариант 1: Сервисы на том же хосте (рекомендуется)

```env
# Используйте localhost - network_mode: host позволяет это
NOCTURNA_API_URL=http://localhost:8000/api
CHART_SERVICE_URL=http://localhost:3000
```

### Вариант 2: Сервисы на другом сервере

```env
# Используйте внешний IP или доменное имя
NOCTURNA_API_URL=http://192.168.1.100:8000/api
CHART_SERVICE_URL=http://chart.example.com:3000
```

### Вариант 3: Без опциональных сервисов

```env
# Оставьте пустыми если не используете
CHART_SERVICE_URL=
CHART_SERVICE_API_KEY=
OPENROUTER_API_KEY=
```

## Распространенные проблемы

### Ошибка: "pull access denied for nocturna/calculations"

**Причина:** Старая версия docker-compose.yml пыталась подтянуть несуществующий образ.

**Решение:** Обновите docker-compose.yml до актуальной версии (без сервиса nocturna-calculations).

### Ошибка: "Connection refused" к API

**Причина:** Nocturna API не запущен или недоступен.

**Решение:**
```bash
# Проверьте, что API запущен
curl http://localhost:8000/api/health

# Проверьте контейнеры
docker ps | grep nocturna

# Проверьте логи API
docker logs nocturna-calculations
```

### Предупреждение: "variable is not set"

**Причина:** Опциональные переменные не заданы в .env.

**Решение:** Это нормально для опциональных переменных. Установите пустое значение в .env:
```env
CHART_SERVICE_URL=
OPENROUTER_API_KEY=
```

### Ошибка: "version is obsolete"

**Причина:** Docker Compose v2 не требует version в файле.

**Решение:** Это просто предупреждение, можно игнорировать. Или удалите строку `version: '3.8'` из docker-compose.yml.

## Проверка перед запуском

```bash
# 1. Проверьте что Nocturna API доступен
curl http://localhost:8000/api/health

# 2. Проверьте .env файл
cat .env | grep -v '^#' | grep -v '^$'

# 3. Проверьте docker-compose конфигурацию
docker compose config

# 4. Запустите бота
docker compose up -d

# 5. Проверьте логи
docker compose logs -f
```

## Альтернативная конфигурация: Bridge Network

Если вам нужна изоляция сетей, можно использовать bridge network:

```yaml
services:
  nocturna-bot:
    # ... other settings ...
    networks:
      - nocturna-network

networks:
  nocturna-network:
    external: true  # Подключиться к существующей сети
```

Тогда в .env используйте имена контейнеров:
```env
NOCTURNA_API_URL=http://nocturna-calculations:8000/api
```

## Best Practices

1. **Всегда используйте .env файл** - не хардкодьте переменные в docker-compose.yml
2. **Проверяйте доступность API** перед запуском бота
3. **Используйте docker compose logs** для отладки
4. **Устанавливайте пустые значения** для неиспользуемых опциональных переменных
5. **Используйте localhost** для локальных сервисов с network_mode: host

## Мониторинг

```bash
# Статус контейнера
docker compose ps

# Логи в реальном времени
docker compose logs -f nocturna-bot

# Использование ресурсов
docker stats nocturna-telegram-bot

# Рестарт
docker compose restart nocturna-bot

# Полная пересборка
docker compose down
docker compose build --no-cache
docker compose up -d
```

