import streamlit as st
import pandas as pd
import config
from database import ZukunftstagDatabase
from utils.helpers import (
    validate_height, show_error_message, show_success_message, 
    show_info_message
)

def show_game1_page(db: ZukunftstagDatabase):
    """Display Game 1: Body Heights measurement and statistics."""
    
    st.title("Spiel 1: Größenmessung")
    st.markdown("Lernt über **Histogramme**, **Korrelation** und **Median** anhand von Größendaten!")
    
    # Check if team is registered
    if not st.session_state.get('team_registered', False):
        show_error_message("Bitte zuerst den Tech Check abschließen!")
        if st.button("Zum Tech Check"):
            st.session_state.current_page = 'tech_check'
            st.rerun()
        return
    
    team_name = st.session_state.team_name
    parent_name = st.session_state.parent_name
    child_name = st.session_state.child_name
    
    # Check if already completed
    progress = db.get_team_progress(team_name)
    if progress.get('game1', False):
        show_existing_data(db, team_name)
        return
    
    # Data collection form
    st.markdown(f"### Team: {team_name}")
    st.markdown(f"Bitte messt und tragt die Größen für **{parent_name}** und **{child_name}** ein")
    
    with st.form("height_form"):
        st.markdown("#### Größenmessungen (in Zentimetern)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            parent_height = st.number_input(
                f"{parent_name}s Größe (cm):",
                min_value=50,
                max_value=250,
                step=1,
                help="Größe in Zentimetern eingeben (z.B. 175)"
            )
        
        with col2:
            child_height = st.number_input(
                f"{child_name}s Größe (cm):",
                min_value=50,
                max_value=200,
                step=1,
                help="Größe in Zentimetern eingeben (z.B. 142)"
            )
        
        submitted = st.form_submit_button("Größen absenden", use_container_width=True)
        
        if submitted:
            # Validate inputs
            parent_valid, parent_error = validate_height(parent_height, 100, 230)
            child_valid, child_error = validate_height(child_height, 80, 200)
            
            if not parent_valid:
                show_error_message(f"Elternteil Größe: {parent_error}")
            elif not child_valid:
                show_error_message(f"Kind Größe: {child_error}")
            else:
                # Save data
                success = db.save_game1_data(team_name, parent_height, child_height)
                
                if success:
                    show_success_message("Größen erfolgreich gespeichert!")
                    
                    # Show immediate results
                    st.rerun()
                else:
                    show_error_message("Speichern der Größendaten fehlgeschlagen. Bitte erneut versuchen.")

def show_existing_data(db: ZukunftstagDatabase, team_name: str):
    """Show results and analysis for teams that have already completed Game 1."""
    
    st.success("Ihr habt Spiel 1 bereits abgeschlossen!")
    
    # Navigation
    if st.button("Weiter zu Spiel 2", use_container_width=True):
        st.session_state.current_page = 'game2'
        st.rerun()
