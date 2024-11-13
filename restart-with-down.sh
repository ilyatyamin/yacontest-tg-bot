docker stop TelegramBot
docker rm TelegramBot
docker image rm TelegramBot
git pull
sync ; echo 1 > /proc/sys/vm/drop_caches
docker-compose up
