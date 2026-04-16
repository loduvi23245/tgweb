# Инструкция по установке и запуску ВЭД-календаря

## 1. Требования

- Python 3.10 или выше
- pip (менеджер пакетов Python)
- Telegram Bot Token (получить у @BotFather)

## 2. Установка

### 2.1. Клонирование проекта

```bash
cd ved_calendar
```

### 2.2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 2.3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 3. Настройка

### 3.1. Создание файла .env

Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

### 3.2. Заполнение переменных окружения

Откройте `.env` и заполните следующие обязательные поля:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=123456789

# Admin Panel Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./ved_calendar.db
```

### 3.3. Получение Telegram Bot Token

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `TELEGRAM_BOT_TOKEN`

### 3.4. Получение Telegram ID администратора

1. Найдите бота @userinfobot в Telegram
2. Отправьте ему любое сообщение
3. Скопируйте ваш ID в `TELEGRAM_ADMIN_IDS`

## 4. Инициализация базы данных

```bash
python -c "from database.models import init_db; import asyncio; asyncio.run(init_db())"
```

## 5. Запуск приложений

### 5.1. Запуск Telegram бота

```bash
python bot/main.py
```

### 5.2. Запуск веб мини-апп

```bash
python webapp/main.py
```

Веб-приложение будет доступно по адресу: http://localhost:8000

### 5.3. Запуск админ-панели

```bash
python admin/main.py
```

Админ-панель будет доступна по адресу: http://localhost:8001/admin/login

**Данные для входа по умолчанию:**
- Логин: `admin`
- Пароль: значение из `ADMIN_PASSWORD` в `.env`

## 6. Настройка Telegram Web App

### 6.1. Добавление кнопки меню в бота

1. Откройте @BotFather
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Нажмите "Bot Settings" → "Menu Button" → "Configure Menu Button"
5. Отправьте URL вашего веб-приложения (например, https://your-domain.com)
6. Введите название кнопки (например, "Открыть календарь")

### 6.2. Настройка HTTPS

Для работы Telegram Web App требуется HTTPS. Используйте один из вариантов:

**Вариант 1: ngrok (для разработки)**
```bash
ngrok http 8000
```
Используйте полученный HTTPS URL в настройках бота.

**Вариант 2: Развертывание на сервере**
Используйте nginx + Let's Encrypt для настройки HTTPS.

## 7. Проверка работы

### 7.1. Проверка бота

1. Откройте вашего бота в Telegram
2. Нажмите `/start`
3. Проверьте работу кнопок меню
4. Попробуйте предложить мероприятие через форму

### 7.2. Проверка админ-панели

1. Откройте http://localhost:8001/admin/login
2. Войдите под администратором
3. Проверьте дашборд
4. Если есть заявки на модерацию, проверьте их

## 8. Production развертывание

### 8.1. Использование PostgreSQL

Для продакшена рекомендуется использовать PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ved_calendar
```

Установите дополнительную зависимость:
```bash
pip install psycopg2-binary
```

### 8.2. Запуск через systemd (Linux)

Создайте файлы служб:

`/etc/systemd/system/ved-calendar-bot.service`:
```ini
[Unit]
Description=VED Calendar Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ved_calendar
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/ved-calendar-webapp.service`:
```ini
[Unit]
Description=VED Calendar Web App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ved_calendar
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn webapp.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте службы:
```bash
sudo systemctl enable ved-calendar-bot
sudo systemctl enable ved-calendar-webapp
sudo systemctl start ved-calendar-bot
sudo systemctl start ved-calendar-webapp
```

## 9. Решение проблем

### Бот не запускается

Проверьте токен бота в `.env`:
```bash
echo $TELEGRAM_BOT_TOKEN
```

### Ошибки базы данных

Удалите файл базы данных и создайте заново:
```bash
rm ved_calendar.db
python -c "from database.models import init_db; import asyncio; asyncio.run(init_db())"
```

### Веб-апп не открывается в Telegram

Убедитесь, что используется HTTPS URL и он указан в настройках бота через @BotFather.

## 10. Дополнительная документация

- [Документация aiogram](https://docs.aiogram.dev/)
- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация SQLAlchemy](https://docs.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
