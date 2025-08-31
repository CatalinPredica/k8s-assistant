# frontend/Dockerfile
FROM node:20.11.1-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN rm -rf dist
RUN npm run build
RUN echo "$(date +%Y-%m-%d_%H-%M-%S)" > /app/build-timestamp.txt