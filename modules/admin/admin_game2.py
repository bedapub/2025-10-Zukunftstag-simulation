"""Game 2 (Perimeter) visualization and analysis for admin dashboard."""

import streamlit as st
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import display_winners, display_statistics, show_waiting_message


def show_game2_analysis(db):
    """Display Game 2 (Perimeter) analysis."""
    perimeter_data = db.get_game_data(2)
    
    if len(perimeter_data) == 0:
        show_waiting_message("Game 2 (Perimeter)",
                           "Results and winners will appear here automatically as teams submit their perimeter estimates.")
        return
    
    st.success(f"**{len(perimeter_data)} teams** have completed Game 2 (Perimeter)")
    
    # Merge with team names
    teams_data = db.get_all_teams()
    perimeter_data = perimeter_data.merge(teams_data[['team_name', 'parent_name', 'child_name']], on='team_name')
    
    # Winners
    st.markdown("#### Perimeter Estimation Results")
    col1, col2 = st.columns(2)
    
    with col1:
        display_winners(perimeter_data, 'parent_abs_delta', 'parent_name', 'team_name', 
                       title="🏆 Parent Winners (Top 3)")
    
    with col2:
        display_winners(perimeter_data, 'child_abs_delta', 'child_name', 'team_name',
                       title="🏆 Child Winners (Top 3)")
    
    # Statistics
    st.markdown("#### Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Parent estimates:**")
        st.write(f"Mean: {perimeter_data['parent_estimate'].mean():.1f}m")
        st.write(f"Median: {perimeter_data['parent_estimate'].median():.1f}m")
        st.write(f"Mean error: {perimeter_data['parent_abs_delta'].mean():.1f}m")
    
    with col2:
        st.write("**Child estimates:**")
        st.write(f"Mean: {perimeter_data['child_estimate'].mean():.1f}m")
        st.write(f"Median: {perimeter_data['child_estimate'].median():.1f}m")
        st.write(f"Mean error: {perimeter_data['child_abs_delta'].mean():.1f}m")
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Histograms", "Winners Bar Chart", "Boxplot"])
    
    with viz_tab1:
        _show_histogram(perimeter_data)
    
    with viz_tab2:
        _show_winners_chart(perimeter_data)
    
    with viz_tab3:
        _show_boxplot(perimeter_data)
    
    # Data table
    st.markdown("#### Data Table")
    display_perimeter = perimeter_data[['team_name', 'parent_name', 'parent_estimate', 'parent_delta', 
                                      'child_name', 'child_estimate', 'child_delta']]
    st.dataframe(display_perimeter, width="stretch")


def _show_histogram(perimeter_data):
    """Show perimeter estimates histogram."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=perimeter_data['parent_estimate'],
        name='Parent Estimates',
        marker_color=config.COLOR_PARENT,
        opacity=0.7
    ))
    fig.add_trace(go.Histogram(
        x=perimeter_data['child_estimate'],
        name='Child Estimates',
        marker_color=config.COLOR_CHILD,
        opacity=0.7
    ))
    
    # Add ground truth line
    actual_perimeter = 28
    fig.add_vline(x=actual_perimeter, line_dash="solid", line_color=config.COLOR_ERROR, 
                  annotation_text=f"Actual: {actual_perimeter}m", line_width=3)
    
    fig.update_layout(
        title="Perimeter Estimates Distribution",
        xaxis_title="Estimate (meters)",
        yaxis_title="Frequency",
        barmode='overlay',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_winners_chart(perimeter_data):
    """Show winners bar charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        parent_sorted = perimeter_data.sort_values('parent_abs_delta')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=parent_sorted['team_name'],
            x=parent_sorted['parent_delta'],
            orientation='h',
            marker_color=[config.COLOR_WARNING if i < 3 else config.COLOR_LIGHT_BLUE 
                         for i in range(len(parent_sorted))]
        ))
        fig.update_layout(
            title="Parent Estimates (sorted by accuracy)",
            xaxis_title="Difference from actual (m)",
            yaxis_title="Team",
            height=600
        )
        fig.add_vline(x=0, line_dash="solid", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        child_sorted = perimeter_data.sort_values('child_abs_delta')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=child_sorted['team_name'],
            x=child_sorted['child_delta'],
            orientation='h',
            marker_color=[config.COLOR_WARNING if i < 3 else config.COLOR_LIGHT_BLUE 
                         for i in range(len(child_sorted))]
        ))
        fig.update_layout(
            title="Child Estimates (sorted by accuracy)",
            xaxis_title="Difference from actual (m)",
            yaxis_title="Team",
            height=600
        )
        fig.add_vline(x=0, line_dash="solid", line_color="black")
        st.plotly_chart(fig, use_container_width=True)


def _show_boxplot(perimeter_data):
    """Show perimeter comparison boxplot."""
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=perimeter_data['child_estimate'],
        name='Children',
        marker_color=config.COLOR_CHILD,
        boxmean=True
    ))
    
    fig.add_trace(go.Box(
        y=perimeter_data['parent_estimate'],
        name='Parents',
        marker_color='darkblue',
        boxmean=True
    ))
    
    fig.add_hline(y=28, line_dash="solid", line_color="red",
                annotation_text="Actual: 28m", line_width=3)
    
    fig.update_layout(
        title="Perimeter Estimates Comparison",
        yaxis_title="Estimate (meters)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
