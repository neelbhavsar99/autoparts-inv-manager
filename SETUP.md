# Setup Guide - AutoParts Invoice Manager

Complete setup instructions for old MacBook Pro (8GB RAM, Intel Core i5).

## System Requirements

- macOS 10.13+ (High Sierra or later)
- Python 3.9+ (check: `python3 --version`)
- Node.js 18+ (check: `node --version`)
- 8GB RAM minimum
- 2GB free disk space

## Installation Steps

### 1. Install Python Dependencies (Backend)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (isolates dependencies)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages (~20MB, takes 1-2 min)
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed Flask-3.0.0 Flask-Login-0.6.3 ...
```

### 2. Initialize Database

```bash
# Still in backend directory with venv activated
python seed.py
```

**Expected output:**
```
🌱 Seeding database...
✅ Created user: admin@autoparts.com
✅ Created business: AutoParts Pro Shop
✅ Created 3 customers
✅ Created invoice: 20250930-001
✅ Created invoice: 20251017-001
✅ Created invoice: 20251028-001

==================================================
✅ Database seeded successfully!
==================================================

📧 Test Login Credentials:
   Email: admin@autoparts.com
   Password: admin123
```

### 3. Start Backend Server

```bash
# In backend directory
python app.py
```

**Expected output:**
```
✅ Database initialized
🚀 Starting Flask server on http://localhost:5000
⚡ Optimized for low-resource environments
 * Running on http://0.0.0.0:5000
```

**Keep this terminal open!** Backend must run continuously.

### 4. Install Frontend Dependencies

Open a **new terminal window/tab**:

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages (~150MB, takes 2-3 min on old hardware)
npm install
```

**Troubleshooting slow install:**
- Use `npm install --prefer-offline` if you have cached packages
- Or install `pnpm` for faster installs: `npm install -g pnpm && pnpm install`

### 5. Start Frontend Server

```bash
# Still in frontend directory
npm run dev
```

**Expected output:**
```
VITE v5.0.8  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h to show help
```

### 6. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

**Login with:**
- Email: `admin@autoparts.com`
- Password: `admin123`

## Verification Checklist

- [ ] Backend running on port 5000
- [ ] Frontend running on port 5173
- [ ] Can login successfully
- [ ] Dashboard shows 3 sample invoices
- [ ] Can view customers (3 customers)
- [ ] Can create new invoice
- [ ] Can download PDF

## Performance Benchmarks (Old MacBook Pro)

| Metric | Target | Typical |
|--------|--------|---------|
| Backend boot time | <3s | 2-3s |
| Frontend boot time | <5s | 3-5s |
| HMR (Hot Module Reload) | <1s | 0.5-1s |
| Page load time | <2s | 1-2s |
| PDF generation | <3s | 1-2s |
| Memory usage (total) | <1GB | 800MB-1GB |

## Common Issues

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# Find process using port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

### Database Locked

**Error:** `database is locked`

**Solution:**
```bash
# Stop all running instances
# Delete database and reseed
cd backend
rm database.db
python seed.py
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### npm Install Fails

**Error:** `EACCES: permission denied`

**Solution:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### React Router 404

**Error:** Blank page or 404 on routes

**Solution:**
- Make sure both backend AND frontend are running
- Check browser console for errors
- Clear browser cache (Cmd+Shift+R)

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Stopping Servers

- Press `Ctrl+C` in each terminal
- Or close terminal windows

### Resetting Data

```bash
cd backend
source venv/bin/activate
rm database.db
python seed.py
```

## Building for Production

### Frontend Build

```bash
cd frontend
npm run build
# Output in frontend/dist/ (~200KB gzipped)
```

### Backend Production Mode

```bash
cd backend
source venv/bin/activate

# Set production environment
export FLASK_ENV=production
export SECRET_KEY="your-secure-random-key-here"

# Run with gunicorn (install first: pip install gunicorn)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

## Deployment Options

### Option 1: Single VPS (Recommended)

**Providers:** DigitalOcean ($6/mo), Linode ($5/mo), Vultr ($5/mo)

1. Build frontend: `npm run build`
2. Copy `frontend/dist/` to server
3. Configure Flask to serve static files
4. Use nginx as reverse proxy
5. Use systemd for auto-restart

### Option 2: Free Tier (Limited)

**Render.com (Free tier):**
- Backend: Python web service
- Frontend: Static site
- Database: SQLite (or upgrade to Postgres)

**Railway.app (Free $5 credit/month):**
- Deploy both backend and frontend
- Auto-scaling disabled for free tier

### Option 3: Local Network Only

Run on your Mac and access from other devices on same WiFi:

```bash
# Backend: Already binds to 0.0.0.0
# Frontend: Add --host flag
npm run dev -- --host
```

Access from other devices: `http://YOUR_MAC_IP:5173`

## Next Steps

1. **Configure Business Settings:** Go to Settings page and update your company info
2. **Add Real Customers:** Replace sample customers with your actual clients
3. **Create Invoices:** Start generating invoices for your business
4. **Backup Database:** Regularly copy `backend/database.db` to safe location
5. **Customize:** Modify colors in `tailwind.config.js`, add logo, etc.

## Support

For issues:
1. Check this guide's Common Issues section
2. Review browser console for errors (F12)
3. Check terminal output for backend errors
4. Verify both servers are running

## Performance Tips

1. **Close unused apps** to free RAM
2. **Use Safari** (lighter than Chrome on old Macs)
3. **Disable browser extensions** while developing
4. **Clear browser cache** if pages load slowly
5. **Restart servers** if memory usage grows (after many hours)

---

**Estimated total setup time:** 10-15 minutes on old hardware
