# Selita Fish - Hetzner Deployment Guide

This guide covers deploying the Selita Fish application to a Hetzner server.

**Domain**: `selitafish.com`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Project Preparation](#project-preparation)
4. [Deployment Steps](#deployment-steps)
5. [SSL/HTTPS Configuration](#sslhttps-configuration)
6. [Database Management](#database-management)
7. [Monitoring & Logs](#monitoring--logs)
8. [Backup Strategy](#backup-strategy)
9. [Updates & Maintenance](#updates--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Local Machine
- Git
- Docker & Docker Compose (for testing locally)
- SSH client

### Hetzner Server (Recommended Specs)
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 40 GB SSD | 80 GB SSD |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |

### Domain & DNS
- Domain name pointing to your Hetzner server IP
- A records configured:
  - `@` → `YOUR_SERVER_IP`
  - `www` → `YOUR_SERVER_IP`

---

## Server Setup

### 1. Initial Server Access

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Update system packages
apt update && apt upgrade -y
```

### 2. Create Non-Root User

```bash
# Create deploy user
adduser deploy
usermod -aG sudo deploy

# Setup SSH key authentication
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 3. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add deploy user to docker group
usermod -aG docker deploy

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### 4. Configure Firewall

```bash
# Install UFW
apt install ufw -y

# Configure rules
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https

# Enable firewall
ufw enable
ufw status
```

### 5. Setup Fail2Ban (Optional but Recommended)

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

---

## Project Preparation

### 1. Clone Repository

```bash
# As deploy user
su - deploy

# Create app directory
mkdir -p /home/deploy/apps
cd /home/deploy/apps

# Clone your repository
git clone https://github.com/YOUR_USERNAME/selita-fish.git
cd selita-fish
```

### 2. Create Production Environment File

```bash
# Copy the example and edit
cp .env.prod.example .env.prod

# Generate a strong secret key
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Edit the file with your actual values
nano .env.prod
```

**Required values in `.env.prod`:**

```env
# Database
DB_NAME=selita_fish
DB_USER=selita_prod_user
DB_PASSWORD=YOUR_STRONG_DB_PASSWORD_HERE

# Django
SECRET_KEY=YOUR_64_CHAR_SECRET_KEY_HERE
DEBUG=False
ADDITIONAL_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_DOMAINS=yourdomain.com,www.yourdomain.com

# Admin credentials (first startup only)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=YOUR_STRONG_ADMIN_PASSWORD
```

### 3. Update Frontend Production API URL

Edit `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: '/api/selita',  // Relative URL through nginx proxy
  // ... rest of config
};
```

---

## Deployment Steps

### 1. Build and Start Services

```bash
cd /home/deploy/apps/selita-fish

# Build all images
docker compose -f docker-compose.prod.yml build --no-cache

# Start services in detached mode
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

### 2. Verify Deployment

```bash
# Check container logs
docker compose -f docker-compose.prod.yml logs -f

# Test API health
curl http://localhost/api/selita/health/

# Check database connection
docker compose -f docker-compose.prod.yml exec backend python manage.py check
```

### 3. Initial Data Setup (First Deploy Only)

```bash
# Run migrations (usually handled by entrypoint.sh)
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

---

## SSL/HTTPS Configuration

### Option A: Using Certbot (Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx

# Stop nginx temporarily
docker compose -f docker-compose.prod.yml stop frontend

# Get certificate
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates are saved at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Configure nginx for SSL

Create/update `frontend/nginx.prod.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location /api/ {
        proxy_pass http://backend:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(?:ico|css|js|gif|jpe?g|png|woff2?|ttf|svg|eot|otf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### Update docker-compose for SSL

Add volume mount in `docker-compose.prod.yml`:

```yaml
frontend:
  volumes:
    - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro
```

### Auto-Renew Certificates

```bash
# Test renewal
certbot renew --dry-run

# Add cron job
crontab -e
# Add this line:
0 3 * * * certbot renew --quiet && docker compose -f /home/deploy/apps/selita-fish/docker-compose.prod.yml restart frontend
```

---

## Database Management

### Connect to Database

```bash
docker compose -f docker-compose.prod.yml exec db psql -U $DB_USER -d selita_fish
```

### Manual Backup

```bash
# Create backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U $DB_USER selita_fish > backup_$(date +%Y%m%d_%H%M%S).sql

# Or using the backup volume
docker compose -f docker-compose.prod.yml exec db pg_dump -U $DB_USER selita_fish > /backups/backup_$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
# Stop backend to prevent writes
docker compose -f docker-compose.prod.yml stop backend

# Restore
docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER selita_fish < backup_YYYYMMDD.sql

# Restart backend
docker compose -f docker-compose.prod.yml start backend
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f db

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Health Check URLs

| Endpoint | Expected Response |
|----------|-------------------|
| `https://yourdomain.com` | Angular app loads |
| `https://yourdomain.com/api/selita/health/` | `{"status": "ok"}` |

---

## Backup Strategy

### Automated Daily Backups

Create `/home/deploy/scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker compose -f /home/deploy/apps/selita-fish/docker-compose.prod.yml exec -T db \
  pg_dump -U selita_prod_user selita_fish | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Remove old backups
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Optional: Upload to remote storage (e.g., Hetzner Storage Box)
# rsync -az $BACKUP_DIR/ user@storage-box:/backups/
```

Add to crontab:
```bash
crontab -e
# Add: Run at 2 AM daily
0 2 * * * /home/deploy/scripts/backup.sh >> /home/deploy/logs/backup.log 2>&1
```

---

## Updates & Maintenance

### Deploying Updates

```bash
cd /home/deploy/apps/selita-fish

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Run migrations if needed
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Zero-Downtime Deployment (Advanced)

```bash
# Build new images without stopping running containers
docker compose -f docker-compose.prod.yml build

# Rolling restart
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker compose -f docker-compose.prod.yml up -d --no-deps --build frontend
```

### System Updates

```bash
# Update system packages monthly
apt update && apt upgrade -y

# Prune old Docker resources
docker system prune -a --volumes -f
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Check if port is in use
netstat -tlnp | grep 80
```

#### 2. Database Connection Failed

```bash
# Check if DB is healthy
docker compose -f docker-compose.prod.yml exec db pg_isready

# Verify credentials
docker compose -f docker-compose.prod.yml exec backend python -c \
  "import os; print(os.environ.get('DB_PASSWORD'))"
```

#### 3. 502 Bad Gateway

- Backend container not running or unhealthy
- nginx can't reach backend container
- Check: `docker compose -f docker-compose.prod.yml ps`

#### 4. Static Files Not Loading

```bash
# Collect static files
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

#### 5. CORS Errors

- Check `ALLOWED_DOMAINS` in `.env.prod`
- Verify `CORS_ALLOWED_ORIGINS` in Django settings

### Emergency Rollback

```bash
# Stop current deployment
docker compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## Quick Reference Commands

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stop all services
docker compose -f docker-compose.prod.yml down

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Enter container shell
docker compose -f docker-compose.prod.yml exec backend bash
docker compose -f docker-compose.prod.yml exec db psql -U selita_prod_user selita_fish

# Check health
docker compose -f docker-compose.prod.yml ps
curl https://yourdomain.com/api/selita/health/
```

---

## Security Checklist

Before going live, verify:

- [ ] `.env.prod` file has strong, unique passwords
- [ ] `.env.prod` is NOT committed to git
- [ ] `DEBUG=False` in production
- [ ] SSL/HTTPS is configured and working
- [ ] Firewall allows only ports 22, 80, 443
- [ ] Fail2Ban is active
- [ ] Database is only accessible within Docker network
- [ ] Admin password has been changed from default
- [ ] Automated backups are configured
- [ ] Log rotation is configured

---

## Support

For issues specific to:
- **Django/Backend**: Check Django documentation
- **Angular/Frontend**: Check Angular documentation
- **Docker**: Check Docker documentation
- **Hetzner**: Contact Hetzner support or check their wiki

---

*Last updated: February 2026*
