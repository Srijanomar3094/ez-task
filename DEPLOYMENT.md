# Production Deployment Guide
## Ez-Task File Sharing System

---

## Overview
This guide covers deploying the Django file-sharing application to AWS EC2 with essential production setup.

---

## Prerequisites
- AWS Account with EC2 access
- Domain name (optional)
- SSH key pair for EC2 access

---

## 1. AWS EC2 Instance Setup

### Launch EC2 Instance
```bash
# Instance Specifications
Instance Type: t3.medium (2 vCPU, 4GB RAM)
OS: Ubuntu 22.04 LTS
Storage: 20GB GP3 SSD
```

## 2. System Setup

### Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server git
sudo apt install -y python3-dev default-libmysqlclient-dev build-essential
```

---

## 3. Database Setup

### Configure MySQL
```bash
sudo mysql_secure_installation
```

### Create Database
```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE ezshare_prod;
CREATE USER 'ezshare_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ezshare_prod.* TO 'ezshare_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 4. Application Deployment

### Clone and Setup
```bash
cd /home/ubuntu
git https://github.com/Srijanomar3094/ez-task.git
cd ez-task

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
```bash
nano .env
```

```env
SECRET_KEY=your_generated_secret_key
DEBUG=False
ALLOWED_HOSTS=your-ec2-public-ip,your-domain.com
DB_NAME=ezshare_prod
DB_USER=ezshare_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
FERNET_KEY=your_generated_fernet_key
```

### Generate Keys
```bash

### Setup Application
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
mkdir -p media
```

---

## 5. Gunicorn Setup

### Create Service File
```bash
sudo nano /etc/systemd/system/ezshare.service
```

```ini
[Unit]
Description=EzShare Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ez-task
Environment="PATH=/home/ubuntu/ez-task/venv/bin"
ExecStart=/home/ubuntu/ez-task/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/ez-task/ezshare.sock ezshare.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start ezshare
sudo systemctl enable ezshare
```

---

## 6. Nginx Configuration

### Create Site Config
```bash
sudo nano /etc/nginx/sites-available/ezshare
```

```nginx
server {
    listen 80;
    server_name your-ec2-public-ip your-domain.com;
    
    location /static/ {
        alias /home/ubuntu/ez-task/static/;
    }
    
    location /media/ {
        alias /home/ubuntu/ez-task/media/;
    }
    
    location / {
        proxy_pass http://unix:/home/ubuntu/ez-task/ezshare.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/ezshare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. SSL Certificate (Optional)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 8. Security Setup

### Set Permissions
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/ez-task
chmod 600 /home/ubuntu/ez-task/.env
```

### Configure Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## 9. Testing Deployment

### Check Services
```bash
sudo systemctl status ezshare
sudo systemctl status nginx
sudo systemctl status mysql
```

### Test Application
```bash
curl http://your-ec2-public-ip/api/list/
```

---

## 10. Maintenance

### Update Application
```bash
cd /home/ubuntu/ez-task
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ezshare
```

---