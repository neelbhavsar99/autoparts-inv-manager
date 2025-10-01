# QuickStart Guide - 5 Minutes to Running App

Get AutoParts Invoice Manager running in 5 minutes on your old MacBook Pro.

## Prerequisites Check

```bash
# Check Python (need 3.9+)
python3 --version

# Check Node.js (need 18+)
node --version

# If missing, install via Homebrew:
# brew install python@3.11 node
```

## 1-Command Setup (Copy & Paste)

### Terminal 1: Backend

```bash
cd backend && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python seed.py && \
python app.py
```

**Wait for:** `🚀 Starting Flask server on http://localhost:5000`

### Terminal 2: Frontend (New Tab)

```bash
cd frontend && \
npm install && \
npm run dev
```

**Wait for:** `➜  Local:   http://localhost:5173/`

## 2. Open & Login

1. Open browser: **http://localhost:5173**
2. Login:
   - Email: `admin@autoparts.com`
   - Password: `admin123`

## 3. Quick Tour

1. **Dashboard** - View sales stats and charts
2. **Invoices** - See 3 sample invoices, create new ones
3. **Customers** - Manage customer database
4. **Settings** - Configure business info

## Done! 🎉

You now have a fully functional invoice manager running locally.

## Next Steps

- **Create Your First Invoice**: Click "New Invoice" button
- **Add Real Customers**: Go to Customers → Add Customer
- **Download PDF**: View any invoice → Download PDF
- **Customize Settings**: Update your business info in Settings

## Stopping the App

Press `Ctrl+C` in both terminal windows.

## Restarting Later

```bash
# Terminal 1
cd backend && source venv/bin/activate && python app.py

# Terminal 2
cd frontend && npm run dev
```

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:5000 | xargs kill -9  # Kill backend
lsof -ti:5173 | xargs kill -9  # Kill frontend
```

**Database issues?**
```bash
cd backend && rm database.db && python seed.py
```

**Need detailed help?** See `SETUP.md` for comprehensive guide.
