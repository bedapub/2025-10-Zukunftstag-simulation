import streamlit as st
import pandas as pd
from database import ZukunftstagDatabase
from utils.helpers import (
    validate_perimeter, show_error_message, show_success_message
)

# Ground truth perimeter value
GROUND_TRUTH_PERIMETER = 28.0

def show_game2_page(db: ZukunftstagDatabase):
    """Display Game 2: Room perimeter estimation."""
    
    st.title("Spiel 2: Raumum fang-Schätzung")
    st.markdown("Lernt über **Schätzung**, **Genauigkeit** und **Ranking**, indem ihr unseren Raum messt!")
    
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
    if progress.get('game2', False):
        show_existing_data(db, team_name)
        return
    
    # Data collection form
    st.markdown(f"### Team: {team_name}")
    
    with st.form("perimeter_form"):
        st.markdown("#### Eure Schätzungen")
        st.info("**Hinweis**: Ihr habt gesehen, wie lang 1 Meter ist. Schätzt jetzt den gesamten Umfang!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            parent_estimate = st.number_input(
                f"{parent_name}s Schätzung (Meter):",
                min_value=5.0,
                max_value=100.0,
                step=0.1,
                help="Wie viele Meter hat der Raumumfang eurer Meinung nach?"
            )
        
        with col2:
            child_estimate = st.number_input(
                f"{child_name}s Schätzung (Meter):",
                min_value=5.0,
                max_value=100.0,
                step=0.1,
                help="Wie viele Meter hat der Raumumfang eurer Meinung nach?"
            )
        
        submitted = st.form_submit_button("Schätzungen absenden", use_container_width=True)
        
        if submitted:
            # Validate inputs
            parent_valid, parent_error = validate_perimeter(parent_estimate)
            child_valid, child_error = validate_perimeter(child_estimate)
            
            if not parent_valid:
                show_error_message(f"Elternteil Schätzung: {parent_error}")
            elif not child_valid:
                show_error_message(f"Kind Schätzung: {child_error}")
            else:
                # Save data
                success = db.save_game2_data(team_name, parent_estimate, child_estimate)
                
                if success:
                    show_success_message("Schätzungen erfolgreich gespeichert!")
                    
                    # Show immediate feedback
                    show_team_results(parent_name, parent_estimate, child_name, child_estimate)
                    
                    st.balloons()
                    st.rerun()
                else:
                    show_error_message("Speichern der Schätzungen fehlgeschlagen. Bitte erneut versuchen.")

def show_team_results(parent_name, parent_estimate, child_name, child_estimate):
    """Show immediate feedback for the team's estimates."""
    
    st.markdown("### Eure Ergebnisse")
    
    parent_delta = parent_estimate - GROUND_TRUTH_PERIMETER
    child_delta = child_estimate - GROUND_TRUTH_PERIMETER
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {parent_name}s Ergebnis")
        st.metric(
            "Schätzung",
            f"{parent_estimate:.1f} m",
            f"{parent_delta:+.1f} m vom wahren Wert"
        )
        
        accuracy = abs(parent_delta)
        if accuracy <= 2:
            st.success("Ausgezeichnete Schätzung!")
        elif accuracy <= 5:
            st.info("Gute Schätzung!")
        else:
            st.warning("Übt weiter euer Schätzen!")
    
    with col2:
        st.markdown(f"#### {child_name}s Ergebnis")
        st.metric(
            "Schätzung",
            f"{child_estimate:.1f} m", 
            f"{child_delta:+.1f} m vom wahren Wert"
        )
        
        accuracy = abs(child_delta)
        if accuracy <= 2:
            st.success("Ausgezeichnete Schätzung!")
        elif accuracy <= 5:
            st.info("Gute Schätzung!")
        else:
            st.warning("Übt weiter euer Schätzen!")
    
    st.info(f"**Wahrer Umfang**: {GROUND_TRUTH_PERIMETER} Meter")

def show_existing_data(db: ZukunftstagDatabase, team_name: str):
    """Show results and analysis for teams that have already completed Game 2."""
    
    st.success("Ihr habt Spiel 2 bereits abgeschlossen!")
    
    # Navigation
    if st.button("Weiter zu Spiel 3", use_container_width=True):
        st.session_state.current_page = 'game3'
        st.rerun()
