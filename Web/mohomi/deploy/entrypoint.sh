#!/bin/bash -e

if [ -z "${FLAG}" ]; then
  echo "Error: FLAG environment variable is not set."
  exit 1
fi

flag_filename="/root/flag_$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt"
echo -n "${FLAG}" > ${flag_filename}
chmod 400 ${flag_filename}
unset FLAG

exec tini runsvdir -P /etc/service