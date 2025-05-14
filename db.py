import psycopg2
from psycopg2 import pool

# Database configuration
DB_NAME = 'railway'
DB_USER = 'postgres'
DB_PASSWORD = 'lYHvrGIWEvlneKyJuPohebsjqbaXikuV'
DB_HOST = 'postgres.railway.internal'
DB_PORT = '5432'

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # minconn
    10,  # maxconn
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

def init_db():
    """Initialize the database and create necessary tables"""
    conn = connection_pool.getconn()
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
                    hostel_preference VARCHAR(10) DEFAULT 'boys',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

def save_user(user_id, username=None, first_name=None, last_name=None):
    """Save or update user information"""
    conn = connection_pool.getconn()
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
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        connection_pool.putconn(conn)

def update_notification_settings(user_id, auto_updates=None, hostel_preference=None):
    """Update user's notification settings"""
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            # First check if user exists
            cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cur.fetchone():
                print(f"User {user_id} not found, creating new user")  # Debug log
                # Create user if doesn't exist
                cur.execute("""
                    INSERT INTO users (user_id, hostel_preference, auto_updates)
                    VALUES (%s, %s, %s)
                """, (user_id, hostel_preference or 'boys', auto_updates or False))
            else:
                # Build update query based on provided parameters
                updates = []
                params = []
                if auto_updates is not None:
                    updates.append("auto_updates = %s")
                    params.append(auto_updates)
                if hostel_preference is not None:
                    updates.append("hostel_preference = %s")
                    params.append(hostel_preference)
                
                if updates:
                    query = f"""
                        UPDATE users 
                        SET {', '.join(updates)}
                        WHERE user_id = %s
                    """
                    params.append(user_id)
                    print(f"Executing query: {query} with params: {params}")  # Debug log
                    cur.execute(query, params)
            
            conn.commit()
            print(f"Successfully updated settings for user {user_id}")  # Debug log
            
            # Verify the update
            cur.execute("SELECT hostel_preference, auto_updates FROM users WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            print(f"Verified settings after update - hostel: {result[0]}, auto_updates: {result[1]}")  # Debug log
            return True
    except Exception as e:
        print(f"Error updating notification settings: {e}")
        conn.rollback()  # Rollback on error
        return False
    finally:
        connection_pool.putconn(conn)

def get_user_settings(user_id):
    """Get user's notification settings"""
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT auto_updates, hostel_preference 
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            result = cur.fetchone()
            if result:
                return (15, result[0], result[1])
            else:
                # Create new user with default settings if not found
                cur.execute("""
                    INSERT INTO users (user_id, auto_updates, hostel_preference)
                    VALUES (%s, %s, %s)
                """, (user_id, False, 'boys'))
                conn.commit()
                return (15, False, 'boys')
    except Exception as e:
        print(f"Error getting user settings: {e}")
        return None
    finally:
        connection_pool.putconn(conn) 