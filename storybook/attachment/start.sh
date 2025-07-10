#!/bin/bash
echo -n $FLAG > /flag
chmod 644 /flag
unset FLAG

socat tcp-listen:1337,fork,reuseaddr,bind=0.0.0.0 exec:"su ubuntu -c '/pwn'",stderr
