# Быстрый старт в WSL

## Шаг 1: Убедитесь, что вы в правильной директории

```bash
cd /mnt/d/YandexDisk/cloudwork/personal/experiments/astrologist/nocturna-tg
pwd
```

## Шаг 2: Создайте conda окружение

```bash
conda create -n nocturna-tg python=3.11 -y
```

## Шаг 3: Активируйте окружение

```bash
conda activate nocturna-tg
```

## Шаг 4: Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Шаг 5: Проверьте, что файл .env существует

```bash
cat .env
```

Вы должны увидеть конфигурацию с вашим токеном бота.

## Шаг 6: Убедитесь, что сервер nocturna-calculations запущен

Проверьте доступность API:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ: `{"status":"healthy"}`

## Шаг 7: Запустите бота

```bash
python -m src.main
```

Вы должны увидеть:
```
INFO - Loading configuration...
INFO - Initializing Nocturna API client: http://localhost:8000/api
INFO - Initializing services...
INFO - Initializing bot handlers...
INFO - Creating Telegram application...
INFO - Starting bot polling...
INFO - Bot is running. Press Ctrl+C to stop.
```

## Шаг 8: Проверьте работу бота

1. Откройте Telegram
2. Найдите `@nocturna_dev_bot`
3. Отправьте `/start`
4. Попробуйте `/transit`

## Команды бота

- `/start` - Приветствие
- `/transit` - Текущие позиции планет и аспекты
- `/help` - Справка

## Остановка бота

Нажмите `Ctrl+C` в терминале, где запущен бот.

## Troubleshooting

### "ModuleNotFoundError"
Убедитесь, что активировано окружение:
```bash
conda activate nocturna-tg
```

### "Connection refused" к API
Проверьте, что сервер nocturna-calculations запущен на порту 8000:
```bash
curl http://localhost:8000/health
```

### Бот не отвечает в Telegram
1. Проверьте логи в консоли
2. Убедитесь, что токен правильный в `.env`
3. Проверьте интернет-соединение

## Структура проекта

```
nocturna-tg/
├── src/
│   ├── api/
│   │   └── nocturna_client.py      # Клиент Nocturna API
│   ├── bot/
│   │   └── handlers.py              # Обработчики команд
│   ├── services/
│   │   └── transit_service.py       # Бизнес-логика
│   ├── formatters/
│   │   └── russian_formatter.py     # Форматирование на русском
│   ├── config.py                    # Конфигурация
│   └── main.py                      # Точка входа
├── .env                             # Переменные окружения
├── requirements.txt                 # Зависимости
└── README.md
```

## Следующие шаги

После успешного запуска можно:
1. Добавить поддержку натальных карт пользователей
2. Добавить базу данных для персистентного хранилища
3. Добавить анализ транзитов к натальной карте
4. Добавить другие команды и функции

