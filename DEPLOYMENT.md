# Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Platform-Specific Guides](#platform-specific-guides)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables](#environment-variables)
6. [Security Checklist](#security-checklist)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Local Development

### Quick Start

1. **Clone and Setup:**
```bash
git clone https://github.com/VishweshTiwari1323/AI-Phishing-Detector.git
cd "Phishing Detector"

# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

2. **Configure Environment:**
```bash
# Edit .env file
VT_API_KEY=your_virustotal_api_key
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

3. **Run Development Server:**
```bash
python app.py
# Or
flask run
```

Access at: `http://localhost:5000`

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Review security settings
- [ ] Set up backups
- [ ] Configure CDN (optional)

### Production Server Setup

#### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With better settings
gunicorn -w 4 \
  --threads 2 \
  --worker-class gthread \
  --timeout 120 \
  --bind 0.0.0.0:5000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  app:app
```

#### Using uWSGI

```bash
# Install uwsgi
pip install uwsgi

# Run
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/project/static;
        expires 30d;
    }
}
```

---

## Platform-Specific Guides

### Heroku

1. **Install Heroku CLI:**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Deploy:**
```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set VT_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set FLASK_ENV=production

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Initialize database
heroku run flask init-db
heroku run flask seed-db

# Open app
heroku open
```

3. **View Logs:**
```bash
heroku logs --tail
```

---

### Railway

1. **Deploy from GitHub:**
   - Go to https://railway.app
   - Connect your GitHub repository
   - Select "Phishing Detector" project

2. **Configure Environment Variables:**
   ```
   VT_API_KEY=your_key
   SECRET_KEY=your_secret
   FLASK_ENV=production
   ```

3. **Add Start Command:**
   ```
   gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

4. **Deploy automatically on push**

---

### Render

1. **Create Web Service:**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repository

2. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

3. **Environment Variables:**
   ```
   VT_API_KEY=your_key
   SECRET_KEY=your_secret
   FLASK_ENV=production
   PYTHON_VERSION=3.11.0
   ```

4. **Database:**
   - Create PostgreSQL database
   - Copy connection string to `DATABASE_URL`

---

### AWS EC2

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.small or larger
   - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Connect and Setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
git clone https://github.com/VishweshTiwari1323/AI-Phishing-Detector.git
cd "Phishing Detector"

# Setup
./setup.sh

# Configure environment
nano .env
```

3. **Setup Systemd Service:**
```bash
sudo nano /etc/systemd/system/phishing-detector.service
```

```ini
[Unit]
Description=AI Phishing Detection System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Phishing Detector
Environment="PATH=/home/ubuntu/Phishing Detector/venv/bin"
ExecStart=/home/ubuntu/Phishing Detector/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

4. **Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start phishing-detector
sudo systemctl enable phishing-detector
sudo systemctl status phishing-detector
```

---

### DigitalOcean

1. **Create Droplet:**
   - Ubuntu 22.04 LTS
   - Basic plan ($6/month recommended)
   - Add SSH key

2. **Follow AWS EC2 setup steps above**

3. **Setup Firewall:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create database directory
RUN mkdir -p /app/instance

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Initialize database and run
CMD ["sh", "-c", "flask init-db && flask seed-db && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - VT_API_KEY=${VT_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/phishing_db
    depends_on:
      - db
    volumes:
      - ./instance:/app/instance

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=phishing_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Run with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VT_API_KEY` | VirusTotal API key | `a1b2c3d4e5...` |
| `SECRET_KEY` | Flask secret key | `random-secret-key-here` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | `development` |
| `DATABASE_URL` | Database connection | `sqlite:///phishing_detector.db` |
| `RATELIMIT_STORAGE_URL` | Rate limit storage | `memory://` |

### Generate Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

---

## Security Checklist

### Before Production

- [ ] Change default admin password
- [ ] Set strong `SECRET_KEY`
- [ ] Use HTTPS/SSL certificates
- [ ] Configure CORS properly
- [ ] Enable CSRF protection (default)
- [ ] Set secure session cookies
- [ ] Implement proper logging
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Disable debug mode
- [ ] Use production database (PostgreSQL)
- [ ] Set up regular backups
- [ ] Configure rate limiting
- [ ] Review file permissions
- [ ] Update dependencies regularly

### SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring

### Application Monitoring

```python
# Add to app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Health Check Endpoint

```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
```

---

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check database exists
flask shell
>>> from app import db
>>> db.create_all()
```

**Port Already in Use:**
```bash
# Find process
lsof -i :5000
# Kill process
kill -9 <PID>
```

**Permission Denied:**
```bash
# Fix file permissions
chmod +x setup.sh
chmod 644 app.py
```

**Module Not Found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Backup Strategy

### Database Backup

```bash
# SQLite
cp phishing_detector.db backups/phishing_detector_$(date +%Y%m%d).db

# PostgreSQL
pg_dump phishing_db > backups/backup_$(date +%Y%m%d).sql
```

### Automated Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

---

## Performance Optimization

### Production Settings

```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Database pooling
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    # Caching
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
```

### CDN for Static Files

Use Cloudflare or AWS CloudFront for serving static assets.

---

## Support

For deployment support:
- Email: akshya1323@gmail.com
- GitHub Issues: https://github.com/VishweshTiwari1323/AI-Phishing-Detector/issues
- Documentation: README.md

---

**Last Updated:** 2026-08-07
