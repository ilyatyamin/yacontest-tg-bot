docker-compose down --rmi all -v --remove-orphans
git pull
sync ; echo 1 > /proc/sys/vm/drop_caches
docker-compose up
