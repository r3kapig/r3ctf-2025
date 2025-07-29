#!/bin/sh

set -euo pipefail

echo "$FLAG" > /work/flag
unset FLAG

setcap CAP_SYS_CHROOT=+ep $(readlink -f $(which python3))

su ctf -c 'socat TCP-LISTEN:1337,fork,max-children=1 EXEC:"python3 -u /app/server.py",stderr'
