# 🚀 Streamlit Deployment Guide - SurveyRewards

Complete guide to deploy and run the SurveyRewards Streamlit application.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🏃 Quick Start (Local Development)

### Option 1: Using the Run Script (Easiest)

```bash
./run_streamlit.sh
```

The app will automatically:
- Install Streamlit if not present
- Create database on first run
- Start on http://localhost:8501

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install --break-system-packages streamlit pandas

# 2. Run the app
streamlit run streamlit_app.py --server.headless true --server.port 8501
```

### Option 3: Using Virtual Environment

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements_streamlit.txt

# 4. Run the app
streamlit run streamlit_app.py
```

## 🌐 Access the App

Once running, access at:
- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

## 📱 Features Available

### 1. **Home Page** (/)
- Landing page with platform overview
- Statistics display
- How it works section
- Featured surveys
- Quick login/register buttons

### 2. **Authentication** (/login, /register)
- User registration with email, username, password
- Secure login system
- Referral code support
- Auto-verification on registration

### 3. **User Dashboard** (/dashboard)
- Balance display
- Total earned/withdrawn
- Surveys completed count
- Referral code
- Available surveys
- Recent transactions

### 4. **Surveys** (/surveys, /survey_detail)
- Browse all available surveys
- View survey details
- Complete surveys with different question types:
  - Multiple choice
  - Rating (1-5)
  - Yes/No
  - Text answers
- Track completed surveys

### 5. **Withdrawals** (/withdraw)
- Multiple withdrawal methods:
  - EasyPaisa (24-48 hours)
  - JazzCash (24-48 hours)
  - PayPal (2-3 business days)
  - Bank Transfer (3-5 business days)
- Minimum withdrawal: $5.00
- Withdrawal history

### 6. **Transactions** (/transactions)
- Complete transaction history
- Survey rewards
- Referral bonuses
- Withdrawals

### 7. **FAQ** (/faq)
- Common questions and answers
- Expandable sections

### 8. **About** (/about)
- Platform information
- Mission and features
- Contact information

## 🗄️ Database

The app uses SQLite (`survey_rewards.db`):
- **Auto-created** on first run
- **Sample data** automatically populated
- **Persistent** - data survives restarts

To reset database:
```bash
rm survey_rewards.db
# Restart the app - fresh database will be created
```

## 🚀 Deployment Options

### 1. Streamlit Cloud (FREE - Recommended)

**Steps:**
1. Push code to GitHub repository
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your repository
5. Set:
   - **Branch**: main
   - **File path**: streamlit_app.py
   - **App URL**: your-custom-name
6. Click "Deploy!"

**Environment Variables (Optional):**
- Add in GitHub repo settings or Streamlit Cloud settings

**URL**: `https://your-app-name.streamlit.app`

### 2. Heroku

**Create `Procfile`:**
```
web: streamlit run streamlit_app.py --server.port $PORT --server.headless true
```

**Create `runtime.txt`:**
```
python-3.12.0
```

**Deploy:**
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Push to Heroku
git push heroku main

# Open app
heroku open
```

### 3. Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Add your repository
5. Set:
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.headless true`
   - **Python Version**: 3.12
6. Deploy!

### 4. Render

1. Go to https://render.com
2. Click "New Web Service"
3. Connect repository
4. Settings:
   - **Build Command**: `pip install -r requirements_streamlit.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.headless true`
5. Deploy!

### 5. DigitalOcean App Platform

1. Push to GitHub
2. Go to DigitalOcean App Platform
3. Create new app from repo
4. Configure:
   - **Run Command**: `streamlit run streamlit_app.py --server.port $PORT --server.headless true`
5. Deploy!

### 6. VPS/Dedicated Server

**Install Streamlit:**
```bash
pip install streamlit pandas
```

**Run with systemd:**

Create `/etc/systemd/system/streamlit.service`:
```ini
[Unit]
Description=SurveyRewards Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/p.g
ExecStart=/usr/local/bin/streamlit run streamlit_app.py --server.port 8501 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable streamlit
sudo systemctl start streamlit
sudo systemctl status streamlit
```

**Nginx Reverse Proxy (Optional):**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

## 🔧 Configuration

### Custom Port
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Custom Address
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### Disable Browser Open
```bash
streamlit run streamlit_app.py --server.headless true
```

### Production Mode
```bash
streamlit run streamlit_app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
```

## 📊 Sample Data

On first run, the app creates:
- **6 sample surveys** with questions
- **4 withdrawal methods** (EasyPaisa, JazzCash, PayPal, Bank Transfer)
- **Database schema** with all tables

### Survey Categories Included:
1. Consumer Shopping Habits
2. Technology Usage & Preferences
3. Health & Wellness Check
4. Food & Dining Preferences
5. Travel & Tourism Survey
6. Financial Planning & Savings

## 💰 Earning Structure

- **Survey Rewards**: $0.50 - $5.00 per survey
- **Referral Bonus**: $1.00 per friend who joins
- **Referral Commission**: 10% of referred user's earnings

## 🔒 Security Features

- Password hashing (SHA-256)
- Session-based authentication
- SQL injection prevention (parameterized queries)
- Input validation
- Unique email/username enforcement

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

### Streamlit Not Found
```bash
pip install --upgrade streamlit
```

### Database Errors
```bash
# Delete and recreate
rm survey_rewards.db
streamlit run streamlit_app.py
```

### Permission Denied
```bash
# Use --break-system-packages (if on externally managed env)
pip install --break-system-packages streamlit pandas

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install streamlit pandas
```

### App Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install --force-reinstall streamlit pandas
```

## 📝 File Structure

```
p.g/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt    # Python dependencies
├── run_streamlit.sh             # Quick start script
├── README_STREAMLIT.md          # Detailed documentation
├── DEPLOYMENT_GUIDE.md          # This file
└── survey_rewards.db            # SQLite database (auto-created)
```

## 📞 Support

For issues:
1. Check FAQ page in the app
2. Review this deployment guide
3. Check Streamlit documentation: https://docs.streamlit.io

## ✅ Post-Deployment Checklist

After deploying, verify:
- [ ] App loads without errors
- [ ] Home page displays correctly
- [ ] Registration works
- [ ] Login works
- [ ] Surveys are visible
- [ ] Can complete a survey
- [ ] Dashboard shows user data
- [ ] Withdrawal page loads
- [ ] FAQ page works
- [ ] All navigation works

## 🎉 Success!

Your SurveyRewards Streamlit app is now deployed and ready to use!

**Default URL**: http://localhost:8501 (local) or your deployment URL

**First Steps:**
1. Register a new account
2. Browse available surveys
3. Complete a survey to earn rewards
4. Check your dashboard
5. Request a withdrawal

---

**Happy Earning!** 💰
