FROM ubuntu:24.04

# 制作者信息
LABEL auther_template="CTF-Archives"

# apt更换镜像源，并安装相关依赖
#RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list && \
#    sed -i 's@//.*security.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list
RUN apt-get update && apt-get -y dist-upgrade && \
    apt-get install -y lib32z1 xinetd \
    cmake gcc g++ libz-dev libzstd-dev zip wget git python3 xz-utils libcurl4-openssl-dev npm unzip

# 新建用户，并进行账户改变
RUN useradd -m ctf
WORKDIR /home/ctf

# 复制相关lib，并处理环境
RUN cp -R /usr/lib* /home/ctf

# 配置特殊管道映射
RUN mkdir /home/ctf/dev && \
    mknod /home/ctf/dev/null c 1 3 && \
    mknod /home/ctf/dev/zero c 1 5 && \
    mknod /home/ctf/dev/random c 1 8 && \
    mknod /home/ctf/dev/urandom c 1 9 && \
    chmod 666 /home/ctf/dev/*

# 设置xinetd启动之后，chroot限制能使用的bin程序
RUN mkdir /home/ctf/bin && \
    cp /bin/sh /home/ctf/bin && \
    cp /bin/ls /home/ctf/bin && \
    cp /bin/cat /home/ctf/bin && \
    cp /usr/bin/timeout /home/ctf/bin

# 部署xinetd服务
COPY ./config/ctf.xinetd /etc/xinetd.d/ctf
RUN echo "Blocked by ctf_xinetd" > /etc/banner_fail

# 复制容器启动脚本
COPY ./service/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# 部署程序
RUN mkdir cmake && cd cmake && \
    wget https://github.com/Kitware/CMake/releases/download/v3.25.1/cmake-3.25.1-linux-x86_64.tar.gz -O cmake.tar.gz && \
    tar -xf cmake.tar.gz
ENV PATH="/home/ctf/cmake/cmake-3.25.1-linux-x86_64/bin:$PATH"
RUN git clone https://github.com/SVF-tools/SVF.git && cd SVF && \
    git reset --hard aa88cd733992ca38c1250ad26158466ddaa76def && ./build.sh
ENV PATH="/home/ctf/SVF/llvm-16.0.0.obj/bin:$PATH"
COPY ./src/main.py /home/ctf/main.py
COPY ./src/SVFChecker /home/ctf/SVFChecker
RUN cd /home/ctf/SVFChecker && bash ./build.sh

# 初始化flag
RUN chown -R root:ctf /home/ctf && \
    chmod -R 750 /home/ctf && \
    touch /home/ctf/flag && \
    chmod 744 /home/ctf/flag

EXPOSE 9999

# 指定容器入口点
ENTRYPOINT ["/bin/bash","/docker-entrypoint.sh"]
