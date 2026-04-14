# 🚀 Streamlit Cloud Deployment Guide

## ❌ Fix "Error installing requirements"

### Problem:
Streamlit Cloud is trying to install Django requirements instead of Streamlit requirements.

---

## ✅ Solution: Create Proper requirements.txt for Streamlit Cloud

### Option 1: Replace requirements.txt (Recommended for Streamlit-only deployment)

**Step 1:** Backup your current Django requirements.txt
```bash
cp requirements.txt requirements_django_backup.txt
```

**Step 2:** Create new requirements.txt for Streamlit
```bash
# Copy the Streamlit requirements
cp requirements_streamlit_cloud.txt requirements.txt
```

**Step 3:** Commit and push to GitHub
```bash
git add requirements.txt
git commit -m "Update requirements.txt for Streamlit Cloud deployment"
git push origin main
```

**Step 4:** Redeploy on Streamlit Cloud
- Go to https://share.streamlit.io
- Click on your app
- Click "Redeploy"

---

### Option 2: Use Separate Git Branch (Keep both Django & Streamlit)

**Step 1:** Create a new branch for Streamlit
```bash
git checkout -b streamlit-deployment
```

**Step 2:** Replace requirements.txt in this branch
```bash
cp requirements_streamlit_cloud.txt requirements.txt
```

**Step 3:** Commit and push
```bash
git add requirements.txt
git commit -m "Streamlit deployment requirements"
git push origin streamlit-deployment
```

**Step 4:** Deploy from streamlit-deployment branch
- Go to Streamlit Cloud
- Select your repository
- Choose branch: **streamlit-deployment**
- Main file: **streamlit_app.py**
- Deploy!

---

## 📋 Correct requirements.txt Content

Your `requirements.txt` should contain ONLY:

```
streamlit>=1.28.0
pandas>=2.0.0
```

**DO NOT include:**
- Django
- gunicorn
- whitenoise
- psycopg2
- Any Django-specific packages

---

## 🔧 Streamlit Cloud Settings

When deploying on Streamlit Cloud:

1. **Repository:** Your GitHub repo
2. **Branch:** main (or streamlit-deployment)
3. **File path:** streamlit_app.py
4. **App URL:** your-custom-name.streamlit.app

---

## 🐛 Common Errors & Fixes

### Error 1: "Error installing requirements"
**Fix:** Use correct requirements.txt (see above)

### Error 2: "ModuleNotFoundError: No module named 'streamlit'"
**Fix:** Make sure `streamlit` is in requirements.txt

### Error 3: "ModuleNotFoundError: No module named 'pandas'"
**Fix:** Make sure `pandas` is in requirements.txt

### Error 4: "File not found: streamlit_app.py"
**Fix:** Set File path to `streamlit_app.py` in Streamlit Cloud settings

### Error 5: Database not created
**Fix:** Database auto-creates on first run. No action needed.

---

## ✅ Deployment Checklist

Before deploying, verify:

- [ ] `requirements.txt` contains ONLY: streamlit, pandas
- [ ] `streamlit_app.py` exists in repository
- [ ] Files are committed and pushed to GitHub
- [ ] Streamlit Cloud points to correct branch
- [ ] File path is set to `streamlit_app.py`

---

## 🚀 Quick Deploy Steps

### 1. Prepare Files
```bash
# In your project directory
cp requirements_streamlit_cloud.txt requirements.txt
git add requirements.txt streamlit_app.py
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to: https://share.streamlit.io
2. Click **"New app"**
3. Select your **GitHub repository**
4. Set:
   - **Branch:** main
   - **File path:** streamlit_app.py
   - **App URL:** (choose your custom name)
5. Click **"Deploy!"**

### 3. Wait for Deployment
- Takes 2-5 minutes
- Watch the deployment logs
- App will be live at: `your-name.streamlit.app`

---

## 📊 After Successful Deployment

Your app will be available at:
```
https://your-app-name.streamlit.app
```

**Features working:**
✅ User registration
✅ Login system
✅ 6 surveys
✅ Withdrawal system
✅ Transaction history
✅ FAQ & About pages

---

## 🔄 Updating Your App

After making changes:
```bash
git add .
git commit -m "Update app"
git push origin main
```

Then click **"Redeploy"** on Streamlit Cloud dashboard.

---

## 📞 Need Help?

If you still face issues:
1. Check deployment logs in Streamlit Cloud ("Manage App" → "Logs")
2. Verify requirements.txt content
3. Make sure all files are pushed to GitHub
4. Try redeploying

---

**Good luck with deployment!** 🚀
