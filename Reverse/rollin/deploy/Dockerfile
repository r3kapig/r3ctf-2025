FROM ubuntu:24.04

ENV FLAG="R3CTF{1f_th15_ch4ll3ng3_m4d3_y0u_l34rn_gl1bc_h34p_c0ns1d3r_b3c0m1ng_4_pwn3r}"

RUN apt-get update && apt-get install -y socat

RUN useradd -m ctf

WORKDIR /app

COPY ./main .

RUN chmod 755 ./main

EXPOSE 5000

CMD ["socat", "-T600", "TCP-LISTEN:5000,reuseaddr,fork,su=ctf", "EXEC:/app/main,pty,echo=0,rawer"]
