# Stock Screener - Cloud Deployment Guide

This guide explains how to deploy the Stock Screener application on a cloud server using Docker Compose.

## Prerequisites

- A cloud server (AWS EC2, DigitalOcean Droplet, Google Cloud VM, etc.)
- Docker and Docker Compose installed on the server
- SSH access to your server
- A domain name (optional, for custom domain setup)

## Quick Start

### 1. Install Docker and Docker Compose

On your cloud server, install Docker:

```bash
# Update package list
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone or Upload the Repository

```bash
# Clone from git
git clone <your-repo-url>
cd screener

# OR upload via SCP
scp -r /local/path/to/screener user@server:/home/user/
```

### 3. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit as needed (optional for basic setup)
nano .env
```

### 4. Initialize the Database

Before starting the containers, set up the database with sample data:

```bash
# Create data directory
mkdir -p data_files

# Install Python dependencies locally (one-time setup)
pip install -r requirements.txt

# Run database setup
python scripts/setup_database.py

# Add sample stock data
python scripts/add_sample_data.py
```

### 5. Build and Start the Application

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

The application will be available at:
- **Frontend**: http://your-server-ip
- **Backend API**: http://your-server-ip:8000
- **API Docs**: http://your-server-ip:8000/docs

## Architecture

### Services

1. **Backend** (FastAPI)
   - Port: 8000
   - Database: SQLite (persisted in `./data_files/`)
   - Health check: `/api/health`

2. **Frontend** (React + Nginx)
   - Port: 80
   - Serves static files and proxies API requests to backend
   - Built using Vite

### Network

Both services run on a private bridge network (`screener-network`) and communicate internally.

## Configuration

### Environment Variables

Edit `.env` file to configure:

```env
# Database
DATABASE_URL=sqlite:///data_files/screener.db

# API Keys (optional)
NOTION_API_KEY=your_notion_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

### Port Configuration

To change the exposed ports, edit `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change 8080 to your desired port

  backend:
    ports:
      - "8001:8000"  # Change 8001 to your desired port
```

## Management Commands

### Start/Stop Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Or rebuild specific service
docker-compose up -d --build backend
```

### Database Management

```bash
# Access backend container
docker-compose exec backend bash

# Run database migrations
docker-compose exec backend python scripts/setup_database.py

# Add more stock data
docker-compose exec backend python scripts/add_sample_data.py

# Backup database
cp data_files/screener.db data_files/screener_backup_$(date +%Y%m%d).db
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check frontend
curl http://localhost/

# Check container health status
docker-compose ps
```

## Production Best Practices

### 1. Use HTTPS with SSL/TLS

Install and configure Nginx or use a reverse proxy like Traefik with Let's Encrypt:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### 2. Set Up a Firewall

```bash
# Using UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. Configure Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          memory: 512M
```

### 4. Enable Automatic Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/screener/data_files/screener.db /path/to/backups/screener_$DATE.db
find /path/to/backups -name "screener_*.db" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### 5. Monitor Application

Use Docker stats:
```bash
docker stats
```

Or set up monitoring with Prometheus/Grafana.

### 6. Log Rotation

Configure Docker logging:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database errors

```bash
# Reset database
docker-compose down
rm -rf data_files/screener.db
docker-compose up -d
docker-compose exec backend python scripts/setup_database.py
```

### Port conflicts

```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a
```

## Scaling

### Horizontal Scaling

To run multiple backend instances:

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

Note: SQLite is not suitable for high-concurrency. Consider migrating to PostgreSQL for production.

### Database Migration to PostgreSQL

1. Update `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: screener
      POSTGRES_USER: screener
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    environment:
      - DATABASE_URL=postgresql://screener:your_password@postgres:5432/screener

volumes:
  postgres_data:
```

2. Update code to use PostgreSQL (requires SQLAlchemy driver change)

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health status: `docker-compose ps`
- Verify network connectivity: `docker network inspect screener_screener-network`

## Security Notes

- Change default passwords
- Keep Docker and images updated
- Use secrets management for API keys
- Enable firewall
- Use HTTPS in production
- Regularly backup database
- Monitor logs for suspicious activity
