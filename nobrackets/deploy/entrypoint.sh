#!/bin/bash

echo "$FLAG" > /flag.txt
unset FLAG
mv /flag.txt /flag-$(md5sum /flag.txt | cut -c-32).txt

socat TCP-LISTEN:5000,fork,reuseaddr EXEC:/app/run
