# Selita Fish - App Update Guide

A quick reference for updating the application after initial deployment.

---

## Quick Update (Recommended)

From your **local machine**:

```bash
# 1. Commit and push your changes
git add .
git commit -m "Your change description"
git push origin main

# 2. SSH to server and deploy (one command)
ssh YOUR_USER@YOUR_SERVER_IP "/home/deploy/apps/selita-fish/scripts/deploy.sh"
```

That's it! The deploy script handles everything automatically.

---

## What the Deploy Script Does

The `scripts/deploy.sh` automatically:

1. ✅ Pulls latest code from GitHub
2. ✅ Rebuilds Docker containers
3. ✅ Restarts services
4. ✅ Runs database migrations
5. ✅ Collects static files
6. ✅ Cleans up old Docker images

**Your database data is preserved** (stored in a Docker volume).

---

## Manual Update Steps

If you prefer manual control or need to debug:

```bash
# SSH into server
ssh YOUR_USER@YOUR_SERVER_IP

# Navigate to project
cd /home/deploy/apps/selita-fish

# Pull latest code
git pull origin main

# Rebuild containers
docker compose -f docker-compose.prod.yml build

# Restart services
docker compose -f docker-compose.prod.yml up -d

# Run migrations (if any)
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Check status
docker compose -f docker-compose.prod.yml ps
```

---

## Common Update Scenarios

### Frontend Only Changes (HTML, CSS, TypeScript)

```bash
# Rebuild and restart only frontend
docker compose -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### Backend Only Changes (Python, Django)

```bash
# Rebuild and restart only backend
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend

# Don't forget migrations if models changed
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Database Schema Changes

If you modified `db/schema.sql`:

> ⚠️ **Warning**: Schema changes on existing data require careful handling!

```bash
# Option 1: Django migrations (recommended for most changes)
docker compose -f docker-compose.prod.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Option 2: Manual SQL (for complex changes)
docker compose -f docker-compose.prod.yml exec db psql -U $DB_USER selita_fish
# Then run your SQL commands
```

### Environment Variable Changes

```bash
# Edit .env.prod
nano .env.prod

# Restart affected services
docker compose -f docker-compose.prod.yml up -d
```

---

## Rollback to Previous Version

If something goes wrong:

```bash
# SSH into server
ssh YOUR_USER@YOUR_SERVER_IP
cd /home/deploy/apps/selita-fish

# Find the previous commit
git log --oneline -10

# Rollback to specific commit
git checkout <commit-hash>

# Rebuild and restart
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

---

## Health Check

```bash
# Check container status
docker compose -f docker-compose.prod.yml ps

# Test API
curl https://selitafish.com/api/selita/health/

# Check resource usage
docker stats
```

---

## Tips

1. **Test locally first**: Run `docker compose -f docker-compose.prod.yml build` locally to catch build errors
2. **Small commits**: Deploy frequently with small changes for easier debugging
3. **Check logs**: Always check logs after deployment for any errors
4. **Backup before major changes**: See `DEPLOYMENT.md` for backup procedures

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker compose -f docker-compose.prod.yml logs backend` |
| 502 Bad Gateway | Backend not running, check logs |
| Migration errors | Check for conflicts, may need manual fix |
| Static files missing | Run `collectstatic` manually |
| Permission denied | Check file ownership and docker group membership |

---

*Quick command reference - see `DEPLOYMENT.md` for full documentation*
