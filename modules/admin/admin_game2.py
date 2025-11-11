"""Game 2 (Perimeter) visualization and analysis for admin dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import display_winners, display_statistics, show_waiting_message


def show_game2_analysis(db):
    """Display Game 2 (Perimeter) analysis."""
    # Get teams that have completed tech check
    teams_data = db.get_all_teams()
    
    if len(teams_data) == 0:
        show_waiting_message("Game 2 (Perimeter)",
                           "Teams will appear here after completing Tech Check. Results will update as teams submit their perimeter estimates.")
        return
    
    # Get perimeter data (refresh from database)
    perimeter_data = db.get_game_data(2)
    
    # Merge with team info for analysis
    if len(perimeter_data) > 0:
        perimeter_data = perimeter_data.merge(teams_data[['team_name', 'parent_name', 'child_name']], on='team_name', how='left')
    
    # Only show analysis if there's data
    if len(perimeter_data) == 0:
        st.info("📊 Statistics and visualizations will appear once teams submit their perimeter estimates.")
        # Show data table at the end even if no data yet
        _show_editable_data_table(db, teams_data, perimeter_data)
        return
    
    st.success(f"**{len(perimeter_data)} teams** have completed Game 2 (Perimeter)")
    
    # Winners
    st.markdown("#### Perimeter Estimation Results")
    col1, col2 = st.columns(2)
    
    with col1:
        display_winners(perimeter_data, 'parent_abs_delta', 'parent_name', 'team_name', 
                       title="🏆 Eltern Gewinner (Top 3)")
    
    with col2:
        display_winners(perimeter_data, 'child_abs_delta', 'child_name', 'team_name',
                       title="🏆 Kind Gewinner (Top 3)")
    
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
    
    # Data table at the end
    _show_editable_data_table(db, teams_data, perimeter_data)


def _show_editable_data_table(db, teams_data, perimeter_data):
    """Show editable data table at the end."""
    st.markdown("---")
    st.markdown("#### Data Table (Editable)")
    
    # Prepare data for editing - always refresh from database
    edit_data = teams_data[['team_name', 'parent_name', 'child_name']].copy()
    
    # Add perimeter columns - merge fresh data from database
    if len(perimeter_data) > 0:
        edit_data = edit_data.merge(
            perimeter_data[['team_name', 'parent_estimate', 'child_estimate']], 
            on='team_name', 
            how='left'
        )
    else:
        edit_data['parent_estimate'] = None
        edit_data['child_estimate'] = None
    
    # Make editable
    edited_df = st.data_editor(
        edit_data,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "team_name": st.column_config.TextColumn("Team Name", disabled=True),
            "parent_name": st.column_config.TextColumn("Parent Name", disabled=True),
            "child_name": st.column_config.TextColumn("Child Name", disabled=True),
            "parent_estimate": st.column_config.NumberColumn("Parent Estimate (m)", min_value=0, max_value=100, format="%.1f"),
            "child_estimate": st.column_config.NumberColumn("Child Estimate (m)", min_value=0, max_value=100, format="%.1f"),
        },
        hide_index=True,
        key="game2_editor"
    )
    
    # Save changes button
    if st.button("💾 Save Changes", key="save_game2"):
        changes_saved = False
        for _, row in edited_df.iterrows():
            if pd.notna(row['parent_estimate']) and pd.notna(row['child_estimate']):
                success = db.save_game2_data(row['team_name'], float(row['parent_estimate']), float(row['child_estimate']))
                if success:
                    changes_saved = True
        
        if changes_saved:
            st.success("✅ Changes saved successfully!")
            st.rerun()
        else:
            st.warning("⚠️ No valid data to save.")


def _show_histogram(perimeter_data):
    """Show perimeter estimates histogram."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=perimeter_data['parent_estimate'],
        name='Eltern',
        marker_color=config.COLOR_PARENT,
        opacity=0.7
    ))
    fig.add_trace(go.Histogram(
        x=perimeter_data['child_estimate'],
        name='Kinder',
        marker_color=config.COLOR_CHILD,
        opacity=0.7
    ))
    
    # Add ground truth line
    actual_perimeter = 28
    fig.add_vline(x=actual_perimeter, line_dash="solid", line_color=config.COLOR_ERROR, 
                  annotation_text=f"Actual: {actual_perimeter}m", line_width=3)
    
    fig.update_layout(
        title="Umfangsschätzungen Verteilung",
        xaxis_title="Schätzung (Meter)",
        yaxis_title="Häufigkeit",
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
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
            title="Eltern Schätzungen (sortiert nach Genauigkeit)",
            xaxis_title="Abweichung vom tatsächlichen Wert (m)",
            yaxis_title="Team",
            xaxis_title_font=dict(size=20, color='black', family='Arial'),
            yaxis_title_font=dict(size=20, color='black', family='Arial'),
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
            title="Kind Schätzungen (sortiert nach Genauigkeit)",
            xaxis_title="Abweichung vom tatsächlichen Wert (m)",
            yaxis_title="Team",
            xaxis_title_font=dict(size=20, color='black', family='Arial'),
            yaxis_title_font=dict(size=20, color='black', family='Arial'),
            height=600
        )
        fig.add_vline(x=0, line_dash="solid", line_color="black")
        st.plotly_chart(fig, use_container_width=True)


def _show_boxplot(perimeter_data):
    """Show perimeter comparison boxplot."""
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=perimeter_data['child_estimate'],
        name='Kinder',
        marker_color=config.COLOR_CHILD,
        boxmean=True
    ))
    
    fig.add_trace(go.Box(
        y=perimeter_data['parent_estimate'],
        name='Eltern',
        marker_color='darkblue',
        boxmean=True
    ))
    
    fig.add_hline(y=28, line_dash="solid", line_color="red",
                annotation_text="Actual: 28m", line_width=3)
    
    fig.update_layout(
        title="Umfangsschätzungen Vergleich",
        yaxis_title="Schätzung (Meter)",
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
