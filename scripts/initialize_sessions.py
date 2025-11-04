"""
Initialize the three workshop sessions: morning, afternoon, and test.
Run this script once to set up the database with empty sessions.
"""

from database import ZukunftstagDatabase

def initialize_sessions():
    """Create the three main sessions for the workshop."""
    
    print("🔧 Initializing workshop sessions...")
    
    # Initialize database
    db = ZukunftstagDatabase()
    
    # Create three sessions
    sessions = [
        ("morning_session", "Morning Session (09:00 - 11:30)", False),
        ("afternoon_session", "Afternoon Session (13:30 - 16:00)", False),
        ("test_session", "Test Session (Development)", True)  # Default active
    ]
    
    # First, deactivate all sessions
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET is_active = 0")
    conn.commit()
    conn.close()
    
    for session_id, session_name, is_active in sessions:
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, session_name, is_active)
                VALUES (?, ?, ?)
            ''', (session_id, session_name, is_active))
            conn.commit()
            conn.close()
            
            active_marker = " (ACTIVE)" if is_active else ""
            print(f"  ✅ Created: {session_name}{active_marker}")
        except Exception as e:
            print(f"  ℹ️  {session_name} already exists")
    
    print("\n✅ Session initialization complete!")

if __name__ == "__main__":
    initialize_sessions()
