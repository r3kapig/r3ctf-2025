FROM python:3.10.13-slim-bullseye

# 制作者信息
LABEL auther_template="WCjrCK"

# apt更换镜像源，并更新软件包列表信息
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN apt-get update || apt-get update

# 通过apt，安装socat用于服务转发
RUN apt-get install -y socat 

RUN apt-get install -y libgmp-dev unzip 
RUN apt-get install -y bison || apt-get install -y bison
RUN apt-get install -y libtool || apt-get install -y libtool
RUN apt-get install -y flex || apt-get install -y flex
RUN apt-get remove -y autoconf || apt-get remove -y autoconf
RUN apt-get install -y make || apt-get install -y make
RUN apt-get install -y automake || apt-get install -y automake
RUN apt-get install -y autoconf-archive || apt-get install -y autoconf-archive
RUN apt-get install -y libssl-dev || apt-get install -y libssl-dev
RUN apt-get install -y wget || apt-get install -y wget

WORKDIR /home/deps
COPY ./deps/ /home/deps

RUN unzip ./pbc-master.zip 
RUN unzip ./charm-dev.zip 
RUN tar -zxvf ./autoconf-2.72.tar.gz
WORKDIR /home/deps/autoconf-2.72
RUN ./configure
RUN make
RUN make install

# RUN ls
WORKDIR /home/deps/pbc-master
RUN ./setup
RUN ./configure
RUN make
RUN make install
RUN ldconfig

RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    hypothesis

RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pyparsing==2.1.5

WORKDIR /home/deps/charm-dev
RUN ./configure.sh
RUN make
RUN make install

# 通过tuna源，安装必要的python依赖库
# 镜像中并没有更换源，只是在pip语句中每次制定了镜像源

RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pycryptodome 

# 拷贝源码和启动脚本至对应目录
COPY ./src/ /app
COPY ./service/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# 新建用户，并进行账户改变
RUN useradd -m ctf
RUN chown ctf:ctf /app
USER ctf

EXPOSE 9999

# 指定容器入口点
ENTRYPOINT ["/bin/bash","/app/docker-entrypoint.sh"]