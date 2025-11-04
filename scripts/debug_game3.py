"""
Debug script to check Game 3 completion status for all teams.
Use this to diagnose why Game 3 might show as completed incorrectly.
"""

from database import ZukunftstagDatabase

def debug_game3_status():
    """Check Game 3 data for all teams in all sessions."""
    
    db = ZukunftstagDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("GAME 3 (Memory) DEBUG REPORT")
    print("="*80 + "\n")
    
    # Get all sessions
    cursor.execute("SELECT session_id, session_name, is_active FROM sessions ORDER BY session_id")
    sessions = cursor.fetchall()
    
    for session_id, session_name, is_active in sessions:
        active_marker = " (ACTIVE)" if is_active else ""
        print(f"\n📋 Session: {session_name} ({session_id}){active_marker}")
        print("-" * 80)
        
        # Get all teams in this session
        cursor.execute("SELECT team_name FROM teams WHERE session_id = ?", (session_id,))
        teams = cursor.fetchall()
        
        if not teams:
            print("  ℹ️  No teams registered in this session\n")
            continue
        
        for (team_name,) in teams:
            # Count game3 rounds for this team
            cursor.execute("""
                SELECT COUNT(*), 
                       SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count
                FROM game3_memory 
                WHERE team_name = ? AND session_id = ?
            """, (team_name, session_id))
            
            result = cursor.fetchone()
            total_rounds = result[0] if result[0] else 0
            correct_count = result[1] if result[1] else 0
            
            # Check progress status
            progress = db.get_team_progress(team_name)
            is_complete = progress.get('game3', False)
            
            if total_rounds == 0:
                status = "❌ Not started"
            elif total_rounds < 5:
                status = f"🟡 In progress ({total_rounds}/5 rounds)"
            elif total_rounds == 5:
                status = f"✅ Complete ({correct_count}/5 correct)"
            else:
                status = f"⚠️  ERROR: {total_rounds} rounds (should be 5!)"
            
            completion_check = "✅" if is_complete else "❌"
            print(f"  {team_name:20s} | {status:35s} | Progress check: {completion_check}")
        
        print()
    
    # Check for orphaned data (game3 data without team registration)
    print("\n🔍 Checking for orphaned Game 3 data...")
    print("-" * 80)
    
    cursor.execute("""
        SELECT DISTINCT g.team_name, g.session_id, COUNT(*) as round_count
        FROM game3_memory g
        LEFT JOIN teams t ON g.team_name = t.team_name AND g.session_id = t.session_id
        WHERE t.team_name IS NULL
        GROUP BY g.team_name, g.session_id
    """)
    
    orphaned = cursor.fetchall()
    
    if orphaned:
        print("\n⚠️  Found orphaned Game 3 data (no matching team registration):")
        for team_name, session_id, round_count in orphaned:
            print(f"  - {team_name} in {session_id}: {round_count} rounds")
        print("\n💡 Recommendation: Clear this data using Admin Dashboard → Session Management → Clear Session Data")
    else:
        print("  ✅ No orphaned data found\n")
    
    conn.close()
    
    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80 + "\n")

if __name__ == "__main__":
    debug_game3_status()
