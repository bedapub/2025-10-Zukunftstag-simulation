"""
Generate test data for development and testing.
This script populates the database with sample teams and game results.
Uses the same data generation approach as the Jupyter notebook.
"""

import sqlite3
import random
from datetime import datetime
import numpy as np
import config
from database import ZukunftstagDatabase

def generate_test_data():
    """Generate sample data for testing the application."""
    
    if not config.DEV_MODE or not config.DEV_GENERATE_TEST_DATA:
        print("Test data generation is disabled. Enable DEV_GENERATE_TEST_DATA in config.py")
        return
    
    print("🔧 Generating test data for development...")
    
    # Set random seeds for reproducibility (same as notebook)
    random.seed(1887)
    np.random.seed(1887)
    
    # Initialize database (creates all tables)
    db = ZukunftstagDatabase()
    
    # Connect to database
    conn = db.get_connection()
    conn = sqlite3.connect('zukunftstag.db')
    cursor = conn.cursor()
    
    # Read team names and parent/child names from files
    with open('data/team_namen.txt', 'r', encoding='utf-8') as f:
        team_lines = [line.strip() for line in f.readlines() if line.strip()]
        all_teams = dict(item.split(":") for item in team_lines)
    
    with open('data/kinder_vornamen.txt', 'r', encoding='utf-8') as f:
        child_names = [line.strip() for line in f.readlines() if line.strip()]
    
    with open('data/eltern_vornamen.txt', 'r', encoding='utf-8') as f:
        parent_names = [line.strip() for line in f.readlines() if line.strip()]
    
    # Generate test data for 29 teams (same as notebook)
    n_teams = 29
    team_names = sorted(random.sample(list(all_teams.keys()), n_teams))
    
    print(f"\n📋 Creating {n_teams} test teams...")
    
    # Generate heights using multivariate normal (correlated parent/child heights)
    # Same as notebook: mean=[180, 120], cov=[[15, 7], [7, 15]]
    # Round to integers (heights in cm should be whole numbers)
    heights = np.around(np.random.multivariate_normal(
        mean=[180, 120], 
        cov=[[15, 7], [7, 15]], 
        size=n_teams
    ).T).astype(int)
    parent_heights = heights[0]
    child_heights = heights[1]
    
    # Generate perimeter estimates (same as notebook)
    ground_truth = 28.0
    parent_perimeter = np.around(np.random.normal(ground_truth * 1.2, scale=5, size=n_teams), 2)
    child_perimeter = np.around(np.random.normal(ground_truth * 0.9, scale=8, size=n_teams), 1)
    
    # Generate clinical trial data (same as notebook)
    # Placebo: loc=0, scale=1
    # Medicine: loc=3, scale=1
    placebo_before = np.random.randint(5, 11, size=n_teams)
    placebo_effect = np.random.normal(loc=0, scale=1, size=n_teams).astype(int)
    placebo_after = np.clip(placebo_before - placebo_effect, a_min=0, a_max=10)
    
    medicine_before = np.random.randint(5, 11, size=n_teams)
    medicine_effect = np.random.normal(loc=3, scale=1, size=n_teams).astype(int)
    medicine_after = np.clip(medicine_before - medicine_effect, a_min=0, a_max=10)
    
    # Assign treatments (half get placebo, half get medicine for parent)
    parent_placebo_teams = random.sample(team_names, k=n_teams//2)
    
    for idx, team_name in enumerate(team_names):
        parent_name = random.choice(parent_names)
        child_name = random.choice(child_names)
        
        # Register team with test_session
        cursor.execute("""
            INSERT OR REPLACE INTO teams (team_name, parent_name, child_name, session_id, created_at)
            VALUES (?, ?, ?, 'test_session', ?)
        """, (team_name, parent_name, child_name, datetime.now().isoformat()))
        
        
        print(f"  ✅ {team_name}: {parent_name} & {child_name}")
        
        # Add Game 1 data (Heights) - using correlated heights from notebook
        cursor.execute("""
            INSERT OR REPLACE INTO game1_heights (team_name, parent_height, child_height, session_id, submitted_at)
            VALUES (?, ?, ?, 'test_session', ?)
        """, (team_name, int(parent_heights[idx]), int(child_heights[idx]), datetime.now().isoformat()))
        
        # Add Game 2 data (Perimeter) - using notebook distributions
        parent_est = float(parent_perimeter[idx])
        child_est = float(child_perimeter[idx])
        cursor.execute("""
            INSERT OR REPLACE INTO game2_perimeter (
                team_name, parent_estimate, child_estimate, 
                parent_delta, child_delta, parent_abs_delta, child_abs_delta,
                session_id, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'test_session', ?)
        """, (team_name, parent_est, child_est,
              parent_est - ground_truth, child_est - ground_truth,
              abs(parent_est - ground_truth), abs(child_est - ground_truth),
              datetime.now().isoformat()))
        
        # Add Game 3 data (Memory) - random 5 rounds
        for round_num in range(1, 6):
            correct = random.choice([True, False])
            correct_answer = f"molecule_{round_num}"
            team_answer = correct_answer if correct else f"wrong_{round_num}"
            cursor.execute("""
                INSERT INTO game3_memory (
                    team_name, round_number, correct_answer, team_answer, is_correct, session_id, submitted_at
                ) VALUES (?, ?, ?, ?, ?, 'test_session', ?)
            """, (team_name, round_num, correct_answer, team_answer, correct, datetime.now().isoformat()))
        
        # Add Game 4 data (Clinical Trial) - using notebook approach
        # Parent gets placebo or medicine based on assignment
        if team_name in parent_placebo_teams:
            parent_treatment = 'placebo'
            parent_before = int(placebo_before[idx])
            parent_after = int(placebo_after[idx])
            # Child gets opposite (medicine)
            child_treatment = 'medicine'
            child_before = int(medicine_before[idx])
            child_after = int(medicine_after[idx])
        else:
            parent_treatment = 'medicine'
            parent_before = int(medicine_before[idx])
            parent_after = int(medicine_after[idx])
            # Child gets opposite (placebo)
            child_treatment = 'placebo'
            child_before = int(placebo_before[idx])
            child_after = int(placebo_after[idx])
        
        cursor.execute("""
            INSERT OR REPLACE INTO game4_clinical (
                team_name, parent_treatment, child_treatment, 
                parent_before, parent_after, child_before, child_after,
                session_id, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'test_session', ?)
        """, (team_name, parent_treatment, child_treatment,
              parent_before, parent_after, child_before, child_after,
              datetime.now().isoformat()))
        
        # Add Feedback
        rating = random.randint(4, 5)
        favorite_game = random.choice(['game1', 'game2', 'game3', 'game4'])
        comments = random.choice([
            "Super Workshop! Hat viel Spaß gemacht.",
            "Sehr interessant und lehrreich.",
            "Tolle Spiele, gut erklärt.",
            "Hat uns beiden gefallen!",
            "Großartig! Sehr empfehlenswert.",
            ""
        ])
        
        cursor.execute("""
            INSERT OR REPLACE INTO feedback (
                team_name, overall_rating, favorite_game, comments, session_id, submitted_at
            ) VALUES (?, ?, ?, ?, 'test_session', ?)
        """, (team_name, rating, favorite_game, comments, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Test data generation complete!")
    print(f"   - {n_teams} teams registered")
    print(f"   - Heights: correlated parent/child (μ=[180,120]cm)")
    print(f"   - Perimeter: realistic estimates around {ground_truth}m")
    print(f"   - Clinical: placebo (μ=0) vs medicine (μ=3) effect")
    print(f"   - All game data and feedback populated")
    print(f"\n💡 Start the app with: streamlit run app.py")
    print(f"🔑 Admin password: {config.ADMIN_PASSWORD}\n")

if __name__ == "__main__":
    generate_test_data()
