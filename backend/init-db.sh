#!/bin/bash
set -e  # Exit immediately if a command fails

# Function to check if a database exists
database_exists() {
    psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$1'" | grep -q 1
}

# Create coin_db if it does not exist
if ! database_exists "coin_db"; then
    echo "🛠 Creating database: coin_db..."
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE coin_db;"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE coin_db TO $POSTGRES_USER;"
else
    echo "✅ Database coin_db already exists."
fi

# Create test_coin_db if it does not exist
if ! database_exists "test_coin_db"; then
    echo "🛠 Creating database: test_coin_db..."
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE test_coin_db;"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE test_coin_db TO $POSTGRES_USER;"
else
    echo "✅ Database test_coin_db already exists."
fi

echo "✅ Databases checked and created if needed."
