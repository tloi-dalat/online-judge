# syntax=docker/dockerfile:1
#
# TLOJ event daemon (websocket/daemon.js).
# Build context: the repo ROOT, not websocket/ — the daemon's dependency (ws)
# is declared in the root package.json.
#
#   docker build -f websocket/Dockerfile .

ARG NODE_IMAGE=node:24-bookworm-slim
FROM ${NODE_IMAGE}
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund
COPY websocket ./websocket
# config.js is gitignored upstream; the env-driven one replaces it.
COPY websocket/config.k8s.js ./websocket/config.js
USER node
# 15100 websocket (browsers), 15101 websocket (site posts events), 15102 long-poll
EXPOSE 15100 15101 15102
CMD ["node", "websocket/daemon.js"]
