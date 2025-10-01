/**
 * Create invoice page with dynamic line items
 */
import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { customersAPI, invoicesAPI } from '../services/api';
import { Customer, InvoiceLineItem } from '../types';
import Toast from '../components/Toast';

export default function CreateInvoice() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(null);
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().split('T')[0]);
  const [lineItems, setLineItems] = useState<InvoiceLineItem[]>([
    { product_name: '', part_number: '', quantity: 1, unit_price: 0 },
  ]);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const data = await customersAPI.list();
      setCustomers(data);
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to load customers', type: 'error' });
    }
  };

  const addLineItem = () => {
    setLineItems([
      ...lineItems,
      { product_name: '', part_number: '', quantity: 1, unit_price: 0 },
    ]);
  };

  const removeLineItem = (index: number) => {
    if (lineItems.length === 1) {
      setToast({ message: 'At least one line item is required', type: 'error' });
      return;
    }
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const updateLineItem = (index: number, field: keyof InvoiceLineItem, value: string | number) => {
    const updated = [...lineItems];
    updated[index] = { ...updated[index], [field]: value };
    setLineItems(updated);
  };

  const calculateSubtotal = () => {
    return lineItems.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  };

  const calculateTax = () => {
    return calculateSubtotal() * 0.0825; // 8.25% fixed
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    if (!selectedCustomerId) {
      setToast({ message: 'Please select a customer', type: 'error' });
      return;
    }

    const validItems = lineItems.filter(
      (item) => item.product_name.trim() && item.quantity > 0 && item.unit_price >= 0
    );

    if (validItems.length === 0) {
      setToast({ message: 'Please add at least one valid line item', type: 'error' });
      return;
    }

    setLoading(true);

    try {
      const invoiceData = {
        customer_id: selectedCustomerId,
        invoice_date: invoiceDate,
        line_items: validItems,
        notes: notes.trim(),
        status: 'unpaid',
      };

      const response = await invoicesAPI.create(invoiceData);
      setToast({ message: 'Invoice created successfully', type: 'success' });

      // Redirect to invoice view after short delay
      setTimeout(() => {
        navigate(`/invoices/${response.data.id}`);
      }, 1000);
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to create invoice', type: 'error' });
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Create Invoice</h1>
        <p className="text-gray-600 mt-1">Generate a new invoice for car parts</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Invoice Info */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Invoice Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedCustomerId || ''}
                onChange={(e) => setSelectedCustomerId(Number(e.target.value))}
                className="input-field"
                required
              >
                <option value="">Select a customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                  </option>
                ))}
              </select>
              {customers.length === 0 && (
                <p className="text-sm text-gray-500 mt-1">
                  No customers found.{' '}
                  <button
                    type="button"
                    onClick={() => navigate('/customers')}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Add a customer first
                  </button>
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Invoice Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={invoiceDate}
                onChange={(e) => setInvoiceDate(e.target.value)}
                className="input-field"
                required
              />
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
            <button
              type="button"
              onClick={addLineItem}
              className="btn-secondary text-sm"
            >
              + Add Item
            </button>
          </div>

          <div className="space-y-4">
            {lineItems.map((item, index) => (
              <div
                key={index}
                className="grid grid-cols-12 gap-4 items-start p-4 bg-gray-50 rounded-lg"
              >
                <div className="col-span-12 md:col-span-4">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Product Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={item.product_name}
                    onChange={(e) => updateLineItem(index, 'product_name', e.target.value)}
                    className="input-field text-sm"
                    placeholder="Brake Pads"
                    required
                  />
                </div>

                <div className="col-span-12 md:col-span-2">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Part Number
                  </label>
                  <input
                    type="text"
                    value={item.part_number}
                    onChange={(e) => updateLineItem(index, 'part_number', e.target.value)}
                    className="input-field text-sm"
                    placeholder="BP-1234"
                  />
                </div>

                <div className="col-span-6 md:col-span-2">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Quantity <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateLineItem(index, 'quantity', Number(e.target.value))}
                    className="input-field text-sm"
                    min="1"
                    required
                  />
                </div>

                <div className="col-span-6 md:col-span-2">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Unit Price <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={item.unit_price}
                    onChange={(e) => updateLineItem(index, 'unit_price', Number(e.target.value))}
                    className="input-field text-sm"
                    min="0"
                    step="0.01"
                    required
                  />
                </div>

                <div className="col-span-10 md:col-span-1">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Total
                  </label>
                  <div className="text-sm font-medium text-gray-900 py-2">
                    ${(item.quantity * item.unit_price).toFixed(2)}
                  </div>
                </div>

                <div className="col-span-2 md:col-span-1">
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    &nbsp;
                  </label>
                  <button
                    type="button"
                    onClick={() => removeLineItem(index)}
                    className="text-red-600 hover:text-red-700 font-medium text-sm py-2"
                    disabled={lineItems.length === 1}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Totals */}
          <div className="mt-6 border-t pt-4">
            <div className="flex justify-end">
              <div className="w-64 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="font-medium">${calculateSubtotal().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax (8.25%):</span>
                  <span className="font-medium">${calculateTax().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total:</span>
                  <span className="text-primary-600">${calculateTotal().toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes (Optional)</h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="input-field"
            rows={4}
            placeholder="Additional notes or payment terms..."
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/invoices')}
            className="btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !selectedCustomerId}
          >
            {loading ? 'Creating...' : 'Create Invoice'}
          </button>
        </div>
      </form>
    </div>
  );
}
