#!/bin/bash

echo "$FLAG" > /flag.txt
unset FLAG

socat TCP-LISTEN:1337,fork,max-children=1 EXEC:"python main.py",stderr
