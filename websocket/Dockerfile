ARG NODE_IMAGE=node:26-trixie-slim

FROM ${NODE_IMAGE}
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund
COPY websocket ./websocket
COPY websocket/config.k8s.js ./websocket/config.js
USER node
EXPOSE 15100 15101 15102
CMD ["node", "websocket/daemon.js"]
