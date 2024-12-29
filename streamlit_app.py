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
    page_title="Fantasy Football Stats 2024",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for fantasy football look
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .big-header {
        font-family: 'Arial Black', sans-serif;
        font-size: 24px;
        color: #333;
        padding: 10px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
    }
    .position-tabs {
        background-color: #f8f9fa;
        padding: 10px 0;
        border-bottom: 1px solid #ddd;
    }
    .stats-table {
        font-size: 14px !important;
    }
    .stats-table td {
        padding: 8px !important;
    }
    .stats-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .player-name {
        font-weight: bold;
        color: #0056b3;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stDataFrame) {
        padding: 0 !important;
    }
    div[data-testid="stDataFrame"] > div {
        padding: 0 !important;
    }
    div[data-testid="stDataFrame"] {
        padding: 0 !important;
    }
    </style>
    <div class="big-header">FANTASY FOOTBALL PLAYER PROJECTIONS</div>
""", unsafe_allow_html=True)

# Position navigation
positions = ["All", "QB", "RB", "WR", "TE", "K", "DEF"]
cols = st.columns(len(positions))
for i, pos in enumerate(positions):
    with cols[i]:
        if st.button(pos, key=f"pos_{pos}", use_container_width=True):
            st.session_state.position = pos

if 'position' not in st.session_state:
    st.session_state.position = "All"

# Search bar
search = st.text_input("Search Player By Name", "")

# Get data based on position
def get_position_data(position):
    conn = get_db_connection()
    if position == "QB":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                passingyards as "Pass Yds",
                passingtds as "TD",
                interceptions as "Int",
                rushingyards as "Rush Yds",
                rushingtds as "Rush TD",
                totalpoints as "Fantasy Points"
            FROM qb_stats
            ORDER BY totalpoints DESC
        """
    elif position == "RB":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                rushingyards as "Rush Yds",
                rushingtds as "TD",
                receptions as "Rec",
                receivingyards as "Rec Yds",
                receivingtds as "Rec TD",
                totalpoints as "Fantasy Points"
            FROM rb_stats
            ORDER BY totalpoints DESC
        """
    elif position in ["WR", "TE"]:
        query = f"""
            SELECT 
                playername as Player,
                team as Team,
                receptions as "Rec",
                targets as "Tgt",
                receivingyards as "Yds",
                receivingtds as "TD",
                totalpoints as "Fantasy Points"
            FROM {position.lower()}_stats
            ORDER BY totalpoints DESC
        """
    elif position == "K":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                fieldgoals as "FG",
                fieldgoalattempts as "FGA",
                extrapoints as "XP",
                extrapointattempts as "XPA",
                totalpoints as "Fantasy Points"
            FROM k_stats
            ORDER BY totalpoints DESC
        """
    elif position == "DEF":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                tackles as "Tkl",
                sacks as "Sck",
                interceptions as "Int",
                totalpoints as "Fantasy Points"
            FROM (
                SELECT * FROM lb_stats
                UNION ALL
                SELECT * FROM dl_stats
                UNION ALL
                SELECT * FROM db_stats
            ) as defense_stats
            ORDER BY totalpoints DESC
        """
    else:  # All
        query = """
            SELECT 
                playername as Player,
                team as Team,
                'QB' as Pos,
                totalpoints as "Fantasy Points"
            FROM qb_stats
            UNION ALL
            SELECT 
                playername,
                team,
                'RB' as Pos,
                totalpoints
            FROM rb_stats
            UNION ALL
            SELECT 
                playername,
                team,
                'WR' as Pos,
                totalpoints
            FROM wr_stats
            UNION ALL
            SELECT 
                playername,
                team,
                'TE' as Pos,
                totalpoints
            FROM te_stats
            ORDER BY "Fantasy Points" DESC
        """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    # Get and filter data
    df = get_position_data(st.session_state.position)
    if search:
        df = df[df['Player'].str.contains(search, case=False, na=False)]
    
    # Display data with custom formatting
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        height=800,
        column_config={
            "Player": st.column_config.TextColumn(
                help="Player name",
                width="large",
            ),
            "Team": st.column_config.TextColumn(
                width="small",
            ),
            "Fantasy Points": st.column_config.NumberColumn(
                help="Fantasy points",
                format="%.2f",
                width="small",
            ),
        }
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure the database connection is properly configured.") 