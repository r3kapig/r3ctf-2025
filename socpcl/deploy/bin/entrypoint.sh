#!/bin/bash

echo "$FLAG" > flag
unset FLAG
./validator --ticks-per-slot 200 --limit-ledger-size 1024*500
