# Token Refresh Flow Guide

## Типы токенов и их сроки действия

### 1. User Access Token (от `/api/auth/login`)
- **Срок действия**: 15 минут
- **Refresh Token**: 7 дней
- **Использование**: Админские операции, фронтенд приложения
- **Обновление**: Через refresh token

### 2. Service Token (для ботов и сервисов)
- **Срок действия**: 30-365 дней или eternal (вечный)
- **Использование**: Долгосрочная работа ботов, backend-to-backend интеграции
- **Обновление**: Через `/api/auth/service-token/refresh` для получения access token

## Флоу обновления User Access Token

### Шаг 1: Получение токенов при логине

```python
import requests

# Логин
response = requests.post(
    "https://your-api-server.com/api/auth/login",
    data={
        "username": "admin@example.com",
        "password": "password123"
    }
)

tokens = response.json()
access_token = tokens["access_token"]      # Живет 15 минут
refresh_token = tokens["refresh_token"]    # Живет 7 дней
```

### Шаг 2: Обновление Access Token через Refresh Token

```python
# Когда access token истекает (каждые 15 минут)
response = requests.post(
    "https://your-api-server.com/api/auth/refresh",
    params={"refresh_token": refresh_token}
)

new_tokens = response.json()
access_token = new_tokens["access_token"]      # Новый access token
refresh_token = new_tokens["refresh_token"]    # Новый refresh token (обновляется)
```

### Шаг 3: Если Refresh Token истек (7 дней)

Если refresh token истек, нужно заново логиниться:

```python
# Полный перелогин
response = requests.post(
    "https://your-api-server.com/api/auth/login",
    data={
        "username": "admin@example.com",
        "password": "password123"
    }
)
```

## Флоу для Service Token (Рекомендуется для ботов)

### Вариант 1: Прямое использование Service Token (Текущий подход)

Если service token долгоживущий (90+ дней или eternal), можно использовать его напрямую:

```python
# В .env
NOCTURNA_SERVICE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Живет 90 дней

# В коде - используется напрямую
headers = {"Authorization": f"Bearer {service_token}"}
```

**Преимущества:**
- Простота
- Не требует обновления долгое время
- Подходит для ботов

**Недостатки:**
- Если токен истечет, нужно создать новый вручную

### Вариант 2: Двухуровневая система (Service Token → Access Token)

Для дополнительной безопасности можно использовать service token для получения короткоживущих access tokens:

```python
import requests
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self, api_url: str, service_token: str):
        self.api_url = api_url.rstrip("/")
        self.service_token = service_token
        self.access_token = None
        self.access_token_expires_at = None
    
    def get_access_token(self) -> str:
        """Get valid access token, refreshing if needed."""
        now = datetime.now()
        
        # Если токен отсутствует или истекает в течение 5 минут
        if (self.access_token is None or 
            self.access_token_expires_at is None or
            self.access_token_expires_at - now < timedelta(minutes=5)):
            self._refresh_access_token()
        
        return self.access_token
    
    def _refresh_access_token(self):
        """Refresh access token using service token."""
        response = requests.post(
            f"{self.api_url}/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {self.service_token}"}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        expires_in = data.get("expires_in", 900)  # По умолчанию 15 минут
        self.access_token_expires_at = datetime.now() + timedelta(seconds=expires_in)

# Использование
token_manager = TokenManager(
    api_url="https://your-api-server.com/api",
    service_token=os.getenv("NOCTURNA_SERVICE_TOKEN")
)

# При каждом запросе
access_token = token_manager.get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}
```

**Преимущества:**
- Более безопасно (короткоживущие токены)
- Автоматическое обновление
- Service token не передается в каждом запросе

**Недостатки:**
- Более сложная реализация
- Дополнительный запрос при первом использовании

## Рекомендации для вашего бота

### Текущая ситуация

Вы используете **Service Token напрямую**, что правильно для бота. Если токен создан на 90 дней или как eternal, текущий подход достаточен.

### Когда нужен автоматический refresh

1. **Если service token короткоживущий** (30 дней) - можно добавить автоматическое обновление
2. **Если нужна дополнительная безопасность** - использовать двухуровневую систему
3. **Если токен может истечь во время работы бота** - добавить обработку 401 ошибок

### Улучшение текущего клиента (опционально)

Можно добавить обработку 401 ошибок с автоматическим refresh:

```python
# В NocturnaClient._make_request добавить обработку 401
if response.status_code == 401:
    # Попытка обновить access token через service token
    if self.service_token:
        try:
            refresh_response = requests.post(
                f"{self.api_url}/auth/service-token/refresh",
                headers={"Authorization": f"Bearer {self.service_token}"}
            )
            if refresh_response.status_code == 200:
                new_access_token = refresh_response.json()["access_token"]
                self.session.headers["Authorization"] = f"Bearer {new_access_token}"
                # Повторить запрос
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            else:
                raise NocturnaAPIError("Service token expired or invalid")
        except Exception as e:
            raise NocturnaAPIError(f"Token refresh failed: {str(e)}")
```

## Практические примеры

### Пример 1: Создание долгоживущего токена для бота

```bash
# Создать токен на 365 дней
python scripts/create_remote_token.py \
  https://your-api-server.com/api \
  admin@example.com \
  password123 \
  365
```

### Пример 2: Проверка срока действия токена

```python
import jwt
from datetime import datetime

def check_token_expiry(token: str):
    """Check when token expires."""
    payload = jwt.decode(token, options={"verify_signature": False})
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        exp_date = datetime.fromtimestamp(exp_timestamp)
        days_left = (exp_date - datetime.now()).days
        print(f"Token expires in {days_left} days")
        return days_left
    return None
```

### Пример 3: Автоматическое создание нового токена перед истечением

```python
import os
import subprocess

def ensure_valid_token(api_url: str, admin_email: str, admin_password: str):
    """Ensure service token is valid, create new one if expiring soon."""
    token = os.getenv("NOCTURNA_SERVICE_TOKEN")
    days_left = check_token_expiry(token)
    
    if days_left and days_left < 7:  # Меньше недели
        print(f"Token expires in {days_left} days, creating new one...")
        # Создать новый токен через скрипт
        subprocess.run([
            "python", "scripts/create_remote_token.py",
            api_url, admin_email, admin_password, "90"
        ])
```

## Выводы

1. **Для бота используйте Service Token** - он долгоживущий и не требует частого обновления
2. **Создавайте токен на 90+ дней** или eternal для долгосрочной работы
3. **Текущая реализация достаточна** - если токен долгоживущий, не нужен автоматический refresh
4. **Мониторьте срок действия** - проверяйте токен при старте бота (как в `main.py`)
5. **Админский access token** нужен только для разовых операций (создание service token), не для постоянной работы бота

