import streamlit as st
from database import ZukunftstagDatabase
from utils.helpers import (
    validate_name_input, 
    show_error_message, show_success_message, show_info_message
)
import config

def show_tech_check_page(db: ZukunftstagDatabase):
    """Display the tech check page where teams register their information."""
    
    st.title("Tech Check")
    st.markdown("### Team Registrierung")
    st.markdown("Willkommen bei **Mathe Macht Medikamente**!")
    
    # Check if team name was provided via QR code
    qr_team_name = st.session_state.get('qr_team_name', '')
    
    # Get available team names
    available_teams = list(db.max_team_names.keys())
    
    # Development mode: bypass QR code requirement
    if config.DEV_MODE and config.DEV_BYPASS_QR:
        
        # Auto-login if configured
        if config.DEV_AUTO_LOGIN_TEAM and not qr_team_name:
            qr_team_name = config.DEV_AUTO_LOGIN_TEAM
            st.session_state.qr_team_name = qr_team_name
        
        # Show team selector in dev mode if no team selected
        if not qr_team_name:
            st.info("In der Produktion scannen Teams QR-Codes. Wähle ein Team zum Testen:")
            selected_team = st.selectbox(
                "Team auswählen (nur DEV):",
                options=[""] + sorted(available_teams),
                index=0
            )
            if selected_team:
                qr_team_name = selected_team
                st.session_state.qr_team_name = qr_team_name
                st.rerun()
            else:
                return
    
    # Production mode: require QR code
    if not qr_team_name or qr_team_name not in available_teams:
        st.error("Bitte scannt den QR-Code auf eurem Tisch, um zu starten!")
        st.info("Jeder Tisch hat einen eigenen QR-Code mit eurem Teamnamen.")
        return
    
    # Display team info from QR code
    team_indication = db.max_team_names.get(qr_team_name, "Unknown Disease")
    
    st.success(f"**Team:** {qr_team_name}")
    st.info(f"**Forschungsgebiet:** {team_indication}")
    st.markdown("---")
    
    with st.form("tech_check_form"):
        st.markdown("### Eure Namen")
        
        # Team name is locked from QR code (hidden field)
        team_name = qr_team_name
        
        # Pre-fill names in dev mode
        default_parent = "Anna" if config.DEV_MODE else ""
        default_child = "Sophie" if config.DEV_MODE else ""
        
        parent_name = st.text_input(
            "Name Elternteil:",
            value=default_parent,
            help="Vorname des Elternteils"
        )
        
        st.markdown("")  # Spacing
        
        child_name = st.text_input(
            "Name Kind:",
            value=default_child,
            help="Vorname des Kindes"
        )
        
        st.markdown("")  # Spacing
        
        submitted = st.form_submit_button("Weiter", type="primary", use_container_width=True)
        
        if submitted:
            # Validate inputs
            parent_valid, parent_error = validate_name_input(parent_name)
            child_valid, child_error = validate_name_input(child_name)
            
            if not parent_valid:
                show_error_message(f"Elternteil: {parent_error}")
            elif not child_valid:
                show_error_message(f"Kind: {child_error}")
            else:
                # Register team
                success = db.register_team(team_name, parent_name, child_name)
                
                if success:
                    # Update session state
                    st.session_state.team_name = team_name
                    st.session_state.parent_name = parent_name
                    st.session_state.child_name = child_name
                    st.session_state.team_registered = True
                    st.session_state.current_page = 'game1'
                    
                    show_success_message(f"Willkommen {parent_name} und {child_name}!")
                    
                    # Auto-advance to next page
                    st.rerun()
                else:
                    show_error_message("Registrierung fehlgeschlagen. Bitte erneut versuchen.")