# AttackSim Clone Management Deployment Guide

## 🚀 You've Successfully Implemented Clone Management!

Your AttackSim platform now has a complete clone management system with email tracking. Here's what's been added:

### ✅ Features Implemented

1. **Clone Management System**
   - Full CRUD operations for managing phishing clone URLs
   - Support for multiple clone types (Discord, Facebook, Gmail, etc.)
   - Status management (Active/Inactive/Maintenance)
   - Usage tracking and analytics

2. **Enhanced Email Campaigns**
   - Clone selection in campaign creation
   - Dynamic clone button generation
   - Proper tracking URL integration

3. **Advanced Email Tracking**
   - Email open tracking (invisible pixel)
   - Click tracking with redirection to clones
   - User behavior analytics

## 🛠️ Deployment Steps for Your Live Platform

### Step 1: Deploy the Updated Code

Since your platform is already deployed, you need to:

1. **Push your updated code** to your repository
2. **Trigger a redeploy** on your hosting platform
3. **Run database migrations** to create the new clone table

### Step 2: Initialize Clone Management (One-time setup)

On your deployed platform, you need to create the clone table and add your Discord clone. You can do this through your platform's console or by creating a simple migration script.

**Option A: Through your deployed admin panel**
1. Access your deployed platform: `https://attacksim-backend.onrender.com/`
2. Log in as admin
3. The clone table should be created automatically

**Option B: Create a simple migration endpoint (Recommended)**

Add this temporary route to your `app/routes/admin.py`:

```python
@bp.route('/setup/init-clones')
@login_required
@admin_required
def init_clones_endpoint():
    """One-time setup endpoint to initialize clones"""
    try:
        # Create clone table
        db.create_all()
        
        # Check if Discord clone already exists
        from app.models.clone import CloneType, CloneStatus
        existing_discord = Clone.query.filter_by(
            clone_type=CloneType.DISCORD,
            base_url='https://discord-clone-tau-smoky.vercel.app'
        ).first()
        
        if existing_discord:
            flash('Discord clone already exists!', 'info')
        else:
            # Create Discord clone
            discord_clone = Clone(
                name="Discord Security Team",
                description="Discord clone deployed on Vercel for phishing simulation",
                clone_type=CloneType.DISCORD,
                status=CloneStatus.ACTIVE,
                base_url="https://discord-clone-tau-smoky.vercel.app",
                landing_path="/",
                icon="📱",
                button_color="blue",
                created_by=current_user.id
            )
            
            db.session.add(discord_clone)
            db.session.commit()
            flash('Discord clone added successfully!', 'success')
        
        return redirect(url_for('admin.clones'))
        
    except Exception as e:
        flash(f'Error initializing clones: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
```

Then visit: `https://attacksim-backend.onrender.com/admin/setup/init-clones`

### Step 3: Set Up Your Clone Management

1. **Access Clone Management**
   - Go to `Admin → Clone Management` in your deployed platform
   - You should see your Discord clone already added

2. **Add More Clones (Optional)**
   - Click "Add Clone" to add more phishing clones
   - Configure each clone with its deployed URL

3. **Test Clone Functionality**
   - Use the "Test Clone" button to verify each clone works
   - Ensure tracking parameters are properly passed

### Step 4: Create Email Campaigns with Clones

1. **Create New Campaign**
   - Go to `Admin → Email Campaigns → Create Campaign`
   - Select your target group
   - Choose a clone from the dropdown (optional)
   - Use the clone quick-add buttons to insert tracking links

2. **Email Body with Tracking**
   - When you click a clone button, it adds: `<a href="{{tracking_url}}">Verify Now</a>`
   - The `{{tracking_url}}` will be automatically replaced with proper tracking URLs

3. **Send and Track**
   - Send your campaign
   - Track opens and clicks in the campaign analytics
   - Users clicking links will be redirected to your chosen clone

## 🎯 Testing Your Setup

### Test Email Tracking Flow

1. **Create a test campaign**:
   - Target: Small test group
   - Clone: Your Discord clone
   - Body: Include `{{tracking_url}}` links

2. **Send test email**:
   - The system will generate unique tracking tokens
   - Email opens will be tracked automatically
   - Link clicks will redirect to: `https://discord-clone-tau-smoky.vercel.app/?campaign_id=X&scenario_id=Y&t=token`

3. **Verify tracking**:
   - Check campaign analytics for open/click rates
   - Monitor clone usage statistics

### Expected Tracking Flow

```
User receives email
    ↓
User opens email → Tracking pixel fires → Open tracked
    ↓
User clicks link → `/track/click/token` → Click tracked
    ↓
Redirect to clone → `https://discord-clone-tau-smoky.vercel.app/?t=token`
    ↓
Clone loads with tracking parameters
```

## 🚀 Next Steps

1. **Deploy More Clones**
   - Deploy Facebook, Gmail, PayPal clones to Vercel
   - Add them to your clone management system

2. **Enhance Your Discord Clone**
   - Ensure it properly handles tracking parameters
   - Add tracking scripts to capture user interactions

3. **Monitor and Analyze**
   - Use the campaign analytics to monitor success rates
   - Identify which clones are most effective

## 🔧 Troubleshooting

**If clones don't redirect properly:**
- Check that the clone URLs are accessible
- Verify tracking parameters are being passed correctly
- Check server logs for redirect errors

**If tracking doesn't work:**
- Ensure your email templates use `{{tracking_url}}`
- Check that the tracking domain is properly configured
- Verify database permissions for creating tracking records

## 🎉 Success!

Your AttackSim platform now has:
- ✅ Complete clone management system
- ✅ Advanced email tracking with redirects
- ✅ Real-time analytics and reporting
- ✅ Integration with your deployed Discord clone
- ✅ Scalable system for adding more clones

You can now create sophisticated phishing simulations that track user behavior and redirect to your actual deployed clones! 