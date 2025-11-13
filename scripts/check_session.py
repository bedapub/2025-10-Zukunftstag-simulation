"""
Quick script to check which session is currently active.
"""

import sqlite3

def check_active_session():
    """Check and display the current active session."""
    
    conn = sqlite3.connect('zukunftstag.db')
    cursor = conn.cursor()
    
    # Get all sessions
    cursor.execute("SELECT session_id, session_name, is_active FROM sessions ORDER BY session_id")
    sessions = cursor.fetchall()
    
    print("\n All Sessions:")
    print("-" * 60)
    for session_id, session_name, is_active in sessions:
        status = "ACTIVE" if is_active else "Inactive"
        print(f"{status} | {session_id:20} | {session_name}")
    print("-" * 60)
    
    # Get active session
    cursor.execute("SELECT session_id, session_name FROM sessions WHERE is_active = 1")
    active = cursor.fetchone()
    
    if active:
        print(f"\n Current Active Session: {active[0]} ({active[1]})")
    else:
        print("\n No active session found!")
    
    conn.close()

if __name__ == "__main__":
    check_active_session()
