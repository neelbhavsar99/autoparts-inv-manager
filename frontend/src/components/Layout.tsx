/**
 * Main layout — Synk sidebar shell
 *
 * Replaces the original top-header layout with a left sidebar
 * + sticky topbar. Routes are unchanged. Adds a "Create invoice"
 * top-level nav entry that links to /invoices/new.
 */
import { Outlet, Link, useLocation } from 'react-router-dom';
import { User } from '../types';

interface LayoutProps {
  user: User;
  onLogout: () => void;
}

interface NavItem {
  path: string;
  label: string;
  match?: (pathname: string) => boolean;
}

const NAV: NavItem[] = [
  { path: '/', label: 'Dashboard', match: (p) => p === '/' },
  {
    path: '/invoices',
    label: 'Invoices',
    // Active for /invoices and /invoices/:id but NOT /invoices/new
    match: (p) => p.startsWith('/invoices') && p !== '/invoices/new',
  },
  {
    path: '/invoices/new',
    label: 'Create invoice',
    match: (p) => p === '/invoices/new',
  },
  { path: '/customers', label: 'Customers', match: (p) => p.startsWith('/customers') },
  { path: '/business', label: 'Settings', match: (p) => p.startsWith('/business') },
];

// Add Users nav for admin users
const getNavItems = (user: User): NavItem[] => {
  const baseNav = [...NAV];
  if (user.role === 'admin') {
    baseNav.splice(-1, 0, { path: '/users', label: 'Users', match: (p) => p.startsWith('/users') });
  }
  return baseNav;
};

// Lucide-ish stroke icons inline to avoid a new dep.
const Ico = {
  dashboard: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/>
      <rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>
    </svg>
  ),
  invoice: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/>
    </svg>
  ),
  plus: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M5 12h14"/>
    </svg>
  ),
  users: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  settings: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>
  ),
  bell: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
    </svg>
  ),
};

const iconFor = (label: string) => {
  if (label === 'Dashboard') return Ico.dashboard;
  if (label === 'Invoices') return Ico.invoice;
  if (label === 'Create invoice') return Ico.plus;
  if (label === 'Customers') return Ico.users;
  if (label === 'Users') return Ico.users;
  if (label === 'Settings') return Ico.settings;
  return Ico.dashboard;
};

const initials = (name: string) =>
  name.split(' ').map((s) => s[0]).slice(0, 2).join('').toUpperCase();

export default function Layout({ user, onLogout }: LayoutProps) {
  const location = useLocation();
  const navItems = getNavItems(user);
  const isActive = (item: NavItem) =>
    item.match ? item.match(location.pathname) : location.pathname === item.path;

  return (
    <div
      className="min-h-screen grid"
      style={{ gridTemplateColumns: '248px 1fr', background: 'var(--bg)' }}
    >
      {/* SIDEBAR */}
      <aside
        className="flex flex-col sticky top-0 h-screen"
        style={{ background: 'var(--bg-elev)', borderRight: '1px solid var(--border)' }}
      >
        {/* Brand */}
        <div
          className="flex items-center gap-3 px-5 py-5"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <div
            className="grid place-items-center font-bold text-white"
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'linear-gradient(135deg, var(--accent), oklch(0.55 0.2 270))',
              fontSize: 15,
              letterSpacing: '-0.04em',
            }}
          >
            S
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15, letterSpacing: '-0.02em' }}>
              Synk
            </div>
            <div style={{ fontSize: 11, color: 'var(--fg-subtle)', marginTop: 1 }}>
              Auto Parts
            </div>
          </div>
        </div>

        {/* Nav */}
        <div className="px-3 pt-4 pb-1">
          <div
            className="px-2.5 pb-2"
            style={{
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: 'var(--fg-subtle)',
            }}
          >
            Workspace
          </div>
          {navItems.map((n) => {
            const active = isActive(n);
            return (
              <Link
                key={n.path}
                to={n.path}
                className="flex items-center gap-3 w-full text-left transition-colors"
                style={{
                  padding: '9px 12px',
                  borderRadius: 8,
                  fontSize: 13.5,
                  fontWeight: 500,
                  color: active ? 'var(--fg)' : 'var(--fg-muted)',
                  background: active ? 'var(--surface)' : 'transparent',
                  boxShadow: active ? 'inset 0 0 0 1px var(--border)' : 'none',
                  textDecoration: 'none',
                  marginBottom: 1,
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.background = 'var(--surface-hover)';
                    (e.currentTarget as HTMLElement).style.color = 'var(--fg)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.background = 'transparent';
                    (e.currentTarget as HTMLElement).style.color = 'var(--fg-muted)';
                  }
                }}
              >
                <span style={{ flexShrink: 0 }}>{iconFor(n.label)}</span>
                <span>{n.label}</span>
              </Link>
            );
          })}
        </div>

        {/* User card */}
        <div
          className="mt-auto p-3.5"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          <div className="flex items-center gap-2.5 p-2 rounded-lg">
            <div
              className="grid place-items-center text-white font-semibold flex-shrink-0"
              style={{
                width: 30,
                height: 30,
                borderRadius: 7,
                background: 'oklch(0.65 0.12 200)',
                fontSize: 12,
              }}
            >
              {initials(user.name)}
            </div>
            <div className="flex-1 min-w-0">
              <div style={{ fontSize: 13, fontWeight: 500 }}>{user.name}</div>
              <div style={{ fontSize: 11, color: 'var(--fg-subtle)' }}>Owner · Synk</div>
            </div>
            <button
              onClick={onLogout}
              title="Logout"
              style={{
                background: 'transparent',
                border: 0,
                color: 'var(--fg-subtle)',
                fontSize: 11,
                fontWeight: 500,
                padding: '4px 6px',
                borderRadius: 6,
                cursor: 'pointer',
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="flex flex-col min-w-0">
        {/* Topbar */}
        <header
          className="sticky top-0 z-10 flex items-center gap-4 px-7"
          style={{
            height: 60,
            borderBottom: '1px solid var(--border)',
            background: 'var(--bg)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <div style={{ fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em' }}>
            AutoParts Invoice Manager
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-2.5">
            <button
              className="grid place-items-center"
              style={{
                width: 34,
                height: 34,
                borderRadius: 8,
                background: 'transparent',
                border: '1px solid transparent',
                color: 'var(--fg-muted)',
              }}
              title="Notifications"
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'var(--surface-hover)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'transparent';
              }}
            >
              {Ico.bell}
            </button>
            <Link to="/invoices/new" className="btn-primary" style={{ padding: '6px 12px', fontSize: 13 }}>
              + New invoice
            </Link>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1" style={{ padding: '32px 32px 60px', maxWidth: 1400, width: '100%' }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}