FROM node:23.11.0-alpine AS builder
WORKDIR '/frontend'
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx ng build --prod demo

FROM nginx
EXPOSE 80
COPY --from=builder /frontend/dist/demo /usr/share/nginx/html