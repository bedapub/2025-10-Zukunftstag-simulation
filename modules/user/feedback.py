import streamlit as st
import pandas as pd
from database import ZukunftstagDatabase
from utils.helpers import show_error_message, show_success_message, show_info_message
from utils.visualizations import create_feedback_summary

def show_feedback_page(db: ZukunftstagDatabase):
    """Display the feedback page."""
    
    st.title("Feedback - Teilt eure Erfahrung!")
    st.markdown("Helft uns, den **Mathe Macht Medikamente** Workshop zu verbessern!")
    
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
    if progress.get('feedback', False):
        show_existing_feedback(db, team_name)
        return
    
    # Show feedback form
    show_feedback_form(db, team_name, parent_name, child_name)

def show_feedback_form(db: ZukunftstagDatabase, team_name: str, parent_name: str, child_name: str):
    """Display the feedback collection form."""
    
    st.markdown(f"### Team: {team_name}")
    st.markdown(f"Vielen Dank **{parent_name}** und **{child_name}** für eure Teilnahme!")
    
    with st.form("feedback_form"):
        
        # Overall rating
        st.markdown("#### Gesamterlebnis")
        overall_rating = st.select_slider(
            "Wie würdet ihr den Workshop insgesamt bewerten?",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x + f" ({x}/5)"
        )
        
        # Favorite game
        st.markdown("#### Lieblingsaktivität")
        favorite_game = st.selectbox(
            "Welche Aktivität hat euch am besten gefallen?",
            options=[
                "Spiel 1: Größenmessung",
                "Spiel 2: Umfang-Schätzung", 
                "Spiel 3: Molekül-Memory",
                "Spiel 4: Klinische Studie",
                "Alle waren toll!",
                "Keine war besonders interessant"
            ]
        )
        
        # Learning assessment
        st.markdown("#### Was habt ihr gelernt?")
        learning_topics = st.multiselect(
            "Über welche Konzepte habt ihr heute etwas gelernt? (Alles Zutreffende auswählen)",
            options=[
                "Histogramme und Datenverteilung",
                "Median und Durchschnitte", 
                "Korrelation zwischen Variablen",
                "Wissenschaftliche Schätztechniken",
                "Statistische Analysemethoden",
                "Wie klinische Studien funktionieren",
                "Doppelblind-Studiendesign",
                "Placebo-Effekte",
                "Molekülstruktur und -funktion",
                "Wie Mathematik in der Medizin eingesetzt wird"
            ]
        )
        
        # Difficulty level
        st.markdown("#### Schwierigkeitsgrad")
        col1, col2 = st.columns(2)
        
        with col1:
            parent_difficulty = st.radio(
                f"Für {parent_name} - Wie anspruchsvoll war der Workshop?",
                options=["Zu einfach", "Genau richtig", "Zu schwierig"],
                index=1
            )
        
        with col2:
            child_difficulty = st.radio(
                f"Für {child_name} - Wie anspruchsvoll war der Workshop?", 
                options=["Zu einfach", "Genau richtig", "Zu schwierig"],
                index=1
            )
        
        # Suggestions for improvement
        st.markdown("#### Verbesserungsvorschläge")
        improvements = st.text_area(
            "Was könnten wir für zukünftige Workshops verbessern?",
            placeholder="Ideen zur Verbesserung des Workshops...",
            help="Optional: Teilt eure Verbesserungsideen"
        )
        
        # Would recommend
        st.markdown("#### Weiterempfehlung")
        would_recommend = st.radio(
            "Würdet ihr diesen Workshop anderen Familien empfehlen?",
            options=["Auf jeden Fall", "Wahrscheinlich ja", "Vielleicht", "Wahrscheinlich nicht", "Auf keinen Fall"],
            index=1
        )
        
        # Additional comments
        additional_comments = st.text_area(
            "Weitere Kommentare oder Gedanken?",
            placeholder="Teilt alles andere über eure Erfahrung...",
            help="Optional: Jegliches weiteres Feedback"
        )
        
        # Combine all comments
        all_comments = f"Schwierigkeit - Elternteil: {parent_difficulty}, Kind: {child_difficulty}. "
        if learning_topics:
            all_comments += f"Gelernt: {', '.join(learning_topics)}. "
        if improvements:
            all_comments += f"Verbesserungen: {improvements}. "
        all_comments += f"Würde empfehlen: {would_recommend}. "
        if additional_comments:
            all_comments += f"Zusätzlich: {additional_comments}"
        
        submitted = st.form_submit_button("Feedback absenden", use_container_width=True)
        
        if submitted:
            success = db.save_feedback(team_name, overall_rating, favorite_game, all_comments)
            
            if success:
                show_success_message(f"Vielen Dank für euer Feedback, {parent_name} und {child_name}!")
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; margin: 20px 0;">
                    <h2 style="color: #0b41cd;">🎉 Herzlichen Glückwunsch! 🎉</h2>
                    <h3>Ihr habt alle Spiele abgeschlossen!</h3>
                    <p style="font-size: 18px; margin-top: 20px;">
                        Vielen Dank <strong>{parent_name}</strong> und <strong>{child_name}</strong> für eure Teilnahme am 
                        <strong>Mathe Macht Medikamente</strong> Workshop!
                    </p>
                    <p style="font-size: 16px; color: #666; margin-top: 15px;">
                        Wir hoffen, ihr hattet viel Spaß und habt viel über Mathematik in der Medizin gelernt! 🧬📊
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                st.rerun()
            else:
                show_error_message("Speichern des Feedbacks fehlgeschlagen. Bitte erneut versuchen.")

def show_existing_feedback(db: ZukunftstagDatabase, team_name: str):
    """Show completion message for teams that have already submitted feedback."""
    
    st.success("Vielen Dank für euer Feedback!")
    
    parent_name = st.session_state.get('parent_name', '')
    child_name = st.session_state.get('child_name', '')
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; margin: 20px 0;">
        <h2 style="color: #0b41cd;">🎉 Herzlichen Glückwunsch! 🎉</h2>
        <h3>Ihr habt bereits alle Spiele abgeschlossen!</h3>
        <p style="font-size: 18px; margin-top: 20px;">
            Vielen Dank <strong>{parent_name}</strong> und <strong>{child_name}</strong> für eure Teilnahme am 
            <strong>Mathe Macht Medikamente</strong> Workshop!
        </p>
        <p style="font-size: 16px; color: #666; margin-top: 15px;">
            Wir hoffen, der Workshop hat euch gefallen! 🧬📊
        </p>
    </div>
    """, unsafe_allow_html=True)
