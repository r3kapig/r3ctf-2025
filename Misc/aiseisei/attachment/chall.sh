#!/bin/bash

proof_of_work() {
  nonce=$(head -c 18 /dev/urandom | base64 -w 0)
  echo "Proof of work (nonce $nonce): "
  read -r line
  hash=$(echo "$nonce$line" | base64 -d | sha256sum -b | cut -d ' ' -f 1)
  echo "hash=$hash"
  [[ $hash == 111111* ]]
}

proof_of_work || exit 1

source /opt/venv/bin/activate

cd /home/ctf/aiseisei

export PYTHONUNBUFFERED=1
python3 main.py 2>&1
