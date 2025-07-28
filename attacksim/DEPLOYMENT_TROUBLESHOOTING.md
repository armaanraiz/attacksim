# 🚨 Deployment Troubleshooting Guide

## Common Error Patterns & Solutions

### 1. **Enum/String Mismatch Errors**
**Error**: `can't adapt type 'CloneType'` or `'str' object has no attribute 'value'`

**Root Cause**: PostgreSQL expects string values, but code is passing/accessing enum objects

**Prevention**:
- ✅ Always store enum values as **strings** in database columns
- ✅ Use string validation arrays instead of `[enum.value for enum in EnumClass]`
- ✅ Templates should use hardcoded options, not enum objects
- ✅ Routes should assign string values directly: `model.field = 'string'`

### 2. **Schema Mismatch Errors** 
**Error**: `column does not exist` or `InFailedSqlTransaction`

**Root Cause**: Database schema doesn't match model definitions

**Prevention**:
- ✅ Run database migrations after model changes
- ✅ Use `ALTER TABLE ADD COLUMN IF NOT EXISTS` for new columns
- ✅ Test schema changes locally before deploying

### 3. **Import Errors**
**Error**: `cannot import name 'X' from 'module'`

**Root Cause**: Importing non-existent classes/functions

**Prevention**:
- ✅ Keep `__init__.py` imports in sync with actual model files
- ✅ Use IDE/linter to catch import errors before deployment
- ✅ Test imports in shell context: `flask shell`

## 🔍 **How to Debug Deployment Errors**

### **1. Real-time Logs**
```bash
# View live deployment logs
heroku logs --tail --app your-app-name
# OR for Render:
# Check the deployment logs in Render dashboard
```

### **2. Test Locally First**
```bash
# Test database operations locally
flask shell
>>> from app.models import Clone
>>> clone = Clone.query.first()
>>> clone.clone_type  # Should be string, not enum
```

### **3. Database Schema Verification**
```python
# Add to run.py for debugging
def verify_schema():
    """Verify database schema matches models"""
    try:
        # Test each model's essential operations
        Clone.query.count()
        print("✅ Clone model: OK")
        
        PhishingCredential.query.count()  
        print("✅ PhishingCredential model: OK")
        
    except Exception as e:
        print(f"❌ Schema error: {e}")
        return False
    return True

# Call during initialization
if not verify_schema():
    print("⚠️  Database schema needs attention")
```

### **4. Staging Environment**
Set up a staging environment that mirrors production:
- Same database type (PostgreSQL)
- Same Python version
- Same dependencies
- Test deployments here first

## 🛡️ **Error Prevention Checklist**

### **Before Every Deployment:**
- [ ] Run `flask shell` and test new model operations
- [ ] Check all templates for enum references (`clone_types`, `clone_statuses`)
- [ ] Verify string/enum consistency in routes
- [ ] Test database operations with new schema locally
- [ ] Run linter: `flake8 app/` or `pylint app/`

### **Model Changes Checklist:**
- [ ] Update field types to strings if using PostgreSQL
- [ ] Remove enum imports if not needed
- [ ] Update validation logic to use string arrays
- [ ] Update templates to use hardcoded options
- [ ] Create migration script for existing data

### **Database Migration Template:**
```python
# Always use this pattern for schema changes
def add_missing_columns():
    """Add new columns safely"""
    try:
        db.engine.execute("""
            DO $$ BEGIN 
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='clones' AND column_name='new_column'
                ) THEN
                    ALTER TABLE clones ADD COLUMN new_column VARCHAR(50) DEFAULT 'default_value';
                END IF;
            END $$;
        """)
        print("✅ Database migration completed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
```

## 🚀 **Deployment Best Practices**

1. **Small, Incremental Changes**: Don't deploy massive changes at once
2. **Feature Flags**: Use environment variables to toggle new features
3. **Database Backups**: Always backup before schema changes
4. **Rollback Plan**: Know how to quickly revert problematic deployments
5. **Monitoring**: Set up error tracking (Sentry, Rollbar, etc.)

## 📱 **Quick Error Fixes**

### **"Column does not exist"**
```bash
# Run the migration script
python update_render_db.py
```

### **"Can't adapt type 'X'"**
```python
# Find and replace enum assignments with strings
# Bad: model.field = EnumClass.VALUE  
# Good: model.field = 'string_value'
```

### **"Import Error"**  
```python
# Check __init__.py files and remove non-existent imports
# Verify all imported classes exist in their modules
```

This guide should help you catch and prevent most deployment errors before they happen! 🛡️ 