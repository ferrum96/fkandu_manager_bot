# Модератор клана BB — Telegram-бот

Бот для набора в игровой клан: проводит опрос с кнопками, ведёт базу участников, синхронизирует данные с Google Sheets и помогает модерировать Telegram-канал.

## Возможности

### Опрос для новичков (`/start`)
1. **Возраст** — набор с 21 года
2. **Уровень** — от 100+
3. **Активность** — минимум раз в неделю
4. **Данные** — ник в игре, имя, Discord
5. **Режим** — FPP / TPP / Mixed mode
6. **Финал** — кнопки на Telegram-канал и Discord

**Правила:**
- 2 попытки пройти опрос; после второго провала — автоматический чёрный список
- Пользователи из чёрного списка не могут начать опрос

### Админ-команды
| Команда | Описание |
|---------|----------|
| `/members` | Список участников: TG / игровой ник / Discord |
| `/stats` | Статистика FPP vs TPP |
| `/search <запрос>` | Поиск по никам и именам |
| `/blacklist` | Просмотр чёрного списка |
| `/unblacklist <id>` | Снять блокировку |
| `/kick_non_members` | Удалить из канала тех, кто не в базе клана |
| `/admin_help` | Справка по командам |

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните .env
python -m bot.main
```

## Настройка

### 1. Telegram Bot
1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Скопируйте токен в `BOT_TOKEN`
3. Узнайте свой Telegram ID (например, через [@userinfobot](https://t.me/userinfobot)) и добавьте в `ADMIN_IDS`
4. Добавьте бота **администратором** в канал клана с правами:
   - Удаление участников
   - Блокировка пользователей
   - Приглашение пользователей (опционально)
5. Укажите `CHANNEL_ID` (для каналов начинается с `-100...`)

> **Важно:** включите в BotFather режим **Privacy Mode → Disabled**, если бот должен видеть все сообщения в группах. Для личных чатов это не нужно.

### 2. Google Sheets (опционально)
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API
3. Создайте Service Account и скачайте JSON-ключ → `credentials.json`
4. Создайте таблицу и дайте service account доступ на редактирование
5. Скопируйте ID таблицы из URL в `GOOGLE_SHEET_ID`

Колонки создаются автоматически: TG Nick, In-game Nick, Discord Nick, Real Name, Perspective, User ID, Date.

### 3. Ссылки
- `TELEGRAM_CHANNEL_LINK` — ссылка на канал клана
- `DISCORD_LINK` — invite-ссылка Discord

## Структура проекта

```
bot/
├── main.py           # точка входа
├── config.py         # конфигурация
├── database.py       # SQLite
├── google_sheets.py  # синхронизация с таблицей
├── messages.py       # тексты сообщений
├── keyboards.py      # кнопки
└── handlers/
    ├── survey.py     # опрос
    └── admin.py      # модерация
```

Данные хранятся в `data/bot.db`.

## Автоматический чёрный список

Пользователь попадает в чёрный список если:
- провалил опрос 2 раза
- был удалён из канала (бот отслеживает через `chat_member` updates)
- удалён командой `/kick_non_members`

Снять блокировку: `/unblacklist <telegram_user_id>`
