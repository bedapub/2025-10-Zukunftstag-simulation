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
    # Get teams that have completed tech check
    teams_data = db.get_all_teams()
    
    if len(teams_data) == 0:
        show_waiting_message("Game 1 (Heights)", 
                           "Teams will appear here after completing Tech Check. Results will update as teams submit their height measurements.")
        return
    
    # Get heights data (refresh from database)
    heights_data = db.get_game_data(1)
    
    # Merge with team info for analysis
    if len(heights_data) > 0:
        heights_data = heights_data.merge(teams_data[['team_name', 'parent_name', 'child_name']], on='team_name', how='left')
    
    # Only show analysis if there's data
    if len(heights_data) == 0:
        # Show data table at the end even if no data yet
        _show_editable_data_table(db, teams_data, heights_data)
        return
    
    st.success(f"**{len(heights_data)} teams** have completed Game 1 (Heights)")
    
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
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Histogramme", "Boxplot", "Streudiagramm"])
    
    with viz_tab1:
        _show_histograms(heights_data)
    
    with viz_tab2:
        _show_boxplot(heights_data)
    
    with viz_tab3:
        _show_scatter_plot(heights_data)
    
    # Data table at the end
    _show_editable_data_table(db, teams_data, heights_data)


def _show_editable_data_table(db, teams_data, heights_data):
    """Show editable data table at the end."""
    st.markdown("---")
    st.markdown("#### Data Table (Editable)")
    
    # Prepare data for editing - always refresh from database
    edit_data = teams_data[['team_name', 'parent_name', 'child_name']].copy()
    
    # Add height columns - merge fresh data from database
    if len(heights_data) > 0:
        edit_data = edit_data.merge(
            heights_data[['team_name', 'parent_height', 'child_height']], 
            on='team_name', 
            how='left'
        )
    else:
        edit_data['parent_height'] = None
        edit_data['child_height'] = None
    
    # Make editable
    edited_df = st.data_editor(
        edit_data,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "team_name": st.column_config.TextColumn("Team Name", disabled=True),
            "parent_name": st.column_config.TextColumn("Parent Name", disabled=True),
            "child_name": st.column_config.TextColumn("Child Name", disabled=True),
            "parent_height": st.column_config.NumberColumn("Parent Height (cm)", min_value=100, max_value=250, format="%.1f"),
            "child_height": st.column_config.NumberColumn("Child Height (cm)", min_value=50, max_value=200, format="%.1f"),
        },
        hide_index=True,
        key="game1_editor"
    )
    
    # Save changes button
    if st.button("💾 Save Changes", key="save_game1"):
        changes_saved = False
        for _, row in edited_df.iterrows():
            if pd.notna(row['parent_height']) and pd.notna(row['child_height']):
                success = db.save_game1_data(row['team_name'], float(row['parent_height']), float(row['child_height']))
                if success:
                    changes_saved = True
        
        if changes_saved:
            st.success("✅ Changes saved successfully!")
            st.rerun()
        else:
            st.warning("⚠️ No valid data to save.")


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
        'Kinder', 'Eltern',
        config.COLOR_CHILD, config.COLOR_PARENT,
        "Größenvergleich - Boxplot mit Einzelpunkten",
        "Größe (cm)",
        custom_data_child, custom_data_parent
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_scatter_plot(heights_data):
    """Show parent vs child height scatter plot."""
    fig = px.scatter(
        heights_data,
        x='parent_height',
        y='child_height',
        title="Eltern vs Kind Größe Korrelation",
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
                name=f'r={correlation:.2f}',
                line=dict(color=config.COLOR_PRIMARY, width=3)
            ))
        except:
            pass
    
    # Add median lines
    median_parent = heights_data['parent_height'].median()
    median_child = heights_data['child_height'].median()
    
    fig.add_hline(y=median_child, line_dash="dash", line_color="purple",
                 annotation_text=f"Median Kind: {median_child:.1f} cm")
    fig.add_vline(x=median_parent, line_dash="dash", line_color="purple",
                 annotation_text=f"Median Eltern: {median_parent:.1f} cm")
    
    fig.update_layout(
        xaxis_title="Eltern Größe (cm)",
        yaxis_title="Kind Größe (cm)",
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
