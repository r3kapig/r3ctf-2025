FROM ghcr.io/puppeteer/puppeteer:24.11.2

WORKDIR /app

USER root
COPY . .
RUN chown -R pptruser:pptruser /app

USER pptruser
RUN npm install

EXPOSE 31337
CMD ["node", "/app/bot.js"]
