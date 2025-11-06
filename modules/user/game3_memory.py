import streamlit as st
import config
from database import ZukunftstagDatabase
from utils.helpers import (
    show_error_message, show_success_message,
    get_molecule_questions
)

def show_game3_page(db: ZukunftstagDatabase):
    """Display Game 3: Molecular Memory Game."""
    
    st.title("Spiel 3: Molekül-Memory-Challenge")
    st.markdown("Testet euer Gedächtnis und lernt wichtige Wirkstoffmoleküle kennen!")
    
    # Check if team is registered
    if not st.session_state.get('team_registered', False):
        show_error_message("Bitte zuerst den Tech Check abschließen!")
        if st.button("Zum Tech Check"):
            st.session_state.current_page = 'tech_check'
            st.rerun()
        return
    
    team_name = st.session_state.team_name
    
    # Check if already completed
    progress = db.get_team_progress(team_name)
    if progress.get('game3', False):
        show_existing_data(db, team_name)
        return
    
    # Initialize game state
    if 'memory_game_round' not in st.session_state:
        st.session_state.memory_game_round = 1
        st.session_state.memory_game_answers = {}
    
    # Get molecule questions
    questions = get_molecule_questions()
    current_round = st.session_state.memory_game_round
    
    if current_round <= len(questions):
        show_memory_round(db, team_name, questions, current_round)
    else:
        show_game_complete(db, team_name)

def show_memory_round(db: ZukunftstagDatabase, team_name: str, questions: list, round_num: int):
    """Display a single round of the memory game."""
    
    current_question = questions[round_num - 1]
    
    st.markdown(f"### Runde {round_num} von {len(questions)}")
    st.info("**Das Molekül wird auf der Präsentation gezeigt. Schaut auf den Bildschirm!**")
    st.markdown("---")
    
    # Answer form
    with st.form(f"memory_round_{round_num}"):
        st.markdown("#### Wähle die passende Struktur:")
        
        answer = st.radio(
            "Welche Option passt zum Molekül, das du gerade gesehen hast?",
            options=current_question['options'],
            index=None,
            help="Schau dir die Strukturdetails genau an!"
        )
        
        submitted = st.form_submit_button("Antwort absenden", use_container_width=True)
        
        if submitted:
            if answer is None:
                show_error_message("Bitte wähle eine Antwort!")
            else:
                # Save answer
                success = db.save_game3_data(
                    team_name, 
                    round_num, 
                    current_question['correct'], 
                    answer
                )
                
                if success:
                    # Store in session for immediate feedback
                    st.session_state.memory_game_answers[round_num] = {
                        'answer': answer,
                        'correct': current_question['correct'],
                        'is_correct': answer == current_question['correct']
                    }
                    
                    # Show immediate feedback
                    if answer == current_question['correct']:
                        show_success_message(f"Richtig! Die Antwort war {answer}.")
                    else:
                        show_error_message(f"Leider falsch. Die richtige Antwort war {current_question['correct']}.")
                    
                    # Advance to next round
                    st.session_state.memory_game_round += 1
                    st.rerun()
                else:
                    show_error_message("Speichern der Antwort fehlgeschlagen. Bitte erneut versuchen.")
    
    # Show progress
    show_game_progress(round_num, len(questions))

def show_game_progress(current_round: int, total_rounds: int):
    """Show progress through the game."""
    progress = current_round / total_rounds
    st.progress(progress)
    st.caption(f"Round {current_round} of {total_rounds}")

def show_game_complete(db: ZukunftstagDatabase, team_name: str):
    """Show completion message and final results."""
    
    st.success("Memory-Spiel abgeschlossen!")
    
    # Calculate final score
    correct_count = sum(1 for ans in st.session_state.memory_game_answers.values() if ans['is_correct'])
    total_rounds = len(st.session_state.memory_game_answers)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Deine Punktzahl", f"{correct_count}/{total_rounds}")
    
    with col2:
        percentage = (correct_count / total_rounds) * 100
        st.metric("Prozent", f"{percentage:.0f}%")
    
    with col3:
        if percentage >= 80:
            grade = "Ausgezeichnet"
        elif percentage >= 60:
            grade = "Gut"
        elif percentage >= 40:
            grade = "Befriedigend"
        else:
            grade = "Weiter üben"
        st.metric("Bewertung", grade)
    
    # Show all answers
    with st.expander("Deine Antworten überprüfen"):
        for round_num, ans_data in st.session_state.memory_game_answers.items():
            status = "Richtig" if ans_data['is_correct'] else "Falsch"
            st.write(f"**Runde {round_num}:** {status} - Du: {ans_data['answer']}, Richtig: {ans_data['correct']}")
    
    # Navigation
    if st.button("Weiter zu Spiel 4", use_container_width=True):
        st.session_state.current_page = 'game4'
        st.rerun()

def show_existing_data(db: ZukunftstagDatabase, team_name: str):
    """Show results for teams that have already completed Game 3."""
    
    st.success("Ihr habt Spiel 3 bereits abgeschlossen!")
    
    # Navigation
    if st.button("Weiter zu Spiel 4", use_container_width=True):
        st.session_state.current_page = 'game4'
        st.rerun()
