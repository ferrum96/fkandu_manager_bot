#!/bin/bash

echo "=== Деплой всех сервисов ==="
echo ""

# Проверка наличия .env файлов
echo "Проверка .env файлов..."
for dir in fkandu_manager_bot pubg_moderator_bot; do
    if [ ! -f "$dir/.env" ]; then
        echo "❌ Отсутствует $dir/.env"
        echo "   Скопируйте $dir/.env.example в $dir/.env и заполните"
        exit 1
    fi
done
echo "✅ Все .env файлы найдены"
echo ""

# Создание директорий для данных
echo "Создание директорий для данных..."
mkdir -p kanban_board/data
mkdir -p fkandu_manager_bot/db
mkdir -p pubg_moderator_bot/data
mkdir -p nginx/certs
mkdir -p nginx/www
echo "✅ Директории созданы"
echo ""

# Сборка и запуск
echo "Сборка и запуск контейнеров..."
docker-compose up -d --build
echo ""

# Проверка статуса
echo "Проверка статуса контейнеров..."
docker-compose ps
echo ""

# Проверка наличия SSL сертификатов
if [ ! -f "nginx/certs/live/kanban.yourdomain.com/fullchain.pem" ]; then
    echo "⚠️  SSL сертификаты не найдены"
    echo "   Запустите ./ssl-setup.sh для получения сертификатов"
    echo ""
fi

echo "=== Деплой завершен ==="
echo ""
echo "Доступные сервисы:"
echo "  - Kanban Board:     https://kanban.yourdomain.com"
echo "  - FKandu Dashboard: https://dashboard.yourdomain.com"
echo "  - FKandu Files:     https://files.yourdomain.com"
echo ""
echo "Для просмотра логов: docker-compose logs -f"
echo "Для остановки: docker-compose down"
