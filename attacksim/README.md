# AttackSim - Security Awareness Training Platform

AttackSim is an educational platform designed to simulate real-world cyber attacks in a safe, controlled environment. It helps users learn to identify and respond to security threats through hands-on experience with phishing emails, fake login pages, and suspicious links.

## 🎯 Features

- **Phishing Email Simulations**: Realistic phishing emails with customizable templates
- **Fake Login Pages**: Convincing fake login pages for popular services
- **Suspicious Link Detection**: Practice identifying malicious URLs
- **Educational Content**: Learning materials and awareness content after each simulation
- **Admin Dashboard**: Complete management interface for scenarios and users
- **Analytics & Reporting**: Detailed statistics on user performance and detection rates
- **Consent Management**: Ethical safeguards with opt-in/opt-out mechanisms
- **User Progress Tracking**: Individual performance metrics and improvement tracking

## 🛡️ Ethical Use Notice

**Important**: This platform is designed for educational purposes only. All simulations are conducted in a controlled environment with proper consent mechanisms. Users can opt out at any time, and no real data is collected or misused.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd attacksim
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python run.py init-db
   ```

5. **Create sample data (optional)**
   ```bash
   python run.py create-sample-data
   ```

6. **Create an admin user**
   ```bash
   python run.py create-admin
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

### Default Credentials (if using sample data)

- **Admin**: username: `admin`, password: `admin123`
- **Test User 1**: username: `testuser1`, password: `password123`
- **Test User 2**: username: `testuser2`, password: `password123`

## 📁 Project Structure

```
attacksim/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── scenario.py         # Scenario model
│   │   └── interaction.py      # Interaction tracking
│   ├── routes/                  # Route handlers
│   │   ├── main.py             # Main routes
│   │   ├── auth.py             # Authentication
│   │   ├── admin.py            # Admin panel
│   │   └── simulations.py      # Simulation routes
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS, images
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root for production settings:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/attacksim
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379
```

### Database Configuration

- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## 🎭 Simulation Types

### 1. Phishing Email Simulations
- Customizable email templates
- Various difficulty levels
- Realistic sender spoofing
- Educational pop-ups after interaction

### 2. Fake Login Pages
- Templates for popular services (Facebook, Gmail, etc.)
- URL spoofing simulation
- Credential capture tracking
- Security awareness education

### 3. Suspicious Link Detection
- Malicious URL patterns
- Social engineering tactics
- Click tracking and analysis
- Safe link verification training

## 👥 User Roles

### Regular Users
- Participate in simulations
- View personal statistics
- Access educational content
- Manage consent preferences

### Administrators
- Create and manage scenarios
- View system-wide analytics
- Manage user accounts
- Monitor interaction logs
- Schedule simulation campaigns

## 📊 Analytics & Reporting

- **Detection Rates**: Success/failure statistics
- **Response Times**: How quickly users identify threats
- **User Progress**: Individual improvement tracking
- **Scenario Performance**: Which simulations are most effective
- **Educational Engagement**: Time spent on learning content

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python run.py
```

### Database Commands

```bash
# Initialize database
python run.py init-db

# Create admin user
python run.py create-admin

# Create sample data
python run.py create-sample-data
```

### Code Formatting

```bash
# Format code with black
black app/

# Lint with flake8
flake8 app/
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t attacksim .

# Run container
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key attacksim
```

### Production Considerations

1. **Security**:
   - Use strong SECRET_KEY
   - Enable HTTPS
   - Set up proper firewall rules
   - Regular security updates

2. **Database**:
   - Use PostgreSQL for production
   - Set up regular backups
   - Configure connection pooling

3. **Email**:
   - Configure SMTP settings
   - Use dedicated email service
   - Set up proper SPF/DKIM records

4. **Monitoring**:
   - Set up logging
   - Monitor application performance
   - Track user engagement

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is for educational purposes only. Please ensure all use complies with local laws and organizational policies regarding security testing and user consent.

## ⚠️ Disclaimer

AttackSim is designed for educational and awareness training purposes only. Users must:

- Obtain proper authorization before deployment
- Ensure all participants provide informed consent
- Use only in controlled, safe environments
- Comply with all applicable laws and regulations
- Respect user privacy and data protection rights

The creators are not responsible for misuse of this software.

## 📞 Support

For questions, issues, or contributions:

1. Check the existing issues in the repository
2. Create a new issue with detailed information
3. Follow the contribution guidelines

---

**Remember**: The goal is education and awareness, not exploitation. Use responsibly! 🛡️ 