"""Game 4 (Clinical Trial) visualization and analysis for admin dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config
from modules.admin.admin_helpers import create_treatment_comparison_boxplot, normalize_treatment_value, show_waiting_message


def show_game4_analysis(db):
    """Display Game 4 (Clinical Trial) analysis."""
    clinical_data = db.get_game_data(4)
    
    if len(clinical_data) == 0:
        show_waiting_message("Game 4 (Clinical Trial)",
                           "Treatment effects and statistical analysis will appear here automatically as teams complete the clinical trial simulation.")
        return
    
    st.success(f"**{len(clinical_data)} teams** have completed Game 4 (Clinical Trial)")
    
    st.markdown("#### Clinical Trial Analysis")
    
    # Prepare combined data
    combined_df = _prepare_clinical_data(clinical_data)
    
    # Calculate treatment effects
    placebo_data = combined_df[combined_df['treatment'] == 'Placebo']
    molekul_data = combined_df[combined_df['treatment'] == 'Molekül']
    
    placebo_effect = placebo_data['after'].mean() - placebo_data['before'].mean()
    molekul_effect = molekul_data['after'].mean() - molekul_data['before'].mean()
    treatment_difference = molekul_effect - placebo_effect
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Placebo Effect", f"{placebo_effect:+.1f} points")
    
    with col2:
        st.metric("Medicine Effect", f"{molekul_effect:+.1f} points")
    
    with col3:
        st.metric("Treatment Difference", f"{treatment_difference:+.1f} points")
    
    st.write(f"**Group sizes:** Placebo: {len(placebo_data)}, Medicine: {len(molekul_data)}")
    
    # Visualizations
    st.markdown("#### Visualizations")
    viz_tab1, viz_tab2 = st.tabs(["Treatment Effects Boxplot", "Individual Changes"])
    
    with viz_tab1:
        _show_treatment_boxplot(placebo_data, molekul_data)
    
    with viz_tab2:
        _show_individual_changes(placebo_data, molekul_data)
    
    # Data table
    st.markdown("#### Data Table")
    display_clinical = clinical_data[['team_name', 'parent_before', 'parent_after', 'child_before', 'child_after']]
    st.dataframe(display_clinical, width="stretch")


def _prepare_clinical_data(clinical_data):
    """Prepare combined parent and child data for clinical trial analysis."""
    all_data = []
    for _, row in clinical_data.iterrows():
        # Parent data
        all_data.append({
            'team_name': row['team_name'],
            'person': 'Parent',
            'treatment': row['parent_treatment'],
            'before': row['parent_before'],
            'after': row['parent_after']
        })
        # Child data
        all_data.append({
            'team_name': row['team_name'],
            'person': 'Child',
            'treatment': row['child_treatment'],
            'before': row['child_before'],
            'after': row['child_after']
        })
    
    combined_df = pd.DataFrame(all_data)
    combined_df['treatment'] = combined_df['treatment'].apply(normalize_treatment_value)
    
    return combined_df


def _show_treatment_boxplot(placebo_data, molekul_data):
    """Show treatment effects boxplot."""
    fig = create_treatment_comparison_boxplot(
        placebo_data['before'], placebo_data['after'],
        molekul_data['before'], molekul_data['after']
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_individual_changes(placebo_data, molekul_data):
    """Show individual patient changes visualization."""
    fig = go.Figure()
    
    # Placebo group individual changes
    for _, row in placebo_data.iterrows():
        fig.add_trace(go.Scatter(
            x=['Before', 'After'],
            y=[row['before'], row['after']],
            mode='lines+markers',
            name=f"{row['team_name']} ({row['person']})",
            line=dict(color='blue', width=1),
            marker=dict(size=8),
            legendgroup='placebo',
            showlegend=False
        ))
    
    # Medicine group individual changes
    for _, row in molekul_data.iterrows():
        fig.add_trace(go.Scatter(
            x=['Before', 'After'],
            y=[row['before'], row['after']],
            mode='lines+markers',
            name=f"{row['team_name']} ({row['person']})",
            line=dict(color='green', width=1),
            marker=dict(size=8),
            legendgroup='medicine',
            showlegend=False
        ))
    
    # Add mean lines
    fig.add_trace(go.Scatter(
        x=['Before', 'After'],
        y=[placebo_data['before'].mean(), placebo_data['after'].mean()],
        mode='lines+markers',
        name='Placebo (mean)',
        line=dict(color='blue', width=4),
        marker=dict(size=12)
    ))
    
    fig.add_trace(go.Scatter(
        x=['Before', 'After'],
        y=[molekul_data['before'].mean(), molekul_data['after'].mean()],
        mode='lines+markers',
        name='Medicine (mean)',
        line=dict(color='green', width=4),
        marker=dict(size=12)
    ))
    
    fig.update_layout(
        title="Individual Patient Changes: Before vs After Treatment",
        yaxis_title="Pain Score (0-10)",
        xaxis_title="Time Point",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
