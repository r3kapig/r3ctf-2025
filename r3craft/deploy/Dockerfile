FROM eclipse-temurin:21-jre as builder

WORKDIR /server

ADD https://fill-data.papermc.io/v1/objects/35e2dfa66b3491b9d2f0bb033679fa5aca1e1fdf097e7a06a80ce8afeda5c214/paper-1.21.6-48.jar .
COPY eula.txt .
COPY server.properties .
COPY bukkit.yml .
COPY plugins/ plugins/
COPY start.sh .

RUN chmod +x start.sh && java -jar paper-1.21.6-48.jar --help

FROM eclipse-temurin:21-jre

RUN adduser --disabled-password --gecos "" paper \
  && mkdir -p /home/paper/server \
  && chown -R paper:paper /home/paper
USER paper

WORKDIR /home/paper/server
COPY --from=builder --chown=paper:paper /server /home/paper/server

EXPOSE 25565
CMD ["./start.sh"]
