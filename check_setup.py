#!/usr/bin/env python3
"""
Pre-deployment Setup Checker for Flussonic Dashboard
Verifies aaPanel environment and requirements
"""

import os
import sys
import subprocess
import socket
import mysql.connector
from pathlib import Path

class SetupChecker:
    def __init__(self):
        self.server_ip = "82.180.144.106"
        self.backend_domain = "backend.imagetv.in"
        self.frontend_domain = "ott.imagetv.in"
        self.db_name = "flussonic_dash"
        self.db_user = "flussonic_dash"
        self.db_password = "i2dz73a32X8cJcFx"
        
        self.checks_passed = 0
        self.checks_total = 0
        
    def log(self, message, status="INFO"):
        """Log messages with status"""
        status_colors = {
            "PASS": "\033[92m✓\033[0m",
            "FAIL": "\033[91m✗\033[0m", 
            "WARN": "\033[93m⚠\033[0m",
            "INFO": "\033[94mℹ\033[0m"
        }
        print(f"{status_colors.get(status, '')} {message}")
        
    def check_item(self, description, check_func):
        """Run a check and track results"""
        self.checks_total += 1
        try:
            result = check_func()
            if result:
                self.log(f"{description}", "PASS")
                self.checks_passed += 1
                return True
            else:
                self.log(f"{description}", "FAIL")
                return False
        except Exception as e:
            self.log(f"{description} - Error: {e}", "FAIL")
            return False
    
    def check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version >= (3, 6):
            self.log(f"Python version: {version.major}.{version.minor}.{version.micro}", "INFO")
            return True
        return False
    
    def check_aapanel_installation(self):
        """Check if aaPanel is installed"""
        return os.path.exists("/www/wwwroot") and os.path.exists("/www/server")
    
    def check_database_connection(self):
        """Check database connectivity"""
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            conn.close()
            return True
        except:
            return False
    
    def check_domain_dns(self):
        """Check if domains resolve to server IP"""
        try:
            backend_ip = socket.gethostbyname(self.backend_domain)
            frontend_ip = socket.gethostbyname(self.frontend_domain)
            
            self.log(f"Backend domain {self.backend_domain} resolves to: {backend_ip}", "INFO")
            self.log(f"Frontend domain {self.frontend_domain} resolves to: {frontend_ip}", "INFO")
            
            return backend_ip == self.server_ip and frontend_ip == self.server_ip
        except:
            return False
    
    def check_node_npm(self):
        """Check Node.js and npm availability"""
        try:
            node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            
            if node_result.returncode == 0 and npm_result.returncode == 0:
                self.log(f"Node.js: {node_result.stdout.strip()}", "INFO")
                self.log(f"npm: {npm_result.stdout.strip()}", "INFO")
                return True
            return False
        except:
            return False
    
    def check_git(self):
        """Check Git availability"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Git: {result.stdout.strip()}", "INFO")
                return True
            return False
        except:
            return False
    
    def check_project_files(self):
        """Check if project files exist"""
        required_files = [
            "backend/main.py",
            "backend/requirements.txt",
            "backend/app/__init__.py",
            "frontend/package.json",
            "frontend/src/main.js"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"Missing files: {', '.join(missing_files)}", "WARN")
            return False
        return True
    
    def check_permissions(self):
        """Check write permissions for web directories"""
        try:
            # Check if we can create directories
            test_backend = f"/www/wwwroot/{self.backend_domain}_test"
            test_frontend = f"/www/wwwroot/{self.frontend_domain}_test"
            
            os.makedirs(test_backend, exist_ok=True)
            os.makedirs(test_frontend, exist_ok=True)
            
            # Clean up test directories
            os.rmdir(test_backend)
            os.rmdir(test_frontend)
            
            return True
        except:
            return False
    
    def check_mysql_version(self):
        """Check MySQL version compatibility"""
        try:
            result = subprocess.run(["mysql", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"MySQL: {result.stdout.strip()}", "INFO")
                return True
            return False
        except:
            return False
    
    def check_pip_packages(self):
        """Check if required Python packages can be installed"""
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "mysql-connector-python"
        ]
        
        try:
            for package in required_packages:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "show", package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try to install
                    install_result = subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], capture_output=True, text=True)
                    
                    if install_result.returncode != 0:
                        self.log(f"Failed to install {package}", "WARN")
                        return False
            
            return True
        except:
            return False
    
    def run_all_checks(self):
        """Run all setup checks"""
        print("=" * 60)
        print("🚀 Flussonic Dashboard - Pre-deployment Setup Check")
        print("=" * 60)
        print()
        
        print("📋 System Requirements:")
        self.check_item("Python 3.6+ installed", self.check_python_version)
        self.check_item("aaPanel installation detected", self.check_aapanel_installation)
        self.check_item("MySQL/MariaDB available", self.check_mysql_version)
        self.check_item("Node.js and npm available", self.check_node_npm)
        self.check_item("Git available", self.check_git)
        
        print("\n🔗 Network & DNS:")
        self.check_item("Database connection successful", self.check_database_connection)
        self.check_item("Domain DNS resolution", self.check_domain_dns)
        
        print("\n📁 File System:")
        self.check_item("Project files present", self.check_project_files)
        self.check_item("Web directory permissions", self.check_permissions)
        
        print("\n📦 Dependencies:")
        self.check_item("Python packages installable", self.check_pip_packages)
        
        print("\n" + "=" * 60)
        print(f"📊 Setup Check Results: {self.checks_passed}/{self.checks_total} passed")
        
        if self.checks_passed == self.checks_total:
            print("🎉 All checks passed! Ready for deployment.")
            self.print_deployment_instructions()
            return True
        else:
            print("❌ Some checks failed. Please resolve issues before deployment.")
            self.print_troubleshooting_tips()
            return False
    
    def print_deployment_instructions(self):
        """Print deployment instructions"""
        print("\n🚀 Ready to Deploy!")
        print("Run the following command to start deployment:")
        print(f"   python3 deploy_aapanel.py")
        print("\nOr follow the manual steps in AAPANEL_DEPLOYMENT_GUIDE.md")
    
    def print_troubleshooting_tips(self):
        """Print troubleshooting tips"""
        print("\n🔧 Troubleshooting Tips:")
        print("1. Install missing packages via aaPanel App Store")
        print("2. Verify database credentials in aaPanel Database manager")
        print("3. Check domain DNS settings point to your server IP")
        print("4. Ensure proper file permissions (chown www:www)")
        print("5. Install Node.js via aaPanel Node.js Manager")
        print("\nFor detailed help, see AAPANEL_DEPLOYMENT_GUIDE.md")

def main():
    checker = SetupChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
