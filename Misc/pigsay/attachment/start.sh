#!/bin/sh

echo $FLAG > /app/flag_$(python -c 'import uuid; print(uuid.uuid4().hex)') && \
chmod 744 /app/flag_*

unset FLAG
export FLAG=R3CTF{fake_flag}
FLAG=R3CTF{fake_flag}

rm -rf $0

su -s /bin/sh r3ctf -c \
'JWT_KEY=$(python -c "import uuid; print(uuid.uuid4().hex)") PIG_KEY=$(python -c "import uuid; print(uuid.uuid4().hex)") uv run app.py'