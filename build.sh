#!/bin/bash
set -e  # Exit on any error

echo "🔨 Building LBM Arena for production..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if database is accessible
echo "🔍 Checking database connection..."
python -c "
try:
    from app.core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database connection warning: {e}')
    print('Database setup will be attempted at runtime')
"

# Only run database setup if we can connect
echo "🗄️  Setting up database (if needed)..."
python -c "
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.database import engine, Base
    from app.models import player, game, move
    
    # Create tables if they don't exist (safe operation)
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables verified/created')
    
except Exception as e:
    print(f'⚠️  Database table creation will be done at runtime: {e}')
"

# Run safe database initialization (only adds data if DB is empty)
echo "📊 Initializing database data (only if empty)..."
python scripts/init_db_safe.py

echo "✅ Build completed successfully!"
