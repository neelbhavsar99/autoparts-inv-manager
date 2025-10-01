/**
 * Customers management page
 */
import { useState, useEffect } from 'react';
import { customersAPI } from '../services/api';
import { Customer } from '../types';
import Toast from '../components/Toast';

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
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
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingCustomer({
      name: '',
      address: '',
      phone: '',
      email: '',
    });
    setShowModal(true);
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this customer?')) {
      return;
    }

    try {
      await customersAPI.delete(id);
      setToast({ message: 'Customer deleted successfully', type: 'success' });
      loadCustomers();
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to delete customer', type: 'error' });
    }
  };

  const handleSave = async (customer: Customer) => {
    try {
      if (customer.id) {
        await customersAPI.update(customer.id, customer);
        setToast({ message: 'Customer updated successfully', type: 'success' });
      } else {
        await customersAPI.create(customer);
        setToast({ message: 'Customer created successfully', type: 'success' });
      }
      setShowModal(false);
      setEditingCustomer(null);
      loadCustomers();
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to save customer', type: 'error' });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

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
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600 mt-1">Manage your customer database</p>
        </div>
        <button onClick={handleAdd} className="btn-primary">
          + Add Customer
        </button>
      </div>

      {customers.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">👥</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No customers yet</h3>
          <p className="text-gray-600 mb-4">
            Start by adding your first customer
          </p>
          <button onClick={handleAdd} className="btn-primary">
            + Add Customer
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="table-base">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Name</th>
                <th className="table-header-cell">Address</th>
                <th className="table-header-cell">Phone</th>
                <th className="table-header-cell">Email</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td className="table-cell font-medium">{customer.name}</td>
                  <td className="table-cell text-gray-600">{customer.address || '-'}</td>
                  <td className="table-cell text-gray-600">{customer.phone || '-'}</td>
                  <td className="table-cell text-gray-600">{customer.email || '-'}</td>
                  <td className="table-cell">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(customer)}
                        className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(customer.id!)}
                        className="text-red-600 hover:text-red-700 font-medium text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && editingCustomer && (
        <CustomerModal
          customer={editingCustomer}
          onSave={handleSave}
          onClose={() => {
            setShowModal(false);
            setEditingCustomer(null);
          }}
        />
      )}
    </div>
  );
}

// Customer Modal Component
interface CustomerModalProps {
  customer: Customer;
  onSave: (customer: Customer) => void;
  onClose: () => void;
}

function CustomerModal({ customer, onSave, onClose }: CustomerModalProps) {
  const [formData, setFormData] = useState<Customer>(customer);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Customer name is required');
      return;
    }
    onSave(formData);
  };

  const handleChange = (field: keyof Customer, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {customer.id ? 'Edit Customer' : 'Add Customer'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="input-field"
                placeholder="John's Auto Repair"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address
              </label>
              <textarea
                value={formData.address}
                onChange={(e) => handleChange('address', e.target.value)}
                className="input-field"
                rows={3}
                placeholder="456 Oak Avenue&#10;Springfield, IL 62702"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  className="input-field"
                  placeholder="(555) 234-5678"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="input-field"
                  placeholder="john@johnsauto.com"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-4 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Save Customer
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
