# OAuth Setup Guide for AttackSim

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
SECURITY_PASSWORD_SALT=your-security-password-salt-here
FLASK_ENV=development

# Database Configuration
DEV_DATABASE_URL=sqlite:///app.db
DATABASE_URL=your-production-database-url-here

# Email Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
ADMIN_EMAIL=admin@attacksim.local
SECURITY_EMAIL_SENDER=your-email@gmail.com

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/oauth/google/callback

# Redis Configuration (for rate limiting and Celery)
REDIS_URL=redis://localhost:6379

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.developers.google.com/

2. **Create a new project or select existing one**
   - Click "Select a project" → "New Project"
   - Name: "AttackSim" or your preferred name

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "AttackSim Web Client"

5. **Configure Authorized redirect URIs**
   - For development: `http://localhost:5000/oauth/google/callback`
   - For production: `https://yourdomain.com/oauth/google/callback`

6. **Get your credentials**
   - Copy the Client ID and Client Secret
   - Add them to your `.env` file

## Features

- ✅ Email/Password authentication with Flask-Security-Too
- ✅ Google OAuth sign-in
- ✅ Password reset functionality
- ✅ Account linking (link Google to existing email account)
- ✅ Secure password hashing
- ✅ Rate limiting on authentication
- ✅ Session management

## Installation

1. Install the new dependencies:
```bash
pip install -r requirements.txt
```

2. Create your `.env` file with the variables above

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
python run.py
```

## Authentication Options

Users can now:
1. **Register with email/password** - Traditional account creation
2. **Sign in with Google** - One-click OAuth authentication
3. **Link accounts** - Connect Google to existing email accounts
4. **Password reset** - Email-based password recovery

All authentication is handled by industry-standard libraries:
- **Flask-Security-Too**: Handles email/password authentication
- **Authlib**: Manages Google OAuth integration

## Security Features

- Passwords are hashed with bcrypt
- CSRF protection on all forms
- Rate limiting on login attempts
- Secure session management
- Industry-standard OAuth 2.0 implementation 