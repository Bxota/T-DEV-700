# ---------- deps ----------
ARG NODE_VERSION
FROM node:${NODE_VERSION} AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# ---------- dev ----------
FROM node:${NODE_VERSION} AS dev
ARG PORT_FRONT
ENV NODE_ENV=development PORT_FRONT=${PORT_FRONT}
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY . .
EXPOSE ${PORT_FRONT}
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "${PORT_FRONT}"]

# ---------- build ----------
FROM node:${NODE_VERSION} AS build
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------- prod ----------
FROM node:${NODE_VERSION} AS prod
WORKDIR /app
COPY --from=build /app/dist /seed
RUN mkdir -p /app/dist
VOLUME ["/app/dist"]
CMD ["sh","-lc","set -e; \
  rsync -a --delete /seed/ /app/dist/ 2>/dev/null || (rm -rf /app/dist/*; cp -a /seed/. /app/dist/); \
  echo 'dist copied to volume'; \
  tail -f /dev/null"]
