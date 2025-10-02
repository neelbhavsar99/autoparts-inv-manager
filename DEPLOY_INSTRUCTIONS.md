# 🚀 Deploy to Railway - Step by Step Instructions

Follow these exact steps to deploy your app to Railway.

---

## ✅ Step 1: Push Code to GitHub (5 minutes)

Open Terminal and run these commands **one by one**:

```bash
# Navigate to your project
cd /Users/neelbhavsar/Documents/GitHub/sahjanand-ap

# Add all new files
git add .

# Commit changes
git commit -m "Add Railway deployment config and backup scripts"

# Push to GitHub
git push origin main
```

**Expected output:** "Everything up-to-date" or commit success message

---

## ✅ Step 2: Create Railway Account (2 minutes)

1. Go to: **https://railway.app**
2. Click **"Login"**
3. Click **"Login with GitHub"**
4. Click **"Authorize Railway"** (allows Railway to access your repos)
5. **Add credit card** (required for verification, won't charge within $5 free tier)

---

## ✅ Step 3: Deploy Backend + Database (3 minutes)

### 3a. Create New Project

1. In Railway Dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and click **"autoparts-inv-manager"**
4. Railway will start deploying automatically

### 3b. Add PostgreSQL Database

1. In your project, click **"New"** button
2. Select **"Database"**
3. Click **"Add PostgreSQL"**
4. Railway creates database and links it automatically
5. Wait for database to deploy (green checkmark)

### 3c. Configure Backend Environment Variables

1. Click on your **backend service** (the one that's building)
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add these **one by one**:

```
Variable 1:
Key: FLASK_ENV
Value: production

Variable 2:
Key: SECRET_KEY
Value: (click "Generate" button to create random value)

Variable 3:
Key: CORS_ORIGINS
Value: http://localhost:5173
(we'll update this later with real frontend URL)
```

4. Click **"Deploy"** (service will restart with new variables)

---

## ✅ Step 4: Deploy Frontend (3 minutes)

### 4a. Add Frontend Service

1. In your project, click **"New"** button
2. Select **"GitHub Repo"**
3. Select **"autoparts-inv-manager"** (same repo)
4. Railway creates a second service

### 4b. Configure Frontend Build

1. Click on the **new service** (this is your frontend)
2. Go to **"Settings"** tab
3. Scroll to **"Build"** section
4. Set these values:

```
Build Command:
cd frontend && npm install && npm run build

Start Command:
(leave empty - it's a static site)

Root Directory:
frontend
```

5. Scroll to **"Deploy"** section
6. Set:

```
Custom Start Command:
(leave empty)
```

7. Click **"Deploy"**

### 4c. Enable Public Access

1. Still in frontend service **"Settings"**
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy the generated URL (looks like: `https://autoparts-frontend-production-xxxx.up.railway.app`)

---

## ✅ Step 5: Update CORS Settings (2 minutes)

Now that you have the frontend URL:

1. Go back to **backend service**
2. Click **"Variables"** tab
3. Find **CORS_ORIGINS** variable
4. Click **"Edit"**
5. Replace with your **actual frontend URL** (the one you just copied)
   ```
   https://autoparts-frontend-production-xxxx.up.railway.app
   ```
6. Click **"Save"**
7. Backend will automatically redeploy

---

## ✅ Step 6: Initialize Database (3 minutes)

### 6a. Wait for Backend to Deploy

1. Click on **backend service**
2. Go to **"Deployments"** tab
3. Wait for latest deployment to show **green checkmark** (✅)
4. This means backend is running

### 6b. Run Database Seed Script

1. In backend service, go to **"Settings"** tab
2. Scroll down to **"Service"** section
3. Under **"One-off Commands"**, enter:
   ```
   cd backend && python seed.py
   ```
4. Click **"Run"**
5. Wait for command to complete (you'll see output in logs)

**Expected output:**
```
🌱 Seeding database...
✅ Created user: admin@autoparts.com
✅ Created business: AutoParts Pro Shop
✅ Created 3 customers
✅ Created invoice: 20251002-001
...
✅ Database seeded successfully!
```

---

## ✅ Step 7: Update Frontend API URL (5 minutes)

Your frontend needs to know where the backend is.

### 7a. Get Backend URL

1. Click on **backend service**
2. Go to **"Settings"** → **"Networking"**
3. Copy the **Public Domain** URL (looks like: `https://autoparts-backend-production-xxxx.up.railway.app`)

### 7b. Update Frontend Code

On your Mac, edit this file:

```bash
# Open the file
nano /Users/neelbhavsar/Documents/GitHub/sahjanand-ap/frontend/src/services/api.ts
```

Find this line (around line 9):
```typescript
const API_BASE = '/api';
```

Replace it with:
```typescript
const API_BASE = 'https://your-backend-url.up.railway.app/api';
```

**Replace `your-backend-url` with your actual backend URL!**

Save and exit (Ctrl+X, then Y, then Enter)

### 7c. Push Updated Code

```bash
cd /Users/neelbhavsar/Documents/GitHub/sahjanand-ap
git add frontend/src/services/api.ts
git commit -m "Update API URL for production"
git push origin main
```

Railway will automatically redeploy frontend (takes 2-3 minutes)

---

## ✅ Step 8: Test Your Deployed App (2 minutes)

### 8a. Open Your App

1. Go to Railway Dashboard
2. Click on **frontend service**
3. Click the **URL** at the top (or copy it)
4. Opens in browser

### 8b. Login

Use test credentials:
- **Email:** `admin@autoparts.com`
- **Password:** `admin123`

### 8c. Test Features

- ✅ Dashboard loads with charts
- ✅ Can view customers (3 sample customers)
- ✅ Can view invoices (3 sample invoices)
- ✅ Can create new invoice
- ✅ Can download PDF
- ✅ HTTPS working (green padlock in browser)

---

## 🎉 You're Live!

Your app is now deployed at:
- **Frontend:** `https://your-frontend.up.railway.app`
- **Backend:** `https://your-backend.up.railway.app`

---

## 🔐 Step 9: Change Default Password (IMPORTANT!)

**Do this immediately after testing:**

1. In Railway Dashboard → **backend service** → **Settings**
2. Under **"One-off Commands"**, run:
   ```python
   python -c "from models import get_db, User; db = get_db(); user = User(email='your@email.com', name='Your Name'); user.set_password('your-secure-password'); db.add(user); db.commit(); print('New user created!')"
   ```

3. Replace:
   - `your@email.com` with your real email
   - `Your Name` with your name
   - `your-secure-password` with a strong password (min 8 chars)

4. Login with your new credentials
5. Delete test user (optional, from app UI later)

---

## 📊 Step 10: Monitor Usage (Optional)

### Check Your Free Credit

1. Railway Dashboard → Click your profile (top right)
2. Click **"Usage"**
3. See current month's usage
4. Should be ~$3-4/month (within $5 free credit)

### Set Up Alerts

1. Go to **"Settings"** → **"Notifications"**
2. Enable email alerts for:
   - Usage approaching $5
   - Deployment failures
   - Service errors

---

## 🔄 Step 11: Set Up Automated Backups (Optional but Recommended)

Follow the backup guide to protect your data permanently:

1. Install rclone: `brew install rclone`
2. Configure Google Drive: `rclone config`
3. Get your DATABASE_URL from Railway:
   - Dashboard → PostgreSQL → **"Connect"** tab
   - Copy the **"Postgres Connection URL"**
4. Edit backup script:
   ```bash
   nano /Users/neelbhavsar/Documents/GitHub/sahjanand-ap/backup_to_cloud.sh
   ```
5. Replace `your_railway_database_url_here` with actual URL
6. Make executable: `chmod +x backup_to_cloud.sh`
7. Test: `./backup_to_cloud.sh`
8. Schedule weekly:
   ```bash
   crontab -e
   # Add this line:
   0 2 * * 0 /Users/neelbhavsar/Documents/GitHub/sahjanand-ap/backup_to_cloud.sh
   ```

---

## 🐛 Troubleshooting

### Frontend shows blank page
- Check browser console (F12) for errors
- Verify API_BASE URL is correct in `api.ts`
- Check CORS_ORIGINS matches frontend URL exactly

### "Network Error" when logging in
- Backend not running - check Railway dashboard
- CORS issue - verify CORS_ORIGINS variable
- DATABASE_URL not set - check backend variables

### Database connection error
- PostgreSQL not created - add it in Railway
- DATABASE_URL not linked - Railway should auto-link
- Restart backend service

### Build failed
- Check deployment logs in Railway
- Common issue: missing dependencies in requirements.txt
- Solution: Verify all packages listed

---

## 📞 Need Help?

**Railway Documentation:**
- https://docs.railway.app

**Railway Discord:**
- https://discord.gg/railway

**Your Project URLs:**
- Frontend: (copy from Railway dashboard)
- Backend: (copy from Railway dashboard)
- Database: (internal, accessed via backend)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Backend deployed
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Frontend deployed
- [ ] CORS configured
- [ ] Database seeded
- [ ] Frontend API URL updated
- [ ] App tested and working
- [ ] Default password changed
- [ ] Usage monitoring set up
- [ ] Backups configured

---

## 🎯 Next Steps

1. **Customize branding** - Update business settings in app
2. **Add real customers** - Delete sample data, add yours
3. **Create invoices** - Start using for your business
4. **Monitor costs** - Check Railway usage weekly
5. **Set up backups** - Protect your data permanently

---

**Total deployment time:** 20-30 minutes  
**Monthly cost:** $0 (within $5 free credit)  
**Your app is now live and secure!** 🚀

---

## 📝 Save These URLs

After deployment, save these for reference:

```
Frontend URL: _________________________________
Backend URL:  _________________________________
Database:     (managed by Railway, no direct access needed)

Login Credentials:
Email:    _________________________________
Password: _________________________________

Railway Dashboard: https://railway.app/dashboard
GitHub Repo: https://github.com/neelbhavsar99/autoparts-inv-manager
```

---

**Congratulations! Your AutoParts Invoice Manager is live!** 🎉
