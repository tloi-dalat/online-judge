export default {
  get_host: process.env.WS__GET_HOST || '0.0.0.0',
  get_port: +(process.env.WS__GET_PORT || 15100),
  post_host: process.env.WS__POST_HOST || '0.0.0.0',
  post_port: +(process.env.WS__POST_PORT || 15101),
  http_host: process.env.WS__HTTP_HOST || '0.0.0.0',
  http_port: +(process.env.WS__HTTP_PORT || 15102),
  long_poll_timeout: +(process.env.WS__LONG_POLL_TIMEOUT || 29000),
};
