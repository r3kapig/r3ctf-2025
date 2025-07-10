#!/bin/sh
# server script
[ -n "$FLAG" ] && echo "$FLAG" > /flag
export FLAG="flag{dbt_shi_ge_sha_bi}"
/etc/init.d/xinetd start;
sleep infinity;


