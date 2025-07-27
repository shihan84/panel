# Flussonic Dashboard - aaPanel Deployment Tools

This repository contains automated deployment tools specifically designed for your aaPanel server setup.

## 🎯 Your Server Configuration

- **Server IP**: 82.180.144.106
- **aaPanel Version**: 7.0.21
- **MySQL Version**: 10.11.6
- **Python Version**: 3.6.8
- **Database**: flussonic_dash
- **Backend Domain**: backend.imagetv.in
- **Frontend Domain**: ott.imagetv.in

## 📦 Deployment Tools Overview

### 1. `check_setup.py` - Pre-deployment Checker
Verifies your server environment before deployment.

**Usage:**
```bash
python3 check_setup.py
```

**What it checks:**
- Python version compatibility
- aaPanel installation
- Database connectivity
- Domain DNS resolution
- Required packages
- File permissions

### 2. `deploy_aapanel.py` - Automated Python Deployer
Comprehensive Python-based deployment script.

**Usage:**
```bash
python3 deploy_aapanel.py
```

**What it does:**
- Sets up backend with virtual environment
- Installs Python dependencies
- Creates configuration files
- Initializes database tables
- Builds and deploys frontend
- Sets up cron jobs
- Configures permissions

### 3. `quick_deploy.sh` - Bash Quick Deploy
Fast bash-based deployment for Linux environments.

**Usage:**
```bash
sudo chmod +x quick_deploy.sh
sudo ./quick_deploy.sh
```

**Features:**
- System dependency installation
- Automated backend/frontend setup
- Database initialization
- Admin user creation
- SSL setup guidance

### 4. `AAPANEL_DEPLOYMENT_GUIDE.md` - Manual Instructions
Detailed step-by-step manual deployment guide.

## 🚀 Recommended Deployment Process

### Option A: Automated Deployment (Recommended)

1. **Check Prerequisites:**
   ```bash
   python3 check_setup.py
   ```

2. **Run Automated Deployment:**
   ```bash
   python3 deploy_aapanel.py
   ```

3. **Configure aaPanel Projects** (see output instructions)

### Option B: Quick Bash Deployment

1. **Run Quick Deploy:**
   ```bash
   sudo ./quick_deploy.sh
   ```

2. **Follow aaPanel Configuration Steps**

### Option C: Manual Deployment

Follow the detailed instructions in `AAPANEL_DEPLOYMENT_GUIDE.md`

## 📋 Post-Deployment aaPanel Configuration

After running any deployment script, you need to configure aaPanel:

### Backend Configuration
1. Go to **Website** → **Add Site**
2. Select **Python Project**
3. Configure:
   - **Domain**: backend.imagetv.in
   - **Project Path**: /www/wwwroot/backend.imagetv.in
   - **Startup File**: app.py
   - **Python Version**: 3.6+
4. **Save** and **Restart**

### Frontend Configuration
1. Go to **Website** → **Add Site**
2. Select **Static Site**
3. Configure:
   - **Domain**: ott.imagetv.in
   - **Document Root**: /www/wwwroot/ott.imagetv.in
4. **Save**

### SSL Setup
1. For both domains, go to **Website** → **Domain** → **SSL**
2. Use **Let's Encrypt** or upload certificates
3. Enable **Force HTTPS**

### Cron Job Setup
1. Go to **Cron** → **Add Cron Job**
2. Configure:
   - **Name**: Flussonic Usage Collector
   - **Type**: Shell Script
   - **Schedule**: 0 * * * * (every hour)
   - **Script**: 
     ```bash
     cd /www/wwwroot/backend.imagetv.in && venv/bin/python backend/app/services/usage_collector.py
     ```

## 🧪 Testing Your Deployment

### Backend API Test
Visit: `https://backend.imagetv.in/docs`
- Should show FastAPI documentation
- Test endpoints are accessible

### Frontend Test
Visit: `https://ott.imagetv.in`
- Should load dashboard login page
- No console errors in browser

### Database Test
```bash
mysql -u flussonic_dash -p flussonic_dash
# Password: i2dz73a32X8cJcFx
SHOW TABLES;
```
Should show: users, flussonic_servers, streams, user_streams, traffic_usage

## 🔧 Troubleshooting

### Common Issues

**Backend 500 Error:**
- Check `/www/wwwroot/backend.imagetv.in/logs/error.log`
- Verify database connection in `.env` file
- Ensure all Python packages are installed

**Frontend Blank Page:**
- Check browser console for errors
- Verify API endpoint configuration
- Check CORS settings

**Database Connection Failed:**
- Verify database credentials
- Check MySQL service status
- Test connection manually

**Permission Denied:**
```bash
sudo chown -R www:www /www/wwwroot/backend.imagetv.in
sudo chown -R www:www /www/wwwroot/ott.imagetv.in
sudo chmod -R 755 /www/wwwroot/backend.imagetv.in
sudo chmod -R 755 /www/wwwroot/ott.imagetv.in
```

### Log Locations
- **Backend Logs**: `/www/wwwroot/backend.imagetv.in/logs/`
- **aaPanel Logs**: `/www/server/panel/logs/`
- **System Logs**: `/var/log/`

## 📁 File Structure After Deployment

```
/www/wwwroot/backend.imagetv.in/
├── backend/                 # Backend application code
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── app/                # Application modules
├── venv/                   # Python virtual environment
├── .env                    # Environment configuration
├── app.py                  # aaPanel startup script
└── logs/                   # Application logs

/www/wwwroot/ott.imagetv.in/
├── index.html              # Frontend entry point
├── static/                 # Static assets
└── ...                     # Built frontend files
```

## 🔐 Security Considerations

1. **Change Default Passwords**: Update database and admin passwords
2. **Secure .env File**: Ensure proper permissions (600)
3. **Regular Updates**: Keep dependencies updated
4. **Backup Strategy**: Implement regular backups
5. **Monitor Logs**: Check for suspicious activity

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review deployment logs
3. Verify aaPanel configuration
4. Test individual components

## 📚 Additional Resources

- **aaPanel Documentation**: https://www.aapanel.com/reference.html
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Vue.js Documentation**: https://vuejs.org/guide/

---

**Last Updated**: $(date)
**Target Server**: 82.180.144.106
**Domains**: backend.imagetv.in, ott.imagetv.in
