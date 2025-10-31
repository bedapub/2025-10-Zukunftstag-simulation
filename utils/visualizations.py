"""
Visualization utilities for the Zukunftstag simulation application.
Centralized chart creation functions to avoid code duplication.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import config

def create_height_histogram(df, height_col, title, color):
    """Create histogram for height data."""
    fig = px.histogram(
        df, 
        x=height_col, 
        nbins=10,
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        xaxis_title="Height (cm)",
        yaxis_title="Frequency",
        showlegend=False
    )
    
    # Add individual points
    fig.add_trace(
        go.Scatter(
            x=df[height_col],
            y=[0] * len(df),
            mode='markers',
            marker=dict(color=color, size=12, symbol='diamond'),
            name='Individual measurements',
            hovertemplate='%{text}<br>Height: %{x} cm<extra></extra>',
            text=[f"{row['team_name']}<br>{row.get('parent_name', 'Parent') if 'parent' in height_col else row.get('child_name', 'Child')}" 
                  for _, row in df.iterrows()]
        )
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, title, hover_data=None):
    """Create scatter plot with correlation line."""
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        hover_data=hover_data
    )
    
    # Add correlation line
    correlation = np.corrcoef(df[x_col], df[y_col])[0, 1]
    z = np.polyfit(df[x_col], df[y_col], 1)
    p = np.poly1d(z)
    
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=p(df[x_col]),
            mode='lines',
            name=f'Correlation line (r={correlation:.2f})',
            line=dict(color=config.COLOR_PRIMARY)
        )
    )
    
    # Add median lines
    median_x = df[x_col].median()
    median_y = df[y_col].median()
    
    fig.add_hline(
        y=median_y, 
        line_dash="dash", 
        line_color="purple",
        annotation_text=f"Median {y_col.split('_')[0]}: {median_y:.1f}"
    )
    
    fig.add_vline(
        x=median_x, 
        line_dash="dash", 
        line_color="purple",
        annotation_text=f"Median {x_col.split('_')[0]}: {median_x:.1f}"
    )
    
    return fig

def create_boxplot(df, value_cols, titles, ground_truth=None):
    """Create side-by-side boxplots."""
    fig = go.Figure()
    
    for i, (col, title) in enumerate(zip(value_cols, titles)):
        fig.add_trace(
            go.Box(
                y=df[col],
                name=title,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                customdata=df[['team_name']],
                hovertemplate='%{customdata[0]}<br>Value: %{y}<extra></extra>'
            )
        )
    
    if ground_truth is not None:
        fig.add_hline(
            y=ground_truth,
            line_dash="solid",
            line_color="red",
            line_width=3,
            annotation_text=f"True value: {ground_truth}"
        )
    
    fig.update_layout(
        title="Distribution Comparison",
        yaxis_title="Value",
        showlegend=True
    )
    
    return fig

def create_perimeter_ranking_chart(df, ground_truth=28):
    """Create ranking chart for perimeter estimates."""
    df_sorted = df.sort_values('parent_abs_delta')
    
    fig = go.Figure()
    
    # Parent estimates
    fig.add_trace(
        go.Bar(
            y=df_sorted['team_name'],
            x=df_sorted['parent_delta'],
            orientation='h',
            name='Parent',
            marker_color=config.BLUE_LIGHT,
            customdata=df_sorted[['parent_estimate', 'parent_name']],
            hovertemplate='%{y}<br>%{customdata[1]}<br>Estimate: %{customdata[0]}m<br>Difference: %{x:+.1f}m<extra></extra>'
        )
    )
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=2)
    
    # Mark top 3 performers
    top_3_parent = df_sorted.nsmallest(3, 'parent_abs_delta')
    for i, (_, row) in enumerate(top_3_parent.iterrows()):
        fig.add_annotation(
            x=row['parent_delta'],
            y=row['team_name'],
            text="⭐",
            showarrow=False,
            font=dict(size=20)
        )
    
    fig.update_layout(
        title="Perimeter Estimation Results - Parents",
        xaxis_title="Difference from True Value (m)",
        yaxis_title="Teams",
        height=max(400, len(df) * 25)
    )
    
    return fig

def create_clinical_trial_boxplot(df_melted):
    """Create boxplot for clinical trial results."""
    fig = px.box(
        df_melted,
        x='treatment',
        y='pain_score',
        color='timepoint',
        title="Clinical Trial Results: Pain Scores by Treatment"
    )
    
    # Add individual points
    fig.add_trace(
        go.Scatter(
            x=df_melted['treatment'],
            y=df_melted['pain_score'],
            mode='markers',
            marker=dict(color=config.COLOR_ERROR, size=8),
            name='Individual scores',
            customdata=df_melted[['team_name', 'person', 'timepoint']],
            hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>%{customdata[2]}: %{y}<extra></extra>'
        )
    )
    
    fig.update_layout(
        xaxis_title="Treatment",
        yaxis_title="Pain Score (0-10)",
        yaxis=dict(range=[0, 10])
    )
    
    return fig

def create_memory_game_results(df):
    """Create bar chart for memory game results."""
    # Count correct answers per team
    team_scores = df.groupby('team_name')['is_correct'].sum().reset_index()
    team_scores = team_scores.sort_values('is_correct', ascending=False)
    
    fig = px.bar(
        team_scores,
        x='team_name',
        y='is_correct',
        title="Memory Game Results - Correct Answers per Team",
        color='is_correct',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Team",
        yaxis_title="Correct Answers",
        xaxis_tickangle=45
    )
    
    return fig

def create_round_results_chart(df, round_num):
    """Create chart showing team choices for a specific round."""
    round_data = df[df['round_number'] == round_num]
    choice_counts = round_data['team_answer'].value_counts()
    
    fig = px.bar(
        x=choice_counts.index,
        y=choice_counts.values,
        title=f"Round {round_num} - Team Choices",
        labels={'x': 'Choice', 'y': 'Number of Teams'}
    )
    
    # Highlight correct answer
    correct_answer = round_data['correct_answer'].iloc[0] if len(round_data) > 0 else None
    if correct_answer:
        colors = [config.COLOR_SUCCESS if x == correct_answer else config.BLUE_LIGHT for x in choice_counts.index]
        fig.update_traces(marker_color=colors)
    
    return fig

def create_feedback_summary(df):
    """Create summary charts for feedback data."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution
        rating_counts = df['overall_rating'].value_counts().sort_index()
        fig_rating = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            title="Overall Rating Distribution",
            labels={'x': 'Rating (1-5)', 'y': 'Number of Teams'}
        )
        st.plotly_chart(fig_rating, width="stretch")
    
    with col2:
        # Favorite game distribution
        game_counts = df['favorite_game'].value_counts()
        fig_games = px.pie(
            values=game_counts.values,
            names=game_counts.index,
            title="Favorite Game Distribution"
        )
        st.plotly_chart(fig_games, width="stretch")

def display_statistics_explanation():
    """Display educational content about statistics concepts."""
    with st.expander("📊 Statistical Concepts Explained"):
        st.markdown("""
        ### Key Concepts We're Learning:
        
        **Histogram**: Shows how data is distributed. Taller bars mean more people have that value.
        
        **Median**: The middle value when all numbers are arranged in order. It's not affected by extreme values.
        
        **Correlation**: How two variables relate to each other. Do taller parents tend to have taller children?
        
        **Boxplot**: Shows the spread of data with the median line in the middle and outliers as dots.
        
        **Clinical Trial**: A scientific way to test if a treatment works by comparing it to a placebo (fake treatment).
        """)


def create_rating_distribution_chart(feedback_df):
    """Create bar chart for feedback rating distribution."""
    rating_counts = feedback_df['overall_rating'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rating_counts.index,
        y=rating_counts.values,
        marker_color=[config.COLOR_ERROR if x <= 2 else config.COLOR_WARNING if x == 3 else config.BLUE_LIGHT if x == 4 else config.COLOR_SUCCESS 
                     for x in rating_counts.index],
        text=rating_counts.values,
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Overall Rating Distribution",
        xaxis_title="Rating (1-5 stars)",
        yaxis_title="Number of Teams",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        height=400
    )
    
    return fig


def create_favorite_game_pie_chart(feedback_df):
    """Create pie chart for favorite game distribution."""
    favorite_counts = feedback_df['favorite_game'].value_counts()
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=favorite_counts.index,
        values=favorite_counts.values,
        hole=0.3
    ))
    
    fig.update_layout(
        title="Which game did teams enjoy most?",
        height=400
    )
    
    return fig


def create_team_performance_bar_chart(team_scores, title="Team Performance"):
    """Create horizontal bar chart for team performance with medals for top 3."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=team_scores['team_name'],
        y=team_scores['percentage'],
        marker_color=[config.GOLD if i == 0 else config.SILVER if i == 1 else config.BRONZE if i == 2 else config.BLUE_LIGHT 
                     for i in range(len(team_scores))],
        text=team_scores['percentage'].apply(lambda x: f'{x:.0f}%'),
        textposition='outside'
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Team",
        yaxis_title="Success Rate (%)",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def create_perimeter_winners_chart(perimeter_data, person_col, delta_col, abs_delta_col, title, color):
    """Create horizontal bar chart for perimeter estimation winners."""
    sorted_data = perimeter_data.sort_values(abs_delta_col)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_data['team_name'],
        x=sorted_data[delta_col],
        orientation='h',
        marker_color=[color if i >= 3 else config.COLOR_WARNING for i in range(len(sorted_data))]
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Difference from actual (m)",
        yaxis_title="Team",
        height=600
    )
    fig.add_vline(x=0, line_dash="solid", line_color="black")
    
    return fig


def create_clinical_treatment_comparison(placebo_data, molekul_data):
    """Create boxplot comparing clinical trial treatment groups before/after."""
    fig = go.Figure()
    
    # Placebo Before
    fig.add_trace(go.Box(
        y=placebo_data['parent_before'],
        name='Placebo Before',
        marker_color=config.COLOR_PLACEBO_LIGHT,
        boxmean=True,
        x0='Placebo',
        offsetgroup='Before'
    ))
    
    # Placebo After
    fig.add_trace(go.Box(
        y=placebo_data['parent_after'],
        name='Placebo After',
        marker_color=config.COLOR_PLACEBO,
        boxmean=True,
        x0='Placebo',
        offsetgroup='After'
    ))
    
    # Medicine Before
    fig.add_trace(go.Box(
        y=molekul_data['parent_before'],
        name='Medicine Before',
        marker_color=config.COLOR_MEDICINE_LIGHT,
        boxmean=True,
        x0='Medicine',
        offsetgroup='Before'
    ))
    
    # Medicine After
    fig.add_trace(go.Box(
        y=molekul_data['parent_after'],
        name='Medicine After',
        marker_color=config.COLOR_MEDICINE,
        boxmean=True,
        x0='Medicine',
        offsetgroup='After'
    ))
    
    fig.update_layout(
        title="Clinical Trial Results: Before vs After Treatment",
        yaxis_title="Pain Score (0-10)",
        xaxis_title="Treatment Group",
        height=500,
        boxmode='group',
        showlegend=True
    )
    
    return fig


def add_correlation_line(fig, x_data, y_data, x_col_name, y_col_name):
    """Add correlation line and median markers to a scatter plot."""
    # Add correlation line
    correlation = x_data.corr(y_data)
    z = np.polyfit(x_data, y_data, 1)
    p = np.poly1d(z)
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=p(x_data),
        mode='lines',
        name=f'Correlation line (r={correlation:.2f})',
        line=dict(color=config.COLOR_PRIMARY, width=3)
    ))
    
    # Add median lines
    median_x = x_data.median()
    median_y = y_data.median()
    
    fig.add_hline(y=median_y, line_dash="dash", line_color=config.PURPLE_BASE,
                 annotation_text=f"Median {y_col_name}: {median_y:.1f} cm")
    fig.add_vline(x=median_x, line_dash="dash", line_color=config.PURPLE_BASE,
                 annotation_text=f"Median {x_col_name}: {median_x:.1f} cm")
    
    return fig
