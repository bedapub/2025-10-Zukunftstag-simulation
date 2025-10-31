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
    st.markdown(f"**Molekül:** {current_question['molecule']}")
    st.info(f"**Wirkung:** {current_question['description']}")
    
    # Show molecule structure (placeholder)
    show_molecule_placeholder(current_question['molecule'])
    
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

def show_molecule_placeholder(molecule_name: str):
    """Show placeholder for molecule structure."""
    
    # In a real implementation, you would show actual molecular structures
    # For now, we'll use a placeholder with educational information
    
    molecule_info = {
        "Aspirin": {
            "formula": "C₉H₈O₄",
            "description": "Contains a benzene ring with acetyl and carboxyl groups",
            "color": config.COLOR_RED_2
        },
        "Glutathione": {
            "formula": "C₁₀H₁₇N₃O₆S",
            "description": "Tripeptide with cysteine, glutamic acid, and glycine",
            "color": config.COLOR_PRIMARY_BLUE
        },
        "Dopamine": {
            "formula": "C₈H₁₁NO₂",
            "description": "Catecholamine neurotransmitter with benzene ring",
            "color": config.COLOR_BRIGHT_BLUE
        },
        "Baloxavir marboxil": {
            "formula": "C₂₇H₂₃F₂N₃O₇S",
            "description": "Complex antiviral with fluorinated aromatic rings",
            "color": config.COLOR_ORANGE_3
        },
        "Risdiplam": {
            "formula": "C₁₉H₂₄N₆O₂",
            "description": "Pyrimidine-based SMN2 splicing modifier",
            "color": config.COLOR_PEACH_1
        }
    }
    
    info = molecule_info.get(molecule_name, {
        "formula": "Unknown",
        "description": "Molecular structure",
        "color": config.COLOR_PURPLE_2
    })
    
    # Create a visual placeholder
    st.markdown(f"""
    <div style="
        background: {config.COLOR_LIGHT_BLUE};
        border: 3px solid {info['color']};
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    ">
        <h2 style="color: {config.COLOR_GRAY_1}; margin-bottom: 10px;">🧪 {molecule_name}</h2>
        <h3 style="color: {config.COLOR_GRAY_2}; margin-bottom: 15px;">Formula: {info['formula']}</h3>
        <p style="color: {config.COLOR_GRAY_3}; font-size: 16px; font-style: italic;">{info['description']}</p>
        <div style="margin-top: 20px; font-size: 14px; color: {config.COLOR_GRAY_4};">
            💡 Study this structure carefully for 10 seconds!
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_game_progress(current_round: int, total_rounds: int):
    """Show progress through the game."""
    progress = current_round / total_rounds
    st.progress(progress)
    st.caption(f"Round {current_round} of {total_rounds}")
    
    # Show answers so far
    if st.session_state.memory_game_answers:
        with st.expander("📊 Your Progress So Far"):
            correct_count = sum(1 for ans in st.session_state.memory_game_answers.values() if ans['is_correct'])
            st.metric("Correct Answers", f"{correct_count}/{len(st.session_state.memory_game_answers)}")
            
            for round_num, ans_data in st.session_state.memory_game_answers.items():
                status = "✅" if ans_data['is_correct'] else "❌"
                st.write(f"Round {round_num}: {status} You answered {ans_data['answer']}, correct was {ans_data['correct']}")

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
