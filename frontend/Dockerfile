# deps
ARG NODE_VERSION
FROM node:${NODE_VERSION} AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# dev server
FROM node:${NODE_VERSION} AS dev
ARG PORT_FRONT
ENV NODE_ENV=development PORT_FRONT=${PORT_FRONT}
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY . .
EXPOSE ${PORT_FRONT}
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "${PORT_FRONT}"]

# build
FROM node:${NODE_VERSION} AS build
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY . .
RUN npm run build
