# Flussonic Dashboard - aaPanel Deployment Guide

## Prerequisites
1. aaPanel installed and running
2. MySQL/MariaDB database created (you've already done this)
3. Python Manager installed in aaPanel
4. Node.js Manager installed in aaPanel

## Step 1: Upload Project Files
1. Access your server via SSH or aaPanel File Manager
2. Navigate to `/www/wwwroot/`
3. Create a new directory for your project: `mkdir flussonic-dashboard`
4. Upload all project files to this directory

## Step 2: Configure Backend
1. In aaPanel, go to **Website** > **Add Site**
2. Select **Python Project**
3. Configure:
   - Domain: Your backend domain (e.g., api.yourdomain.com)
   - Project Path: `/www/wwwroot/flussonic-dashboard`
   - Python Version: 3.8+ (recommended)
   - Framework: FastAPI
4. Click **Submit**

## Step 3: Install Backend Dependencies
1. SSH into your server
2. Activate virtual environment:
   ```bash
   cd /www/wwwroot/flussonic-dashboard
   source venv/bin/activate
   ```
3. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```

## Step 4: Configure Environment
1. Create `.env` file in project root:
   ```bash
   nano /www/wwwroot/flussonic-dashboard/.env
   ```
2. Add configuration:
   ```env
   DATABASE_URL=mysql+mysqlconnector://[DB_USER]:[DB_PASS]@localhost/[DB_NAME]
   SECRET_KEY=your_secure_secret_key
   DEBUG=False
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

## Step 5: Initialize Database
1. Run database setup:
   ```bash
   cd /www/wwwroot/flussonic-dashboard
   source venv/bin/activate
   python backend/create_admin.py
   ```

## Step 6: Configure Frontend
1. In aaPanel, go to **Website** > **Add Site**
2. Select **Static Site** for frontend
3. Configure:
   - Domain: Your frontend domain (e.g., dashboard.yourdomain.com)
   - Project Path: `/www/wwwroot/flussonic-dashboard/frontend/dist`
4. Build frontend:
   ```bash
   cd /www/wwwroot/flussonic-dashboard/frontend
   npm install
   npm run build
   ```

## Step 7: Configure Python Project
1. Go to your Python project in aaPanel
2. Set configuration:
   - Run Directory: `/www/wwwroot/flussonic-dashboard`
   - Startup File: `backend/main.py`
   - Startup Function: `app`
   - Port: 5000 (or your chosen port)

## Step 8: Setup Cron Job
1. In aaPanel, go to **Cron**
2. Add new cron job:
   - Time: `0 * * * *` (runs hourly)
   - Script:
   ```bash
   cd /www/wwwroot/flussonic-dashboard
   source venv/bin/activate
   python backend/app/services/usage_collector.py
   ```

## Step 9: Final Configuration
1. Update frontend to point to your backend domain:
   Edit `frontend/src/main.js`:
   ```js
   axios.defaults.baseURL = 'https://api.yourdomain.com'
   ```
2. Rebuild frontend:
   ```bash
   cd frontend
   npm run build
   ```

## Verification
1. Access backend: `https://api.yourdomain.com` should show welcome message
2. Access frontend: `https://dashboard.yourdomain.com` should show login page
3. Test admin login (credentials from Step 5)

## Troubleshooting
- Check logs in `/www/wwwroot/flussonic-dashboard/logs`
- Verify database connection credentials
- Ensure ports are open in firewall
