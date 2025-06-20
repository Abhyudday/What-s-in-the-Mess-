import psycopg2
from psycopg2 import pool
import os

# Database configuration - using Railway PostgreSQL URL
# You can also set these as environment variables
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:lYHvrGIWEvlneKyJuPohebsjqbaXikuV@postgres.railway.internal:5432/railway')

# Parse the database URL
def parse_db_url(db_url):
    """Parse database URL to extract connection parameters"""
    try:
        # Remove postgresql:// prefix
        url = db_url.replace('postgresql://', '')
        # Split into user:pass@host:port/dbname
        auth_part, rest = url.split('@')
        user_pass = auth_part.split(':')
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        
        host_port_db = rest.split('/')
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        dbname = host_port_db[1] if len(host_port_db) > 1 else 'railway'
        
        return {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
    except Exception as e:
        print(f"Error parsing database URL: {e}")
        # Fallback to default values
        return {
            'dbname': 'railway',
            'user': 'postgres',
            'password': 'lYHvrGIWEvlneKyJuPohebsjqbaXikuV',
            'host': 'postgres.railway.internal',
            'port': '5432'
        }

# Parse database configuration
db_config = parse_db_url(DB_URL)

# Create a connection pool with error handling
try:
    connection_pool = pool.SimpleConnectionPool(
        1,  # minconn
        10,  # maxconn
        **db_config
    )
    print(f"Database connection pool created successfully")
except Exception as e:
    print(f"Failed to create database connection pool: {e}")
    connection_pool = None

def get_connection():
    """Get a database connection with error handling"""
    if connection_pool is None:
        raise Exception("Database connection pool not available")
    return connection_pool.getconn()

def init_db():
    """Initialize the database and create necessary tables"""
    if connection_pool is None:
        print("Database connection pool not available, skipping initialization")
        return
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create users table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    auto_updates BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

def save_user(user_id, username=None, first_name=None, last_name=None):
    """Save or update user information"""
    if connection_pool is None:
        print("Database not available, skipping user save")
        return
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, last_interaction)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_interaction = CURRENT_TIMESTAMP
            """, (user_id, username, first_name, last_name))
            conn.commit()
    except Exception as e:
        print(f"Error saving user: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

def get_all_users():
    """Get all user IDs from the database"""
    if connection_pool is None:
        print("Database not available, returning empty user list")
        return []
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        connection_pool.putconn(conn)

def update_notification_settings(user_id, auto_updates=None):
    """Update user's notification settings"""
    if connection_pool is None:
        print("Database not available, skipping notification settings update")
        return
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if auto_updates is not None:
                cur.execute("""
                    UPDATE users 
                    SET auto_updates = %s
                    WHERE user_id = %s
                """, (auto_updates, user_id))
                conn.commit()
    except Exception as e:
        print(f"Error updating notification settings: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

def get_user_settings(user_id):
    """Get user's notification settings"""
    if connection_pool is None:
        print("Database not available, returning default settings")
        return (15, False)
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT auto_updates 
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            result = cur.fetchone()
            return (15, result[0]) if result else (15, False)
    except Exception as e:
        print(f"Error getting user settings: {e}")
        return (15, False)
    finally:
        connection_pool.putconn(conn) 