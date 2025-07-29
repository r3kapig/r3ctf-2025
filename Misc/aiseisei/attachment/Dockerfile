FROM ubuntu:24.04

COPY ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-full python3-pip \
    unzip \
    xinetd \
    libtiff-dev libpng-dev libjpeg-dev libxml2-dev nlohmann-json3-dev \
    git \
    cmake make \
    exiftool \
    libwxgtk3.2-dev \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

ARG PIP_SOURCE=https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip config set global.index-url ${PIP_SOURCE}

RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools && \
    pip install pandas pyarrow pylibtiff==0.6.1 numpy==1.26.4 pillow
RUN . /opt/venv/bin/activate && \
    cp /usr/include/x86_64-linux-gnu/tiff.h /opt/venv/include/ && \
    python3 -c 'import libtiff'

WORKDIR /opt/
RUN git clone https://github.com/InternationalColorConsortium/DemoIccMAX.git
WORKDIR /opt/DemoIccMAX
# RUN git checkout v2.1.26
RUN git checkout eefb986ba3450ce23ddde1d06f183f625a7cc534
RUN cd Build && cmake Cmake && make -j iccApplyProfiles
RUN cp Build/Tools/IccApplyProfiles/iccApplyProfiles /usr/local/bin/

COPY ctf.xinetd /etc/xinetd.d/ctf
RUN echo "Blocked by ctf_xinetd. Please try again later." > /etc/banner_fail
COPY start.sh /

RUN useradd -m ctf
WORKDIR /home/ctf/aiseisei

COPY mnist ./mnist
COPY chall.sh .
COPY flag.py .
COPY main.py .

CMD ["/start.sh"]
EXPOSE 9999
