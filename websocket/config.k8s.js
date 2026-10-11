// websocket/config.k8s.js — commit next to daemon.js.
// The wsevent Dockerfile copies it into place:  COPY config.k8s.js config.js
// (config.js itself stays gitignored, as upstream intends).
//
// Ports follow the DMOJ standard so they match EVENT_DAEMON_POST in .k8s.settings.py:
//   15100  websocket GET   — browsers, routed from https://<domain>/event/
//   15101  websocket POST  — the site pushes events here (cluster-internal only)
//   15102  HTTP long-poll  — browsers, routed from https://<domain>/channels/
export default {
  get_host: process.env.WS__GET_HOST || '0.0.0.0',
  get_port: +(process.env.WS__GET_PORT || 15100),
  post_host: process.env.WS__POST_HOST || '0.0.0.0',
  post_port: +(process.env.WS__POST_PORT || 15101),
  http_host: process.env.WS__HTTP_HOST || '0.0.0.0',
  http_port: +(process.env.WS__HTTP_PORT || 15102),
  // 29s, as upstream VNOJ uses: comfortably under proxy idle timeouts.
  long_poll_timeout: +(process.env.WS__LONG_POLL_TIMEOUT || 29000),
};
