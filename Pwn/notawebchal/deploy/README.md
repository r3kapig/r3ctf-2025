# NoT a wEb ch4l

# Build
`docker build . -t r3ctf-pwn`

Flag at src/flag and will be copied to container.

The chal port is container's 80 by default.

Goal is to pwn the php to bypass the `disable_functions` and `open_base_dir` sandbox (in the PHP-8.4 which introduces heap hardening). 

# For CTFers:
TBA