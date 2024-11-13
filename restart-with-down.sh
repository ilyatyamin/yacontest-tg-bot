docker stop yacontest_testbot-bot
docker rm yacontest_testbot-bot
docker image rm yacontest_testbot-bot
git pull
sync ; echo 1 > /proc/sys/vm/drop_caches
docker-compose up
