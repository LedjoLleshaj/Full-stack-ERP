# Use Node to build and serve the app
FROM node:22.15.0-alpine AS builder

# Set working directory
WORKDIR /frontend

# Install dependencies
COPY package*.json ./
RUN npm install --force
# Copy source and build the Angular app
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=builder /frontend/dist/frontend /usr/share/nginx/html
# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port 80 for production
EXPOSE 80
# Start nginx server
CMD ["nginx", "-g", "daemon off;"]


