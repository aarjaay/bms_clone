import psycopg2

# Define connection parameters
DB_NAME = "bms_db"
DB_USER = "postgres"  # Default PostgreSQL user
DB_PASSWORD = "mysecretpassword"  # Use the password you set in Docker
DB_HOST = "localhost"  # Or use "bmsdb" if running from another container
DB_PORT = "5432"  # Default PostgreSQL port

try:
    # Attempt to connect
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("✅ Successfully connected to the database!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
