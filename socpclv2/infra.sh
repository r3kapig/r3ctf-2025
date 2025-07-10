docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/socpclv2:v0
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "1" --memory "2048m" -p 30015:8899 -p 30026:8900 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/socpclv2:v0
