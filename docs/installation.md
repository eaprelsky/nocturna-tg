# Инструкция по установке и запуску

## Шаг 1: Создание окружения

```bash
make setup
```

Эта команда создаст conda окружение с именем `nocturna-tg` и Python 3.11.

## Шаг 2: Активация окружения

```bash
conda activate nocturna-tg
```

## Шаг 3: Установка зависимостей

```bash
make install
```

Эта команда установит все необходимые Python пакеты из `requirements.txt`.

## Шаг 4: Проверка конфигурации

Файл `.env` уже создан с вашими учетными данными:
- Token: `8438385382:AAHxYsqXtXoR6BIFIWPyF8xjLaY_MT8aLA0`
- Username: `nocturna_dev_bot`
- API URL: `http://localhost:8000/api`

## Шаг 5: Убедитесь, что сервер nocturna-calculations запущен

Сервер должен быть доступен по адресу `http://localhost:8000`

Можете проверить:
```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{"status": "healthy"}
```

## Шаг 6: Запуск бота

```bash
make run
```

Или напрямую:
```bash
python -m src.main
```

## Проверка работы

1. Откройте Telegram
2. Найдите бота `@nocturna_dev_bot`
3. Отправьте команду `/start`
4. Попробуйте команду `/transit`

## Структура проекта

```
nocturna-tg/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── nocturna_client.py      # Клиент для Nocturna API
│   ├── bot/
│   │   ├── __init__.py
│   │   └── handlers.py              # Обработчики команд бота
│   ├── services/
│   │   ├── __init__.py
│   │   └── transit_service.py       # Бизнес-логика транзитов
│   ├── formatters/
│   │   ├── __init__.py
│   │   └── russian_formatter.py     # Форматирование на русском
│   ├── __init__.py
│   ├── config.py                    # Конфигурация
│   └── main.py                      # Точка входа
├── tests/                           # Тесты
├── .env                             # Переменные окружения
├── .gitignore
├── requirements.txt
├── Makefile
└── README.md
```

## Полезные команды

```bash
make help       # Показать все команды
make test       # Запустить тесты
make format     # Форматировать код
make lint       # Проверить код линтерами
make clean      # Удалить временные файлы
```

## Команды бота

- `/start` - Приветствие и информация о боте
- `/transit` - Текущие позиции планет и аспекты
- `/help` - Справка по командам

## Troubleshooting

### Ошибка "Could not validate credentials"

Проверьте:
1. Правильность токена в `.env`
2. Доступность сервера nocturna-calculations

### Ошибка подключения к API

Убедитесь, что:
1. Сервер nocturna-calculations запущен
2. URL в `.env` правильный: `http://localhost:8000/api`

### Бот не отвечает

1. Проверьте логи в консоли
2. Убедитесь, что бот активен в Telegram
3. Проверьте интернет-соединение

