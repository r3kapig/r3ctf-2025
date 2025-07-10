cd bot
docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/silentprofit_bot:v0
cd ../html
docker build . -t r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/silentprofit_html:v0
cd ..
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "0.1" --memory "128m" -p 30018:31337 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/silentprofit_bot:v0
docker run --rm -d -e FLAG=flag{infra_test_flag} --cpus "0.1" --memory "128m" -p 30019:80 r3ctf.ops.ret.sh.cn/r3ctf_2025_68688720/silentprofit_html:v0