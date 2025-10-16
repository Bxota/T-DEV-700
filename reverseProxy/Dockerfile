ARG NGX_VERSION

FROM nginx:${NGX_VERSION} as base
COPY nginx.conf /etc/nginx/nginx.conf
RUN apk add --no-cache curl

# ---- DEV ----
FROM base as dev
COPY templates/default.dev.conf.template /etc/nginx/templates/default.conf.template

# ---- PROD ----
FROM base as prod
COPY templates/default.prod.conf.template /etc/nginx/templates/default.conf.template
