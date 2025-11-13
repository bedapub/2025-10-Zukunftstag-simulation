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
import plotly.io as pio

pio.templates["custom"] = go.layout.Template(
    layout=go.Layout(
        font=dict(size=18, color='black', family='Arial'),
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis=dict(
            title_font=dict(size=20, color='black', family='Arial'),
            tickfont=dict(size=18, color='black', family='Arial')
        ),
        yaxis=dict(
            title_font=dict(size=20, color='black', family='Arial'),
            tickfont=dict(size=18, color='black', family='Arial')
        ),
        legend=dict(
            font=dict(size=14, color='black', family='Arial'),
            orientation='v',
            itemwidth=30
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
)
pio.templates.default = "custom"

def create_height_histogram(df, height_col, title, color):
    """Create histogram for height data."""
    dark_color = config.COLOR_ORANGE_1 if color in [config.COLOR_ORANGE_2, config.COLOR_PEACH_3] else config.COLOR_PRIMARY_BLUE
    
    fig = px.histogram(
        df, 
        x=height_col, 
        nbins=10,
        title=title,
        color_discrete_sequence=[dark_color]
    )
    
    fig.update_layout(
        xaxis_title="Größe (cm)",
        yaxis_title="Häufigkeit",
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
        margin=dict(l=120, r=280, t=100, b=80),
        width=None,
        height=600
    )
    
    # Add individual points
    fig.add_trace(
        go.Scatter(
            x=df[height_col],
            y=[0] * len(df),
            mode='markers',
            marker=dict(color=dark_color, size=16, symbol='diamond'),
            name='Messung',
            hovertemplate='%{text}<br>Größe: %{x} cm<extra></extra>',
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
    
    fig.update_traces(marker=dict(size=12, color=config.COLOR_PRIMARY_BLUE, line=dict(width=2, color='white')))
    
    # Add correlation line
    correlation = np.corrcoef(df[x_col], df[y_col])[0, 1]
    z = np.polyfit(df[x_col], df[y_col], 1)
    p = np.poly1d(z)
    
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=p(df[x_col]),
            mode='lines',
            name=f'r={correlation:.2f}',
            line=dict(color=config.COLOR_RED_2, width=4)
        )
    )
    
    # Add median lines
    median_x = df[x_col].median()
    median_y = df[y_col].median()
    
    fig.add_hline(
        y=median_y, 
        line_dash="dash", 
        line_color=config.COLOR_PURPLE_1,
        line_width=3,
        annotation_text=f"Median {y_col.split('_')[0]}: {median_y:.1f}",
        annotation_font_size=18
    )
    
    fig.add_vline(
        x=median_x, 
        line_dash="dash", 
        line_color=config.COLOR_PURPLE_1,
        line_width=3,
        annotation_text=f"Median {x_col.split('_')[0]}: {median_x:.1f}",
        annotation_font_size=18
    )
    
    fig.update_layout(
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

def create_boxplot(df, value_cols, titles, ground_truth=None):
    """Create side-by-side boxplots."""
    fig = go.Figure()
    
    box_colors = [config.COLOR_ORANGE_1, config.COLOR_PRIMARY_BLUE, config.COLOR_PURPLE_1]
    
    for i, (col, title) in enumerate(zip(value_cols, titles)):
        fig.add_trace(
            go.Box(
                y=df[col],
                name=title,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8,
                customdata=df[['team_name']],
                hovertemplate='%{customdata[0]}<br>Value: %{y}<extra></extra>',
                marker=dict(color=box_colors[i % len(box_colors)], size=8, line=dict(width=2)),
                line=dict(width=3)
            )
        )
    
    if ground_truth is not None:
        fig.add_hline(
            y=ground_truth,
            line_dash="solid",
            line_color=config.COLOR_RED_1,
            line_width=4,
            annotation_text=f"Wahrer Wert: {ground_truth}",
            annotation_font_size=18
        )
    
    fig.update_layout(
        title="Verteilungsvergleich",
        yaxis_title="Wert",
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

def create_perimeter_ranking_chart(df, ground_truth=61.4):
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
            marker_color=config.COLOR_ORANGE_1,
            customdata=df_sorted[['parent_estimate', 'parent_name']],
            hovertemplate='%{y}<br>%{customdata[1]}<br>Estimate: %{customdata[0]}m<br>Difference: %{x:+.1f}m<extra></extra>'
        )
    )
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=3)
    
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
        title="Umfangsschätzung Ergebnisse - Eltern",
        xaxis_title="Abweichung vom wahren Wert (m)",
        yaxis_title="Teams",
        height=max(400, len(df) * 25),
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=80, t=100, b=80)
    )
    
    return fig

def create_clinical_trial_boxplot(df_melted):
    """Create boxplot for clinical trial results."""
    fig = px.box(
        df_melted,
        x='treatment',
        y='pain_score',
        color='timepoint',
        title="Klinische Studie: Schmerzwerte nach Behandlung",
        color_discrete_map={'Before': config.COLOR_GRAY_2, 'After': config.COLOR_PURPLE_1}
    )
    
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    
    fig.add_trace(
        go.Scatter(
            x=df_melted['treatment'],
            y=df_melted['pain_score'],
            mode='markers',
            marker=dict(color=config.COLOR_RED_2, size=10, line=dict(width=2, color='white')),
            name='Messung',
            customdata=df_melted[['team_name', 'person', 'timepoint']],
            hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>%{customdata[2]}: %{y}<extra></extra>'
        )
    )
    
    fig.update_layout(
        xaxis_title="Behandlung",
        yaxis_title="Schmerzwert (0-10)",
        yaxis=dict(range=[0, 10]),
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

def create_memory_game_results(df):
    """Create bar chart for memory game results."""
    # Count correct answers per team
    team_scores = df.groupby('team_name')['is_correct'].sum().reset_index()
    team_scores = team_scores.sort_values('is_correct', ascending=False)
    
    fig = px.bar(
        team_scores,
        x='team_name',
        y='is_correct',
        title="Memory Spiel Ergebnisse - Richtige Antworten pro Team",
        color='is_correct',
        color_continuous_scale=[[0, config.COLOR_RED_1], [0.5, config.COLOR_ORANGE_1], [1, config.COLOR_PRIMARY_BLUE]]
    )
    
    fig.update_layout(
        xaxis_title="Team",
        yaxis_title="Richtige Antworten",
        xaxis_tickangle=45,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=120)
    )
    
    return fig

def create_round_results_chart(df, round_num):
    """Create chart showing team choices for a specific round."""
    round_data = df[df['round_number'] == round_num]
    choice_counts = round_data['team_answer'].value_counts()
    
    fig = px.bar(
        x=choice_counts.index,
        y=choice_counts.values,
        title=f"Runde {round_num} - Team Auswahl",
        labels={'x': 'Auswahl', 'y': 'Anzahl Teams'}
    )
    
    correct_answer = round_data['correct_answer'].iloc[0] if len(round_data) > 0 else None
    if correct_answer:
        colors = [config.COLOR_PRIMARY_BLUE if x == correct_answer else config.COLOR_ORANGE_1 for x in choice_counts.index]
        fig.update_traces(marker_color=colors)
    
    fig.update_layout(
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

def create_feedback_summary(df):
    """Create summary charts for feedback data."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution
        rating_counts = df['overall_rating'].value_counts().sort_index()
        fig_rating = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            title="Gesamtbewertung Verteilung",
            labels={'x': 'Bewertung (1-5)', 'y': 'Anzahl Teams'},
            color=rating_counts.index,
            color_discrete_map={1: config.COLOR_RED_1, 2: config.COLOR_RED_2, 
                               3: config.COLOR_ORANGE_1, 4: config.COLOR_PURPLE_1, 
                               5: config.COLOR_PRIMARY_BLUE}
        )
        fig_rating.update_layout(
            title_font=dict(size=32, color='black', family='Arial Black'),
            xaxis_title_font=dict(size=20, color='black', family='Arial'),
            yaxis_title_font=dict(size=20, color='black', family='Arial'),
            xaxis_tickfont=dict(size=18, color='black', family='Arial'),
            yaxis_tickfont=dict(size=18, color='black', family='Arial'),
            font=dict(size=18, color='black', family='Arial'),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=120, r=280, t=100, b=80)
        )
        st.plotly_chart(fig_rating, width="stretch")
    
    with col2:
        # Favorite game distribution
        game_counts = df['favorite_game'].value_counts()
        dark_colors = [config.COLOR_PRIMARY_BLUE, config.COLOR_ORANGE_1, 
                      config.COLOR_PURPLE_1, config.COLOR_RED_2]
        fig_games = px.pie(
            values=game_counts.values,
            names=game_counts.index,
            title="Lieblingsspiel Verteilung",
            color_discrete_sequence=dark_colors
        )
        fig_games.update_traces(
            marker=dict(line=dict(color='white', width=4)),
            textfont=dict(size=18, color='white')
        )
        fig_games.update_layout(
            title_font=dict(size=32, color='black', family='Arial Black'),
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
            paper_bgcolor='white',
            margin=dict(l=120, r=280, t=100, b=80)
        )
        st.plotly_chart(fig_games, width="stretch")


def create_rating_distribution_chart(feedback_df):
    """Create bar chart for feedback rating distribution."""
    rating_counts = feedback_df['overall_rating'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rating_counts.index,
        y=rating_counts.values,
        marker_color=[config.COLOR_RED_1 if x <= 2 else config.COLOR_ORANGE_1 if x == 3 else config.COLOR_PURPLE_1 if x == 4 else config.COLOR_PRIMARY_BLUE 
                     for x in rating_counts.index],
        text=rating_counts.values,
        textposition='outside',
        textfont=dict(size=18, color='black')
    ))
    
    fig.update_layout(
        title="Gesamtbewertung Verteilung",
        xaxis_title="Bewertung (1-5 Sterne)",
        yaxis_title="Anzahl Teams",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        height=400,
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


def create_favorite_game_pie_chart(feedback_df):
    """Create pie chart for favorite game distribution."""
    favorite_counts = feedback_df['favorite_game'].value_counts()
    
    dark_colors = [config.COLOR_PRIMARY_BLUE, config.COLOR_ORANGE_1, config.COLOR_PURPLE_1, config.COLOR_RED_2]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=favorite_counts.index,
        values=favorite_counts.values,
        hole=0.3,
        marker=dict(colors=dark_colors[:len(favorite_counts)], line=dict(color='white', width=4)),
        textfont=dict(size=18, color='white')
    ))
    
    fig.update_layout(
        title="Welches Spiel hat den Teams am besten gefallen?",
        height=400,
        title_font=dict(size=32, color='black', family='Arial Black'),
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
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=80)
    )
    
    return fig


def create_team_performance_bar_chart(team_scores, title="Team Leistung"):
    """Create horizontal bar chart for team performance with medals for top 3."""
    # Define medal colors
    GOLD_DARK = '#D4AF37'
    SILVER_DARK = '#8C8C8C'
    BRONZE_DARK = '#8C5E3B'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=team_scores['team_name'],
        y=team_scores['percentage'],
        marker_color=[GOLD_DARK if i == 0 else SILVER_DARK if i == 1 else BRONZE_DARK if i == 2 else config.COLOR_PRIMARY_BLUE 
                     for i in range(len(team_scores))],
        text=team_scores['percentage'].apply(lambda x: f'{x:.0f}%'),
        textposition='outside',
        textfont=dict(size=18, color='black')
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Team",
        yaxis_title="Erfolgsquote (%)",
        height=500,
        xaxis_tickangle=-45,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=280, t=100, b=120)
    )
    
    return fig


def create_perimeter_winners_chart(perimeter_data, person_col, delta_col, abs_delta_col, title, color):
    """Create horizontal bar chart for perimeter estimation winners."""
    sorted_data = perimeter_data.sort_values(abs_delta_col)
    
    dark_color = config.COLOR_PRIMARY_BLUE if color == config.BLUE_LIGHT else config.COLOR_ORANGE_1
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_data['team_name'],
        x=sorted_data[delta_col],
        orientation='h',
        marker_color=[dark_color if i >= 3 else config.COLOR_RED_1 for i in range(len(sorted_data))]
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Abweichung vom tatsächlichen Wert (m)",
        yaxis_title="Team",
        height=600,
        title_font=dict(size=32, color='black', family='Arial Black'),
        xaxis_title_font=dict(size=20, color='black', family='Arial'),
        yaxis_title_font=dict(size=20, color='black', family='Arial'),
        xaxis_tickfont=dict(size=18, color='black', family='Arial'),
        yaxis_tickfont=dict(size=18, color='black', family='Arial'),
        font=dict(size=18, color='black', family='Arial'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=120, r=80, t=100, b=80)
    )
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=3)
    
    return fig


def create_clinical_treatment_comparison(placebo_data, molekul_data):
    """Create boxplot comparing clinical trial treatment groups before/after."""
    fig = go.Figure()
    
    # Placebo Before
    fig.add_trace(go.Box(
        y=placebo_data['parent_before'],
        name='Placebo Vorher',
        marker_color=config.COLOR_GRAY_2,
        boxmean=True,
        x0='Placebo',
        offsetgroup='Before',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    # Placebo After
    fig.add_trace(go.Box(
        y=placebo_data['parent_after'],
        name='Placebo Nachher',
        marker_color=config.COLOR_GRAY_1,
        boxmean=True,
        x0='Placebo',
        offsetgroup='After',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    # Medicine Before
    fig.add_trace(go.Box(
        y=molekul_data['parent_before'],
        name='Medikament Vorher',
        marker_color=config.COLOR_PURPLE_2,
        boxmean=True,
        x0='Medicine',
        offsetgroup='Before',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    # Medicine After
    fig.add_trace(go.Box(
        y=molekul_data['parent_after'],
        name='Medikament Nachher',
        marker_color=config.COLOR_PURPLE_1,
        boxmean=True,
        x0='Medicine',
        offsetgroup='After',
        line=dict(width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Klinische Studie: Vorher vs Nachher Behandlung",
        yaxis_title="Schmerzwert (0-10)",
        xaxis_title="Behandlungsgruppe",
        height=500,
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
        name=f'r={correlation:.2f}',
        line=dict(color=config.COLOR_RED_2, width=4)
    ))
    
    # Add median lines
    median_x = x_data.median()
    median_y = y_data.median()
    
    fig.add_hline(y=median_y, line_dash="dash", line_color=config.COLOR_PURPLE_1,
                 line_width=3,
                 annotation_text=f"Median {y_col_name}: {median_y:.1f} cm",
                 annotation_font_size=18)
    fig.add_vline(x=median_x, line_dash="dash", line_color=config.COLOR_PURPLE_1,
                 line_width=3,
                 annotation_text=f"Median {x_col_name}: {median_x:.1f} cm",
                 annotation_font_size=18)
    
    return fig
