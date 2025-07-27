#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os

class InstallerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flussonic Dashboard Installer")
        self.geometry("600x600")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Database config
        ttk.Label(frame, text="Database Configuration", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0,5))
        self.db_host = self.create_labeled_entry(frame, "DB Host:", "127.0.0.1")
        self.db_port = self.create_labeled_entry(frame, "DB Port:", "3306")
        self.db_name = self.create_labeled_entry(frame, "DB Name:", "")
        self.db_user = self.create_labeled_entry(frame, "DB User:", "")
        self.db_password = self.create_labeled_entry(frame, "DB Password:", "", show="*")

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Backend config
        ttk.Label(frame, text="Backend Configuration", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0,5))
        self.backend_domain = self.create_labeled_entry(frame, "Backend Domain:", "")
        self.python_version = self.create_labeled_entry(frame, "Python Version (aaPanel):", "3.10")

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Frontend config
        ttk.Label(frame, text="Frontend Configuration", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0,5))
        self.frontend_domain = self.create_labeled_entry(frame, "Frontend Domain:", "")

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Buttons
        self.install_button = ttk.Button(frame, text="Start Installation", command=self.start_installation)
        self.install_button.pack(pady=10)

        # Log output
        ttk.Label(frame, text="Installation Log:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_labeled_entry(self, parent, label_text, default="", show=None):
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=2)
        label = ttk.Label(container, text=label_text, width=20)
        label.pack(side=tk.LEFT)
        entry = ttk.Entry(container, show=show)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.insert(0, default)
        return entry

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update()

    def run_command(self, command, cwd=None):
        self.log(f"Running: {command}")
        try:
            process = subprocess.Popen(command, shell=True, cwd=cwd,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
            if process.returncode != 0:
                self.log(f"Command failed with exit code {process.returncode}")
                return False
            return True
        except Exception as e:
            self.log(f"Exception running command: {e}")
            return False

    def start_installation(self):
        self.install_button.config(state=tk.DISABLED)
        threading.Thread(target=self.installation_process).start()

    def installation_process(self):
        db_name = self.db_name.get().strip()
        db_user = self.db_user.get().strip()
        db_password = self.db_password.get().strip()
        backend_domain = self.backend_domain.get().strip()
        frontend_domain = self.frontend_domain.get().strip()
        python_version = self.python_version.get().strip()

        if not db_name or not db_user or not db_password or not backend_domain or not frontend_domain:
            messagebox.showerror("Input Error", "Please fill in all required fields.")
            self.install_button.config(state=tk.NORMAL)
            return

        if not os.path.exists("jd"):
            self.log("Cloning repository...")
            if not self.run_command("git clone https://github.com/shihan84/jd.git jd"):
                messagebox.showerror("Error", "Failed to clone repository.")
                self.install_button.config(state=tk.NORMAL)
                return
        else:
            self.log("Repository already cloned.")

        backend_path = os.path.join("jd", "backend")
        venv_path = os.path.join(backend_path, "venv")
        if not os.path.exists(venv_path):
            self.log("Creating virtual environment for backend...")
            if not self.run_command(f"python -m venv {venv_path}"):
                messagebox.showerror("Error", "Failed to create virtual environment.")
                self.install_button.config(state=tk.NORMAL)
                return
        else:
            self.log("Virtual environment already exists.")

        self.log("Installing backend dependencies...")
        if os.name == "nt":
            pip_install_cmd = f"{venv_path}\\Scripts\\pip install -r requirements.txt"
        else:
            pip_install_cmd = f"source {venv_path}/bin/activate && pip install -r requirements.txt"

        if not self.run_command(pip_install_cmd, cwd=backend_path):
            messagebox.showerror("Error", "Failed to install backend dependencies.")
            self.install_button.config(state=tk.NORMAL)
            return

        env_path = os.path.join("jd", ".env")
        self.log("Creating .env file...")
        env_content = f"DATABASE_URL=mysql+mysqlconnector://{db_user}:{db_password}@127.0.0.1:3306/{db_name}\nSECRET_KEY=your_strong_secret_key\n"
        try:
            with open(env_path, "w") as f:
                f.write(env_content)
            self.log(".env file created.")
        except Exception as e:
            self.log(f"Failed to create .env file: {e}")
            messagebox.showerror("Error", "Failed to create .env file.")
            self.install_button.config(state=tk.NORMAL)
            return

        frontend_path = os.path.join("jd", "frontend")
        self.log("Installing frontend dependencies...")
        if not self.run_command("npm install", cwd=frontend_path):
            messagebox.showerror("Error", "Failed to install frontend dependencies.")
            self.install_button.config(state=tk.NORMAL)
            return

        self.log("Building frontend...")
        if not self.run_command("npm run build", cwd=frontend_path):
            messagebox.showerror("Error", "Failed to build frontend.")
            self.install_button.config(state=tk.NORMAL)
            return

        self.log("\nInstallation complete.\n")
        self.log("Please follow these steps to finalize deployment on aaPanel:")
        self.log(f"1. Create Python project site in aaPanel with domain: {backend_domain}")
        self.log(f"2. Set project path to: /www/wwwroot/{backend_domain}")
        self.log(f"3. Select Python version: {python_version}")
        self.log(f"4. Set startup file to: backend/main.py")
        self.log(f"5. Set startup function to: app")
        self.log(f"6. Create frontend site in aaPanel with domain: {frontend_domain}")
        self.log(f"7. Copy contents of frontend/dist to /www/wwwroot/{frontend_domain}")
        self.log(f"8. Setup cron job to run usage_collector.py script periodically")
        self.log("Refer to README.md for detailed instructions.")

        messagebox.showinfo("Installation Complete", "Installation steps completed. Please follow the instructions in the log to finalize deployment.")
        self.install_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = InstallerGUI()
    app.mainloop()
