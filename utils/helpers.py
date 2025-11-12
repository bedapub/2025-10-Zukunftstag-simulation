"""
Helper utilities for the Zukunftstag simulation application.
Centralized validation, state management, and UI helper functions.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import (
    ADMIN_PASSWORD, SESSION_OPTIONS, HEIGHT_MIN, HEIGHT_MAX,
    PERIMETER_MIN, PERIMETER_MAX, NAME_MIN_LENGTH
)

def validate_team_name(team_name, available_teams):
    """Validate if team name exists in available teams."""
    if not team_name:
        return False, "Please enter a team name."
    
    if team_name not in available_teams:
        return False, f"Team '{team_name}' not found. Please check the spelling."
    
    return True, ""

def validate_name_input(name):
    """Validate name input."""
    if not name or len(name.strip()) < NAME_MIN_LENGTH:
        return False, f"Please enter a valid name (at least {NAME_MIN_LENGTH} characters)."
    
    if not name.replace(" ", "").replace("-", "").isalpha():
        return False, "Name should only contain letters, spaces, and hyphens."
    
    return True, ""

def validate_height(height, min_height=HEIGHT_MIN, max_height=HEIGHT_MAX):
    """Validate height input."""
    try:
        height_val = float(height)
        if height_val < min_height or height_val > max_height:
            return False, f"Height must be between {min_height} and {max_height} cm."
        return True, ""
    except (ValueError, TypeError):
        return False, "Please enter a valid number for height."

def validate_perimeter(perimeter, min_val=PERIMETER_MIN, max_val=PERIMETER_MAX):
    """Validate perimeter estimate."""
    try:
        perimeter_val = float(perimeter)
        if perimeter_val < min_val or perimeter_val > max_val:
            return False, f"Perimeter estimate must be between {min_val} and {max_val} meters."
        return True, ""
    except (ValueError, TypeError):
        return False, "Please enter a valid number for perimeter estimate."

def show_progress_indicator(progress_dict):
    """Show progress indicator for completed games."""
    st.sidebar.markdown("### 📋 Your Progress")
    
    progress_items = [
        ("🔧 Tech Check", progress_dict.get('tech_check', False)),
        ("📏 Game 1: Heights", progress_dict.get('game1', False)),
        ("📐 Game 2: Perimeter", progress_dict.get('game2', False)),
        ("🧠 Game 3: Memory", progress_dict.get('game3', False)),
        ("💊 Game 4: Clinical Trial", progress_dict.get('game4', False)),
        ("💬 Feedback", progress_dict.get('feedback', False))
    ]
    
    for item, completed in progress_items:
        status = "✅" if completed else "⏳"
        st.sidebar.markdown(f"{status} {item}")

def format_team_display_name(team_name, team_indication):
    """Format team name for display."""
    return f"**{team_name}** - {team_indication}"

def get_molecule_questions():
    """Get predefined molecule memory game questions."""
    return [
        {
            "round": 1,
            "molecule": "Aspirin",
            "description": "Pain reliever and anti-inflammatory",
            "options": ["A", "B", "C", "D"],
            "correct": "C"
        },
        {
            "round": 2,
            "molecule": "Glutathione",
            "description": "Antioxidant that protects cells",
            "options": ["A", "B", "C", "D"],
            "correct": "A"
        },
        {
            "round": 3,
            "molecule": "Dopamine",
            "description": "Neurotransmitter for movement and mood",
            "options": ["A", "B", "C", "D"],
            "correct": "D"
        }
    ]

def check_admin_password():
    """Check if admin password is correct."""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.sidebar.markdown("### 🔐 Admin Login")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.sidebar.success("Logged in successfully!")
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
        
        return False
    
    return True

def logout_admin():
    """Logout admin user."""
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

def get_session_options():
    """Get available session management options."""
    return SESSION_OPTIONS

def init_session_state():
    """Initialize session state variables."""
    default_values = {
        'current_page': 'home',
        'team_name': '',
        'parent_name': '',
        'child_name': '',
        'team_registered': False,
        'admin_authenticated': False
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_get_query_param(param_name, default=None):
    """Safely get query parameter from URL."""
    try:
        query_params = st.query_params
        return query_params.get(param_name, default)
    except:
        return default

def create_download_link(df, filename, link_text="Download CSV"):
    """Create a download link for dataframe."""
    csv = df.to_csv(index=False)
    st.download_button(
        label=link_text,
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def show_error_message(message):
    """Display error message with consistent styling."""
    st.error(f"{message}")

def show_success_message(message):
    """Display success message with consistent styling."""
    st.success(f"{message}")

def show_info_message(message):
    """Display info message with consistent styling."""
    st.info(f"{message}")

def show_warning_message(message):
    """Display warning message with consistent styling."""
    st.warning(f"{message}")

def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = pd.to_datetime(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def calculate_statistics(values):
    """Calculate basic statistics for a list of values."""
    if not values:
        return {}
    
    values_series = pd.Series(values)
    return {
        'count': len(values),
        'mean': values_series.mean(),
        'median': values_series.median(),
        'std': values_series.std(),
        'min': values_series.min(),
        'max': values_series.max()
    }


def check_team_registered():
    """
    Check if team is registered and return team info.
    Returns: (is_registered: bool, team_name: str, parent_name: str, child_name: str)
    """
    is_registered = st.session_state.get('team_registered', False)
    team_name = st.session_state.get('team_name', '')
    parent_name = st.session_state.get('parent_name', '')
    child_name = st.session_state.get('child_name', '')
    
    return is_registered, team_name, parent_name, child_name


def require_team_registration():
    """
    Ensure team is registered before allowing access to game pages.
    Returns team info if registered, otherwise shows error and returns None.
    """
    is_registered, team_name, parent_name, child_name = check_team_registered()
    
    if not is_registered:
        st.error("Bitte zuerst den Tech Check abschließen, um euer Team zu registrieren!")
        st.info("Geht zur Tech Check-Seite, um zu beginnen.")
        if st.button("Go to Tech Check"):
            st.session_state.current_page = 'tech_check'
            st.rerun()
        return None
    
    return {
        'team_name': team_name,
        'parent_name': parent_name,
        'child_name': child_name
    }


def display_team_header(team_name, parent_name, child_name):
    """Display team information header."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #1f77b4, #17becf);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    ">
        <h3>👥 {team_name}</h3>
        <p>👨‍🦳 {parent_name} & 👶 {child_name}</p>
    </div>
    """, unsafe_allow_html=True)


def get_completion_status_emoji(completed):
    """Get emoji for completion status."""
    return "✅" if completed else "⏳"