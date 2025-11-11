"""Game 3 (Memory) visualization and analysis for admin dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import show_waiting_message


def show_game3_analysis(db):
    """Display Game 3 (Memory) analysis."""
    # Get teams that have completed tech check
    teams_data = db.get_all_teams()
    
    if len(teams_data) == 0:
        show_waiting_message("Game 3 (Memory)",
                           "Teams will appear here after completing Tech Check. Rankings will update as teams complete memory rounds.")
        return
    
    # Get memory data (refresh from database)
    memory_data = db.get_game_data(3)
    
    # Only show analysis if there's data
    if len(memory_data) == 0:
        st.info("📊 Statistics and visualizations will appear once teams complete memory rounds.")
        # Show data table at the end even if no data yet
        _show_editable_data_table(db, teams_data, memory_data)
        return
    
    st.success(f"**{len(memory_data.groupby('team_name'))} teams** have completed Game 3 (Memory)")
    
    st.markdown("#### Memory Game Results")
    
    # Team scores
    team_scores = memory_data.groupby('team_name')['is_correct'].agg(['sum', 'count']).reset_index()
    team_scores.columns = ['team_name', 'correct_answers', 'total_rounds']
    team_scores['percentage'] = (team_scores['correct_answers'] / team_scores['total_rounds']) * 100
    team_scores = team_scores.sort_values('percentage', ascending=False)
    
    # Display rankings
    st.markdown("**🏆 Team Rankings:**")
    medals = ["🥇", "🥈", "🥉"]
    for i, (_, team) in enumerate(team_scores.iterrows()):
        medal = medals[i] if i < 3 else "🏅"
        st.write(f"{medal} **{team['team_name']}**: {team['correct_answers']}/{team['total_rounds']} ({team['percentage']:.0f}%)")
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2 = st.tabs(["Team Performance", "Answer Distribution per Round"])
    
    with viz_tab1:
        _show_team_performance(team_scores)
    
    with viz_tab2:
        _show_answer_distribution_per_round(memory_data)
    
    # Data table at the end
    _show_editable_data_table(db, teams_data, memory_data)


def _show_editable_data_table(db, teams_data, memory_data):
    """Show simplified editable data table at the end."""
    st.markdown("---")
    st.markdown("#### Data Table (Editable)")
    
    # Prepare simplified data for editing
    edit_data = teams_data[['team_name', 'parent_name', 'child_name']].copy()
    
    # Add simple round answer columns
    for round_num in range(1, 4):  # 3 rounds
        edit_data[f'round_{round_num}'] = None
    
    # Fill in existing answers (only rounds 1-3)
    if len(memory_data) > 0:
        for _, row in memory_data.iterrows():
            round_num = int(row["round_number"])
            if round_num <= 3:  # Only process rounds 1-3
                team_mask = edit_data['team_name'] == row['team_name']
                round_col = f'round_{round_num}'
                edit_data.loc[team_mask, round_col] = row['team_answer']
    
    # Configure columns
    column_config = {
        "team_name": st.column_config.TextColumn("Team Name", disabled=True),
        "parent_name": st.column_config.TextColumn("Parent Name", disabled=True),
        "child_name": st.column_config.TextColumn("Child Name", disabled=True),
    }
    
    for round_num in range(1, 4):  # 3 rounds
        column_config[f'round_{round_num}'] = st.column_config.SelectboxColumn(
            f"Round {round_num}",
            options=["A", "B", "C", "D"],
            help=f"Round {round_num} answer"
        )
    
    edited_df = st.data_editor(
        edit_data,
        use_container_width=True,
        num_rows="fixed",
        column_config=column_config,
        hide_index=True,
        key="game3_editor"
    )
    
    # Save changes button
    if st.button("💾 Save Changes", key="save_game3"):
        from utils.helpers import get_molecule_questions
        questions = get_molecule_questions()
        
        changes_saved = False
        for _, row in edited_df.iterrows():
            for round_num in range(1, 4):  # 3 rounds
                answer_col = f'round_{round_num}'
                if pd.notna(row[answer_col]):
                    correct_answer = questions[round_num - 1]['correct']
                    success = db.save_game3_data(
                        row['team_name'],
                        round_num,
                        correct_answer,
                        row[answer_col]
                    )
                    if success:
                        changes_saved = True
        
        if changes_saved:
            st.success("✅ Changes saved successfully!")
            st.rerun()
        else:
            st.warning("⚠️ No valid data to save.")


def _show_team_performance(team_scores):
    """Show team performance bar chart."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=team_scores['team_name'],
        y=team_scores['percentage'],
        marker_color=[config.COLOR_ORANGE_1 if i == 0 else config.COLOR_GRAY_3 if i == 1 
                     else config.COLOR_ORANGE_4 if i == 2 else config.COLOR_LIGHT_BLUE 
                     for i in range(len(team_scores))],
        text=team_scores['percentage'].apply(lambda x: f'{x:.0f}%'),
        textposition='outside'
    ))
    fig.update_layout(
        title="Team Leistung - Memory Spiel",
        xaxis_title="Team",
        yaxis_title="Erfolgsquote (%)",
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        height=500,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_answer_distribution_per_round(memory_data):
    """Show which teams chose which answers for each round."""
    st.markdown("**Antwortverteilung: Welche Teams haben A, B, C, D für jede Runde gewählt**")
    
    rounds = sorted(memory_data['round_number'].unique())
    
    # Initialize session state for showing answers
    if 'show_answers' not in st.session_state:
        st.session_state.show_answers = {}
    
    for round_num in rounds:
        round_data = memory_data[memory_data['round_number'] == round_num]
        
        st.markdown(f"##### Runde {int(round_num)}")
        
        # Button to reveal correct answer
        col1, col2 = st.columns([3, 1])
        with col2:
            button_key = f"reveal_round_{int(round_num)}"
            if st.button("Antwort zeigen", key=button_key, 
                        type="secondary", use_container_width=True):
                # Toggle the state
                st.session_state.show_answers[round_num] = not st.session_state.show_answers.get(round_num, False)
        
        # Check if answer should be shown
        show_answer = st.session_state.show_answers.get(round_num, False)
        
        # Count answers
        answer_counts = round_data['team_answer'].value_counts().sort_index()
        all_options = ['A', 'B', 'C', 'D']
        
        # Create bar chart
        fig = go.Figure()
        
        # Get correct answer
        correct_answer = round_data['correct_answer'].iloc[0] if len(round_data) > 0 else None
        
        # Use colors based on whether answer is revealed
        if show_answer:
            # Highlight correct answer in green when revealed
            colors = [config.COLOR_SUCCESS if option == correct_answer else config.COLOR_LIGHT_BLUE 
                     for option in all_options]
        else:
            # Use uniform colors when not revealed
            colors = [config.COLOR_LIGHT_BLUE for _ in all_options]
        
        counts = [answer_counts.get(option, 0) for option in all_options]
        
        fig.add_trace(go.Bar(
            x=all_options,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='outside',
            showlegend=False
        ))
        
        # Show correct answer in title if button clicked
        chart_title = f"Richtige Antwort: {correct_answer}" if show_answer else "Antwortverteilung"
        
        fig.update_layout(
            xaxis_title="Antwort Option",
            yaxis_title="Anzahl Teams",
            xaxis_title_font=dict(size=20, color='black', family='Arial'),
            yaxis_title_font=dict(size=20, color='black', family='Arial'),
            height=400,
            title=chart_title
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"answer_dist_round_{int(round_num)}")
        
        # Show which teams chose what
        with st.expander(f"Teamdetails für Runde {int(round_num)} anzeigen"):
            for option in all_options:
                teams_with_option = round_data[round_data['team_answer'] == option]['team_name'].tolist()
                if teams_with_option:
                    st.write(f"**{option}:** {', '.join(teams_with_option)}")
                else:
                    st.write(f"**{option}:** (keine Teams)")

