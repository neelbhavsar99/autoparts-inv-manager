/**
 * Business settings page
 */
import { useState, useEffect, FormEvent } from 'react';
import { businessAPI } from '../services/api';
import { BusinessInfo } from '../types';
import Toast from '../components/Toast';

export default function BusinessSettings() {
  const [formData, setFormData] = useState<BusinessInfo>({
    company_name: '',
    address: '',
    phone: '',
    email: '',
    tax_id: '',
    logo_url: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadBusinessInfo();
  }, []);

  const loadBusinessInfo = async () => {
    try {
      const data = await businessAPI.get();
      setFormData(data);
    } catch (err: any) {
      // If not found, keep empty form
      if (!err.message.includes('404')) {
        setToast({ message: err.message || 'Failed to load business info', type: 'error' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.company_name.trim() || !formData.address.trim()) {
      setToast({ message: 'Company name and address are required', type: 'error' });
      return;
    }

    setSaving(true);

    try {
      await businessAPI.update(formData);
      setToast({ message: 'Business settings saved successfully', type: 'success' });
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to save settings', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof BusinessInfo, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Business Settings</h1>
        <p className="text-gray-600 mt-1">
          Configure your company information for invoices
        </p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-2">
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              id="company_name"
              type="text"
              value={formData.company_name}
              onChange={(e) => handleChange('company_name', e.target.value)}
              className="input-field"
              placeholder="AutoParts Pro Shop"
              required
            />
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
              Address <span className="text-red-500">*</span>
            </label>
            <textarea
              id="address"
              value={formData.address}
              onChange={(e) => handleChange('address', e.target.value)}
              className="input-field"
              rows={3}
              placeholder="123 Main Street&#10;Springfield, IL 62701"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone
              </label>
              <input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                className="input-field"
                placeholder="(555) 123-4567"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className="input-field"
                placeholder="contact@autoparts.com"
              />
            </div>
          </div>

          <div>
            <label htmlFor="tax_id" className="block text-sm font-medium text-gray-700 mb-2">
              Tax ID / EIN
            </label>
            <input
              id="tax_id"
              type="text"
              value={formData.tax_id}
              onChange={(e) => handleChange('tax_id', e.target.value)}
              className="input-field"
              placeholder="12-3456789"
            />
          </div>

          <div>
            <label htmlFor="logo_url" className="block text-sm font-medium text-gray-700 mb-2">
              Logo URL (optional)
            </label>
            <input
              id="logo_url"
              type="url"
              value={formData.logo_url}
              onChange={(e) => handleChange('logo_url', e.target.value)}
              className="input-field"
              placeholder="https://example.com/logo.png"
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter a URL to your company logo (will be displayed on invoices)
            </p>
          </div>

          <div className="flex justify-end space-x-4 pt-4">
            <button
              type="button"
              onClick={loadBusinessInfo}
              className="btn-secondary"
              disabled={saving}
            >
              Reset
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>

      {/* Info box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">ℹ️</span>
          <div>
            <h3 className="font-medium text-blue-900">About Business Settings</h3>
            <p className="text-sm text-blue-700 mt-1">
              This information will be automatically included in all your invoices. Make sure
              to keep it up to date for professional-looking documents.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
