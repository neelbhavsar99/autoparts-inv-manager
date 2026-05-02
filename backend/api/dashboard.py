"""
Dashboard analytics API endpoints
"""
from flask import Blueprint, jsonify
from auth import token_required
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from models import get_db, Invoice, InvoiceLineItem

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats(user):
    """Get sales statistics for dashboard"""
    db = get_db()
    try:
        # Previous month stats
        now = datetime.utcnow()
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
        
        # Total sales last month
        last_month_invoices = db.query(Invoice).filter(
            Invoice.user_id == user.id,
            Invoice.date >= first_day_last_month,
            Invoice.date < first_day_this_month
        ).all()
        
        total_sales = sum(inv.total for inv in last_month_invoices)
        num_invoices = len(last_month_invoices)
        avg_order_value = round(total_sales / num_invoices, 2) if num_invoices > 0 else 0
        
        # Monthly sales for last 12 months (bar chart data)
        twelve_months_ago = now - timedelta(days=365)
        monthly_sales = db.query(
            extract('year', Invoice.date).label('year'),
            extract('month', Invoice.date).label('month'),
            func.sum(Invoice.total).label('total')
        ).filter(
            Invoice.user_id == user.id,
            Invoice.date >= twelve_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        monthly_chart_data = [{
            'month': f"{int(row.year)}-{int(row.month):02d}",
            'total': float(row.total)
        } for row in monthly_sales]
        
        # Top products by revenue (pie chart data)
        top_products = db.query(
            InvoiceLineItem.description,
            func.sum(InvoiceLineItem.total).label('revenue')
        ).join(Invoice).filter(
            Invoice.user_id == user.id,
            Invoice.date >= twelve_months_ago
        ).group_by(InvoiceLineItem.description).order_by(func.sum(InvoiceLineItem.total).desc()).limit(10).all()
        
        product_chart_data = [{
            'product': row.description,
            'revenue': float(row.revenue)
        } for row in top_products]
        
        return jsonify({
            'overview': {
                'total_sales': round(total_sales, 2),
                'num_invoices': num_invoices,
                'avg_order_value': avg_order_value,
                'period': 'Last Month'
            },
            'monthly_sales': monthly_chart_data,
            'top_products': product_chart_data
        }), 200
    finally:
        db.close()
