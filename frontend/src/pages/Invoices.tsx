/**
 * Invoices list page with search/filter
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { invoicesAPI } from '../services/api';
import { format } from 'date-fns';
import Toast from '../components/Toast';

interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  customer_name: string;
  customer_id: number;
  total: number;
  status: string;
  notes: string;
}

export default function Invoices() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    status: '',
  });
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadInvoices();
  }, [filters]);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;
      if (filters.status) params.status = filters.status;

      const data = await invoicesAPI.list(params);
      setInvoices(data.data || []);
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to load invoices', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (id: number) => {
    try {
      await invoicesAPI.downloadPDF(id);
      setToast({ message: 'PDF downloaded successfully', type: 'success' });
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to download PDF', type: 'error' });
    }
  };

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await invoicesAPI.update(id, { status });
      setToast({ message: 'Invoice status updated', type: 'success' });
      loadInvoices();
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to update status', type: 'error' });
    }
  };

  const clearFilters = () => {
    setFilters({ start_date: '', end_date: '', status: '' });
  };

  return (
    <div>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-600 mt-1">View and manage all invoices</p>
        </div>
        <Link to="/invoices/new" className="btn-primary">
          + Create Invoice
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <h3 className="font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="input-field"
            >
              <option value="">All</option>
              <option value="paid">Paid</option>
              <option value="unpaid">Unpaid</option>
            </select>
          </div>

          <div className="flex items-end">
            <button onClick={clearFilters} className="btn-secondary w-full">
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Invoices Table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="spinner"></div>
        </div>
      ) : invoices.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
          <p className="text-gray-600 mb-4">
            {filters.start_date || filters.end_date || filters.status
              ? 'Try adjusting your filters'
              : 'Create your first invoice to get started'}
          </p>
          <Link to="/invoices/new" className="btn-primary">
            + Create Invoice
          </Link>
        </div>
      ) : (
        <div className="table-container">
          <table className="table-base">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Invoice #</th>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Customer</th>
                <th className="table-header-cell">Total</th>
                <th className="table-header-cell">Status</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {invoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="table-cell font-medium">
                    <Link
                      to={`/invoices/${invoice.id}`}
                      className="text-primary-600 hover:text-primary-700"
                    >
                      {invoice.invoice_number}
                    </Link>
                  </td>
                  <td className="table-cell text-gray-600">
                    {format(new Date(invoice.invoice_date), 'MMM d, yyyy')}
                  </td>
                  <td className="table-cell">{invoice.customer_name}</td>
                  <td className="table-cell font-medium">
                    ${invoice.total.toFixed(2)}
                  </td>
                  <td className="table-cell">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        invoice.status === 'paid'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {invoice.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="table-cell">
                    <div className="flex space-x-2">
                      <Link
                        to={`/invoices/${invoice.id}`}
                        className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => handleDownloadPDF(invoice.id)}
                        className="text-green-600 hover:text-green-700 font-medium text-sm"
                      >
                        PDF
                      </button>
                      {invoice.status === 'unpaid' && (
                        <button
                          onClick={() => handleUpdateStatus(invoice.id, 'paid')}
                          className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                        >
                          Mark Paid
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary */}
      {invoices.length > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <p className="text-sm text-gray-600">Total Invoices</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{invoices.length}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Total Amount</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              ${invoices.reduce((sum, inv) => sum + inv.total, 0).toFixed(2)}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Unpaid</p>
            <p className="text-2xl font-bold text-yellow-600 mt-1">
              ${invoices
                .filter((inv) => inv.status === 'unpaid')
                .reduce((sum, inv) => sum + inv.total, 0)
                .toFixed(2)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
