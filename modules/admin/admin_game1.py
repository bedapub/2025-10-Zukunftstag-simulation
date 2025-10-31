"""Game 1 (Heights) visualization and analysis for admin dashboard."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import (
    create_histogram_with_points, create_boxplot_comparison,
    display_statistics, show_waiting_message
)


def show_game1_analysis(db):
    """Display Game 1 (Heights) analysis."""
    heights_data = db.get_game_data(1)
    
    if len(heights_data) == 0:
        show_waiting_message("Game 1 (Heights)", 
                           "Results will appear here automatically as teams submit their height measurements.")
        return
    
    st.success(f"**{len(heights_data)} teams** have completed Game 1 (Heights)")
    
    # Merge with team names
    teams_data = db.get_all_teams()
    heights_data = heights_data.merge(teams_data[['team_name', 'parent_name', 'child_name']], on='team_name')
    
    # Statistics
    st.markdown("#### Height Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        display_statistics(heights_data, ['parent_height'], "Parent - ")
    
    with col2:
        display_statistics(heights_data, ['child_height'], "Child - ")
    
    # Correlation
    if len(heights_data) >= 3:
        with np.errstate(all='ignore'):
            correlation = heights_data['parent_height'].corr(heights_data['child_height'])
        if not np.isnan(correlation):
            st.metric("Parent-Child Height Correlation", f"{correlation:.3f}")
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Histograms", "Boxplot", "Scatter Plot"])
    
    with viz_tab1:
        _show_histograms(heights_data)
    
    with viz_tab2:
        _show_boxplot(heights_data)
    
    with viz_tab3:
        _show_scatter_plot(heights_data)
    
    # Data table
    st.markdown("#### Data Table")
    display_heights = heights_data[['team_name', 'parent_name', 'parent_height', 'child_name', 'child_height']]
    st.dataframe(display_heights, width="stretch")


def _show_histograms(heights_data):
    """Show height distribution histograms."""
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_histogram_with_points(
            heights_data, 'parent_height', 
            "Parent Heights Distribution",
            config.COLOR_PARENT,
            'parent_name', 'team_name'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_histogram_with_points(
            heights_data, 'child_height',
            "Child Heights Distribution",
            config.COLOR_CHILD,
            'child_name', 'team_name'
        )
        st.plotly_chart(fig, use_container_width=True)


def _show_boxplot(heights_data):
    """Show height comparison boxplot."""
    custom_data_child = heights_data[['team_name', 'child_name']].values
    custom_data_parent = heights_data[['team_name', 'parent_name']].values
    
    fig = create_boxplot_comparison(
        heights_data['child_height'], heights_data['parent_height'],
        'Children', 'Parents',
        config.COLOR_CHILD, config.COLOR_PARENT,
        "Height Comparison - Boxplot with Individual Points",
        "Height (cm)",
        custom_data_child, custom_data_parent
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_scatter_plot(heights_data):
    """Show parent vs child height scatter plot."""
    fig = px.scatter(
        heights_data,
        x='parent_height',
        y='child_height',
        title="Parent vs Child Height Correlation",
        hover_data=['team_name', 'parent_name', 'child_name']
    )
    
    # Add correlation line
    if len(heights_data) >= 3:
        try:
            correlation = heights_data['parent_height'].corr(heights_data['child_height'])
            with np.errstate(all='ignore'):
                z = np.polyfit(heights_data['parent_height'], heights_data['child_height'], 1)
                p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=heights_data['parent_height'],
                y=p(heights_data['parent_height']),
                mode='lines',
                name=f'Correlation line (r={correlation:.2f})',
                line=dict(color=config.COLOR_PRIMARY, width=3)
            ))
        except:
            pass
    
    # Add median lines
    median_parent = heights_data['parent_height'].median()
    median_child = heights_data['child_height'].median()
    
    fig.add_hline(y=median_child, line_dash="dash", line_color="purple",
                 annotation_text=f"Median child: {median_child:.1f} cm")
    fig.add_vline(x=median_parent, line_dash="dash", line_color="purple",
                 annotation_text=f"Median parent: {median_parent:.1f} cm")
    
    fig.update_layout(
        xaxis_title="Parent Height (cm)",
        yaxis_title="Child Height (cm)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
