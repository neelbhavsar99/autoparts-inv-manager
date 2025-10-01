/**
 * TypeScript type definitions
 */

export interface User {
  id: number;
  email: string;
  name: string;
}

export interface BusinessInfo {
  id?: number;
  company_name: string;
  address: string;
  phone: string;
  email: string;
  tax_id: string;
  logo_url: string;
}

export interface Customer {
  id?: number;
  name: string;
  address: string;
  phone: string;
  email: string;
  created_at?: string;
}

export interface InvoiceLineItem {
  id?: number;
  product_name: string;
  part_number: string;
  quantity: number;
  unit_price: number;
  line_total?: number;
}

export interface Invoice {
  id?: number;
  invoice_number?: string;
  invoice_date: string;
  customer_id?: number;
  customer?: Customer;
  line_items: InvoiceLineItem[];
  subtotal?: number;
  tax_rate?: number;
  tax_amount?: number;
  total?: number;
  status: 'paid' | 'unpaid';
  notes: string;
}

export interface DashboardStats {
  overview: {
    total_sales: number;
    num_invoices: number;
    avg_order_value: number;
    period: string;
  };
  monthly_sales: Array<{
    month: string;
    total: number;
  }>;
  top_products: Array<{
    product: string;
    revenue: number;
  }>;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
}
