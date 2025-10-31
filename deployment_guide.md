# Deployment Guide: Zukunftstag Simulation App

## Overview
This guide compares deployment options for the Zukunftstag simulation application and provides step-by-step instructions for the recommended approach.

## Run Commands
**Run the app local**: python -m streamlit run app.py --server.port 8504
**Generate QR Code**: python generate_qr_codes.py
**Generate Test Data**: python generate_test_data.py
**Initialize Sessions**: python initialize_sessions.py

## Session Management

The app uses **three separate sessions** to organize workshop data:

1. **Morning Session** (`morning_session`) - For live morning workshop (09:00 - 11:30)
2. **Afternoon Session** (`afternoon_session`) - For live afternoon workshop (13:30 - 16:00)  
3. **Test Session** (`test_session`) - For development and testing (pre-populated with 29 teams)

### Development Mode Setup

```bash
# 1. Initialize all three sessions
python initialize_sessions.py

# 2. Generate test data (populates ONLY test_session with 29 teams)
python generate_test_data.py
```

**Current configuration (`config.py`):**
```python
DEV_MODE = True                  # Enables development features
DEV_BYPASS_QR = True            # No QR codes needed - teams can select from dropdown
DEV_AUTO_LOGIN_TEAM = "Herceptin"  # Auto-selects this team (or None to disable)
```

### Development Workflow

**With DEV_MODE = True:**
- ✅ **test_session**: Pre-populated with 29 teams and complete game data
- ✅ **morning_session**: Empty - you can register teams WITHOUT QR codes
- ✅ **afternoon_session**: Empty - you can register teams WITHOUT QR codes

**How to test in development:**
1. Start app: `python -m streamlit run app.py --server.port 8504`
2. Admin can switch sessions via **Admin Dashboard → Session Management**
3. Teams can register by selecting from dropdown (no QR code needed)
4. Each session keeps its own data separate

### Switching Sessions

**Important: Session switching is GLOBAL for all users!**

- Use **Admin Dashboard → Session Management** tab
- Select session from dropdown and click "Switch to Selected Session"
- **All users** (teams and admin) will immediately use the new session
- Current active session shown at top of admin dashboard
- All data is session-specific and persists in database

**How it works:**
- Session is stored in database with `is_active` flag
- When admin switches sessions, the `is_active` flag updates globally
- All users automatically use the active session on their next page load/interaction
- No need for users to refresh - they'll see the new session automatically

## Production Deployment

### Switch to Production Mode

Edit `config.py`:

```python
DEV_MODE = False               # Disable dev mode
DEV_BYPASS_QR = False         # Require QR codes (mandatory)
DEV_AUTO_LOGIN_TEAM = None    # No auto-login
DEV_GENERATE_TEST_DATA = False # No test data generation
```

**In production:**
- ❌ Teams CANNOT select from dropdown
- ✅ Teams MUST scan QR codes on tables
- ✅ Each QR code pre-fills the team name
- ✅ Morning and afternoon sessions are separate

### Prepare Sessions

```bash
# Sessions already exist (from development)
# Optionally clear morning/afternoon sessions if they have test data
# Use Admin Dashboard → Session Management → Clear Session Data
```

### Update QR Code URLs

Edit `generate_qr_codes.py`:

```python
base_url = "https://your-deployed-app-url.com"
```

Then regenerate QR codes:

```bash
python generate_qr_codes.py

## Streamlit Cloud
**Cost**: Free
**Deployment Time**: 5-10 minutes
**Technical Complexity**: Low

**Pros**:
- Zero cost for up to 30 teams
- Automatic HTTPS/SSL
- Direct GitHub integration
- Built-in analytics
- Global CDN
- Auto-scaling
- No server management

**Cons**:
- Resource limits (1GB memory)
- Public repository required (for free tier)
- Streamlit branding

**Best For**: Quick deployment, zero budget, Python-only teams

## Step-by-Step Deployment

### 1. Prepare Your Repository
```bash
# Ensure your repository has these files:
├── app_starter.py
├── database.py
├── requirements.txt
├── data/
│   ├── team_namen.txt
│   ├── kinder_vornamen.txt
│   └── eltern_vornamen.txt
└── README.md
```

### 2. Create Streamlit Cloud Account
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### 3. Deploy Application
1. Click "New app"
2. Select your repository
3. Choose main branch
4. Set main file path: `app_starter.py`
5. Click "Deploy!"

### 4. Configure Environment (if needed)
```toml
# .streamlit/config.toml (optional)
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### 5. Custom Domain (Optional)
1. Go to app settings
2. Click "Custom domain"
3. Add your domain (requires DNS configuration)

## Environment Variables
```bash
# For sensitive data (in Streamlit Cloud secrets)
ADMIN_PASSWORD = "your_secure_password"
SESSION_SECRET = "your_session_key"
```

## Alternative Quick Deployment Options

### Local Network Deployment
Perfect for testing or local events:

```bash
# Run locally and share on network
streamlit run app_starter.py --server.address 0.0.0.0 --server.port 8501
# Access via: http://[your-ip]:8501
```

### Docker Deployment
For more control:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app_starter.py", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t zukunftstag-app .
docker run -p 8501:8501 zukunftstag-app
```

## QR Code Generation

### After deployment, generate QR codes for teams:

```python
import qrcode
import pandas as pd

# Read team names
with open('data/team_namen.txt', 'r') as f:
    teams = [line.split(':')[0] for line in f.read().splitlines() if line]

# Your deployed app URL
base_url = "https://your-app-name.streamlit.app"

# Generate QR codes
for team in teams:
    url = f"{base_url}?team={team}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"qr_codes/{team}.png")
```