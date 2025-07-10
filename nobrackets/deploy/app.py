#!/usr/bin/python3
import sys
import subprocess
import tempfile

BANNER = """
Welcome to R3CTF 2025!
I Have Studied Some Funny Go Trick from Some Jail Challenge.
It's Cool, So I Made This Challenge.

Remember No Brackets Allowed!! 
And Plz Input your program (the last line must start with __EOF__):
"""

print(BANNER, flush=True)

# Input
code = ""
while True:
    line = sys.stdin.readline()
    if line.startswith("__EOF__"):
        break
    code += line


# Validation
brackets = "[](){}<>"
if any(c in brackets for c in code):
    print("No brackets allowed")
    exit(1)


# Run
with tempfile.TemporaryDirectory() as dirname:
    filename = "main.go"
    #print(f"{dirname}/{filename}")
    open(f"{dirname}/{filename}", "w").write(code)

    try:
        proc = subprocess.run(
            ["go", "run", filename],
            cwd=dirname,
            timeout=15,
            env={
                "PATH": "/usr/local/go/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "HOME": dirname,
            },
        )
        print("Executed")
    except subprocess.TimeoutExpired:
        print("Timeout")
    except Exception:
        print("Error")
