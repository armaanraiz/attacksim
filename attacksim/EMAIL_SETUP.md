# Email Configuration Setup

## Gmail Configuration for AttackSim

The application is now configured to use `it.help.service.alerts@gmail.com` as the default email sender.

### Required Environment Variables

To use Gmail for sending emails, you need to set the following environment variable:

```bash
export MAIL_PASSWORD="your-app-password-here"
```

### Setting up Gmail App Password

1. **Enable 2-Factor Authentication** on the Gmail account `it.help.service.alerts@gmail.com`
2. **Generate an App Password**:
   - Go to Google Account settings
   - Navigate to Security > 2-Step Verification > App passwords
   - Generate a new app password for "AttackSim"
   - Use this 16-character password as your `MAIL_PASSWORD`

### Alternative Configuration

If you want to use different email settings, you can override them with environment variables:

```bash
export MAIL_SERVER="your-smtp-server.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="True"
export MAIL_USERNAME="your-email@domain.com"
export MAIL_PASSWORD="your-password"
export ADMIN_EMAIL="your-admin@domain.com"
export SECURITY_EMAIL_SENDER="your-sender@domain.com"
```

### Testing Email Configuration

After setting up the email configuration, you can test it by:

1. Creating a group with external email addresses
2. Creating an email campaign
3. Sending the campaign to test recipients

### Security Notes

- Never commit email passwords to version control
- Use App Passwords instead of regular passwords for Gmail
- Consider using environment-specific configuration files
- Monitor email sending limits and quotas 