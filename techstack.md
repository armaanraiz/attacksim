# AttackSim Tech Stack

## Backend Framework
- **Python3.11rimary programming language
- **Flask** - Lightweight web framework for API and web routes
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Mail** - Email sending capabilities

## Database
- **SQLite** - Development database (simple setup)
- **PostgreSQL** - Production database (optional upgrade)
- **Alembic** - Database migrations

## Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript (ES6+)** - Client-side interactivity
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Analytics dashboard charts
- **SweetAlert2** - Beautiful pop-ups and alerts

## Email & Communication
- **SMTP** - Email delivery for phishing simulations
- **Jinja2** - Email template rendering
- **Celery** - Background task queue for scheduled emails
- **Redis** - Message broker for Celery

## Security & Authentication
- **bcrypt** - Password hashing
- **PyJWT** - JWT tokens for API authentication
- **cryptography** - Additional encryption if needed
- **Flask-Limiter** - Rate limiting

## Development Tools
- **pip** - Package management
- **virtualenv/venv** - Virtual environment
- **pytest** - Unit testing
- **black** - Code formatting
- **flake8 - Linting
- **pre-commit** - Git hooks

## Deployment & DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container setup
- **Gunicorn** - WSGI server for production
- **Nginx** - Reverse proxy (optional)
- **Heroku/Vercel** - Cloud deployment platforms

## Monitoring & Logging
- **logging** - Python standard library logging
- **Flask-Logging** - Web request logging
- **Sentry** - Error tracking (optional)

## File Structure
```
attacksim/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── scenario.py
│   │   └── interaction.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   └── simulations.py
│   ├── templates/
│   │   ├── admin/
│   │   ├── simulations/
│   │   └── base.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/
│       ├── __init__.py
│       ├── email_sender.py
│       └── analytics.py
├── migrations/
├── tests/
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Key Dependencies (requirements.txt)
```
Flask==2.3.3Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
Flask-Mail==00.9.1
Flask-Limiter==3.5.0SQLAlchemy==2.0.21
Werkzeug==2.37ja2==3.10.2Forms==3.00.1
email-validator==2.00
bcrypt==401yJWT==2.8elery==5.3.1redis==5.0.1
gunicorn==21.2ytest==7.4.2lack==23.9.1lake8==6.1.0
```

## Development Setup Commands
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate
flask db upgrade

# Run development server
flask run

# Run tests
pytest

# Format code
black app/
```

## Production Considerations
- Use environment variables for sensitive data
- Set up proper logging and monitoring
- Implement rate limiting and security headers
- Use HTTPS in production
- Set up automated backups for database
- Consider using a CDN for static assets

## Security Features
- CSRF protection on all forms
- Rate limiting on authentication endpoints
- Secure password hashing with bcrypt
- JWT token expiration
- Input validation and sanitization
- Audit logging for admin actions
- Consent tracking for ethical compliance 