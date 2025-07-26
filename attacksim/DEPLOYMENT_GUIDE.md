# Phishing Simulation Platform - Deployment Guide

This guide explains how to deploy your phishing simulation platform with hosted clones and a scalable backend infrastructure.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Email Client  │ -> │  Phishing Clone  │ -> │ Flask Backend   │
│                 │    │   (Vercel)       │    │  (Railway/      │
│                 │    │                  │    │   Render)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │                        │
                                 │                        │
                                 v                        v
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Educational     │    │  PostgreSQL     │
                       │ Message         │    │  Database       │
                       │                 │    │  (Supabase)     │
                       └─────────────────┘    └─────────────────┘
```

## Phase 1: Prepare Your Backend for Production

### 1.1 Environment Configuration

Create a production configuration file:

```bash
# Create .env file for production
touch .env
```

Add the following environment variables:

```env
# Production Environment
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-min-32-chars

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# CORS Configuration (Update with your actual domains)
CORS_ORIGINS=https://discord-clone.vercel.app,https://facebook-clone.vercel.app

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis (for rate limiting and caching)
REDIS_URL=redis://localhost:6379

# Security
SECURITY_PASSWORD_SALT=your-security-salt-here
```

### 1.2 Database Setup

#### Option A: Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Get your database URL from Settings > Database
4. Update `DATABASE_URL` in your `.env` file

#### Option B: Railway PostgreSQL
1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Add PostgreSQL service
4. Copy the database URL

### 1.3 Update CORS Configuration

Update your Flask app to use environment-specific CORS origins:

```python
# In app/__init__.py
cors.init_app(app, resources={
    r"/api/*": {
        "origins": os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(','),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Phase 2: Deploy Backend to Cloud

### 2.1 Railway Deployment (Recommended)

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login and Deploy:**
```bash
railway login
railway init
railway add postgresql
railway deploy
```

3. **Set Environment Variables:**
```bash
railway variables:set FLASK_ENV=production
railway variables:set SECRET_KEY=your-secret-key
# ... add all other variables
```

### 2.2 Alternative: Render Deployment

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: attacksim-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: attacksim-db
          property: connectionString

databases:
  - name: attacksim-db
    databaseName: attacksim
    user: attacksim
```

2. Push to GitHub and connect to Render

## Phase 3: Deploy Phishing Clones to Vercel

### 3.1 Prepare Discord Clone for Vercel

1. **Create `vercel.json` in your discord-clone directory:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

2. **Update JavaScript configuration:**

In `js/script.js`, update the API base URL:

```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? 'https://your-backend-domain.railway.app'  // Replace with your actual backend URL
    : 'http://localhost:5001';
```

3. **Deploy to Vercel:**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd discord-clone
vercel --prod
```

### 3.2 Create Multiple Clone Variants

For different platforms, create separate directories:

```
clones/
├── discord-clone/
├── facebook-clone/
├── gmail-clone/
└── linkedin-clone/
```

Deploy each one separately to Vercel with different domains.

## Phase 4: Update Email Campaign Links

### 4.1 Modify Email Templates

Update your email campaign templates to point to the hosted clones:

```python
# In your email template
phishing_url = f"https://discord-clone.vercel.app/?campaign_id={campaign.id}&scenario_id={scenario.id}&t={recipient.unique_token}"
```

### 4.2 Update Campaign Creation

Modify the campaign creation to include clone URLs:

```python
# Add to EmailCampaign model
clone_urls = {
    'discord': 'https://discord-clone.vercel.app',
    'facebook': 'https://facebook-clone.vercel.app',
    'gmail': 'https://gmail-clone.vercel.app'
}
```

## Phase 5: Enhanced Analytics Dashboard

### 5.1 Real-time Dashboard Updates

Add WebSocket support for real-time updates:

```bash
pip install flask-socketio
```

### 5.2 Export Analytics Data

Add CSV export functionality:

```python
@bp.route('/analytics/export')
@login_required
@admin_required
def export_analytics():
    # Generate CSV with campaign data
    pass
```

## Phase 6: Monitoring and Security

### 6.1 Logging Setup

Configure production logging:

```python
# In production config
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/attacksim.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### 6.2 Security Headers

Add security headers:

```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Phase 7: Testing the Complete Setup

### 7.1 End-to-End Test

1. Create a test email campaign
2. Send test emails with clone links
3. Click the links and submit test credentials
4. Verify data appears in admin dashboard
5. Check educational messages display correctly

### 7.2 Performance Testing

```bash
# Install tools
pip install locust

# Create test script
# locustfile.py
from locust import HttpUser, task, between

class SimulationUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def submit_credentials(self):
        self.client.post("/api/track-submission", json={
            "email": "test@example.com",
            "password": "testpass",
            "clone_type": "discord"
        })
```

## Phase 8: Scaling Considerations

### 8.1 Database Optimization

Add database indexes:

```sql
CREATE INDEX idx_interactions_scenario_id ON interactions(scenario_id);
CREATE INDEX idx_interactions_created_at ON interactions(created_at);
CREATE INDEX idx_email_recipients_token ON email_recipients(unique_token);
```

### 8.2 Caching

Implement Redis caching:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def get_campaign_stats(campaign_id):
    # Cached analytics data
    pass
```

## Phase 9: Backup and Recovery

### 9.1 Database Backups

```bash
# Automated backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### 9.2 Application Monitoring

Set up monitoring with:
- Sentry for error tracking
- New Relic or DataDog for performance
- Uptime monitoring for availability

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Check your CORS_ORIGINS environment variable
   - Verify the clone domains are correct

2. **Database Connection Issues:**
   - Verify DATABASE_URL format
   - Check firewall settings

3. **Email Delivery Issues:**
   - Verify SMTP credentials
   - Check spam folder policies

4. **Clone Not Loading:**
   - Check Vercel deployment logs
   - Verify DNS settings

### Debug Commands

```bash
# Check backend logs
railway logs

# Test API endpoints
curl -X POST https://your-backend.railway.app/api/track-view \
  -H "Content-Type: application/json" \
  -d '{"clone_type": "test"}'

# Database connection test
python -c "from app import create_app; app = create_app(); print('DB connected')"
```

## Cost Estimates

### Monthly Costs (Approximate)

- **Vercel:** Free tier (sufficient for multiple clones)
- **Railway:** $5-10/month (depending on usage)
- **Supabase:** Free tier up to 500MB, then $25/month
- **Domain names:** $10-15/year each

**Total estimated cost:** $10-40/month depending on scale

## Security Best Practices

1. **Never log real passwords** - Always hash immediately
2. **Use HTTPS everywhere** - Ensure all clones use SSL
3. **Regular security audits** - Monitor for suspicious activity
4. **User consent management** - Clear opt-out mechanisms
5. **Data retention policies** - Auto-delete old interaction data

## Next Steps

After deployment:

1. Create user documentation
2. Set up regular security training
3. Monitor campaign effectiveness
4. Expand clone library
5. Implement advanced analytics

This completes your production-ready phishing simulation platform with hosted clones and comprehensive tracking! 