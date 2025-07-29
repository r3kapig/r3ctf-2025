# dockerfile for axb2020 pwn3
FROM ubuntu:22.04

# set source download and install xinted
RUN apt update && apt install -y lib32z1 xinetd openssl && rm -rf /root/.cache && apt autoclean && rm -rf /tmp/* /var/lib/apt/* /var/cache/* /var/log/*

# copy base server file
COPY ./pwn.xinetd /etc/xinetd.d/pwn
COPY ./service.sh /service.sh
RUN chmod 700 /service.sh

# useradd
RUN useradd pwn 

# copy file
COPY ./files/* /

# chown & chmod
RUN chmod 755 /pwn && chmod 755 /libc.so.6 && chmod 755 /ld-linux-x86-64.so.2
RUN chmod 744 /flag


CMD ["/service.sh"]

