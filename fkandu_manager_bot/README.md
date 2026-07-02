# fkandu_manager_bot

Telegram-бот и CRM-дашборд для канала **«Дети и Желания»** ([@fkandu](https://t.me/fkandu)).

## Структура

```
fkandu_manager_bot/
├── bot/                   # Telegram-бот (aiogram)
│   ├── main.py            # Точка входа + файловый сервер
│   ├── config.py          # Конфигурация из .env
│   ├── database.py        # SQLite
│   ├── keyboards.py       # Кнопки
│   └── handlers/
│       └── lead_form.py   # Обработка заявок
├── dashboard/
│   ├── backend/           # FastAPI (API для дашборда)
│   │   ├── api.py
│   │   └── Dockerfile
│   └── frontend/          # Next.js (дашборд)
│       ├── src/
│       │   ├── components/
│       │   └── app/
│       └── Dockerfile
├── data/                  # SQLite база (leads.db)
├── .env                   # Переменные окружения
├── requirements.txt       # Python зависимости
└── Dockerfile
```

## Возможности

- **Бот** — принимает заявки через Telegram (категория → товар → бюджет → сроки), оценивает лид, сохраняет в SQLite, уведомляет админа
- **Файловый сервер** — отдаёт файлы из БД по URL (`/files/{file_id}`)
- **Дашборд** — 5 страниц: метрики, канбан с drag-and-drop, список заявок с фильтрами, горячие лиды, аналитика

## Запуск (разработка)

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Настроить .env
cp .env.example .env
# Заполните BOT_TOKEN, ADMIN_ID, HOSTNAME

# 3. Запустить бота (включает файловый сервер на порту 8088)
python -m bot.main

# 4. Запустить API дашборда (отдельный терминал)
cd dashboard/backend
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000

# 5. Запустить фронтенд дашборда (отдельный терминал)
cd dashboard/frontend
npm install
npm run dev
```

## Docker

```bash
# Из корня BotsRepo/
docker-compose up -d --build
```

Сервисы (порты на хосте):
- `fkandu-nginx` — reverse proxy → **http://IP** (порт 80)
- `fkandu-frontend` — дашборд → `127.0.0.1:8000` (через nginx)
- `fkandu-backend` — API → `127.0.0.1:8001` (через nginx `/api/`)
- `fkandu-bot` — бот + файловый сервер → порт 8088 (через nginx `/files/`)

Снаружи открывайте только порт **80** в firewall хостера:

```bash
# Проверка с Mac
curl -I http://2.26.249.118
curl http://2.26.249.118/api/stats
```

Запуск nginx:

```bash
cd fkandu_manager_bot
docker compose up -d nginx
```

Если порт 80 занят:

```bash
ss -tlnp | grep :80
systemctl stop nginx   # если системный nginx мешает
```

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_ID` | Telegram ID администратора |
| `HOSTNAME` | IP-адрес сервера (для файлового сервера) |
