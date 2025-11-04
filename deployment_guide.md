# Deployment Guide: Zukunftstag Simulation App

## Overview
This guide compares deployment options for the Zukunftstag simulation application and provides step-by-step instructions for the recommended approach.

## Run Commands
**Run the app locally**: `streamlit run app.py`
**Generate QR Codes**: `python scripts/generate_qr_codes.py`
**Generate Test Data**: `python scripts/generate_test_data.py`
**Initialize Sessions**: `python scripts/initialize_sessions.py`

## Session Management

The app uses **three separate sessions** to organize workshop data:

1. **Morning Session** (`morning_session`) - For live morning workshop (09:00 - 11:30)
2. **Afternoon Session** (`afternoon_session`) - For live afternoon workshop (13:30 - 16:00)  
3. **Test Session** (`test_session`) - For development and testing (pre-populated with 29 teams)

## Production Deployment

### Switch to Production Mode

Edit `config.py`:

```python
DEV_MODE = False               # Disable dev mode
DEV_BYPASS_QR = False         # Require QR codes (mandatory)
DEV_AUTO_LOGIN_TEAM = None    # No auto-login
DEV_GENERATE_TEST_DATA = False # No test data generation
```

**Set Admin Password** in Streamlit Cloud Secrets (not in code):
- Go to app settings → Secrets
- Add: `ADMIN_PASSWORD = "your_secure_password"`
- Never commit passwords to Git!

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

Edit `scripts/generate_qr_codes.py`:

```python
base_url = "https://your-deployed-app-url.com"
```

Then regenerate QR codes:

```bash
python scripts/generate_qr_codes.py
```


## Step-by-Step Deployment

### 1. Prepare Your Repository
```bash
# Ensure your repository has these files:
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── modules/
│   ├── user/
│   │   ├── tech_check.py
│   │   ├── game1_heights.py
│   │   ├── game2_perimeter.py
│   │   ├── game3_memory.py
│   │   ├── game4_clinical.py
│   │   └── feedback.py
│   └── admin/
│       ├── admin_dashboard.py
│       ├── admin_game1.py
│       ├── admin_game2.py
│       ├── admin_game3.py
│       ├── admin_game4.py
│       └── admin_helpers.py
├── utils/
│   ├── helpers.py
│   └── visualizations.py
├── data/
│   ├── team_namen.txt
│   ├── kinder_vornamen.txt
│   └── eltern_vornamen.txt
└── scripts/
    ├── generate_qr_codes.py
    ├── generate_test_data.py
    └── initialize_sessions.py
```

### 2. Create Streamlit Cloud Account
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### 3. Deploy Application
1. Click "New app"
2. Select your repository
3. Choose main branch (or `Streamlit_simul` branch)
4. Set main file path: `app.py`
5. **Advanced settings** → Add to Secrets:
   ```toml
   ADMIN_PASSWORD = "your_secure_password"
   ```
6. Click "Deploy!"

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

## Database Considerations

### Current Setup: SQLite (Local File)
- **Database**: `zukunftstag.db` (SQLite file stored locally)
- **Perfect for**: Single-day workshops, testing, development
- **Limitation on Streamlit Cloud**: Data is lost when app redeploys

### For Streamlit Cloud Deployment:
**Option 1: SQLite (Current - Recommended for workshops)**
- ✅ No additional setup needed
- ✅ Data persists during workshop day
- ⚠️ Data lost on app restart/redeploy
- **Best for**: Single-day events where you export data at end of day

**Option 2: PostgreSQL (For production)**
- Use external database like Supabase, Neon, or ElephantSQL
- Data persists across redeploys
- Requires database connection string in secrets

### Streamlit Cloud Secrets Configuration

Click "Advanced settings" → "Secrets" during deployment, or go to app settings after deployment:

```toml
# .streamlit/secrets.toml
ADMIN_PASSWORD = "your_secure_password_here"

# Optional: For PostgreSQL (if switching from SQLite)
# DB_CONNECTION_STRING = "postgresql://user:password@host:port/database"
```

**How it works:**
- The app reads `ADMIN_PASSWORD` from environment variable
- In production: Uses the value from Streamlit secrets

## Alternative Quick Deployment Options

### Local Network Deployment
Perfect for testing or local events:

```bash
# Run locally and share on network
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
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