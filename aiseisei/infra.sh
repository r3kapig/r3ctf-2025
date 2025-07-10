docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/aiseisei:v0
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "1" --memory "512m" -p 30000:9999 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/aiseisei:v0
