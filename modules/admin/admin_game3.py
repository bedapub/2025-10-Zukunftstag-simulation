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
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2 = st.tabs(["Team Performance", "Answer Distribution per Round"])
    
    with viz_tab1:
        _show_team_performance(team_scores)
    
    with viz_tab2:
        _show_answer_distribution_per_round(memory_data)
    
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


def _show_answer_distribution_per_round(memory_data):
    """Show which teams chose which answers for each round."""
    st.markdown("**Answer Distribution: Which teams chose A, B, C, D for each round**")
    
    rounds = sorted(memory_data['round_number'].unique())
    
    for round_num in rounds:
        round_data = memory_data[memory_data['round_number'] == round_num]
        
        st.markdown(f"##### Round {int(round_num)}")
        
        # Button to reveal correct answer
        col1, col2 = st.columns([3, 1])
        with col2:
            show_answer = st.button("Answer", key=f"reveal_round_{int(round_num)}", 
                                   type="secondary", use_container_width=True)
        
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
        chart_title = f"Correct Answer: {correct_answer}" if show_answer else "Answer Distribution"
        
        fig.update_layout(
            xaxis_title="Answer Option",
            yaxis_title="Number of Teams",
            height=300,
            title=chart_title
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"answer_dist_round_{int(round_num)}")
        
        # Show which teams chose what
        with st.expander(f"View team details for Round {int(round_num)}"):
            for option in all_options:
                teams_with_option = round_data[round_data['team_answer'] == option]['team_name'].tolist()
                if teams_with_option:
                    st.write(f"**{option}:** {', '.join(teams_with_option)}")
                else:
                    st.write(f"**{option}:** (keine Teams)")

