# Flussonic Dashboard - Ubuntu 24 Deployment Guide

## Prerequisites
- Ubuntu 24 server with sudo privileges
- Domain names configured (optional but recommended)
- Database created (MySQL/MariaDB)

---

## Step 1: Update System and Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js (LTS version) and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install MySQL client (optional, if you want to manage DB from server)
sudo apt install -y mysql-client

# Install build essentials (for compiling any native modules)
sudo apt install -y build-essential

# Install nginx (for serving frontend and reverse proxy)
sudo apt install -y nginx
```

---

## Step 2: Clone Project Repository

```bash
cd /var/www
sudo git clone https://github.com/yourusername/your-repo.git flussonic-dashboard
cd flussonic-dashboard
```

---

## Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

---

## Step 4: Configure Environment Variables

Create a `.env` file in the project root (`/var/www/flussonic-dashboard`) with the following content:

```
DATABASE_URL=mysql+mysqlconnector://DB_USER:DB_PASSWORD@localhost:3306/DB_NAME
SECRET_KEY=your_secret_key_here
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
```

Replace `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `your-frontend-domain.com` accordingly.

---

## Step 5: Initialize Database and Create Admin User

```bash
# Activate virtual environment if not already active
source backend/venv/bin/activate

# Initialize database tables
python -c "from backend.app.db.database import engine, Base; from backend.app.db.models import *; Base.metadata.create_all(bind=engine)"

# Create admin user
python backend/create_admin.py
```

---

## Step 6: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Update API endpoint in src/main.js or config file to point to your backend domain
# For example:
# axios.defaults.baseURL = 'https://api.yourdomain.com'

# Build production assets
npm run build
```

---

## Step 7: Configure nginx

Create an nginx configuration file `/etc/nginx/sites-available/flussonic-dashboard`:

```
server {
    listen 80;
    server_name your-frontend-domain.com;

    root /var/www/flussonic-dashboard/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and restart nginx:

```bash
sudo ln -s /etc/nginx/sites-available/flussonic-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 8: Run Backend with systemd

Create a systemd service file `/etc/systemd/system/flussonic-dashboard.service`:

```
[Unit]
Description=Flussonic Dashboard Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/flussonic-dashboard/backend
Environment="PATH=/var/www/flussonic-dashboard/backend/venv/bin"
ExecStart=/var/www/flussonic-dashboard/backend/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flussonic-dashboard
sudo systemctl start flussonic-dashboard
sudo systemctl status flussonic-dashboard
```

---

## Step 9: Setup Cron Job for Usage Collector

Edit crontab:

```bash
crontab -e
```

Add the following line to run usage collector every hour:

```
0 * * * * cd /var/www/flussonic-dashboard && source backend/venv/bin/activate && python backend/app/services/usage_collector.py
```

---

## Step 10: Verify Deployment

- Visit `http://your-frontend-domain.com` to see the frontend
- Visit `http://api.yourdomain.com/docs` to see FastAPI docs
- Test login and admin features

---

## Troubleshooting

- Check backend logs via `journalctl -u flussonic-dashboard -f`
- Check nginx logs in `/var/log/nginx/`
- Verify database connectivity and credentials

---

## Security Recommendations

- Use HTTPS with Let's Encrypt certificates
- Secure your server firewall
- Regularly update system packages and dependencies

---

This completes the deployment setup for Ubuntu 24 server.
