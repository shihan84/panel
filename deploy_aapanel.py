#!/usr/bin/env python3
"""
Automated Deployment Script for Flussonic Dashboard on aaPanel
Tailored for: backend.imagetv.in & ott.imagetv.in
Server: 82.180.144.106
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import secrets
import string

class AAPanelDeployer:
    def __init__(self):
        # Server Configuration
        self.server_ip = "82.180.144.106"
        self.backend_domain = "backend.imagetv.in"
        self.frontend_domain = "ott.imagetv.in"
        
        # Database Configuration
        self.db_name = "flussonic_dash"
        self.db_user = "flussonic_dash"
        self.db_password = "i2dz73a32X8cJcFx"
        self.db_host = "127.0.0.1"
        self.db_port = "3306"
        
        # Paths
        self.backend_path = f"/www/wwwroot/{self.backend_domain}"
        self.frontend_path = f"/www/wwwroot/{self.frontend_domain}"
        self.project_root = os.getcwd()
        
        # Generate secure secret key
        self.secret_key = self.generate_secret_key()
        
    def generate_secret_key(self, length=50):
        """Generate a secure secret key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_command(self, command, cwd=None, check=True):
        """Run shell command and return result"""
        self.log(f"Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                check=check
            )
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error: {e.stderr.strip()}", "ERROR")
            raise
    
    def check_prerequisites(self):
        """Check if required tools are available"""
        self.log("Checking prerequisites...")
        
        # Check if we're running on the server
        try:
            hostname = subprocess.check_output("hostname -I", shell=True).decode().strip()
            if self.server_ip not in hostname:
                self.log(f"Warning: Not running on target server {self.server_ip}", "WARNING")
        except:
            pass
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 6):
            raise Exception("Python 3.6+ required")
        self.log(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check if aaPanel directories exist
        if not os.path.exists("/www/wwwroot"):
            raise Exception("aaPanel not detected. /www/wwwroot directory not found.")
        
        # Check MySQL connection
        try:
            self.run_command(f"mysql -u {self.db_user} -p{self.db_password} -e 'USE {self.db_name}; SHOW TABLES;'")
            self.log("Database connection successful")
        except:
            self.log("Database connection failed. Please verify credentials.", "ERROR")
            raise
    
    def setup_backend(self):
        """Setup backend application"""
        self.log("Setting up backend...")
        
        # Create backend directory if it doesn't exist
        os.makedirs(self.backend_path, exist_ok=True)
        
        # Copy backend files
        backend_src = os.path.join(self.project_root, "backend")
        if os.path.exists(backend_src):
            self.log("Copying backend files...")
            for item in os.listdir(backend_src):
                src = os.path.join(backend_src, item)
                dst = os.path.join(self.backend_path, "backend", item)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        # Create virtual environment
        venv_path = os.path.join(self.backend_path, "venv")
        if not os.path.exists(venv_path):
            self.log("Creating virtual environment...")
            self.run_command(f"python3 -m venv {venv_path}")
        
        # Install requirements
        self.log("Installing Python dependencies...")
        pip_path = os.path.join(venv_path, "bin", "pip")
        requirements_path = os.path.join(self.backend_path, "backend", "requirements.txt")
        
        if os.path.exists(requirements_path):
            self.run_command(f"{pip_path} install --upgrade pip")
            self.run_command(f"{pip_path} install -r {requirements_path}")
        
        # Create .env file
        self.create_env_file()
        
        # Initialize database
        self.initialize_database()
    
    def create_env_file(self):
        """Create environment configuration file"""
        self.log("Creating .env file...")
        
        env_content = f"""# Flussonic Dashboard Configuration
DATABASE_URL=mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}
SECRET_KEY={self.secret_key}
DEBUG=False
CORS_ORIGINS=https://{self.frontend_domain}

# Server Configuration
BACKEND_DOMAIN={self.backend_domain}
FRONTEND_DOMAIN={self.frontend_domain}
SERVER_IP={self.server_ip}

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
"""
        
        env_path = os.path.join(self.backend_path, ".env")
        with open(env_path, "w") as f:
            f.write(env_content)
        
        self.log(f".env file created at {env_path}")
    
    def initialize_database(self):
        """Initialize database tables"""
        self.log("Initializing database...")
        
        python_path = os.path.join(self.backend_path, "venv", "bin", "python")
        init_script = f"""
import sys
sys.path.append('{self.backend_path}')
from backend.app.db.database import engine, Base
from backend.app.db.models import User, FlussonicServer, Stream, UserStream, TrafficUsage

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
"""
        
        script_path = os.path.join(self.backend_path, "init_db.py")
        with open(script_path, "w") as f:
            f.write(init_script)
        
        try:
            self.run_command(f"{python_path} {script_path}", cwd=self.backend_path)
            os.remove(script_path)  # Clean up
        except Exception as e:
            self.log(f"Database initialization failed: {e}", "ERROR")
            raise
    
    def create_admin_user(self):
        """Create admin user interactively"""
        self.log("Creating admin user...")
        
        python_path = os.path.join(self.backend_path, "venv", "bin", "python")
        admin_script = os.path.join(self.backend_path, "backend", "create_admin.py")
        
        if os.path.exists(admin_script):
            self.log("Please run the following command to create admin user:")
            self.log(f"cd {self.backend_path} && {python_path} {admin_script}")
        else:
            # Create inline admin creation script
            create_admin_script = f"""
import sys
import getpass
sys.path.append('{self.backend_path}')
from sqlalchemy.orm import sessionmaker
from backend.app.db.database import engine
from backend.app.db.models import User
from backend.app.core.security import get_password_hash

def create_admin():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"User '{{username}}' already exists.")
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
    
    print(f"Admin user '{{username}}' created successfully!")

if __name__ == "__main__":
    create_admin()
"""
            
            script_path = os.path.join(self.backend_path, "create_admin_temp.py")
            with open(script_path, "w") as f:
                f.write(create_admin_script)
            
            self.log(f"Run: cd {self.backend_path} && {python_path} create_admin_temp.py")
    
    def setup_frontend(self):
        """Setup frontend application"""
        self.log("Setting up frontend...")
        
        # Create frontend directory
        os.makedirs(self.frontend_path, exist_ok=True)
        
        # Copy frontend source
        frontend_src = os.path.join(self.project_root, "frontend")
        frontend_build_dir = os.path.join(self.backend_path, "frontend_build")
        
        if os.path.exists(frontend_src):
            # Copy to build directory
            if os.path.exists(frontend_build_dir):
                shutil.rmtree(frontend_build_dir)
            shutil.copytree(frontend_src, frontend_build_dir)
            
            # Update API endpoint in frontend config
            self.update_frontend_config(frontend_build_dir)
            
            # Install npm dependencies and build
            try:
                self.run_command("npm install", cwd=frontend_build_dir)
                self.run_command("npm run build", cwd=frontend_build_dir)
                
                # Copy built files to web directory
                dist_path = os.path.join(frontend_build_dir, "dist")
                if os.path.exists(dist_path):
                    for item in os.listdir(dist_path):
                        src = os.path.join(dist_path, item)
                        dst = os.path.join(self.frontend_path, item)
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
                    
                    self.log("Frontend built and deployed successfully")
                else:
                    self.log("Frontend build failed - dist directory not found", "ERROR")
                    
            except Exception as e:
                self.log(f"Frontend build failed: {e}", "ERROR")
                self.log("You may need to build frontend manually", "WARNING")
    
    def update_frontend_config(self, frontend_dir):
        """Update frontend configuration with correct API endpoint"""
        self.log("Updating frontend configuration...")
        
        # Update main.js or config files to point to correct backend
        main_js_path = os.path.join(frontend_dir, "src", "main.js")
        if os.path.exists(main_js_path):
            with open(main_js_path, "r") as f:
                content = f.read()
            
            # Replace localhost or other API endpoints
            content = content.replace("localhost:8000", self.backend_domain)
            content = content.replace("127.0.0.1:8000", self.backend_domain)
            content = content.replace("http://", "https://")
            
            with open(main_js_path, "w") as f:
                f.write(content)
    
    def setup_cron_job(self):
        """Setup cron job for usage collector"""
        self.log("Setting up cron job...")
        
        python_path = os.path.join(self.backend_path, "venv", "bin", "python")
        collector_script = os.path.join(self.backend_path, "backend", "app", "services", "usage_collector.py")
        
        cron_command = f"0 * * * * cd {self.backend_path} && {python_path} {collector_script}"
        
        self.log("Add the following cron job in aaPanel:")
        self.log(f"Command: {cron_command}")
        self.log("Schedule: Every hour (0 * * * *)")
    
    def create_startup_script(self):
        """Create startup script for aaPanel"""
        self.log("Creating startup script...")
        
        startup_content = f"""#!/usr/bin/env python3
import sys
import os

# Add project path to Python path
sys.path.insert(0, '{self.backend_path}')

# Import the FastAPI app
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
"""
        
        startup_path = os.path.join(self.backend_path, "app.py")
        with open(startup_path, "w") as f:
            f.write(startup_content)
        
        self.log(f"Startup script created: {startup_path}")
    
    def set_permissions(self):
        """Set proper file permissions"""
        self.log("Setting file permissions...")
        
        try:
            self.run_command(f"chown -R www:www {self.backend_path}")
            self.run_command(f"chown -R www:www {self.frontend_path}")
            self.run_command(f"chmod -R 755 {self.backend_path}")
            self.run_command(f"chmod -R 755 {self.frontend_path}")
        except Exception as e:
            self.log(f"Permission setting failed: {e}", "WARNING")
    
    def generate_deployment_summary(self):
        """Generate deployment summary"""
        summary = f"""
=== DEPLOYMENT SUMMARY ===

Server: {self.server_ip}
Backend Domain: https://{self.backend_domain}
Frontend Domain: https://{self.frontend_domain}

Backend Path: {self.backend_path}
Frontend Path: {self.frontend_path}

Database: {self.db_name}
Database User: {self.db_user}

=== NEXT STEPS ===

1. Configure aaPanel Python Project:
   - Domain: {self.backend_domain}
   - Project Path: {self.backend_path}
   - Startup File: app.py
   - Python Version: 3.6+

2. Configure aaPanel Website:
   - Domain: {self.frontend_domain}
   - Document Root: {self.frontend_path}

3. Setup SSL certificates for both domains

4. Create admin user:
   cd {self.backend_path}
   source venv/bin/activate
   python backend/create_admin.py

5. Add cron job in aaPanel:
   Schedule: 0 * * * *
   Command: cd {self.backend_path} && venv/bin/python backend/app/services/usage_collector.py

6. Test deployment:
   - Backend API: https://{self.backend_domain}/docs
   - Frontend: https://{self.frontend_domain}

=== CONFIGURATION FILES ===
- Environment: {self.backend_path}/.env
- Startup Script: {self.backend_path}/app.py

"""
        
        summary_path = os.path.join(self.project_root, "DEPLOYMENT_SUMMARY.txt")
        with open(summary_path, "w") as f:
            f.write(summary)
        
        print(summary)
        self.log(f"Deployment summary saved to: {summary_path}")
    
    def deploy(self):
        """Main deployment function"""
        try:
            self.log("Starting Flussonic Dashboard deployment...")
            
            # Check prerequisites
            self.check_prerequisites()
            
            # Setup backend
            self.setup_backend()
            
            # Setup frontend
            self.setup_frontend()
            
            # Create startup script
            self.create_startup_script()
            
            # Set permissions
            self.set_permissions()
            
            # Setup cron job info
            self.setup_cron_job()
            
            # Create admin user info
            self.create_admin_user()
            
            # Generate summary
            self.generate_deployment_summary()
            
            self.log("Deployment completed successfully!", "SUCCESS")
            
        except Exception as e:
            self.log(f"Deployment failed: {e}", "ERROR")
            sys.exit(1)

if __name__ == "__main__":
    deployer = AAPanelDeployer()
    deployer.deploy()
