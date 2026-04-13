# EasyPaisa Real Merchant Account Setup Guide

## Step 1: EasyPaisa Merchant Account Registration

### Online Registration:
1. **Visit:** https://www.easypaisa.com.pk/merchant
2. **Click:** "Register Now" or "Sign Up"
3. **Fill the form:**
   - Business Name (your company name)
   - CNIC Number (13 digits without dashes)
   - Mobile Number (registered EasyPaisa account)
   - Email Address
   - Business Type (Individual/Company)
   - Business Description

### Required Documents:
- **CNIC Copy** (front & back)
- **Business Registration** (if applicable)
- **Bank Account Details**
- **EasyPaisa Account** (must be active and verified)

### Account Activation with OTP:
After registration, you'll see the **Merchant Activation Screen**:

```
┌─────────────────────────────────────────┐
│  Merchant Account Activation            │
├─────────────────────────────────────────┤
│                                         │
│  SMS VERIFICATION CODE:                 │
│  [ _ _ _ _ _ _ ]   [Resend SMS OTP]    │
│                                         │
│  EMAIL VERIFICATION CODE:               │
│  [ _ _ _ _ _ _ ]   [Resend Email OTP]   │
│                                         │
│  *Please enter Captcha                  │
│  [captcha image]                        │
│  Type the text: [ _ _ _ _ ]             │
│                                         │
│  [Activate Account]                     │
└─────────────────────────────────────────┘
```

**How to verify OTP:**
1. **Check your phone** - EasyPaisa sends 6-digit OTP via SMS
2. **Check your email** - EasyPaisa sends 6-digit OTP via email
3. **Enter Captcha** from the image
4. **Click "Activate Account"**

### If OTP Not Received:
- Click **"Resend SMS OTP"** (wait 60 seconds)
- Check SMS inbox (not spam)
- Ensure mobile number is correct
- EasyPaisa account must be fully verified

---

## Step 2: Get Your Merchant Credentials

After successful activation, EasyPaisa will provide:

### You'll receive via Email/Dashboard:
- **Store ID** (e.g., `MC-123456789`)
- **Password** (API password, different from login password)
- **Hash Key/Integrity Salt** (for signature generation)

### Where to find credentials:
1. **Login:** https://www.easypaisa.com.pk/merchant
2. **Go to:** Merchant Dashboard → API Settings
3. **Or check:** Email from EasyPaisa (subject: "Merchant API Credentials")

---

## Step 3: Configure Django Settings

Open `survey_rewards_site/settings.py` and update:

```python
# EasyPaisa Configuration
EASYPAISA_CONFIG = {
    'store_id': 'MC-YOUR_STORE_ID_HERE',      # Replace with your Store ID
    'password': 'your_password_here',           # Replace with your Password
    'is_production': True,                       # True for real money
}
```

### Example (Replace with your real credentials):
```python
EASYPAISA_CONFIG = {
    'store_id': 'MC-987654321',
    'password': 'MySecureP@ss123',
    'is_production': True,  # IMPORTANT: Set True for real transactions
}
```

---

## Step 4: Test Real Integration

### Test with Real Credentials:
```bash
python manage.py shell
```

```python
from payments.easypaisa_gateway import EasyPaisaGateway

gateway = EasyPaisaGateway()
print(f"Configured: {gateway.is_configured()}")

# Test transaction
result = gateway.process_disbursement(
    amount=100,
    account_number='03001234567',
    account_name='Test User'
)
print(result)
```

### Expected Output (Real Mode):
```
Configured: True
{
    'success': True,
    'message': 'Disbursement initiated',
    'transaction_id': 'EP123456789',
    'status': 'processing',
    'is_demo': False
}
```

---

## Step 5: Go Live

### Checklist:
- [x] EasyPaisa merchant account activated (OTP verified)
- [x] Store ID and Password obtained
- [x] Django settings updated
- [x] `is_production: True` set
- [x] Test transaction successful

### Important:
⚠️ **NEVER** commit real credentials to Git
⚠️ Use environment variables in production:

```python
import os

EASYPAISA_CONFIG = {
    'store_id': os.environ.get('EASYPAISA_STORE_ID', ''),
    'password': os.environ.get('EASYPAISA_PASSWORD', ''),
    'is_production': os.environ.get('EASYPAISA_PROD', 'False') == 'True',
}
```

---

## Troubleshooting

### "Invalid Credentials" Error:
- Double-check Store ID format (starts with `MC-`)
- Ensure password is API password, not login password
- Contact EasyPaisa support if still not working

### "OTP Not Received" Error:
- Wait 2-3 minutes
- Click "Resend OTP"
- Check spam folder
- Ensure mobile number is active
- Call EasyPaisa helpline: 042-111-003-229

### "Merchant Not Found" Error:
- Account may not be fully activated
- Complete all verification steps
- Contact EasyPaisa merchant support

---

## EasyPaisa Support
- **Helpline:** 042-111-003-229
- **Email:** merchant@easypaisa.com.pk
- **Portal:** https://www.easypaisa.com.pk/merchant
- **API Docs:** https://developer.easypaisa.com.pk
