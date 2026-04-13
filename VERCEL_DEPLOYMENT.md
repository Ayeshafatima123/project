# Vercel Deployment Guide

## Files Created for Vercel:
✅ `vercel.json` - Vercel configuration
✅ `requirements.txt` - Python dependencies
✅ `api/index.py` - Serverless entry point
✅ Updated `settings.py` - Production-ready

## Deploy to Vercel:

### Option 1: Vercel CLI (Easiest)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
cd C:\Users\ahmed\OneDrive\Desktop\p.g
vercel
```

### Option 2: Vercel Dashboard (No CLI)
1. Go to: https://vercel.com/new
2. Import your Git repository
3. Configure:
   - **Framework:** Python
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Output Directory:** `staticfiles`
4. Add environment variables (see below)
5. Click **Deploy**

## Environment Variables to Add on Vercel:

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these:

```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.vercel.app,.now.sh,your-domain.com

# Email (for OTP/notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# EasyPaisa (when you get merchant credentials)
EASYPAISA_STORE_ID=MC-xxxxxxxxx
EASYPAISA_PASSWORD=your-easypaisa-password
EASYPAISA_IS_PRODUCTION=False

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Database Setup:

Vercel serverless functions are stateless, so SQLite won't work in production.

### Option A: Use PostgreSQL (Recommended)
1. Create PostgreSQL database on:
   - **Neon:** https://neon.tech/
   - **Supabase:** https://supabase.com/
   - **Railway:** https://railway.app/
2. Get connection string
3. Add `DATABASE_URL` env variable on Vercel

### Option B: Use SQLite (For Testing Only)
SQLite will work but data will be lost on each deployment.

## Test Deployment:

After deployment, test these URLs:
- `https://your-app.vercel.app/` - Home page
- `https://your-app.vercel.app/auth/login/` - Login
- `https://your-app.vercel.app/auth/register/` - Register

## Important Notes:

⚠️ **SQLite on Vercel:** Not recommended for production (data loss on redeploy)
⚠️ **Static Files:** WhiteNoise handles static files automatically
⚠️ **Media Files:** Use cloud storage (S3, Cloudinary) for user uploads
⚠️ **Sessions:** Use database-backed sessions (already configured)

## EasyPaisa Integration:

Once you get your EasyPaisa merchant credentials:
1. Add `EASYPAISA_STORE_ID` and `EASYPAISA_PASSWORD` to Vercel env variables
2. Set `EASYPAISA_IS_PRODUCTION=True`
3. Redeploy: `vercel --prod`

## Troubleshooting:

### "Application Error"
- Check Vercel logs: Dashboard → Logs
- Verify all env variables are set
- Check requirements.txt has all dependencies

### Static Files Not Loading
- Run: `python manage.py collectstatic`
- Verify WhiteNoise middleware is in MIDDLEWARE

### Database Errors
- Ensure DATABASE_URL is set correctly
- Check PostgreSQL database is accessible

## Need Help?
- Vercel Docs: https://vercel.com/docs
- Django on Vercel: https://vercel.com/docs/concepts/support/deployment-methods/python
