#!/bin/bash

set -e

if [ "$FLAG" ]; then
  sed -i "2s/.*/flag: $FLAG/" plugins/R3Craft/config.yml
  unset FLAG
fi

java -Xms512M -Xmx512M -jar paper-1.21.6-48.jar nogui
