"""Helper functions for admin dashboard visualizations."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import config


def create_histogram_with_points(data, column, title, color, person_names_col=None, team_names_col=None):
    """Create a histogram with individual data points overlay."""
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=data[column],
        nbinsx=10,
        marker_color=color,
        name='Distribution',
        showlegend=False
    ))
    
    # Individual points
    hover_text = None
    if team_names_col and person_names_col:
        hover_text = [f"{row[team_names_col]}<br>{row[person_names_col]}" 
                     for _, row in data.iterrows()]
    
    fig.add_trace(go.Scatter(
        x=data[column],
        y=[0] * len(data),
        mode='markers',
        marker=dict(color=color, size=10, symbol='diamond'),
        name='Messung',
        hovertemplate='%{text}<br>Wert: %{x}<extra></extra>' if hover_text else None,
        text=hover_text
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=column.replace('_', ' ').title(),
        yaxis_title="Häufigkeit",
        height=600,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=80)
    )
    
    return fig


def create_boxplot_comparison(data1, data2, name1, name2, color1, color2, title, y_label, 
                              custom_data1=None, custom_data2=None):
    """Create a boxplot comparing two datasets."""
    fig = go.Figure()
    
    # First boxplot
    fig.add_trace(go.Box(
        y=data1,
        name=name1,
        marker_color=color1,
        boxmean=True,
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        customdata=custom_data1,
        hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Value: %{y}<extra></extra>' if custom_data1 is not None else None
    ))
    
    # Second boxplot
    fig.add_trace(go.Box(
        y=data2,
        name=name2,
        marker_color=color2,
        boxmean=True,
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        customdata=custom_data2,
        hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Value: %{y}<extra></extra>' if custom_data2 is not None else None
    ))
    
    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        height=600,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        legend=dict(
            font=dict(size=14, family='Arial'),
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top',
            orientation='v',
            itemwidth=30
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=80)
    )
    
    return fig


def create_bar_chart_with_highlight(data, x_col, y_col, title, x_label, y_label, 
                                    highlight_top_n=3, highlight_color=None):
    """Create a bar chart with highlighted top N entries."""
    if highlight_color is None:
        highlight_color = config.COLOR_WARNING
    
    colors = [highlight_color if i < highlight_top_n else config.COLOR_LIGHT_BLUE 
             for i in range(len(data))]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y_col],
        marker_color=colors,
        text=data[y_col].apply(lambda x: f'{x:.0f}' if isinstance(x, (int, float)) else str(x)),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=600,
        xaxis_tickangle=-45,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=80)
    )
    
    return fig


def display_winners(data, metric_col, name_col, team_col, n=3, title="Winners"):
    """Display top N winners with medals."""
    st.markdown(f"**{title}:**")
    top_performers = data.nsmallest(n, metric_col) if 'delta' in metric_col or 'error' in metric_col else data.nlargest(n, metric_col)
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (_, winner) in enumerate(top_performers.iterrows()):
        medal = medals[i] if i < 3 else "🏅"
        metric_value = winner[metric_col]
        metric_str = f"{metric_value:.1f}" if isinstance(metric_value, float) else str(metric_value)
        st.write(f"{medal} {winner[name_col]} (Team {winner[team_col]}) - {metric_str}")


def display_statistics(data, columns, prefix=""):
    """Display basic statistics for given columns."""
    for col in columns:
        st.write(f"**{prefix}{col.replace('_', ' ').title()}:**")
        st.write(f"Mean: {data[col].mean():.1f}")
        st.write(f"Median: {data[col].median():.1f}")
        if 'height' in col or 'estimate' in col:
            st.write(f"Range: {data[col].min():.1f} - {data[col].max():.1f}")


def show_waiting_message(game_name, additional_info=""):
    """Display a standardized waiting message for incomplete games."""
    st.warning(f"**Waiting for teams to complete {game_name}**")
    if additional_info:
        st.info(additional_info)
    else:
        st.info(f"Results will appear here automatically as teams complete {game_name}.")


def create_treatment_comparison_boxplot(placebo_before, placebo_after, medicine_before, medicine_after):
    """Create boxplot comparing treatment effects."""
    fig = go.Figure()
    
    # Placebo Before
    fig.add_trace(go.Box(
        y=placebo_before,
        name='Placebo Vorher',
        marker_color=config.COLOR_PLACEBO,
        boxmean=True,
        x0='Placebo',
        offsetgroup='Before'
    ))
    
    # Placebo After
    fig.add_trace(go.Box(
        y=placebo_after,
        name='Placebo Nachher',
        marker_color=config.COLOR_PLACEBO,
        boxmean=True,
        x0='Placebo',
        offsetgroup='After'
    ))
    
    # Medicine Before
    fig.add_trace(go.Box(
        y=medicine_before,
        name='Medikament Vorher',
        marker_color=config.COLOR_MEDICINE,
        boxmean=True,
        x0='Medicine',
        offsetgroup='Before'
    ))
    
    # Medicine After
    fig.add_trace(go.Box(
        y=medicine_after,
        name='Medikament Nachher',
        marker_color=config.COLOR_MEDICINE,
        boxmean=True,
        x0='Medicine',
        offsetgroup='After'
    ))
    
    fig.update_layout(
        title="Klinische Studie: Vorher vs Nachher Behandlung",
        yaxis_title="Schmerzwert (0-10)",
        xaxis_title="Behandlungsgruppe",
        height=600,
        boxmode='group',
        showlegend=True,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        legend=dict(
            font=dict(size=14, family='Arial'),
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top',
            orientation='v',
            itemwidth=30
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=80)
    )
    
    return fig


def normalize_treatment_value(treatment):
    """Normalize treatment values to handle case variations."""
    if treatment:
        treatment_lower = str(treatment).lower()
        if 'placebo' in treatment_lower:
            return 'Placebo'
        elif 'medic' in treatment_lower or 'molekül' in treatment_lower or 'molekul' in treatment_lower:
            return 'Molekül'
    return treatment
