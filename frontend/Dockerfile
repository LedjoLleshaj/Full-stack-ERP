FROM node:22.16.0-alpine AS builder
WORKDIR '/frontend'
COPY package*.json ./
RUN npm ci --legacy-peer-deps
COPY . .
RUN npx ng build --configuration=production

FROM nginx:1.27-alpine
EXPOSE 80
COPY --from=builder /frontend/dist/frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
