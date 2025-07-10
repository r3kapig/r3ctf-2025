docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/nobrackets:v0
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "1" --memory "1024m" -p 30004:5000 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/nobrackets:v0
