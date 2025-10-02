# Manual seed endpoint (for debugging)
@app.route('/api/seed-db', methods=['POST', 'GET'])
def manual_seed():
    """Manually seed the database"""
    try:
        # Ensure tables exist first
        init_db()
        from seed import seed_database
        seed_database()
        return jsonify({'message': 'Database seeded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
