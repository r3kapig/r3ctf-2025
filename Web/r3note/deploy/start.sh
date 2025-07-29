#!/bin/sh

setup() {
    rm -rf /start.sh

    echo -n $FLAG > /flag
    chown bot:bot /flag
    chmod 400 /flag
    unset FLAG
}

start_nginx() {
    echo "Starting nginx..."
    /usr/sbin/nginx -g "daemon off;" &
    NGINX_PID=$!
    echo "Nginx started with PID: $NGINX_PID"
}

start_app() {
    echo "Starting app..."
    sed -i "s/secret: \"[^\"]*\"/secret: \"$(openssl rand -base64 32)\"/" /app/config.yaml
    su -s /bin/bash app -c "cd /app && ./r3note" &
    APP_PID=$!
    echo "App started with PID: $APP_PID"
}

start_bot() {
    echo "Starting bot..."
    su -s /bin/bash bot -c "cd /bot && export PUPPETEER_CACHE_DIR=/bot/puppeteer_cache && /usr/bin/node /bot/bot.mjs" &
    BOT_PID=$!
    echo "Bot started with PID: $BOT_PID"
}

setup
start_app
start_bot
start_nginx

while true; do
    sleep 5
done