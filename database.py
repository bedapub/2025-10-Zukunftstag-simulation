"""
Database management for the Zukunftstag simulation application.
"""

import sqlite3
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import streamlit as st
from config import (
    RANDOM_SEED, TEAM_NAMES_FILE, CHILD_NAMES_FILE, 
    PARENT_NAMES_FILE, PERIMETER_GROUND_TRUTH
)

class ZukunftstagDatabase:
    """Database helper class for the Zukunftstag simulation app."""
    
    def __init__(self, db_path: str = "zukunftstag.db"):
        self.db_path = os.path.abspath(db_path)
        
        db_exists = os.path.exists(self.db_path)
        
        self.init_database()
        self.load_simulation_data()
        
        if not db_exists:
            print(f"Created new database at: {self.db_path}")
        else:
            print(f"Using existing database at: {self.db_path}")
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_name TEXT PRIMARY KEY,
                team_indication TEXT,
                parent_name TEXT,
                child_name TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Game 1: Heights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game1_heights (
                team_name TEXT PRIMARY KEY,
                parent_height REAL,
                child_height REAL,
                session_id TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams (team_name)
            )
        ''')
        
        # Game 2: Perimeter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game2_perimeter (
                team_name TEXT PRIMARY KEY,
                parent_estimate REAL,
                child_estimate REAL,
                parent_delta REAL,
                child_delta REAL,
                parent_abs_delta REAL,
                child_abs_delta REAL,
                session_id TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams (team_name)
            )
        ''')
        
        # Game 3: Memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game3_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                round_number INTEGER,
                correct_answer TEXT,
                team_answer TEXT,
                is_correct BOOLEAN,
                session_id TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams (team_name)
            )
        ''')
        
        # Game 4: Clinical Trial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game4_clinical (
                team_name TEXT PRIMARY KEY,
                parent_treatment TEXT,
                child_treatment TEXT,
                parent_before INTEGER,
                parent_after INTEGER,
                child_before INTEGER,
                child_after INTEGER,
                session_id TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams (team_name)
            )
        ''')
        
        # Feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                team_name TEXT PRIMARY KEY,
                overall_rating INTEGER,
                favorite_game TEXT,
                comments TEXT,
                session_id TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams (team_name)
            )
        ''')
        
        # Sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                session_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Secret data for clinical trial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secret_clinical_data (
                team_name TEXT PRIMARY KEY,
                parent_treatment TEXT,
                child_treatment TEXT,
                placebo_before_parent INTEGER,
                placebo_after_parent INTEGER,
                molecular_before_parent INTEGER,
                molecular_after_parent INTEGER,
                placebo_before_child INTEGER,
                placebo_after_child INTEGER,
                molecular_before_child INTEGER,
                molecular_after_child INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_default_sessions(self, cursor, conn):
        """Initialize the three default workshop sessions."""
        sessions = [
            ("morning_session", "Morning Session (09:00 - 11:30)", False),
            ("afternoon_session", "Afternoon Session (13:30 - 16:00)", False),
            ("test_session", "Test Session (Development)", True)
        ]
        
        for session_id, session_name, is_active in sessions:
            cursor.execute('''
                INSERT OR IGNORE INTO sessions (session_id, session_name, is_active)
                VALUES (?, ?, ?)
            ''', (session_id, session_name, is_active))
        
        conn.commit()
    
    def load_simulation_data(self):
        """Load and prepare simulation data from files."""
        try:
            # Load team names
            with open(TEAM_NAMES_FILE, 'r', encoding='utf-8') as f:
                team_lines = [line.strip() for line in f.readlines() if line.strip()]
                self.max_team_names = dict(item.split(":") for item in team_lines)
            
            # Load children names
            with open(CHILD_NAMES_FILE, 'r', encoding='utf-8') as f:
                self.child_names = [line.strip() for line in f.readlines() if line.strip()]
            
            # Load parent names
            with open(PARENT_NAMES_FILE, 'r', encoding='utf-8') as f:
                self.parent_names = [line.strip() for line in f.readlines() if line.strip()]
                
            # Prepare clinical trial simulation data
            self.prepare_clinical_simulation_data()
            
        except FileNotFoundError as e:
            st.error(f"Data file not found: {e}")
            # Fallback data
            self.max_team_names = {"Team Alpha": "Alpha Disease", "Team Beta": "Beta Disease"}
            self.child_names = ["Anna", "Ben", "Clara", "David"]
            self.parent_names = ["Andrea", "Beat", "Carla", "Daniel"]
    
    def prepare_clinical_simulation_data(self):
        """Prepare clinical trial simulation data."""
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)
        
        team_list = list(self.max_team_names.keys())
        n_teams = len(team_list)
        
        # Generate placebo data
        placebo_before = np.random.randint(5, 11, size=n_teams)
        placebo_effect = np.random.normal(loc=0, scale=1, size=n_teams).astype(int)
        placebo_after = np.clip(placebo_before - placebo_effect, a_min=0, a_max=10)
        
        # Generate molecular data
        molecular_before = np.random.randint(5, 11, size=n_teams)
        molecular_effect = np.random.normal(loc=3, scale=1, size=n_teams).astype(int)
        molecular_after = np.clip(molecular_before - molecular_effect, a_min=0, a_max=10)
        
        # Assign treatments
        parent_placebo_teams = random.sample(team_list, k=int(n_teams/2))
        
        # Store secret clinical data
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for i, team in enumerate(team_list):
            parent_treatment = "Placebo" if team in parent_placebo_teams else "Molekül"
            child_treatment = "Molekül" if team in parent_placebo_teams else "Placebo"
            
            cursor.execute('''
                INSERT OR REPLACE INTO secret_clinical_data 
                (team_name, parent_treatment, child_treatment,
                 placebo_before_parent, placebo_after_parent,
                 molecular_before_parent, molecular_after_parent,
                 placebo_before_child, placebo_after_child,
                 molecular_before_child, molecular_after_child)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (team, parent_treatment, child_treatment,
                  int(placebo_before[i]), int(placebo_after[i]),
                  int(molecular_before[i]), int(molecular_after[i]),
                  int(placebo_before[i]), int(placebo_after[i]),
                  int(molecular_before[i]), int(molecular_after[i])))
        
        conn.commit()
        conn.close()
    
    def get_current_session_id(self) -> str:
        """Get current active session ID from database (global across all users)."""
        # Always check database for the active session
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT session_id FROM sessions WHERE is_active = 1 ORDER BY session_id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            session_id = result[0]
        else:
            # Create all sessions if none exist
            self._initialize_default_sessions(cursor, conn)
            session_id = "test_session"
        
        conn.close()
        
        # Update session state to match database
        st.session_state.session_id = session_id
        
        return session_id
    
    def set_active_session(self, session_id: str):
        """Set the active session globally for all users."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Deactivate all sessions
        cursor.execute("UPDATE sessions SET is_active = 0")
        
        # Activate the selected session
        cursor.execute("UPDATE sessions SET is_active = 1 WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
        
        # Update session state
        st.session_state.session_id = session_id
    
    def create_session(self, session_id: str, session_name: str):
        """Create a new session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_id, session_name, is_active)
            VALUES (?, ?, TRUE)
        ''', (session_id, session_name))
        conn.commit()
        conn.close()
    
    def clear_session_data(self, session_id: str):
        """Clear all data for a specific session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tables = ['teams', 'game1_heights', 'game2_perimeter', 'game3_memory', 'game4_clinical', 'feedback']
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    def register_team(self, team_name: str, parent_name: str, child_name: str) -> bool:
        """Register a team with parent and child names."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            team_indication = self.max_team_names.get(team_name, "Unknown Disease")
            session_id = self.get_current_session_id()
            
            cursor.execute('''
                INSERT OR REPLACE INTO teams (team_name, team_indication, parent_name, child_name, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (team_name, team_indication, parent_name, child_name, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error registering team: {e}")
            return False
    
    def save_game1_data(self, team_name: str, parent_height: float, child_height: float) -> bool:
        """Save height data for game 1."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            session_id = self.get_current_session_id()
            
            cursor.execute('''
                INSERT OR REPLACE INTO game1_heights (team_name, parent_height, child_height, session_id)
                VALUES (?, ?, ?, ?)
            ''', (team_name, parent_height, child_height, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving height data: {e}")
            return False
    
    def save_game2_data(self, team_name: str, parent_estimate: float, child_estimate: float) -> bool:
        """Save perimeter estimates for game 2."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            session_id = self.get_current_session_id()
            
            # Calculate deltas using ground truth from config
            parent_delta = parent_estimate - PERIMETER_GROUND_TRUTH
            child_delta = child_estimate - PERIMETER_GROUND_TRUTH
            parent_abs_delta = abs(parent_delta)
            child_abs_delta = abs(child_delta)
            
            cursor.execute('''
                INSERT OR REPLACE INTO game2_perimeter 
                (team_name, parent_estimate, child_estimate, parent_delta, child_delta, 
                 parent_abs_delta, child_abs_delta, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (team_name, parent_estimate, child_estimate, parent_delta, child_delta,
                  parent_abs_delta, child_abs_delta, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving perimeter data: {e}")
            return False
    
    def save_game3_data(self, team_name: str, round_number: int, correct_answer: str, team_answer: str) -> bool:
        """Save memory game result for a round."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            session_id = self.get_current_session_id()
            
            is_correct = (correct_answer == team_answer)
            
            cursor.execute('''
                INSERT INTO game3_memory 
                (team_name, round_number, correct_answer, team_answer, is_correct, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (team_name, round_number, correct_answer, team_answer, is_correct, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving memory game data: {e}")
            return False
    
    def update_game3_correct_answers(self) -> bool:
        """Update game3_memory table with new correct answers and recalculate is_correct."""
        try:
            from utils.helpers import get_molecule_questions
            questions = get_molecule_questions()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update each round with the new correct answer
            for question in questions:
                round_num = question['round']
                new_correct_answer = question['correct']
                
                # Update the correct_answer and recalculate is_correct
                cursor.execute('''
                    UPDATE game3_memory 
                    SET correct_answer = ?,
                        is_correct = CASE WHEN team_answer = ? THEN 1 ELSE 0 END
                    WHERE round_number = ?
                ''', (new_correct_answer, new_correct_answer, round_num))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating game3 correct answers: {e}")
            return False
    
    def get_clinical_trial_data(self, team_name: str) -> Dict:
        """Get clinical trial data for a team."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT parent_treatment, child_treatment,
                   placebo_before_parent, placebo_after_parent,
                   molecular_before_parent, molecular_after_parent,
                   placebo_before_child, placebo_after_child,
                   molecular_before_child, molecular_after_child
            FROM secret_clinical_data WHERE team_name = ?
        ''', (team_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            (parent_treatment, child_treatment,
             placebo_before_parent, placebo_after_parent,
             molecular_before_parent, molecular_after_parent,
             placebo_before_child, placebo_after_child,
             molecular_before_child, molecular_after_child) = result
            
            # Get appropriate values based on treatment
            if parent_treatment == "Placebo":
                parent_before = placebo_before_parent
                parent_after = placebo_after_parent
            else:
                parent_before = molecular_before_parent
                parent_after = molecular_after_parent
            
            if child_treatment == "Placebo":
                child_before = placebo_before_child
                child_after = placebo_after_child
            else:
                child_before = molecular_before_child
                child_after = molecular_after_child
            
            # Safe integer conversion
            def safe_int(value):
                if isinstance(value, bytes):
                    try:
                        return int.from_bytes(value, byteorder='little')
                    except:
                        return int(value.decode()) if value else 0
                elif isinstance(value, (int, float)):
                    return int(value)
                else:
                    return int(value) if value else 0
            
            return {
                'parent_treatment': parent_treatment,
                'child_treatment': child_treatment,
                'parent_before': safe_int(parent_before),
                'parent_after': safe_int(parent_after),
                'child_before': safe_int(child_before),
                'child_after': safe_int(child_after)
            }
        
        return None
    
    def save_game4_data(self, team_name: str, parent_before: int = None, parent_after: int = None, 
                       child_before: int = None, child_after: int = None) -> bool:
        """Save clinical trial data for game 4."""
        try:
            clinical_data = self.get_clinical_trial_data(team_name)
            if not clinical_data:
                return False
            
            # Use provided values
            parent_before_val = parent_before if parent_before is not None else clinical_data['parent_before']
            parent_after_val = parent_after if parent_after is not None else clinical_data['parent_after']
            child_before_val = child_before if child_before is not None else clinical_data['child_before']
            child_after_val = child_after if child_after is not None else clinical_data['child_after']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            session_id = self.get_current_session_id()
            
            cursor.execute('''
                INSERT OR REPLACE INTO game4_clinical 
                (team_name, parent_treatment, child_treatment, parent_before, parent_after, 
                 child_before, child_after, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (team_name, clinical_data['parent_treatment'], clinical_data['child_treatment'],
                  parent_before_val, parent_after_val,
                  child_before_val, child_after_val, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving clinical trial data: {e}")
            return False
    
    def save_feedback(self, team_name: str, overall_rating: int, favorite_game: str, comments: str) -> bool:
        """Save feedback data."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            session_id = self.get_current_session_id()
            
            cursor.execute('''
                INSERT OR REPLACE INTO feedback (team_name, overall_rating, favorite_game, comments, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (team_name, overall_rating, favorite_game, comments, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving feedback: {e}")
            return False
    
    def get_all_teams(self, session_id: str = None) -> pd.DataFrame:
        """Get all registered teams."""
        conn = self.get_connection()
        
        if session_id is None:
            session_id = self.get_current_session_id()
        
        query = "SELECT * FROM teams WHERE session_id = ? ORDER BY team_name"
        df = pd.read_sql_query(query, conn, params=(session_id,))
        conn.close()
        return df
    
    def get_game_data(self, game_number: int, session_id: str = None) -> pd.DataFrame:
        """Get data for a specific game."""
        conn = self.get_connection()
        
        if session_id is None:
            session_id = self.get_current_session_id()
        
        table_map = {
            1: "game1_heights",
            2: "game2_perimeter", 
            3: "game3_memory",
            4: "game4_clinical"
        }
        
        table = table_map.get(game_number)
        if not table:
            return pd.DataFrame()
        
        query = f"SELECT * FROM {table} WHERE session_id = ? ORDER BY team_name"
        df = pd.read_sql_query(query, conn, params=(session_id,))
        conn.close()
        return df
    
    def get_team_progress(self, team_name: str) -> Dict[str, bool]:
        """Check which games a team has completed."""
        session_id = self.get_current_session_id()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        progress = {
            'tech_check': False,
            'game1': False,
            'game2': False,
            'game3': False,
            'game4': False,
            'feedback': False
        }
        
        # Check tech check
        cursor.execute("SELECT COUNT(*) FROM teams WHERE team_name = ? AND session_id = ?", (team_name, session_id))
        progress['tech_check'] = cursor.fetchone()[0] > 0
        
        # Check Game 1, 2, 4
        for i, game in [(1, 'game1_heights'), (2, 'game2_perimeter'), (4, 'game4_clinical')]:
            cursor.execute(f"SELECT COUNT(*) FROM {game} WHERE team_name = ? AND session_id = ?", (team_name, session_id))
            progress[f'game{i}'] = cursor.fetchone()[0] > 0
        
        # Check Game 3
        cursor.execute("SELECT COUNT(*) FROM game3_memory WHERE team_name = ? AND session_id = ?", (team_name, session_id))
        game3_count = cursor.fetchone()[0]
        progress['game3'] = game3_count == 3
        
        # Check feedback
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE team_name = ? AND session_id = ?", (team_name, session_id))
        progress['feedback'] = cursor.fetchone()[0] > 0
        
        conn.close()
        return progress
    
    def export_all_data(self, session_id: str = None) -> Dict[str, pd.DataFrame]:
        """Export all data as DataFrames for analysis."""
        if session_id is None:
            session_id = self.get_current_session_id()
        
        conn = self.get_connection()
        
        data = {}
        tables = ['teams', 'game1_heights', 'game2_perimeter', 'game3_memory', 'game4_clinical', 'feedback']
        
        for table in tables:
            query = f"SELECT * FROM {table} WHERE session_id = ?"
            data[table] = pd.read_sql_query(query, conn, params=(session_id,))
        
        conn.close()
        return data