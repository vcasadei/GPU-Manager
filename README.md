
# 🚦 GPU Manager Dashboard

A lightweight, real-time coordination dashboard for shared GPU servers.

This Streamlit application allows research teams to manually coordinate GPU usage, view real-time hardware statistics, and provides administration controls (server restart) via a web interface.

## ✨ Features

* **Real-time Hardware Monitoring:** Displays live stats from `gpustat` (Memory, Utilization, Users).
* **Manual Booking System:** Users can "Check-in" and "Check-out" to signal they are using the machine.
* **Usage History:** Keeps a CSV log of who used the GPU, for what activity, and for how long.
* **Admin Controls:** A protected "Restart Server" button to reboot the machine remotely.
* **UX Enhancements:** Toast notifications and auto-clearing forms for smooth interaction.

## 🛠️ Prerequisites

* **Linux Server** (Ubuntu/Debian recommended)
* **Python 3.8+**
* **UV** (An extremely fast Python package installer and resolver)
* **NVIDIA Drivers** (Expected for `gpustat`)

---

## 🚀 Installation & Deployment

### 1. Setup the Repository
Connect to your server and clone the repository:

```bash
git clone [https://github.com/your-username/GPU-Manager.git](https://github.com/your-username/GPU-Manager.git)
cd GPU-Manager
```

### 2. Install Dependencies (using UV)

This project uses `uv` for dependency management.


```bash
# Install uv if you don't have it
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Initialize and install dependencies
uv init
uv add streamlit pandas gpustat
```

### 3. Configure Permissions (Crucial for Restart Button)

To allow the web dashboard to restart the server, you must grant the user permission to run `shutdown` without a password.

1.  Open the sudo configuration
    
    ```bash
    sudo visudo
    ```
    
2.  Add this line at the very bottom (replace `your_username` with your actual Linux user, e.g., `ubuntu`):
    
    
    ```plaintext
    your_username ALL=(ALL) NOPASSWD: /usr/sbin/shutdown
    ```
    
3.  Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).
    

----------

## 🤖 Run as a Service (Systemd)

To keep the dashboard running 24/7 and restart automatically on boot, set it up as a system service.

### 1. Get your Python Path

Run this inside the `GPU-Manager` folder and **copy the output**:


```bash
uv run which python
# Example output: /home/ubuntu/GPU-Manager/.venv/bin/python
```

### 2. Create the Service File

Create the service configuration file:


```bash
sudo nano /etc/systemd/system/gpu-dashboard.service

```

Paste the following content. **Make sure to update the `User`, `WorkingDirectory`, and `ExecStart` paths** to match your server setup.

```Ini, TOML
[Unit]
Description=GPU Dashboard Web App
After=network.target

[Service]
# CHANGE THIS to your Linux username
User=ubuntu
Group=ubuntu

# CHANGE THIS to the path where you cloned the repo
WorkingDirectory=/home/ubuntu/GPU-Manager

# CHANGE THIS to the python path you copied in Step 1
ExecStart=/home/ubuntu/GPU-Manager/.venv/bin/python -m streamlit run gpu_dashboard.py --server.port 8085

# Restart automatically if it crashes
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start


```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service on boot
sudo systemctl enable gpu-dashboard

# Start the service immediately
sudo systemctl start gpu-dashboard
```

### 4. Check Status


```bash
sudo systemctl status gpu-dashboard
```

----------

## 🌐 Accessing the Dashboard

Open your web browser and navigate to:

```plaintext
http://<your-server-ip>:8085
```

> **Note:** If the page does not load, ensure port **8085** is allowed in your firewall (UFW or Cloud Security Groups).
> 
> -   **UFW:** `sudo ufw allow 8085`
>     

----------

## 💻 Local Development (Testing)

If you want to run this on your local machine for testing:


```bash
uv run streamlit run gpu_dashboard.py
```