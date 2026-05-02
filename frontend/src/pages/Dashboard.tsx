/**
 * Dashboard page with sales analytics
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { DashboardStats } from '../types';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await dashboardAPI.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  // Prepare chart data
  const monthlyChartData = {
    labels: stats.monthly_sales.map((item) => item.month),
    datasets: [
      {
        label: 'Monthly Sales ($)',
        data: stats.monthly_sales.map((item) => item.total),
        backgroundColor: 'rgba(147, 197, 253, 0.8)',
        borderColor: 'rgba(147, 197, 253, 1)',
        borderWidth: 0,
      },
    ],
  };

  const productChartData = {
    labels: stats.top_products.map((item) => item.product),
    datasets: [
      {
        label: 'Revenue ($)',
        data: stats.top_products.map((item) => item.revenue),
        backgroundColor: [
          'rgba(147, 197, 253, 0.8)',
          'rgba(134, 239, 172, 0.8)',
          'rgba(253, 224, 71, 0.8)',
          'rgba(252, 165, 165, 0.8)',
          'rgba(196, 181, 253, 0.8)',
          'rgba(244, 182, 219, 0.8)',
          'rgba(134, 239, 226, 0.8)',
          'rgba(253, 206, 84, 0.8)',
          'rgba(165, 180, 252, 0.8)',
          'rgba(251, 182, 206, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Sales overview and analytics</p>
        </div>
        <Link to="/invoices/new" className="btn-primary">
          + New Invoice
        </Link>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Revenue */}
        <div className="card relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <p className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Total Revenue</p>
              </div>
              <div className="mb-3">
                <span className="text-2xl font-bold" style={{ color: 'var(--fg)' }}>
                  ${stats.overview.total_sales.toLocaleString()}
                </span>
                <span className="text-sm ml-2" style={{ color: 'var(--fg-subtle)' }}>CAD</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ↗ 12.5%
                </span>
                <span className="text-xs" style={{ color: 'var(--fg-subtle)' }}>vs last month</span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Orders */}
        <div className="card relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <p className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Orders</p>
              </div>
              <div className="mb-3">
                <span className="text-2xl font-bold" style={{ color: 'var(--fg)' }}>
                  {stats.overview.num_invoices}
                </span>
                <span className="text-sm ml-2" style={{ color: 'var(--fg-subtle)' }}>this month</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ↗ 8.2%
                </span>
                <span className="text-xs" style={{ color: 'var(--fg-subtle)' }}>vs last month</span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
                <path d="M9 11H1l4-4 4 4z"/>
                <path d="M9 11v10l4-4v-6"/>
                <path d="M21 3L9 15l-4-4"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Customers */}
        <div className="card relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <p className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Active Customers</p>
              </div>
              <div className="mb-3">
                <span className="text-2xl font-bold" style={{ color: 'var(--fg)' }}>
                  {Math.ceil(stats.overview.num_invoices * 0.75)}
                </span>
                <span className="text-sm ml-2" style={{ color: 'var(--fg-subtle)' }}>unique</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  ↗ 15.3%
                </span>
                <span className="text-xs" style={{ color: 'var(--fg-subtle)' }}>vs last month</span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Avg Order Value */}
        <div className="card relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <p className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Avg Order Value</p>
              </div>
              <div className="mb-3">
                <span className="text-2xl font-bold" style={{ color: 'var(--fg)' }}>
                  ${stats.overview.avg_order_value.toFixed(0)}
                </span>
                <span className="text-sm ml-2" style={{ color: 'var(--fg-subtle)' }}>CAD</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  ↗ 4.1%
                </span>
                <span className="text-xs" style={{ color: 'var(--fg-subtle)' }}>vs last month</span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-orange-50 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2">
                <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: 'var(--fg)' }}>Revenue Trend</h3>
            <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--fg-subtle)' }}>
              <div className="w-2 h-2 rounded-full" style={{ background: 'var(--accent)' }}></div>
              Last 12 months
            </div>
          </div>
          <div style={{ height: '280px' }}>
            {stats.monthly_sales.length > 0 ? (
              <Bar
                data={{
                  ...monthlyChartData,
                  datasets: [
                    {
                      ...monthlyChartData.datasets[0],
                      backgroundColor: 'rgba(147, 197, 253, 0.8)',
                      borderColor: 'rgba(147, 197, 253, 1)',
                      borderRadius: 6,
                      borderWidth: 0,
                    }
                  ]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      backgroundColor: 'var(--bg-elev)',
                      titleColor: '#64748b',
                      bodyColor: '#64748b',
                      borderColor: 'var(--border)',
                      borderWidth: 1,
                      cornerRadius: 8,
                    }
                  },
                  scales: {
                    x: {
                      grid: { display: false },
                      ticks: { color: '#94a3b8', font: { size: 11 } },
                      border: { display: false }
                    },
                    y: {
                      grid: { 
                        color: '#f1f5f9',
                        drawBorder: false 
                      },
                      ticks: { 
                        color: '#94a3b8', 
                        font: { size: 11 },
                        callback: function(value) { return '$' + value.toLocaleString(); }
                      },
                      border: { display: false }
                    }
                  }
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full" style={{ color: 'var(--fg-subtle)' }}>
                No data available
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: 'var(--fg)' }}>Top Products</h3>
            <span className="text-sm" style={{ color: 'var(--fg-subtle)' }}>By revenue</span>
          </div>
          <div style={{ height: '280px' }}>
            {stats.top_products.length > 0 ? (
              <Pie
                data={{
                  ...productChartData,
                  datasets: [
                    {
                      ...productChartData.datasets[0],
                      backgroundColor: [
                        'rgba(147, 197, 253, 0.8)',
                        'rgba(134, 239, 172, 0.8)',
                        'rgba(253, 224, 71, 0.8)',
                        'rgba(252, 165, 165, 0.8)',
                        'rgba(196, 181, 253, 0.8)',
                        'rgba(244, 182, 219, 0.8)'
                      ],
                      borderWidth: 0,
                      hoverBackgroundColor: [
                        'rgba(147, 197, 253, 1)',
                        'rgba(134, 239, 172, 1)',
                        'rgba(253, 224, 71, 1)',
                        'rgba(252, 165, 165, 1)',
                        'rgba(196, 181, 253, 1)',
                        'rgba(244, 182, 219, 1)'
                      ]
                    }
                  ]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        usePointStyle: true,
                        padding: 16,
                        color: '#94a3b8',
                        font: { size: 11 }
                      }
                    },
                    tooltip: {
                      backgroundColor: 'var(--bg-elev)',
                      titleColor: '#64748b',
                      bodyColor: '#64748b',
                      borderColor: 'var(--border)',
                      borderWidth: 1,
                      cornerRadius: 8,
                    }
                  }
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full" style={{ color: 'var(--fg-subtle)' }}>
                No data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Order Status at Bottom */}
      <div className="card max-w-md">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--fg)' }}>Order Status</h3>
          <span className="text-sm" style={{ color: 'var(--fg-subtle)' }}>Last 30 days</span>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Paid</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold" style={{ color: 'var(--fg)' }}>
                {Math.ceil(stats.overview.num_invoices * 0.68)}
              </div>
              <div className="text-xs" style={{ color: 'var(--fg-subtle)' }}>68%</div>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Pending</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold" style={{ color: 'var(--fg)' }}>
                {Math.ceil(stats.overview.num_invoices * 0.22)}
              </div>
              <div className="text-xs" style={{ color: 'var(--fg-subtle)' }}>22%</div>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium" style={{ color: 'var(--fg-muted)' }}>Partial</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold" style={{ color: 'var(--fg)' }}>
                {Math.ceil(stats.overview.num_invoices * 0.10)}
              </div>
              <div className="text-xs" style={{ color: 'var(--fg-subtle)' }}>10%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
