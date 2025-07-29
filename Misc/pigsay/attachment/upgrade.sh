#!/bin/sh
cd /app

if uv add -U pigsay && uv tool upgrade pigsay; then
    uvx pigsay encrypt "[$(date "+%Y-%m-%d %H:%M:%S")] Upgrade Success!"
else
    uvx pigsay encrypt "[$(date "+%Y-%m-%d %H:%M:%S")] Upgrade failed!"
fi