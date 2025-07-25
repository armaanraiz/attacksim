# Email Phishing Campaign System

This document describes the new email phishing campaign system that allows administrators to create groups, draft phishing emails, and send them to users with detailed analytics tracking.

## 🚀 Features

### Group Management
- **Create Groups**: Organize users into groups (e.g., "Students of UNSW")
- **Mixed Membership**: Groups can contain both registered users and external email addresses
- **Bulk Email Management**: Add multiple emails via comma-separated lists
- **Group Analytics**: Track campaign performance per group

### Email Campaign Creation
- **Campaign Builder**: Intuitive interface for creating phishing campaigns
- **Email Templates**: Pre-built phishing scenarios with customizable content
- **Email Preview**: Preview emails before sending
- **One-Click Sending**: Send campaigns to entire groups instantly

### Advanced Email Tracking
- **Open Tracking**: Track when emails are opened (invisible pixel)
- **Click Tracking**: Monitor link clicks with detailed analytics
- **User Behavior**: Track individual user responses and interactions
- **Report Tracking**: Monitor users who report emails as phishing (good behavior!)

### Comprehensive Analytics
- **Campaign Metrics**: Open rates, click rates, delivery rates
- **Individual Tracking**: Per-recipient interaction details
- **Educational Insights**: Identify users who need additional training
- **Progress Tracking**: Monitor improvement over time

## 📊 How It Works

### 1. Create a Group
```
Admin Panel → Groups → Create Group
- Enter group name (e.g., "Students of UNSW")
- Add registered users (with consent)
- Add external email addresses
- Save group
```

### 2. Create Email Campaign
```
Admin Panel → Email Campaigns → Create Campaign
- Select target group
- Choose phishing scenario template
- Customize email content
- Preview email
- Create campaign
```

### 3. Send Campaign
```
Campaign Details → Send Now
- Emails sent with tracking enabled
- Recipients receive phishing simulation
- All interactions tracked automatically
```

### 4. Monitor Results
```
Campaign Analytics Dashboard:
- View open/click/report rates
- Individual recipient details
- Educational opportunities identified
- Export data for reporting
```

## 🔧 Technical Implementation

### Database Models

#### Group Model
- Stores group information and metadata
- Links to both registered users and external emails
- Tracks campaign associations

#### EmailCampaign Model
- Campaign configuration and content
- Links to scenarios and target groups
- Comprehensive analytics tracking

#### EmailRecipient Model
- Individual recipient tracking
- Unique tokens for email tracking
- Detailed interaction timestamps

### Email Tracking System

#### Open Tracking
- Invisible 1x1 pixel image in emails
- Tracks when email is opened
- Records IP address and user agent

#### Click Tracking
- All email links replaced with tracking URLs
- Redirects to phishing simulation
- Records click events and user behavior

#### Integration with Existing System
- Seamlessly integrates with current simulation system
- Maintains all existing educational features
- Preserves user consent and privacy controls

## 📈 Analytics Dashboard

### Campaign-Level Metrics
- **Recipients**: Total number of people targeted
- **Delivery Rate**: Successfully delivered emails
- **Open Rate**: Percentage who opened the email
- **Click Rate**: Percentage who clicked phishing links
- **Report Rate**: Percentage who reported as phishing (good!)

### Individual Recipient Tracking
- Email delivery status
- Open timestamps and frequency
- Click behavior and patterns
- Educational content engagement
- Response to simulation

### Educational Insights
- Users who need additional training
- Most effective phishing techniques
- Improvement trends over time
- Department/group performance comparison

## 🛡️ Security & Ethics

### Privacy Protection
- All tracking respects user consent
- No personal data stored unnecessarily
- Secure token-based tracking system
- Option to opt-out of campaigns

### Educational Focus
- Clear educational messaging after interaction
- Immediate feedback on user actions
- Links to security awareness resources
- Positive reinforcement for good behavior

### Administrative Controls
- Admin-only access to campaign creation
- Audit trail of all campaign activities
- Secure email template management
- Rate limiting and abuse prevention

## 🚀 Getting Started

### Prerequisites
1. Existing AttackSim installation
2. Email server configuration (SMTP)
3. Admin user account

### Setup Steps

1. **Initialize New Database Tables**
   ```bash
   python init_db.py
   ```

2. **Configure Email Settings**
   ```bash
   # Set environment variables
   export MAIL_SERVER=smtp.gmail.com
   export MAIL_PORT=587
   export MAIL_USERNAME=your-email@gmail.com
   export MAIL_PASSWORD=your-app-password
   ```

3. **Create First Group**
   - Login as admin
   - Go to Admin Panel → Groups
   - Click "Create Group"
   - Add group name and member emails
   - Save group

4. **Create Email Campaign**
   - Go to Admin Panel → Email Campaigns
   - Click "Create Campaign"
   - Select group and scenario
   - Customize email content
   - Send campaign

### Example Group Creation

**Group Name**: Students of UNSW
**Description**: Computer Science students for security awareness training

**Registered Users**: 
- Select from consented users in the system

**External Emails**:
```
student1@unsw.edu.au,
student2@unsw.edu.au,
student3@unsw.edu.au
```

### Example Email Campaign

**Campaign Name**: UNSW Students Phishing Test Q1
**Target Group**: Students of UNSW
**Scenario**: PayPal Account Suspension
**Email Subject**: 🚨 URGENT: Your PayPal Account Has Been Limited

The system will automatically:
- Send personalized emails to all group members
- Track opens, clicks, and user responses
- Redirect clicks to educational simulation
- Provide detailed analytics dashboard

## 📋 Best Practices

### Group Management
- Use descriptive group names
- Keep groups reasonably sized (50-200 members)
- Regularly update group membership
- Remove inactive email addresses

### Campaign Creation
- Test campaigns with small groups first
- Use realistic but educational scenarios
- Provide clear educational content
- Schedule campaigns during appropriate times

### Analytics Review
- Review campaign results within 24-48 hours
- Identify users needing additional training
- Share positive results with leadership
- Use data to improve future campaigns

### Educational Follow-up
- Send educational materials to all participants
- Provide additional training for high-risk users
- Celebrate users who correctly identified phishing
- Create ongoing awareness programs

## 🔮 Future Enhancements

### Planned Features
- **Scheduled Campaigns**: Schedule campaigns for future sending
- **A/B Testing**: Test different email variations
- **Advanced Templates**: More sophisticated phishing scenarios
- **Automated Follow-up**: Automatic educational content delivery
- **Integration APIs**: Connect with existing security tools
- **Mobile Optimization**: Better mobile email experience

### Reporting Enhancements
- **Executive Dashboards**: High-level summary reports
- **Trend Analysis**: Long-term performance tracking
- **Benchmark Comparisons**: Industry standard comparisons
- **Custom Reports**: Tailored reporting for different audiences

## 📞 Support

For questions about the email campaign system:

1. Check existing GitHub issues
2. Review this documentation
3. Contact the development team
4. Submit feature requests

---

**Remember**: The goal is education and awareness, not embarrassment. Use this system responsibly to improve your organization's security posture! 🛡️ 