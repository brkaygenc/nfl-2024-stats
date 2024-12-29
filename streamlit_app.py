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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'NFL Fantasy Football Stats 2024'
    }
)

# Apply dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .dataframe {
        font-size: 14px !important;
    }
    .stSelectbox label, .stSlider label {
        color: #fafafa !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏈 Fantasy Football")
    selected_position = st.selectbox(
        "Position",
        ["All Offense", "QB", "RB", "WR", "TE", "K", "DEF"]
    )
    
    st.markdown("---")
    st.markdown("### Filters")
    search_name = st.text_input("Search Player By Name")

# Main content area
st.title("Fantasy Football Players")

# Position tabs
tab_positions = ["All Offense", "QB", "RB", "WR", "TE", "K", "DEF"]
tabs = st.tabs(tab_positions)

# Get data based on position
def get_position_data(position):
    conn = get_db_connection()
    if position == "QB":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                passingyards as "Pass YDS",
                passingtds as "Pass TD",
                interceptions as INT,
                rushingyards as "Rush YDS",
                rushingtds as "Rush TD",
                totalpoints as Points,
                rank as Rank
            FROM qb_stats
            ORDER BY totalpoints DESC
        """
    elif position == "RB":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                rushingyards as "Rush YDS",
                rushingtds as "Rush TD",
                receptions as REC,
                receivingyards as "Rec YDS",
                receivingtds as "Rec TD",
                totalpoints as Points,
                rank as Rank
            FROM rb_stats
            ORDER BY totalpoints DESC
        """
    elif position in ["WR", "TE"]:
        query = f"""
            SELECT 
                playername as Player,
                team as Team,
                receptions as REC,
                targets as TGT,
                receivingyards as "Rec YDS",
                receivingtds as "Rec TD",
                totalpoints as Points,
                rank as Rank
            FROM {position.lower()}_stats
            ORDER BY totalpoints DESC
        """
    elif position == "K":
        query = """
            SELECT 
                playername as Player,
                team as Team,
                fieldgoals as FG,
                fieldgoalattempts as "FG ATT",
                extrapoints as XP,
                extrapointattempts as "XP ATT",
                totalpoints as Points,
                rank as Rank
            FROM k_stats
            ORDER BY totalpoints DESC
        """
    else:  # DEF (combining LB, DL, DB)
        query = f"""
            SELECT 
                playername as Player,
                team as Team,
                tackles as TCK,
                sacks as SCK,
                interceptions as INT,
                totalpoints as Points,
                rank as Rank
            FROM (
                SELECT * FROM lb_stats
                UNION ALL
                SELECT * FROM dl_stats
                UNION ALL
                SELECT * FROM db_stats
            ) as defense_stats
            ORDER BY totalpoints DESC
        """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Display data for each position tab
for i, tab in enumerate(tabs):
    position = tab_positions[i]
    with tab:
        try:
            df = get_position_data(position if position != "All Offense" else "QB")
            
            # Apply name search filter
            if search_name:
                df = df[df['Player'].str.contains(search_name, case=False, na=False)]
            
            # Pagination
            items_per_page = 20
            total_pages = len(df) // items_per_page + (1 if len(df) % items_per_page > 0 else 0)
            
            col1, col2 = st.columns([8, 2])
            with col2:
                page = st.selectbox(f'Page ({total_pages} total)', 
                                  range(1, total_pages + 1),
                                  key=f"page_{position}")
            
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            
            # Display data table
            st.dataframe(
                df.iloc[start_idx:end_idx],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Points": st.column_config.NumberColumn(
                        format="%.2f",
                        help="Fantasy points"
                    ),
                }
            )
            
            # Show top performers
            if position != "All Offense":
                st.subheader(f"Top 5 {position} Performers")
                top_5 = df.head(5)
                cols = st.columns(5)
                for idx, (_, player) in enumerate(top_5.iterrows()):
                    with cols[idx]:
                        st.metric(
                            label=f"{player['Player']} ({player['Team']})",
                            value=f"{player['Points']:.1f} pts",
                            delta=f"Rank: {player['Rank']}"
                        )

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Please make sure the database connection is properly configured.") 