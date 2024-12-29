import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
    return conn

# Page configuration
st.set_page_config(
    page_title="NFL Stats 2024",
    page_icon="🏈",
    layout="wide"
)

# Sidebar for navigation
st.sidebar.title("NFL Stats 2024")
selected_position = st.sidebar.selectbox(
    "Select Position",
    ["QB", "RB", "WR", "TE", "K", "LB", "DL", "DB"]
)

# Main content
st.title(f"{selected_position} Statistics")

# Get data based on position
def get_position_data(position):
    conn = get_db_connection()
    if position == "QB":
        query = """
            SELECT playername, team, passingyards, passingtds, interceptions,
                   rushingyards, rushingtds, totalpoints, rank
            FROM qb_stats
            ORDER BY totalpoints DESC
        """
    elif position == "RB":
        query = """
            SELECT playername, team, rushingyards, rushingtds,
                   receptions, receivingyards, receivingtds, totalpoints, rank
            FROM rb_stats
            ORDER BY totalpoints DESC
        """
    elif position in ["WR", "TE"]:
        query = f"""
            SELECT playername, team, receptions, targets,
                   receivingyards, receivingtds, totalpoints, rank
            FROM {position.lower()}_stats
            ORDER BY totalpoints DESC
        """
    elif position == "K":
        query = """
            SELECT playername, team, fieldgoals, fieldgoalattempts,
                   extrapoints, extrapointattempts, totalpoints, rank
            FROM k_stats
            ORDER BY totalpoints DESC
        """
    else:  # LB, DL, DB
        query = f"""
            SELECT playername, team, tackles, sacks,
                   interceptions, totalpoints, rank
            FROM {position.lower()}_stats
            ORDER BY totalpoints DESC
        """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Get and display data
try:
    df = get_position_data(selected_position)
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.multiselect("Filter by Team", sorted(df['team'].unique()))
    with col2:
        min_points = st.slider("Minimum Total Points", 
                             float(df['totalpoints'].min()), 
                             float(df['totalpoints'].max()),
                             float(df['totalpoints'].min()))

    # Apply filters
    if team_filter:
        df = df[df['team'].isin(team_filter)]
    df = df[df['totalpoints'] >= min_points]

    # Display stats
    st.dataframe(df, use_container_width=True)

    # Show top performers
    st.subheader("Top 5 Performers")
    top_5 = df.head(5)
    
    # Create columns for top performers
    cols = st.columns(5)
    for idx, (_, player) in enumerate(top_5.iterrows()):
        with cols[idx]:
            st.metric(
                label=player['playername'],
                value=f"{player['totalpoints']:.1f} pts",
                delta=f"Rank: {player['rank']}"
            )

    # Add position-specific visualizations
    st.subheader("Statistics Visualization")
    if selected_position == "QB":
        # Passing vs Rushing TDs
        st.bar_chart(
            df.head(10).set_index('playername')[['passingtds', 'rushingtds']]
        )
    elif selected_position in ["WR", "TE"]:
        # Reception Yards vs TDs
        st.scatter_chart(
            df.head(20),
            x='receivingyards',
            y='receivingtds',
            size='totalpoints',
            color='team'
        )
    elif selected_position == "RB":
        # Rushing vs Receiving Yards
        st.scatter_chart(
            df.head(20),
            x='rushingyards',
            y='receivingyards',
            size='totalpoints',
            color='team'
        )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure the database connection is properly configured.") 