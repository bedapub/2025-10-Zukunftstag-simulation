"""Refactored admin dashboard with modular game analysis."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import config
from database import ZukunftstagDatabase
from utils.helpers import (
    check_admin_password, logout_admin, show_success_message,
    show_error_message, get_session_options
)
from modules.admin.admin_game1 import show_game1_analysis
from modules.admin.admin_game2 import show_game2_analysis
from modules.admin.admin_game3 import show_game3_analysis
from modules.admin.admin_game4 import show_game4_analysis


def show_admin_page(db: ZukunftstagDatabase):
    """Display the admin dashboard."""
    
    # Check authentication
    if not check_admin_password():
        st.title("Admin Dashboard")
        st.info("Please enter the admin password to access the dashboard.")
        return
    
    # Admin is authenticated
    st.title("Admin Dashboard")
    
    # Warning banner for Streamlit Cloud
    if not config.DEV_MODE:
        st.warning("""
        ⚠️ **IMPORTANT - Streamlit Cloud Data Persistence**: 
        SQLite data may be lost when the app restarts. **Export data regularly!** 
        Use the "Download Session Data" buttons below to backup your data.
        """)
    
    logout_admin()
    
    # Admin navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", 
        "Game Data", 
        "Feedback",
        "Secret Data", 
        "Session Management"
    ])
    
    with tab1:
        show_overview_tab(db)
    
    with tab2:
        show_game_data_tab(db)
    
    with tab3:
        show_feedback_tab(db)
    
    with tab4:
        show_secret_data_tab(db)
    
    with tab5:
        show_session_management_tab(db)


def show_overview_tab(db: ZukunftstagDatabase):
    """Show overview statistics."""
    
    st.markdown("### Workshop Overview")
    
    # Get current session data
    session_id = db.get_current_session_id()
    teams_df = db.get_all_teams(session_id)
    
    if len(teams_df) == 0:
        st.info("No teams registered yet.")
        return
    
    # Progress overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Teams", len(teams_df))
    
    with col2:
        conn = db.get_connection()
        feedback_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM feedback WHERE session_id = ?",
            conn, params=(session_id,)
        ).iloc[0]['count']
        conn.close()
        
        feedback_rate = (feedback_count / len(teams_df)) * 100 if len(teams_df) > 0 else 0
        st.metric("Feedback Submitted", f"{feedback_rate:.0f}%")
    
    # Team progress tracking
    st.markdown("### Team Progress Tracking")
    
    progress_data = []
    for _, team in teams_df.iterrows():
        team_name = team['team_name']
        progress = db.get_team_progress(team_name)
        
        progress_data.append({
            'Team': team_name,
            'Parent': team['parent_name'],
            'Child': team['child_name'],
            'Tech Check': "✅" if progress['tech_check'] else "⏳",
            'Game 1': "✅" if progress['game1'] else "⏳",
            'Game 2': "✅" if progress['game2'] else "⏳", 
            'Game 3': "✅" if progress['game3'] else "⏳",
            'Game 4': "✅" if progress['game4'] else "⏳",
            'Feedback': "✅" if progress['feedback'] else "⏳"
        })
    
    progress_df = pd.DataFrame(progress_data)
    st.dataframe(progress_df, width="stretch")
    
    # Real-time updates
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Live monitoring**: Data refreshes automatically as teams progress!")
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    # Auto-refresh indicator
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    st.caption(f"🕐 Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")


def show_game_data_tab(db: ZukunftstagDatabase):
    """Show game data analysis."""
    
    st.markdown("### Game Data Analysis")
    
    # Real-time data refresh
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("**Live Results**: Data updates automatically as teams complete each game!")
    with col2:
        if st.button("Refresh Now"):
            st.rerun()
    
    game_tabs = st.tabs(["Game 1", "Game 2", "Game 3", "Game 4"])
    
    with game_tabs[0]:
        show_game1_analysis(db)
    
    with game_tabs[1]:
        show_game2_analysis(db)
    
    with game_tabs[2]:
        show_game3_analysis(db)
    
    with game_tabs[3]:
        show_game4_analysis(db)


def show_feedback_tab(db: ZukunftstagDatabase):
    """Show team feedback and ratings."""
    
    st.markdown("### Team Feedback")
    
    session_id = db.get_current_session_id()
    conn = db.get_connection()
    feedback_df = pd.read_sql_query(
        "SELECT * FROM feedback WHERE session_id = ? ORDER BY submitted_at DESC",
        conn, params=(session_id,)
    )
    conn.close()
    
    if len(feedback_df) == 0:
        st.warning("**Waiting for teams to submit feedback**")
        st.info("Feedback will appear here automatically as teams complete the workshop and submit their ratings.")
        return
    
    st.success(f"**{len(feedback_df)} teams** have submitted feedback")
    
    # Overall statistics
    st.markdown("#### Overall Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_rating = feedback_df['overall_rating'].mean()
        st.metric("Average Overall Rating", f"{avg_rating:.1f}/5", 
                 delta=None if avg_rating >= 4 else "Below 4.0")
    
    with col2:
        rating_counts = feedback_df['overall_rating'].value_counts().sort_index(ascending=False)
        most_common = rating_counts.index[0] if len(rating_counts) > 0 else 0
        st.metric("Most Common Rating", f"{most_common}/5")
    
    with col3:
        response_rate = (len(feedback_df) / len(db.get_all_teams(session_id))) * 100 if len(db.get_all_teams(session_id)) > 0 else 0
        st.metric("Response Rate", f"{response_rate:.0f}%")
    
    # Rating distribution
    st.markdown("#### Rating Distribution")
    rating_counts = feedback_df['overall_rating'].value_counts().sort_index()
    
    fig_ratings = go.Figure()
    fig_ratings.add_trace(go.Bar(
        x=rating_counts.index,
        y=rating_counts.values,
        marker_color=['red' if x <= 2 else 'orange' if x == 3 else 'lightblue' if x == 4 else 'green' 
                     for x in rating_counts.index],
        text=rating_counts.values,
        textposition='outside'
    ))
    
    fig_ratings.update_layout(
        title="Overall Rating Distribution",
        xaxis_title="Rating (1-5 stars)",
        yaxis_title="Number of Teams",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        height=400
    )
    st.plotly_chart(fig_ratings, use_container_width=True)
    
    # Favorite game analysis
    st.markdown("#### Favorite Games")
    
    col1, col2 = st.columns(2)
    
    with col1:
        favorite_counts = feedback_df['favorite_game'].value_counts()
        
        fig_favorites = go.Figure()
        fig_favorites.add_trace(go.Pie(
            labels=favorite_counts.index,
            values=favorite_counts.values,
            hole=0.3
        ))
        
        fig_favorites.update_layout(
            title="Which game did teams enjoy most?",
            height=400
        )
        st.plotly_chart(fig_favorites, use_container_width=True)
    
    with col2:
        st.markdown("**Favorite Game Rankings:**")
        medals = ["🥇", "🥈", "🥉"]
        for i, (game, count) in enumerate(favorite_counts.items(), 1):
            percentage = (count / len(feedback_df)) * 100
            medal = medals[i-1] if i <= 3 else ""
            st.write(f"{medal} **{game}**: {count} teams ({percentage:.0f}%)")
    
    # Individual feedback
    st.markdown("#### Individual Team Feedback")
    
    rating_filter = st.multiselect(
        "Filter by rating:",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5]
    )
    
    filtered_feedback = feedback_df[feedback_df['overall_rating'].isin(rating_filter)]
    
    for _, feedback in filtered_feedback.iterrows():
        with st.expander(f"{feedback['overall_rating']}/5 - **{feedback['team_name']}** - {feedback['submitted_at']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Overall Rating:** {'⭐' * feedback['overall_rating']}")
                st.markdown(f"**Favorite Game:** {feedback['favorite_game']}")
            
            with col2:
                st.markdown(f"**Submitted:** {feedback['submitted_at']}")
            
            if feedback['comments'] and str(feedback['comments']).strip():
                st.markdown("**Comments:**")
                st.info(feedback['comments'])
            else:
                st.markdown("*No comments provided*")


def show_secret_data_tab(db: ZukunftstagDatabase):
    """Show user assignment data that should not be revealed to participants."""
    
    conn = db.get_connection()
    secret_data = pd.read_sql_query("SELECT * FROM secret_clinical_data", conn)
    conn.close()
    
    if len(secret_data) == 0:
        st.info("No secret data available yet.")
        return
    
    st.markdown("#### Clinical Trial Treatment Assignments")
    
    display_secret = secret_data[['team_name', 'parent_treatment', 'child_treatment']].copy()
    display_secret.columns = ['Team Name', 'Parent Treatment', 'Child Treatment']
    st.dataframe(display_secret, width="stretch")
    
    # Treatment balance
    parent_placebo_count = len(secret_data[secret_data['parent_treatment'] == 'Placebo'])
    parent_molekul_count = len(secret_data[secret_data['parent_treatment'] == 'Molekül'])
    
    st.write("**Treatment balance:**")
    st.write(f"Parents - Placebo: {parent_placebo_count}, Medicine: {parent_molekul_count}")
    
    st.info("🔴 **Red chocolate balls** = Placebo\n⚫ **Black chocolate balls** = Medicine")


def show_session_management_tab(db: ZukunftstagDatabase):
    """Show session management tools."""
    
    st.markdown("### Session Management")
    
    current_session = db.get_current_session_id()
    
    conn = db.get_connection()
    sessions_df = pd.read_sql("SELECT * FROM sessions ORDER BY session_id", conn)
    conn.close()
    
    # Prominent current session indicator
    st.markdown(f"""
    <div style="padding: 1px; border-radius: 1px; text-align: center; margin-bottom: 5px;">
        <h3 style="margin: 0;color: green">Current Active Session: {current_session}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if len(sessions_df) > 0:
        # Add visual indicator for active session
        sessions_display = sessions_df.copy()
        sessions_display['Status'] = sessions_display['is_active'].apply(lambda x: '🟢 ACTIVE' if x else '⚪ Inactive')
        st.dataframe(sessions_display, use_container_width=True)
    
    # Export data for each session
    st.markdown("#### Export Session Data (Backup)")
    
    export_session = st.selectbox(
        "Select session to export:",
        options=sessions_df['session_id'].tolist() if len(sessions_df) > 0 else [],
        key="export_session_select"
    )
    
    if st.button("Download Session Data as CSV", type="secondary"):
        all_data = db.export_all_data(export_session)
        
        # Create a combined export with all tables
        import io
        buffer = io.StringIO()
        
        for table_name, df in all_data.items():
            if len(df) > 0:
                buffer.write(f"\n### {table_name.upper()} ###\n")
                df.to_csv(buffer, index=False)
                buffer.write("\n")
        
        csv_data = buffer.getvalue()
        
        st.download_button(
            label=f"💾 Download {export_session} Data",
            data=csv_data,
            file_name=f"{export_session}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_csv"
        )
        
        show_success_message(f"Data export ready for {export_session}!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Switch Session")
        
        if len(sessions_df) > 0:
            session_choices = sessions_df['session_id'].tolist()
            selected_session = st.selectbox(
                "Select Session:",
                options=session_choices,
                index=session_choices.index(current_session) if current_session in session_choices else 0
            )
            
            if st.button("Switch to Selected Session", type="secondary"):
                db.set_active_session(selected_session)
                show_success_message(f"Switched to session: {selected_session} (Global for all users)")
                st.rerun()
    
    with col2:
        st.markdown("#### Clear Session Data")
        
        clear_session = st.selectbox(
            "Session to Clear:",
            options=sessions_df['session_id'].tolist() if len(sessions_df) > 0 else [],
            key="clear_session_select"
        )
        
        if st.button("Clear Session Data", type="primary"):
            if st.button("Confirm Delete", type="primary", key="confirm_clear"):
                db.clear_session_data(clear_session)
                show_success_message(f"Session '{clear_session}' data cleared successfully!")
                st.rerun()
    
    # Database statistics
    st.markdown("#### Database Statistics (All Sessions)")
    
    stats_data = []
    for table in ['teams', 'game1_heights', 'game2_perimeter', 'game3_memory', 'game4_clinical', 'feedback']:
        conn = db.get_connection()
        count_df = pd.read_sql(f"SELECT session_id, COUNT(*) as count FROM {table} GROUP BY session_id", conn)
        conn.close()
        
        for _, row in count_df.iterrows():
            stats_data.append({
                'Session': row['session_id'],
                'Table': table,
                'Records': row['count']
            })
    
    if stats_data:
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.info("No data recorded yet.")
