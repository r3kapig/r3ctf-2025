
docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/evalgelist:v0
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "0.1" --memory "128m" -p 30020:80 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/evalgelist:v0

