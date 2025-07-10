1. 题目用到chrome的库 ，所以编译需要先拉chrome源码拉完之后 看diff文件找到对应文件夹把本地ctf.cc 和ctf.h  拖进去

2. 接下来 就是编译 对chromium 主要目录 先生成out/release 使用命令`gn gen out/release`

3. 最后编译 `autoninja -C out/release ctf`