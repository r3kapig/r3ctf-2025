docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/signin:v2
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "0.5" --memory "512m" -p 30024:8888 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/signin:v2
