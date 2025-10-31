"""Game 3 (Memory) visualization and analysis for admin dashboard."""

import streamlit as st
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import show_waiting_message


def show_game3_analysis(db):
    """Display Game 3 (Memory) analysis."""
    memory_data = db.get_game_data(3)
    
    if len(memory_data) == 0:
        show_waiting_message("Game 3 (Memory)",
                           "Team rankings and round statistics will appear here automatically as teams complete memory rounds.")
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
    
    # Round difficulty analysis
    st.markdown("#### Round Difficulty Analysis")
    round_stats = memory_data.groupby('round_number')['is_correct'].agg(['sum', 'count', 'mean']).reset_index()
    round_stats.columns = ['round_number', 'correct_answers', 'total_teams', 'success_rate']
    round_stats['success_rate'] *= 100
    
    for _, round_data in round_stats.iterrows():
        difficulty = "Easy" if round_data['success_rate'] >= 70 else "Medium" if round_data['success_rate'] >= 40 else "Hard"
        st.write(f"**Round {int(round_data['round_number'])}**: {round_data['success_rate']:.0f}% success ({difficulty})")
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2 = st.tabs(["Team Performance", "Round Difficulty"])
    
    with viz_tab1:
        _show_team_performance(team_scores)
    
    with viz_tab2:
        _show_round_difficulty(round_stats)
    
    # Data table
    st.markdown("#### Data Table")
    display_memory = memory_data[['team_name', 'round_number', 'correct_answer', 'team_answer', 'is_correct']]
    st.dataframe(display_memory, width="stretch")


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
        title="Team Performance - Memory Game",
        xaxis_title="Team",
        yaxis_title="Success Rate (%)",
        height=500,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_round_difficulty(round_stats):
    """Show round difficulty visualization."""
    colors = [config.COLOR_SUCCESS if rate >= 70 else config.COLOR_WARNING if rate >= 40 
             else config.COLOR_ERROR for rate in round_stats['success_rate']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Round {int(r)}" for r in round_stats['round_number']],
        y=round_stats['success_rate'],
        marker_color=colors,
        text=round_stats['success_rate'].apply(lambda x: f'{x:.0f}%'),
        textposition='outside'
    ))
    fig.update_layout(
        title="Round Difficulty Analysis",
        xaxis_title="Round",
        yaxis_title="Success Rate (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
