/**
 * API client service
 * Handles all HTTP requests to Flask backend
 */

// Use environment variable or fallback to relative path
const API_BASE = import.meta.env.VITE_API_URL || '/api';

interface FetchOptions extends RequestInit {
  body?: any;
}

async function fetchAPI<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const config: RequestInit = {
    ...options,
    credentials: 'include', // Include cookies for session
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (options.body && typeof options.body !== 'string') {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    fetchAPI<{ message: string; user: any }>('/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  logout: () =>
    fetchAPI<{ message: string }>('/auth/logout', {
      method: 'POST',
    }),

  checkAuth: () =>
    fetchAPI<{ authenticated: boolean; user?: any }>('/auth/check'),

  getCurrentUser: () =>
    fetchAPI<any>('/auth/user'),
};

// Business API
export const businessAPI = {
  get: () => fetchAPI<any>('/business'),

  update: (data: any) =>
    fetchAPI<any>('/business', {
      method: 'PUT',
      body: data,
    }),
};

// Customers API
export const customersAPI = {
  list: () => fetchAPI<any[]>('/customers'),

  create: (data: any) =>
    fetchAPI<any>('/customers', {
      method: 'POST',
      body: data,
    }),

  update: (id: number, data: any) =>
    fetchAPI<any>(`/customers/${id}`, {
      method: 'PUT',
      body: data,
    }),

  delete: (id: number) =>
    fetchAPI<any>(`/customers/${id}`, {
      method: 'DELETE',
    }),
};

// Invoices API
export const invoicesAPI = {
  list: (params?: Record<string, any>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return fetchAPI<any>(`/invoices${query}`);
  },

  get: (id: number) => fetchAPI<any>(`/invoices/${id}`),

  create: (data: any) =>
    fetchAPI<any>('/invoices', {
      method: 'POST',
      body: data,
    }),

  update: (id: number, data: any) =>
    fetchAPI<any>(`/invoices/${id}`, {
      method: 'PUT',
      body: data,
    }),

  downloadPDF: (id: number) => {
    // Special handling for PDF download
    return fetch(`${API_BASE}/invoices/${id}/pdf`, {
      credentials: 'include',
    }).then(async (response) => {
      if (!response.ok) throw new Error('Failed to download PDF');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    });
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => fetchAPI<any>('/dashboard/stats'),
};
