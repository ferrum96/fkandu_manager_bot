# Деплой всех сервисов на VPS

## Структура проекта

```
BotsRepo/
├── kanban_board/          # Next.js kanban доска (порт 3000)
├── fkandu_manager_bot/    # Python бот + дашборд (порты 8088, 8000)
├── pubg_moderator_bot/    # Python бот
├── nginx/                 # Конфигурация nginx
├── docker-compose.yml     # Основной файл деплоя
├── deploy.sh             # Скрипт деплоя
├── ssl-setup.sh          # Скрипт настройки SSL
└── .dockerignore         # Игнорируемые файлы
```

## Быстрый старт

1. **Клонируйте репозиторий на сервер:**
```bash
git clone <your-repo-url>
cd BotsRepo
```

2. **Настройте домены:**
Отредактируйте файлы:
- `nginx/nginx.conf` — замените `yourdomain.com` на ваш домен
- `ssl-setup.sh` — замените `your-email@domain.com` и домены

3. **Создайте .env файлы:**
```bash
cp fkandu_manager_bot/.env.example fkandu_manager_bot/.env
cp pubg_moderator_bot/.env.example pubg_moderator_bot/.env
# Заполните переменные окружения
```

4. **Настройте DNS:**
```
kanban.yourdomain.com     → your-server-ip
dashboard.yourdomain.com  → your-server-ip
files.yourdomain.com      → your-server-ip
```

5. **Запустите деплой:**
```bash
./deploy.sh
```

6. **Получите SSL сертификаты:**
```bash
./ssl-setup.sh
```

## SSL сертификаты (Let's Encrypt)

### Автоматическое получение

```bash
./ssl-setup.sh
```

Скрипт автоматически:
- Получает сертификаты для всех доменов
- Настраивает HTTPS в nginx
- Обновляет сертификаты каждые 12 часов

### Ручное обновление

```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

### Проверка сертификатов

```bash
docker-compose run --rm certbot certificates
```

## Сервисы

| Сервис | Описание | URL |
|--------|----------|-----|
| nginx | Reverse proxy + SSL | 80, 443 |
| kanban-board | Kanban доска (Next.js) | https://kanban.yourdomain.com |
| fkandu-bot | Telegram бот FKandu | - |
| fkandu-dashboard | Дашборд FKandu (FastAPI) | https://dashboard.yourdomain.com |
| fkandu-files | Файловый сервер | https://files.yourdomain.com |
| pubg-bot | Telegram бот PUBG | - |

## Команды

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Просмотра логов
docker-compose logs -f

# Перезапуск конкретного сервиса
docker-compose restart kanban

# Сборка без кеша
docker-compose build --no-cache

# Обновление SSL сертификатов
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## Хранение данных

| Сервис | Данные | Путь в контейнере |
|--------|--------|-------------------|
| kanban-board | SQLite БД | /app/data/prod.db |
| fkandu | SQLite БД | /app/db/leads.db |
| pubg-bot | Данные | /app/data/ |

## Устранение проблем

### Сертификат не получается

1. Проверьте DNS записи
2. Убедитесь, что порт 80 доступен извне
3. Проверьте логи: `docker-compose logs certbot`

### nginx не запускается

1. Проверьте конфигурацию: `docker-compose exec nginx nginx -t`
2. Проверьте логи: `docker-compose logs nginx`

### Обновление сертификатов

Сертификаты обновляются автоматически каждые 12 часов.
Для ручного обновления:
```bash
docker-compose run --rm certbot renew --force-renewal
docker-compose restart nginx
```
