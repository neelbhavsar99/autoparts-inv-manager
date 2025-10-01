# Architecture Documentation

## System Overview

AutoParts Invoice Manager is a lightweight full-stack web application optimized for resource-constrained environments (old MacBook Pro with 8GB RAM).

## Tech Stack Rationale

### Why Vite + React + Flask?

**Frontend: Vite + React + TypeScript**
- **Vite**: 10-100x faster than Webpack, HMR in <1s, minimal config
- **React 18**: Mature ecosystem, efficient rendering, 45KB gzipped
- **TypeScript**: Type safety prevents runtime errors, better DX
- **TailwindCSS**: Utility-first, tree-shakeable, ~10KB in production

**Backend: Flask + SQLite**
- **Flask**: Lightest Python web framework (~10 dependencies vs 50+ in Django)
- **SQLite**: Zero-config, file-based, perfect for single-user/small team
- **Flask-Login**: Battle-tested session auth, minimal overhead
- **ReportLab**: Pure Python PDF generation, no external dependencies

**Rejected Alternatives:**
- ❌ Next.js: 500MB+ node_modules, slow dev server on old hardware
- ❌ Django: Overkill for simple CRUD, 50+ dependencies
- ❌ Streamlit: Limited UI customization, not production-ready
- ❌ Electron: 200MB+ app size, slow startup

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Client)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  React App (Vite Dev Server: 5173)                │  │
│  │  - React Router (client-side routing)             │  │
│  │  - Chart.js (dashboard visualizations)            │  │
│  │  - TailwindCSS (styling)                          │  │
│  └───────────────┬───────────────────────────────────┘  │
└──────────────────┼──────────────────────────────────────┘
                   │ HTTP/JSON (fetch API)
                   │ Credentials: include (session cookies)
┌──────────────────▼──────────────────────────────────────┐
│              Flask Backend (Port 5000)                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Flask App (app.py)                               │  │
│  │  - Flask-CORS (dev: allow localhost:5173)        │  │
│  │  - Flask-Login (session management)               │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                        │
│  ┌───────────────▼───────────────────────────────────┐  │
│  │  API Blueprints                                    │  │
│  │  - /api/auth (login, logout, check)               │  │
│  │  - /api/business (CRUD business settings)         │  │
│  │  - /api/customers (CRUD customers)                │  │
│  │  - /api/invoices (CRUD invoices, PDF download)    │  │
│  │  - /api/dashboard (analytics queries)             │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                        │
│  ┌───────────────▼───────────────────────────────────┐  │
│  │  Services                                          │  │
│  │  - pdf_service.py (ReportLab PDF generation)      │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                        │
│  ┌───────────────▼───────────────────────────────────┐  │
│  │  SQLAlchemy ORM (models.py)                       │  │
│  │  - User, BusinessInfo, Customer                   │  │
│  │  - Invoice, InvoiceLineItem                       │  │
│  └───────────────┬───────────────────────────────────┘  │
└──────────────────┼──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│              SQLite Database (database.db)               │
│  - Single file, no server process                        │
│  - ACID compliant, supports concurrent reads             │
│  - ~1MB for 1000 invoices                                │
└──────────────────────────────────────────────────────────┘
```

## Directory Structure

```
sahjanand-ap/
├── backend/
│   ├── app.py                    # Flask app entry point
│   ├── models.py                 # SQLAlchemy models
│   ├── auth.py                   # Authentication routes
│   ├── seed.py                   # Database seeding script
│   ├── requirements.txt          # Python dependencies (7 packages)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── business.py           # Business settings endpoints
│   │   ├── customers.py          # Customers CRUD endpoints
│   │   ├── invoices.py           # Invoices CRUD + PDF
│   │   └── dashboard.py          # Analytics endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── pdf_service.py        # PDF generation logic
│   └── database.db               # SQLite database (auto-created)
│
├── frontend/
│   ├── index.html                # HTML entry point
│   ├── package.json              # npm dependencies (~40 packages)
│   ├── vite.config.ts            # Vite configuration
│   ├── tsconfig.json             # TypeScript config
│   ├── tailwind.config.js        # TailwindCSS config
│   ├── postcss.config.js         # PostCSS config
│   ├── src/
│   │   ├── main.tsx              # React entry point
│   │   ├── App.tsx               # Root component + routing
│   │   ├── index.css             # Global styles + Tailwind
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript type definitions
│   │   ├── services/
│   │   │   └── api.ts            # API client (fetch wrapper)
│   │   ├── components/
│   │   │   ├── Layout.tsx        # Main layout with nav
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── Toast.tsx         # Toast notifications
│   │   └── pages/
│   │       ├── Login.tsx         # Login page
│   │       ├── Dashboard.tsx     # Dashboard with charts
│   │       ├── BusinessSettings.tsx
│   │       ├── Customers.tsx     # Customers list + modal
│   │       ├── Invoices.tsx      # Invoices list + filters
│   │       ├── CreateInvoice.tsx # Invoice creation form
│   │       └── ViewInvoice.tsx   # Invoice details view
│   └── dist/                     # Production build output
│
├── README.md                     # Main documentation
├── SETUP.md                      # Setup instructions
├── ARCHITECTURE.md               # This file
└── .gitignore                    # Git ignore rules
```

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│ email       │◄──────┐
│ password    │       │
│ name        │       │
└─────────────┘       │
                      │
       ┌──────────────┼──────────────┬──────────────┐
       │              │              │              │
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│BusinessInfo │ │  Customer  │ │  Invoice  │ │  Invoice  │
│─────────────│ │────────────│ │───────────│ │───────────│
│ id (PK)     │ │ id (PK)    │ │ id (PK)   │ │ ...       │
│ user_id(FK) │ │ user_id(FK)│ │ user_id   │ │           │
│ company_name│ │ name       │ │ customer  │◄┼───────────┘
│ address     │ │ address    │ │ invoice_# │ │
│ phone       │ │ phone      │ │ date      │ │
│ email       │ │ email      │ │ subtotal  │ │
│ tax_id      │ └────────────┘ │ tax       │ │
│ logo_url    │                │ total     │ │
└─────────────┘                │ status    │ │
  (1:1 with User)              │ notes     │ │
                               └───────────┘ │
                                      │      │
                                      │      │
                               ┌──────▼──────▼──────┐
                               │ InvoiceLineItem    │
                               │────────────────────│
                               │ id (PK)            │
                               │ invoice_id (FK)    │
                               │ product_name       │
                               │ part_number        │
                               │ quantity           │
                               │ unit_price         │
                               │ line_total         │
                               └────────────────────┘
```

### Key Relationships

- **User → BusinessInfo**: One-to-One (each user has one business profile)
- **User → Customers**: One-to-Many (user owns multiple customers)
- **User → Invoices**: One-to-Many (user creates multiple invoices)
- **Customer → Invoices**: One-to-Many (customer has multiple invoices)
- **Invoice → LineItems**: One-to-Many (invoice has multiple line items)

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/login` | Login with email/password | No |
| POST | `/logout` | Logout current user | Yes |
| GET | `/check` | Check if authenticated | No |
| GET | `/user` | Get current user info | Yes |

### Business Settings (`/api/business`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get business settings | Yes |
| PUT | `/` | Update business settings | Yes |

### Customers (`/api/customers`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List all customers | Yes |
| POST | `/` | Create new customer | Yes |
| PUT | `/:id` | Update customer | Yes |
| DELETE | `/:id` | Delete customer | Yes |

### Invoices (`/api/invoices`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List invoices (with filters) | Yes |
| GET | `/:id` | Get invoice details | Yes |
| POST | `/` | Create new invoice | Yes |
| PUT | `/:id` | Update invoice (status/notes) | Yes |
| GET | `/:id/pdf` | Download invoice PDF | Yes |

**Query Parameters for GET `/`:**
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)
- `customer_id`: Filter by customer ID
- `status`: Filter by status (paid/unpaid)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

### Dashboard (`/api/dashboard`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/stats` | Get sales statistics | Yes |

**Response includes:**
- Overview: total_sales, num_invoices, avg_order_value (last month)
- Monthly sales: Last 12 months aggregated by month
- Top products: Top 10 products by revenue

## Authentication Flow

```
┌─────────┐                ┌─────────┐                ┌──────────┐
│ Browser │                │  Flask  │                │ Database │
└────┬────┘                └────┬────┘                └────┬─────┘
     │                          │                          │
     │  POST /api/auth/login    │                          │
     │  {email, password}       │                          │
     ├─────────────────────────►│                          │
     │                          │  Query user by email     │
     │                          ├─────────────────────────►│
     │                          │                          │
     │                          │  User record             │
     │                          │◄─────────────────────────┤
     │                          │                          │
     │                          │  Verify password hash    │
     │                          │  (werkzeug.security)     │
     │                          │                          │
     │                          │  Create session          │
     │                          │  (Flask-Login)           │
     │                          │                          │
     │  Set-Cookie: session=... │                          │
     │◄─────────────────────────┤                          │
     │  {user: {...}}           │                          │
     │                          │                          │
     │  GET /api/invoices       │                          │
     │  Cookie: session=...     │                          │
     ├─────────────────────────►│                          │
     │                          │  Load user from session  │
     │                          │  (@login_required)       │
     │                          │                          │
     │                          │  Query invoices          │
     │                          ├─────────────────────────►│
     │                          │                          │
     │                          │  Invoice records         │
     │                          │◄─────────────────────────┤
     │                          │                          │
     │  {data: [...]}           │                          │
     │◄─────────────────────────┤                          │
     │                          │                          │
```

## Performance Optimizations

### Backend

1. **SQLite Optimizations**
   - Indexed columns: `user_id`, `email`, `invoice_number`
   - Lazy loading relationships (avoid N+1 queries)
   - Connection pooling via SQLAlchemy

2. **Flask Optimizations**
   - Threaded mode enabled (handle concurrent requests)
   - Minimal middleware (only CORS + Login)
   - No template rendering (API-only)

3. **PDF Generation**
   - ReportLab (pure Python, no external deps)
   - Streamed response (BytesIO buffer)
   - No disk I/O for temporary files

### Frontend

1. **Vite Optimizations**
   - esbuild bundler (10-100x faster than Webpack)
   - Code splitting (vendor chunks)
   - Tree shaking (unused code removed)

2. **React Optimizations**
   - Lazy loading for Chart.js (only on dashboard)
   - Controlled components (avoid unnecessary re-renders)
   - Key props on lists (efficient reconciliation)

3. **TailwindCSS Optimizations**
   - PurgeCSS (removes unused styles)
   - Production build: ~10KB gzipped
   - No runtime overhead

4. **Bundle Size**
   - Main bundle: ~80KB gzipped
   - Vendor bundle: ~120KB gzipped
   - Chart bundle: ~60KB gzipped (lazy loaded)
   - Total initial load: ~200KB

## Security Considerations

### Authentication

- **Password Hashing**: PBKDF2 via `werkzeug.security` (100,000 iterations)
- **Session Management**: Flask-Login with secure cookies
- **CSRF Protection**: SameSite cookies (Lax mode)
- **Password Policy**: Minimum 8 characters (enforced on backend)

### API Security

- **Authentication Required**: All endpoints except `/login` and `/check`
- **User Isolation**: All queries filtered by `user_id` (no cross-user access)
- **Input Validation**: Required fields checked, positive numbers enforced
- **SQL Injection**: Protected by SQLAlchemy ORM (parameterized queries)

### Production Recommendations

1. **Environment Variables**
   - Set `SECRET_KEY` to random 32-byte string
   - Set `FLASK_ENV=production`
   - Disable debug mode

2. **HTTPS**
   - Use reverse proxy (nginx) with SSL certificate
   - Set `SESSION_COOKIE_SECURE=True`

3. **Rate Limiting**
   - Add Flask-Limiter for login endpoint
   - Limit: 5 attempts per minute per IP

4. **Database Backups**
   - Daily backups of `database.db`
   - Store offsite (S3, Dropbox, etc.)

## Scalability Considerations

### Current Limits (SQLite)

- **Concurrent Users**: 10-20 (read-heavy workload)
- **Database Size**: Up to 281TB (practical: <10GB)
- **Invoices**: 100,000+ (with proper indexing)

### When to Migrate to PostgreSQL

- More than 20 concurrent users
- Multiple application servers (load balancing)
- Database size > 5GB
- Need for advanced features (full-text search, JSON queries)

### Migration Path

1. Install PostgreSQL
2. Update `models.py`: Change connection string
3. Run migrations (Alembic recommended)
4. Update deployment config

## Testing Strategy

### Manual Testing Checklist

- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Logout and verify redirect
- [ ] Create/edit/delete customer
- [ ] Create invoice with multiple line items
- [ ] View invoice details
- [ ] Download invoice PDF
- [ ] Mark invoice as paid/unpaid
- [ ] Filter invoices by date/status
- [ ] View dashboard charts
- [ ] Update business settings

### Automated Testing (Future)

**Backend:**
- Unit tests: `pytest` for models and API endpoints
- Integration tests: Test full request/response cycle
- Coverage target: >80%

**Frontend:**
- Unit tests: `vitest` for components
- E2E tests: `Playwright` for user flows
- Coverage target: >70%

## Deployment Checklist

- [ ] Set production `SECRET_KEY`
- [ ] Set `FLASK_ENV=production`
- [ ] Build frontend: `npm run build`
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure systemd service (auto-restart)
- [ ] Set up database backups (cron job)
- [ ] Configure firewall (allow 80/443 only)
- [ ] Test all features in production
- [ ] Monitor logs for errors

## Maintenance

### Regular Tasks

- **Daily**: Check application logs
- **Weekly**: Review database size, backup verification
- **Monthly**: Update dependencies (security patches)
- **Quarterly**: Full backup test (restore to staging)

### Monitoring

- **Application**: Flask logs (stdout/stderr)
- **Database**: SQLite size, query performance
- **Server**: CPU, RAM, disk usage
- **Uptime**: Use external monitoring (UptimeRobot, Pingdom)

---

**Last Updated**: 2025-10-01  
**Version**: 1.0.0
