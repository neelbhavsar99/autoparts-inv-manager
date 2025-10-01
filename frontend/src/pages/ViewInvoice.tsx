/**
 * View invoice details page
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { invoicesAPI } from '../services/api';
import { format } from 'date-fns';
import Toast from '../components/Toast';

interface InvoiceDetail {
  id: number;
  invoice_number: string;
  invoice_date: string;
  customer: {
    id: number;
    name: string;
    address: string;
    phone: string;
    email: string;
  };
  line_items: Array<{
    id: number;
    product_name: string;
    part_number: string;
    quantity: number;
    unit_price: number;
    line_total: number;
  }>;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;
  status: string;
  notes: string;
}

export default function ViewInvoice() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    if (id) {
      loadInvoice(Number(id));
    }
  }, [id]);

  const loadInvoice = async (invoiceId: number) => {
    try {
      const data = await invoicesAPI.get(invoiceId);
      setInvoice(data);
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to load invoice', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!invoice) return;
    try {
      await invoicesAPI.downloadPDF(invoice.id);
      setToast({ message: 'PDF downloaded successfully', type: 'success' });
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to download PDF', type: 'error' });
    }
  };

  const handleUpdateStatus = async (status: string) => {
    if (!invoice) return;
    try {
      await invoicesAPI.update(invoice.id, { status });
      setToast({ message: 'Invoice status updated', type: 'success' });
      loadInvoice(invoice.id);
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to update status', type: 'error' });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="card text-center py-12">
        <div className="text-6xl mb-4">❌</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Invoice not found</h3>
        <Link to="/invoices" className="btn-primary">
          Back to Invoices
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Invoice {invoice.invoice_number}
          </h1>
          <p className="text-gray-600 mt-1">
            {format(new Date(invoice.invoice_date), 'MMMM d, yyyy')}
          </p>
        </div>
        <div className="flex space-x-3">
          <button onClick={handleDownloadPDF} className="btn-primary">
            📥 Download PDF
          </button>
          {invoice.status === 'unpaid' && (
            <button
              onClick={() => handleUpdateStatus('paid')}
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg"
            >
              Mark as Paid
            </button>
          )}
        </div>
      </div>

      {/* Status Badge */}
      <div className="mb-6">
        <span
          className={`inline-flex px-4 py-2 text-sm font-semibold rounded-full ${
            invoice.status === 'paid'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {invoice.status.toUpperCase()}
        </span>
      </div>

      {/* Customer Info */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Bill To</h2>
        <div className="text-gray-700">
          <p className="font-medium text-gray-900">{invoice.customer.name}</p>
          {invoice.customer.address && (
            <p className="mt-1 whitespace-pre-line">{invoice.customer.address}</p>
          )}
          {invoice.customer.phone && (
            <p className="mt-1">Phone: {invoice.customer.phone}</p>
          )}
          {invoice.customer.email && (
            <p className="mt-1">Email: {invoice.customer.email}</p>
          )}
        </div>
      </div>

      {/* Line Items */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Items</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Product
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Part #
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Qty
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Unit Price
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoice.line_items.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {item.product_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {item.part_number || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900 text-center">
                    {item.quantity}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900 text-right">
                    ${item.unit_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 text-right">
                    ${item.line_total.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="mt-6 border-t pt-4">
          <div className="flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-medium">${invoice.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Tax ({invoice.tax_rate}%):</span>
                <span className="font-medium">${invoice.tax_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-xl font-bold border-t pt-2">
                <span>Total:</span>
                <span className="text-primary-600">${invoice.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Notes */}
      {invoice.notes && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
          <p className="text-gray-700 whitespace-pre-line">{invoice.notes}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <button
          onClick={() => navigate('/invoices')}
          className="btn-secondary"
        >
          ← Back to Invoices
        </button>
        <div className="flex space-x-3">
          {invoice.status === 'paid' && (
            <button
              onClick={() => handleUpdateStatus('unpaid')}
              className="bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg"
            >
              Mark as Unpaid
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
