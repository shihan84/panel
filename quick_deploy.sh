#!/bin/bash

# Flussonic Dashboard - Quick Deploy Script for aaPanel
# Server: 82.180.144.106
# Backend: backend.imagetv.in
# Frontend: ott.imagetv.in

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="82.180.144.106"
BACKEND_DOMAIN="backend.imagetv.in"
FRONTEND_DOMAIN="ott.imagetv.in"
DB_NAME="flussonic_dash"
DB_USER="flussonic_dash"
DB_PASSWORD="i2dz73a32X8cJcFx"

BACKEND_PATH="/www/wwwroot/${BACKEND_DOMAIN}"
FRONTEND_PATH="/www/wwwroot/${FRONTEND_DOMAIN}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_aapanel() {
    if [ ! -d "/www/wwwroot" ]; then
        log_error "aaPanel not detected. Please install aaPanel first."
        exit 1
    fi
    log_success "aaPanel detected"
}

check_database() {
    log_info "Testing database connection..."
    if mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME; SHOW TABLES;" >/dev/null 2>&1; then
        log_success "Database connection successful"
    else
        log_error "Database connection failed. Please check credentials."
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Update package list
    apt-get update -qq
    
    # Install required packages
    apt-get install -y python3-pip python3-venv nodejs npm git curl
    
    # Install PM2 globally for process management
    npm install -g pm2
    
    log_success "Dependencies installed"
}

setup_backend() {
    log_info "Setting up backend application..."
    
    # Create backend directory
    mkdir -p "$BACKEND_PATH"
    cd "$BACKEND_PATH"
    
    # Copy backend files
    if [ -d "$(pwd)/backend" ]; then
        rm -rf backend
    fi
    cp -r "$(dirname "$0")/backend" .
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install requirements
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    # Create .env file
    cat > .env << EOF
DATABASE_URL=mysql+mysqlconnector://${DB_USER}:${DB_PASSWORD}@127.0.0.1:3306/${DB_NAME}
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
CORS_ORIGINS=https://${FRONTEND_DOMAIN}
BACKEND_DOMAIN=${BACKEND_DOMAIN}
FRONTEND_DOMAIN=${FRONTEND_DOMAIN}
SERVER_IP=${SERVER_IP}
EOF
    
    # Create startup script for aaPanel
    cat > app.py << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add project path to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
EOF
    
    # Initialize database
    python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from backend.app.db.database import engine, Base
from backend.app.db.models import *

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
EOF
    
    # Set permissions
    chown -R www:www "$BACKEND_PATH"
    chmod -R 755 "$BACKEND_PATH"
    
    log_success "Backend setup completed"
}

setup_frontend() {
    log_info "Setting up frontend application..."
    
    # Create frontend directory
    mkdir -p "$FRONTEND_PATH"
    
    # Copy and build frontend
    TEMP_FRONTEND="/tmp/frontend_build"
    rm -rf "$TEMP_FRONTEND"
    cp -r "$(dirname "$0")/frontend" "$TEMP_FRONTEND"
    
    cd "$TEMP_FRONTEND"
    
    # Update API endpoint in frontend
    if [ -f "src/main.js" ]; then
        sed -i "s|localhost:8000|${BACKEND_DOMAIN}|g" src/main.js
        sed -i "s|127.0.0.1:8000|${BACKEND_DOMAIN}|g" src/main.js
        sed -i "s|http://|https://|g" src/main.js
    fi
    
    # Install dependencies and build
    npm install
    npm run build
    
    # Copy built files to web directory
    if [ -d "dist" ]; then
        cp -r dist/* "$FRONTEND_PATH/"
        log_success "Frontend built and deployed"
    else
        log_error "Frontend build failed"
        exit 1
    fi
    
    # Set permissions
    chown -R www:www "$FRONTEND_PATH"
    chmod -R 755 "$FRONTEND_PATH"
    
    # Clean up
    rm -rf "$TEMP_FRONTEND"
}

setup_cron_job() {
    log_info "Setting up cron job for usage collector..."
    
    CRON_COMMAND="0 * * * * cd ${BACKEND_PATH} && ${BACKEND_PATH}/venv/bin/python ${BACKEND_PATH}/backend/app/services/usage_collector.py"
    
    # Add to crontab if not already present
    (crontab -l 2>/dev/null | grep -v "usage_collector.py"; echo "$CRON_COMMAND") | crontab -
    
    log_success "Cron job added"
}

create_admin_user() {
    log_info "Creating admin user..."
    
    cd "$BACKEND_PATH"
    source venv/bin/activate
    
    # Create admin user script
    cat > create_admin_temp.py << 'EOF'
import sys
import getpass
sys.path.insert(0, '.')
from sqlalchemy.orm import sessionmaker
from backend.app.db.database import engine
from backend.app.db.models import User
from backend.app.core.security import get_password_hash

def create_admin():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("Creating admin user...")
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"User '{username}' already exists.")
        return
    
    hashed_password = get_password_hash(password)
    admin_user = User(
        username=username,
        hashed_password=hashed_password,
        is_admin=1
    )
    
    session.add(admin_user)
    session.commit()
    session.close()
    
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    create_admin()
EOF
    
    python3 create_admin_temp.py
    rm create_admin_temp.py
}

setup_ssl() {
    log_info "SSL setup instructions..."
    log_warning "Please setup SSL certificates manually in aaPanel:"
    log_warning "1. Go to Website -> ${BACKEND_DOMAIN} -> SSL"
    log_warning "2. Go to Website -> ${FRONTEND_DOMAIN} -> SSL"
    log_warning "3. Use Let's Encrypt or upload your certificates"
    log_warning "4. Enable 'Force HTTPS'"
}

print_summary() {
    echo ""
    echo "=================================="
    echo "🎉 DEPLOYMENT COMPLETED!"
    echo "=================================="
    echo ""
    echo "📋 Configuration Summary:"
    echo "   Server IP: $SERVER_IP"
    echo "   Backend: https://$BACKEND_DOMAIN"
    echo "   Frontend: https://$FRONTEND_DOMAIN"
    echo "   Database: $DB_NAME"
    echo ""
    echo "📁 File Locations:"
    echo "   Backend: $BACKEND_PATH"
    echo "   Frontend: $FRONTEND_PATH"
    echo "   Environment: $BACKEND_PATH/.env"
    echo ""
    echo "🔧 Next Steps in aaPanel:"
    echo "1. Create Python Project:"
    echo "   - Domain: $BACKEND_DOMAIN"
    echo "   - Path: $BACKEND_PATH"
    echo "   - Startup File: app.py"
    echo "   - Python Version: 3.6+"
    echo ""
    echo "2. Create Website:"
    echo "   - Domain: $FRONTEND_DOMAIN"
    echo "   - Path: $FRONTEND_PATH"
    echo ""
    echo "3. Setup SSL certificates for both domains"
    echo ""
    echo "🧪 Test URLs:"
    echo "   Backend API: https://$BACKEND_DOMAIN/docs"
    echo "   Frontend: https://$FRONTEND_DOMAIN"
    echo ""
    echo "📚 For detailed instructions, see:"
    echo "   - AAPANEL_DEPLOYMENT_GUIDE.md"
    echo "   - DEPLOYMENT_SUMMARY.txt"
    echo ""
}

# Main deployment process
main() {
    echo "🚀 Starting Flussonic Dashboard Deployment"
    echo "Server: $SERVER_IP"
    echo "Backend: $BACKEND_DOMAIN"
    echo "Frontend: $FRONTEND_DOMAIN"
    echo ""
    
    # Pre-flight checks
    check_root
    check_aapanel
    check_database
    
    # Installation steps
    install_dependencies
    setup_backend
    setup_frontend
    setup_cron_job
    create_admin_user
    setup_ssl
    
    # Summary
    print_summary
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "🎯 Ready to configure in aaPanel!"
}

# Run main function
main "$@"
