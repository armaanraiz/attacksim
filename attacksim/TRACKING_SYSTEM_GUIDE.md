# 🎯 Universal Phishing Clone Tracking System

This document explains the complete tracking system implementation that automatically handles phishing campaign tracking across any clone.

## 🚀 What's Been Fixed & Implemented

### ✅ Core Issues Resolved

1. **Email campaigns now use actual clone URLs** instead of generic tracking URLs
2. **Discord clone properly connects** to the Render backend 
3. **Universal tracking system** works with any clone type
4. **Proper credential storage** with security hashing
5. **Campaign/clone linking** with detailed analytics
6. **Next.js integration** for Vercel frontend tracking

### ✅ New Components Created

- **Universal Tracking Library** (`universal-tracking.js`)
- **PhishingCredential Model** for secure credential storage
- **Enhanced Clone Model** with tracking counters
- **React Hook** (`use-phishing-tracker.ts`) for Next.js apps
- **Education Component** for post-submission learning
- **Enhanced API endpoints** with proper clone integration

## 📋 How the New System Works

### 1. Email Campaign → Clone URL Generation

When you create an email campaign and select a clone:

```python
# OLD: Generic tracking URLs
return f"{self.protocol}://{self.tracking_domain}/sim/phishing/{scenario_id}?t={token}"

# NEW: Clone-specific URLs with tracking
clone = Clone.query.get(campaign.clone_id)
return clone.get_full_url(campaign_id=campaign.id, scenario_id=scenario_id, token=token)
# Example: https://discord-clone.vercel.app/login?campaign_id=123&scenario_id=456&t=abc123
```

### 2. Universal Tracking Integration

Any clone can now use tracking by including the universal script:

```html
<!-- Include in any clone -->
<script src="https://attacksim.onrender.com/static/js/universal-tracking.js"></script>

<!-- Auto-detects tracking parameters and clone type -->
<!-- Automatically tracks page views, form submissions, and exits -->
```

### 3. Credential Storage Flow

```
User submits form → Clone sends to API → PhishingCredential created → Analytics updated
```

Data is stored securely with:
- Hashed passwords (SHA-256)
- Campaign/clone/scenario linking
- IP address and user agent tracking
- Timestamp and referrer information

## 🔧 How to Use the New System

### For Email Campaigns

1. **Create a Clone** in Admin → Clones
   - Set clone type (discord, facebook, etc.)
   - Enter the clone's Vercel URL
   - Mark as Active

2. **Create Email Campaign** in Admin → Email Campaigns
   - Select your target group
   - **Select the clone** you want to use
   - The system will automatically generate proper tracking URLs

3. **Send Campaign**
   - URLs will now point to your actual clone with tracking parameters
   - All interactions are automatically tracked

### For Existing Clones (Discord, etc.)

**Option A: Use Universal Tracking (Recommended)**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Your Clone</title>
</head>
<body>
    <!-- Your clone content -->
    <form id="loginForm">
        <input type="email" name="email" required>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>

    <!-- Include universal tracking -->
    <script src="https://attacksim.onrender.com/static/js/universal-tracking.js"></script>
    
    <!-- Optional: Manual configuration -->
    <script>
        PhishingTracker.configure({
            cloneType: 'discord',
            debug: true
        });
    </script>
</body>
</html>
```

**Option B: Manual Integration**
```javascript
// Manual form handling
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const response = await PhishingTracker.trackSubmission({
        email: document.querySelector('[name="email"]').value,
        password: document.querySelector('[name="password"]').value
    });
    
    if (response.educational_message) {
        PhishingTracker.showEducationalMessage(response.educational_message);
    }
});
```

### For Next.js Apps (Vercel)

```tsx
// components/PhishingDemo.tsx
import { usePhishingTracker } from '@/hooks/use-phishing-tracker';
import { PhishingEducation } from '@/components/ui/phishing-education';

export default function PhishingDemo() {
    const { trackSubmission } = usePhishingTracker({ 
        cloneType: 'discord',
        debug: true 
    });
    const [showEducation, setShowEducation] = useState(false);
    const [educationMessage, setEducationMessage] = useState('');

    const handleSubmit = async (formData: FormData) => {
        const result = await trackSubmission({
            email: formData.get('email') as string,
            password: formData.get('password') as string
        });
        
        if (result.success) {
            setEducationMessage(result.educational_message || 'This was a simulation!');
            setShowEducation(true);
        }
    };

    return (
        <>
            <form action={handleSubmit}>
                <input name="email" type="email" required />
                <input name="password" type="password" required />
                <button type="submit">Sign In</button>
            </form>
            
            <PhishingEducation 
                isOpen={showEducation}
                onClose={() => setShowEducation(false)}
                message={educationMessage}
                cloneType="discord"
            />
        </>
    );
}
```

## 📊 Analytics & Tracking Data

### What Gets Tracked

1. **Page Views**: When users visit clone URLs
2. **Form Submissions**: When users enter credentials
3. **Time on Page**: How long users spend before submitting/leaving
4. **Exit Behavior**: Users who leave without submitting (good security behavior!)

### Where to View Analytics

- **Campaign Details**: See per-campaign metrics
- **Clone Management**: View clone-specific statistics
- **Credential Collection**: Admin can view collected data (hashed passwords)

### Clone Statistics Include

```json
{
    "total_visits": 150,
    "total_submissions": 45,
    "submission_rate": 30.0,
    "recent_credentials": 12,
    "times_used_in_campaigns": 8,
    "last_used": "2025-01-15T10:30:00Z"
}
```

## 🔐 Security Features

### Password Protection
- All passwords are hashed using SHA-256
- Raw passwords are never stored
- Credential records include hash only

### Data Isolation
- Each campaign/clone tracks separately
- User consent is respected
- IP addresses are logged for audit trails

### Educational Integration
- Automatic educational messages post-submission
- Clone-specific security tips
- Links to cybersecurity resources

## 🧪 Testing the System

Run the integration test:

```bash
cd Project/attacksim
python test_tracking_integration.py
```

This tests:
- Clone creation and URL generation
- Campaign/clone linking
- Credential storage and hashing
- Data relationships and analytics
- Cleanup procedures

## 🚀 Next Steps

### For New Clones
1. Create clone in admin panel
2. Include universal tracking script
3. Deploy to your preferred platform (Vercel, Netlify, etc.)
4. Test with a sample campaign

### For Enhanced Features
- Add more clone types in `CloneType` enum
- Customize educational messages per scenario
- Implement advanced analytics dashboards
- Add real-time notifications for submissions

## 📁 Key Files Modified/Created

### Backend (Flask/Render)
- `app/models/credential.py` - New credential storage model
- `app/models/clone.py` - Enhanced with tracking counters
- `app/utils/email_sender.py` - Fixed to use clone URLs
- `app/routes/api.py` - Enhanced tracking endpoints
- `universal-tracking.js` - Universal tracking library

### Frontend (Next.js/Vercel)
- `hooks/use-phishing-tracker.ts` - React hook for tracking
- `components/ui/phishing-education.tsx` - Educational component

### Static Clones
- `discord-clone/js/script.js` - Updated with proper backend URL
- `app/static/js/universal-tracking.js` - Served universal library

## 🎯 Summary

The new tracking system provides:

✅ **Unified tracking** across all clone types  
✅ **Proper URL generation** using actual clone domains  
✅ **Secure credential storage** with hashing  
✅ **Comprehensive analytics** at campaign and clone levels  
✅ **Educational integration** for security awareness  
✅ **Easy deployment** for new clones  
✅ **React/Next.js support** for modern frontend frameworks  

Your phishing simulation platform now has enterprise-grade tracking capabilities that work seamlessly across any clone type! 🎉 