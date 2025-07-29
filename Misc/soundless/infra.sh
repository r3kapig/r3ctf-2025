docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/soundless:v1
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "1" --memory "2048m" -p 30039:5000 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/soundless:v1
