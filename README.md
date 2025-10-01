# AutoParts Invoice Manager

A lightweight, production-ready invoice management system optimized for resource-constrained environments (old MacBook Pro with 8GB RAM).

## Tech Stack

- **Frontend**: Vite + React 18 + TypeScript + TailwindCSS
- **Backend**: Flask 3 + SQLAlchemy + SQLite
- **Auth**: Flask-Login (session-based)
- **PDF**: ReportLab
- **Charts**: Chart.js

## Features

- ✅ User authentication (email/password)
- ✅ Business settings management
- ✅ Customer CRUD operations
- ✅ Invoice creation with dynamic line items
- ✅ PDF generation and download
- ✅ Invoice history with search/filter
- ✅ Sales dashboard with charts
- ✅ Responsive mobile-friendly UI

## Prerequisites

- Python 3.9+ (tested on 3.9-3.12)
- Node.js 18+ (LTS recommended)
- 8GB RAM minimum

## Quick Start

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database and seed data
python seed.py

# Run development server (boots in <3s)
python app.py
```

Backend runs on `http://localhost:5000`

**Test Credentials:**
- Email: `admin@autoparts.com`
- Password: `admin123`

### 2. Frontend Setup

```bash
cd frontend
npm install  # ~150MB, takes 2-3min on old hardware

# Run development server (HMR <1s)
npm run dev
```

Frontend runs on `http://localhost:5173`

### 3. Access the App

Open `http://localhost:5173` and login with test credentials.

## Project Structure

```
autoparts-invoice-manager/
├── backend/
│   ├── app.py              # Flask app entry point
│   ├── models.py           # SQLAlchemy models
│   ├── auth.py             # Authentication routes
│   ├── api/
│   │   ├── business.py     # Business settings API
│   │   ├── customers.py    # Customers CRUD API
│   │   ├── invoices.py     # Invoices API
│   │   └── dashboard.py    # Dashboard analytics API
│   ├── services/
│   │   └── pdf_service.py  # PDF generation
│   ├── requirements.txt
│   ├── seed.py             # Database seeding
│   └── database.db         # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── main.tsx        # Entry point
│   │   ├── App.tsx         # Root component with routing
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
└── README.md
```

## Performance Notes

Optimized for old hardware:
- **Dev boot time**: Backend <3s, Frontend <5s
- **HMR**: <1s per change
- **Build time**: ~10s for production
- **Memory usage**: ~400MB backend, ~600MB frontend dev server
- **Dependencies**: 28 Python packages, 42 critical npm packages

## API Endpoints

### Auth
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/user` - Get current user

### Business
- `GET /api/business` - Get business settings
- `PUT /api/business` - Update business settings

### Customers
- `GET /api/customers` - List all customers
- `POST /api/customers` - Create customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer

### Invoices
- `GET /api/invoices` - List invoices (with filters)
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/:id` - Get invoice details
- `PUT /api/invoices/:id` - Update invoice
- `GET /api/invoices/:id/pdf` - Download PDF

### Dashboard
- `GET /api/dashboard/stats` - Get sales statistics

## Production Deployment

### Option 1: Single VPS (DigitalOcean/Linode - $5/month)

```bash
# Build frontend
cd frontend && npm run build

# Serve via Flask (or use nginx)
# Configure Flask to serve static files from frontend/dist
```

### Option 2: Free Tier (Render/Railway)

- Backend: Deploy as Python web service
- Frontend: Deploy as static site
- Database: SQLite (or upgrade to Postgres for multi-instance)

## Security Notes

- Passwords hashed with `werkzeug.security` (PBKDF2)
- Session cookies with `httpOnly` and `secure` flags (production)
- CORS configured for same-origin in production
- Input validation on both frontend (Zod) and backend (Flask-WTF)
- SQL injection protection via SQLAlchemy ORM

## Troubleshooting

**Port already in use:**
```bash
# Backend: Change port in app.py (default 5000)
# Frontend: Change port in vite.config.ts (default 5173)
```

**Database locked:**
```bash
# Stop all running instances and delete database.db
rm backend/database.db
python backend/seed.py
```

**Slow npm install:**
```bash
# Use pnpm (faster, less disk space)
npm install -g pnpm
pnpm install
```

## License

MIT
