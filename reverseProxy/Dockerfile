ARG NGX_VERSION
FROM nginx:${NGX_VERSION}

COPY nginx.conf /etc/nginx/nginx.conf

COPY templates/default.conf.template /etc/nginx/templates/default.conf.template

RUN apk add --no-cache curl
