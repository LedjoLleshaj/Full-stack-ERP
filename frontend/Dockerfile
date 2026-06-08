FROM node:22.16.0-alpine AS builder
WORKDIR '/frontend'
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx ng build --configuration=production

FROM nginx
EXPOSE 80
COPY --from=builder /frontend/dist/frontend /usr/share/nginx/html
