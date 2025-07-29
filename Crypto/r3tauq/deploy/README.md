# crypto-sagemath_9.6

## 环境说明

提供 `SageMath 9.6` + `Python 3.10.3` 的基础环境，并已经添加 `pycryptodome` + `gmpy2` 库，并基于 `socat` 实现服务转发，默认暴露端口位于9999

实现：当选手连接到对应端口（默认为9999端口，默认选手使用 `netcat` ）的时候，运行 `.py项目`，并将会话转发至选手的连接

此环境适用于项目中没有引入 `socket` 等库，并依赖于 `SageMath` 核心，需要镜像做到：
- 选手通过端口连接到容器/靶机
- 服务启动项目，生成SageMath会话
- 将会话转发给选手的连接



## 如何使用

直接将SageMath文件/项目放入 `./src` 目录即可，文件名建议使用 `main.sage` ，便于环境识别，如需更改文件名，请在 `./service/docker-entrypoint.sh` 内更改

如使用了Python其他第三方库，请在 `./Dockerfile` 内补充pip安装语句

源码放置进 `./src` 目录之后，执行 
```shell
docker build .
```
即可开始编译镜像

也可以在安放好相关项目文件之后，直接使用 `./docker/docker-compose.yml` 内的 `docker-compose` 文件实现一键启动测试容器

```shell
cd ./docker
docker-compose up -d
```



### note

进入目录，执行：

```
docker build . -t 镜像名
```

这样就做好了镜像。

> 如果需要把镜像导出为文件，则：
>
> ```
> docker save -o <输出文件路径> <镜像名称>:<标签>
> ```
>
> 这个文件可以按如下方式被作为镜像导入：
>
> ```
> docker load -i <输入文件路径>
> ```



运行docker：

```
docker run --name 镜像名字 -d -p x:9999 容器名字
```

此时可以在本机`localhost:x`访问到，可以有多个`-p`参数使得容器的9999暴露给多个主机实际端口，比如：

```
docker run --name 镜像名字 -d -p 10002:9999 -p 10003:9999 容器名字
```

此时10002和10003端口均可以访问到。



如果要push到dockerhub，则：

```
docker tag local-image:latest new-repo:latest
docker push new-repo:latest
```



要把镜像保存到本地，则：

```
docker save -o 输出文件名 image:latest
```

