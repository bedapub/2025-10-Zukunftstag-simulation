import streamlit as st
from database import ZukunftstagDatabase
from utils.helpers import init_session_state, safe_get_query_param, show_progress_indicator
from modules.user.tech_check import show_tech_check_page
from modules.user.game1_heights import show_game1_page
from modules.user.game2_perimeter import show_game2_page
from modules.user.game3_memory import show_game3_page
from modules.user.game4_clinical import show_game4_page
from modules.user.feedback import show_feedback_page
from modules.admin.admin_dashboard import show_admin_page

st.set_page_config(
    page_title="Mathe Macht Medikamente - Zukunftstag",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
    }
    
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 0.5rem;
    }
    
    .stTextInput > div > div > input {
        font-size: 1.1rem;
        height: 3rem;
        border-radius: 0.5rem;
    }
    
    .stNumberInput > div > div > input {
        font-size: 1.1rem;
        height: 3rem;
        border-radius: 0.5rem;
    }
    
    .stSelectbox > div > div {
        font-size: 1.1rem;
    }
    
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    /* Touch-friendly form elements */
    .stForm {
        padding: 1rem;
    }
    
    /* Progress indicators */
    .progress-item {
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
    }
    
    /* Sidebar optimizations for desktop only */
    @media (min-width: 768px) {
        .main .block-container {
            max-width: 900px;
        }
    }
    
    /* Team header styling */
    .team-header {
        background: linear-gradient(90deg, #1f77b4, #17becf);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Initialize session state
    init_session_state()
    
    # Initialize database
    db = ZukunftstagDatabase()
    
    # Handle QR code landing (NEW: No team name in URL anymore)
    handle_qr_code_landing()
    
    # Show main content
    if st.session_state.current_page == 'admin':
        show_admin_page(db)
    else:
        show_main_app(db)

def handle_qr_code_landing():
    """Handle QR code landing page - team-specific QR codes on tables."""
    
    # Check if this is a QR code scan with team name embedded
    team_param = safe_get_query_param('team')
    
    if team_param and not st.session_state.get('qr_processed', False):
        # QR code contains team name - store it in session state
        st.session_state.qr_team_name = team_param
        st.session_state.from_qr_code = True
        st.session_state.current_page = 'tech_check'
        st.session_state.qr_processed = True  # Mark as processed to avoid repeating balloons

def show_main_app(db: ZukunftstagDatabase):
    """Show the main application interface."""
    
    # Sidebar navigation
    show_sidebar_navigation(db)
    
    # Main content area
    page = st.session_state.get('current_page', 'home')
    
    if page == 'home':
        show_home_page()
    elif page == 'tech_check':
        show_tech_check_page(db)
    elif page == 'game1':
        show_game1_page(db)
    elif page == 'game2':
        show_game2_page(db)
    elif page == 'game3':
        show_game3_page(db)
    elif page == 'game4':
        show_game4_page(db)
    elif page == 'feedback':
        show_feedback_page(db)
    else:
        show_home_page()

def show_sidebar_navigation(db: ZukunftstagDatabase):
    """Show sidebar navigation and progress tracking."""
    
    st.sidebar.title("Zukunftstag")
    st.sidebar.markdown("**Mathe Macht Medikamente**")
    
    # Prominent Home button (always visible)
    st.sidebar.markdown("---")
    if st.sidebar.button("**Start**", type="primary", key="nav_home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()
    st.sidebar.markdown("---")
    
    # Team information (if registered)
    if st.session_state.get('team_registered', False):
        team_name = st.session_state.get('team_name', '')
        parent_name = st.session_state.get('parent_name', '')
        child_name = st.session_state.get('child_name', '')
        
        st.sidebar.markdown(f"""
        <div class="team-header">
            <h3>{team_name}</h3>
            <p>{parent_name} & {child_name}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show progress
        progress = db.get_team_progress(team_name)
        show_progress_indicator(progress)
    
    # Navigation menu
    st.sidebar.markdown("### Navigation")
    
    nav_options = {
        'tech_check': 'Tech Check',
        'game1': 'Spiel 1: Größen',
        'game2': 'Spiel 2: Umfang',
        'game3': 'Spiel 3: Memory',
        'game4': 'Spiel 4: Klinische Studie',
        'feedback': 'Feedback'
    }
    
    for page_key, page_label in nav_options.items():
        if st.sidebar.button(page_label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()
    
    # Admin access
    st.sidebar.markdown("---")
    if st.sidebar.button("Admin Dashboard", key="nav_admin", use_container_width=True):
        st.session_state.current_page = 'admin'
        st.rerun()
    
    # Development mode indicator
    import config
    if config.DEV_MODE:
        st.sidebar.markdown("---")
        st.sidebar.warning("**DEV MODE**")
        with st.sidebar.expander("Dev Tools"):
            st.write("**Config:**")
            st.write(f"- QR Bypass: {config.DEV_BYPASS_QR}")
            st.write(f"- Auto Team: {config.DEV_AUTO_LOGIN_TEAM}")
            
            if st.button("Reset Session", key="dev_reset"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # QR code info (if came from QR)
    if st.session_state.get('from_qr_code', False):
        st.sidebar.info("Zugang via QR-Code")

def show_home_page():
    """Show the home/landing page."""
    
    st.title("🧬 Mathe Macht Medikamente")
    st.markdown("## Willkommen zum Zukunftstag Workshop!")
    
    st.markdown("")
    st.markdown("")
    
    # Start button
    if st.button("🚀 Beginne deine Reise", type="primary", use_container_width=True):
        st.session_state.current_page = 'tech_check'
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🧬 <strong>Mathe Macht Medikamente</strong> | Roche Zukunftstag 2025</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()