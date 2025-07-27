# Flussonic Client & Admin Dashboard

This project provides a web-based dashboard for clients to monitor their Flussonic stream's data usage, view a live preview, and manage restreaming. It also includes an admin panel to manage multiple Flussonic servers, create client accounts, and assign specific streams to them.

## Technology Stack

- **Backend:** Python (FastAPI)
- **Frontend:** Vue.js
- **Database:** MySQL/MariaDB
- **Deployment:** aaPanel

## Setup and Deployment on aaPanel

### 1. Prerequisites

- A server with aaPanel installed.
- A domain or subdomain pointed to your server's IP address.
- Flussonic Media Server installed and running.

### 2. Database Setup

1.  Log in to your aaPanel dashboard.
2.  Go to the **Databases** section and click **Add Database**.
3.  Create a new MySQL/MariaDB database. Note down the database name, username, and password.

### 3. Backend Setup

1.  **Install Python via Python Manager:**
    *   In aaPanel, go to the **App Store**.
    *   Find and install **Python Manager** (e.g., v2.5).
    *   Open Python Manager and install a recent version of Python, such as **3.10**. This project requires Python 3.7+.

2.  **Create the Python Project Site:**
    *   Go to the **Website** section and click **Add Site**.
    *   Select **Python project** from the dropdown menu.
    *   Fill in your domain name.
    *   For the **Project path**, select the directory that was just created (e.g., `/www/wwwroot/your_domain`).
    *   For **Python version**, select the version you installed via Python Manager (e.g., 3.10).
    *   Click **Submit**. This will also create a virtual environment for you.

3.  **Deploy the Code:**
    *   Connect to your server via SSH or use the **Terminal** feature in aaPanel.
    *   Navigate to your project directory: `cd /www/wwwroot/your_domain`
    *   Remove any default files created by aaPanel: `rm -f *.py requirements.txt`
    *   Clone this repository's contents into the current directory: `git clone https://github.com/shihan84/jd.git .`
    *   Activate the virtual environment created by aaPanel: `source venv/bin/activate`
    *   Install the required Python packages: `pip install -r backend/requirements.txt`

4.  **Configure Environment:**
    *   Create a `.env` file in the project root (`/www/wwwroot/your_domain`) by copying `.env.example`.
    *   Edit the `.env` file with your database credentials and a strong secret key.
        ```
        DATABASE_URL=mysql+mysqlconnector://your_db_user:your_db_password@127.0.0.1:3306/your_db_name
        SECRET_KEY=your_strong_secret_key
        ```

5.  **Configure aaPanel Project:**
    *   Go back to the **Website** settings for your project in aaPanel.
    *   Set the **Run directory** to `/www/wwwroot/your_domain`.
    *   Set the **Startup file/directory** to `backend/main.py`.
    *   Set the **Startup function** to `app`.
    *   Save the settings and restart the Python project.


### 4. Frontend Setup

1.  Go to the **Website** section in aaPanel and click **Add Site**.
2.  Create a new site for your frontend (e.g., `dashboard.yourdomain.com`).
3.  Connect to your server via SSH or use the **Terminal** feature in aaPanel.
4.  Navigate to the `frontend` directory in your project.
5.  Install the required Javascript packages: `npm install`
6.  Build the frontend application: `npm run build`
7.  Copy the contents of the `frontend/dist` directory to the root of your frontend site (`/www/wwwroot/dashboard.yourdomain.com`).

### 5. Scheduled Task for Data Collection

1.  Go to the **Cron** section in aaPanel.
2.  Click **Add Cron Job**.
3.  Set the **Type of Task** to **Shell Script**.
4.  Set the **Name of Task** to "Flussonic Usage Collector".
5.  Set the **Period** to run as often as you need (e.g., every hour).
6.  In the **Script content** box, add the command to run the usage collector script:
    ```bash
    /www/wwwroot/your_domain/venv/bin/python /www/wwwroot/your_domain/backend/app/services/usage_collector.py
    ```

7.  Click **Add Task**.
