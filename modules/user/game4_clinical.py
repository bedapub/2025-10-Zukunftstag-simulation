import streamlit as st
import pandas as pd
from database import ZukunftstagDatabase
from utils.helpers import show_error_message, show_success_message, show_info_message
from utils.visualizations import create_clinical_trial_boxplot

def show_game4_page(db: ZukunftstagDatabase):
    """Display Game 4: Clinical Trial Simulation."""
    
    st.title("Spiel 4: Klinische Studie-Simulation")
    st.markdown("Lernt über **Doppelblind-Studien**, **Placebo-Effekte** und **statistische Signifikanz**!")
    
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
    if progress.get('game4', False):
        show_existing_data(db, team_name)
        return
    
    # Get clinical trial data for this team
    clinical_data = db.get_clinical_trial_data(team_name)
    
    if clinical_data is None:
        show_error_message("Klinische Studiendaten nicht verfügbar für euer Team. Bitte kontaktiert einen Administrator.")
        return
    
    # Show the clinical trial interface
    show_clinical_trial_simulation(db, team_name, parent_name, child_name, clinical_data)

def show_clinical_trial_simulation(db: ZukunftstagDatabase, team_name: str, parent_name: str, child_name: str, clinical_data: dict):
    """Show the clinical trial data entry interface."""
    
    st.markdown(f"### Team: {team_name}")
    st.markdown("**Bitte tragt eure Schmerzwerte vom Papier ein:**")
    
    # Show chocolate ball colors
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {parent_name}s Medikament")
        color = "Rot" if clinical_data['parent_treatment'] == "Placebo" else "Schwarz"
        st.info(f"Du hast erhalten: {color}e Medikamentenkugel")
    
    with col2:
        st.markdown(f"#### {child_name}s Medikament") 
        color = "Rot" if clinical_data['child_treatment'] == "Placebo" else "Schwarz"
        st.info(f"Du hast erhalten: {color}e Medikamentenkugel")
    
    # Pain score entry form
    with st.form("clinical_trial_form"):
        st.markdown("#### Schmerzwerte (0 = Kein Schmerz, 10 = Schlimmster Schmerz)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{parent_name}s Werte:**")
            
            parent_before = st.number_input(
                "Vor der Behandlung:",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                key="parent_before",
                help="Bitte den Wert vom Papier eingeben"
            )
            
            parent_after = st.number_input(
                "Nach der Behandlung:",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                key="parent_after",
                help="Bitte den Wert vom Papier eingeben"
            )
        
        with col2:
            st.markdown(f"**{child_name}s Werte:**")
            
            child_before = st.number_input(
                "Vor der Behandlung:",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                key="child_before",
                help="Bitte den Wert vom Papier eingeben"
            )
            
            child_after = st.number_input(
                "Nach dem Medikament:",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                key="child_after",
                help="Bitte den Wert vom Papier eingeben"
            )
        
        submitted = st.form_submit_button("Klinische Studiendaten absenden", use_container_width=True)
        
        if submitted:
            parent_change = parent_after - parent_before
            child_change = child_after - child_before
            
            # Save the actual entered values
            success = db.save_game4_data(
                team_name, 
                parent_before=parent_before,
                parent_after=parent_after,
                child_before=child_before,
                child_after=child_after
            )
            
            if success:
                show_success_message("Klinische Studiendaten erfolgreich gespeichert!")
                st.rerun()
            else:
                show_error_message("Speichern der klinischen Studiendaten fehlgeschlagen. Bitte erneut versuchen.")

def show_existing_data(db: ZukunftstagDatabase, team_name: str):
    """Show results for teams that have already completed Game 4."""
    
    st.success("Ihr habt Spiel 4 bereits abgeschlossen!")
    
    if st.button("Weiter zum Feedback", use_container_width=True):
        st.session_state.current_page = 'feedback'
        st.rerun()
