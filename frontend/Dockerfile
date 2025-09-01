FROM node:24.7.0-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN rm -rf dist
RUN npm run build
RUN echo "$(date +%Y-%m-%d_%H-%M-%S)" > /app/build-timestamp.txt

FROM nginx:1.29.1-alpine
RUN echo "Triggering cache bust for next layer."
COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/build-timestamp.txt /usr/share/nginx/html/build-timestamp.txt
COPY nginx.conf /etc/nginx/nginx.conf
# Serve API via Ingress; or add simple proxy config if co-hosting