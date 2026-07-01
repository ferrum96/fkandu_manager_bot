#!/bin/bash

# Конфигурация
EMAIL="your-email@domain.com"  # Замените на ваш email
DOMAINS=(
    "kanban.yourdomain.com"
    "dashboard.yourdomain.com"
    "files.yourdomain.com"
)

# Создание директорий
echo "Создание директорий для сертификатов..."
mkdir -p nginx/certs
mkdir -p nginx/www

# Запуск nginx в режиме HTTP-only для получения сертификатов
echo "Запуск nginx для получения сертификатов..."
cat > nginx/nginx-temp.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name kanban.yourdomain.com dashboard.yourdomain.com files.yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'OK';
        }
    }
}
EOF

# Временно заменяем конфиг
cp nginx/nginx.conf nginx/nginx.conf.backup
cp nginx/nginx-temp.conf nginx/nginx.conf

# Запуск nginx
docker-compose up -d nginx
sleep 3

# Получение сертификатов
echo "Получение SSL сертификатов..."
DOMAIN_ARGS=""
for DOMAIN in "${DOMAINS[@]}"; do
    DOMAIN_ARGS="$DOMAIN_ARGS -d $DOMAIN"
done

docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    $DOMAIN_ARGS

# Восстановление конфигурации
echo "Восстановление конфигурации nginx..."
cp nginx/nginx.conf.backup nginx/nginx.conf
rm nginx/nginx-temp.conf nginx/nginx.conf.backup

# Перезапуск nginx с SSL
echo "Перезапуск nginx с SSL..."
docker-compose restart nginx

echo ""
echo "=== SSL сертификаты установлены ==="
echo ""
echo "Сертификаты:"
for DOMAIN in "${DOMAINS[@]}"; do
    echo "  - $DOMAIN"
done
echo ""
echo "Сертификаты будут автоматически обновляться каждые 12 часов."
echo "Для ручного обновления: docker-compose run --rm certbot renew"
