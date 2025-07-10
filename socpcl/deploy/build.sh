#!/bin/sh
sudo docker build -t "socpcl" . && 

sudo docker run -d \
  -p "0.0.0.0:9999:9999" \
  -p "0.0.0.0:8899:8899" \
  -p "0.0.0.0:8900:8900" \
  -p "0.0.0.0:1024:1024/udp" \
  -p "0.0.0.0:1027:1027/udp" \
  -h "socpcl" \
  --name="socpcl" \
  socpcl