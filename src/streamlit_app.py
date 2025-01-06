import streamlit as st
import pandas as pd
import os
import re
from sqlalchemy import create_engine, text
from database import get_db_connection

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/nfl_stats')

# Create a connection to the database using SQLAlchemy
try:
    # Replace 'postgres://' with 'postgresql://' for SQLAlchemy
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Create SQLAlchemy engine with appropriate SSL mode
    if 'localhost' in DATABASE_URL:
        engine = create_engine(DATABASE_URL)
    else:
        # For Heroku, we need to specify SSL mode
        engine = create_engine(DATABASE_URL, connect_args={'sslmode': 'require'})
    
    # Test the connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        st.success("Successfully connected to the database!")
except Exception as e:
    st.error(f"Failed to connect to database: {str(e)}")
    st.stop()

# Set page config
st.set_page_config(
    page_title="NFL Stats 2024",
    page_icon="🏈",
    layout="wide"
)

# Title
st.title("NFL Stats 2024 🏈")

# Sidebar for filtering
st.sidebar.header("Navigation")

# Add radio button for switching between normal view and SQL query
view_mode = st.sidebar.radio("Select Mode", ["Stats View", "SQL Query"])

if view_mode == "Stats View":
    # Original stats view code
    st.sidebar.header("Filters")

    # Position groups
    position_groups = {
        "Offense": ["QB", "RB", "WR", "TE"],
        "Defense": ["LB", "DL", "DB"],
        "Special Teams": ["K"]
    }

    # Position group selection
    position_group = st.sidebar.selectbox(
        "Select Position Group",
        list(position_groups.keys())
    )

    # Position selection based on group
    position = st.sidebar.selectbox(
        "Select Position",
        position_groups[position_group]
    )

    # Get table name based on position
    table_name = f"{position.lower()}_stats"

    # Query to get all data for the selected position
    if position in ["LB", "DL", "DB"]:
        query = f"""
            SELECT 
                playername,
                playerid,
                team,
                COALESCE(tackles, 0) as tackles,
                COALESCE(tackles_ast, 0) as tackles_ast,
                COALESCE(sacks, 0) as sacks,
                COALESCE(tackles_tfl, 0) as tackles_tfl,
                COALESCE(interceptions, 0) as interceptions,
                COALESCE(forced_fumbles, 0) as forced_fumbles,
                COALESCE(fumble_recoveries, 0) as fumble_recoveries,
                COALESCE(passes_defended, 0) as passes_defended,
                COALESCE(qb_hits, 0) as qb_hits,
                COALESCE(totalpoints, 0) as totalpoints,
                rank
            FROM {table_name}
            ORDER BY totalpoints DESC
        """
    elif position == "QB":
        query = f"""
            SELECT 
                playername,
                playerid,
                team,
                COALESCE(passingyards, 0) as passingyards,
                COALESCE(passingtds, 0) as passingtds,
                COALESCE(interceptions, 0) as interceptions,
                COALESCE(rushingyards, 0) as rushingyards,
                COALESCE(rushingtds, 0) as rushingtds,
                COALESCE(totalpoints, 0) as totalpoints,
                rank
            FROM {table_name}
            ORDER BY totalpoints DESC
        """
    elif position == "RB":
        query = f"""
            SELECT 
                playername,
                playerid,
                team,
                COALESCE(rushingyards, 0) as rushingyards,
                COALESCE(rushingtds, 0) as rushingtds,
                COALESCE(receptions, 0) as receptions,
                COALESCE(receivingyards, 0) as receivingyards,
                COALESCE(receivingtds, 0) as receivingtds,
                COALESCE(totalpoints, 0) as totalpoints,
                rank
            FROM {table_name}
            ORDER BY totalpoints DESC
        """
    elif position in ["WR", "TE"]:
        query = f"""
            SELECT 
                playername,
                playerid,
                team,
                COALESCE(receptions, 0) as receptions,
                COALESCE(targets, 0) as targets,
                COALESCE(receivingyards, 0) as receivingyards,
                COALESCE(receivingtds, 0) as receivingtds,
                COALESCE(totalpoints, 0) as totalpoints,
                rank
            FROM {table_name}
            ORDER BY totalpoints DESC
        """
    else:  # Kickers
        query = f"""
            SELECT 
                playername,
                playerid,
                team,
                COALESCE(fieldgoals, 0) as fieldgoals,
                COALESCE(fieldgoalattempts, 0) as fieldgoalattempts,
                COALESCE(extrapoints, 0) as extrapoints,
                COALESCE(extrapointattempts, 0) as extrapointattempts,
                COALESCE(totalpoints, 0) as totalpoints,
                rank
            FROM {table_name}
            ORDER BY totalpoints DESC
        """

    try:
        # Read data into a pandas DataFrame using SQLAlchemy engine
        df = pd.read_sql_query(query, engine)
        
        # Convert totalpoints to numeric, replacing any invalid values with 0
        df['totalpoints'] = pd.to_numeric(df['totalpoints'], errors='coerce').fillna(0)
        
        # Display the data
        st.dataframe(df)
        
        # Basic stats
        st.subheader("Summary Statistics")
        st.write(df.describe())
        
        # Additional position-specific stats
        if position in ["QB", "RB", "WR", "TE"]:
            st.subheader(f"Top 10 {position}s by Total Points")
            top_10 = df.nlargest(10, 'totalpoints')[['playername', 'playerid', 'team', 'totalpoints']]
            st.dataframe(top_10)
        elif position in ["LB", "DL", "DB"]:
            st.subheader(f"Top 10 {position}s by Total Points")
            top_10 = df.nlargest(10, 'totalpoints')[['playername', 'playerid', 'team', 'tackles', 'tackles_ast', 'sacks', 'tackles_tfl', 'interceptions', 'forced_fumbles', 'fumble_recoveries', 'passes_defended', 'qb_hits', 'totalpoints']]
            st.dataframe(top_10)
        elif position == "K":
            st.subheader("Kicker Rankings")
            kicker_stats = df[['playername', 'playerid', 'team', 'totalpoints']]
            st.dataframe(kicker_stats)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

else:
    # SQL Query view
    st.sidebar.header("Available Tables")
    st.sidebar.markdown("""
    - qb_stats
    - rb_stats
    - wr_stats
    - te_stats
    - lb_stats
    - dl_stats
    - db_stats
    - k_stats
    """)

    # Example queries
    st.sidebar.header("Example Queries")
    st.sidebar.markdown("""
    ```sql
    SELECT * FROM qb_stats WHERE totalpoints > 200
    ```
    ```sql
    SELECT playername, team, tackles FROM lb_stats ORDER BY tackles DESC LIMIT 5
    ```
    """)

    # Main query input area
    st.subheader("Custom SQL Query")
    query = st.text_area("Enter your SQL query:", height=150)
    
    # Execute button
    if st.button("Execute Query"):
        if query:
            # Basic SQL injection prevention
            if re.search(r'\b(DELETE|INSERT|UPDATE|DROP|CREATE|ALTER)\b', query, re.IGNORECASE):
                st.error("Only SELECT queries are allowed!")
            elif not query.strip().upper().startswith('SELECT'):
                st.error("Only SELECT queries are allowed!")
            else:
                try:
                    df = pd.read_sql_query(query, engine)
                    st.success("Query executed successfully!")
                    st.dataframe(df)
                    
                    # Show row count
                    st.info(f"Number of rows returned: {len(df)}")
                    
                    # Show basic stats for numeric columns
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                    if not numeric_cols.empty:
                        st.subheader("Summary Statistics for Numeric Columns")
                        st.write(df[numeric_cols].describe())
                except Exception as e:
                    st.error(f"Error executing query: {str(e)}")
        else:
            st.warning("Please enter a SQL query.")

# Add a new section for testing procedures
st.header("Database Procedures Testing")

# Test Team Stats Procedure
st.subheader("Test Team Stats Procedure")
team_code = st.selectbox("Select Team", ["KC", "SF", "DAL", "PHI", "BUF"])
if st.button("Get Team Stats"):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM get_team_player_stats(%s)", (team_code,))
        results = cur.fetchall()
        if results:
            df = pd.DataFrame(results, columns=['Player Name', 'Position', 'Team', 'Points'])
            st.dataframe(df)
        else:
            st.warning("No players found for this team")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        cur.close()
        conn.close()

# Test Trigger - Update Player Stats
st.subheader("Test Points Calculation Trigger")
player_name = st.text_input("Enter QB Name (e.g., Patrick Mahomes)")
passing_yards = st.number_input("Passing Yards", min_value=0, value=300)
passing_tds = st.number_input("Passing TDs", min_value=0, value=3)
interceptions = st.number_input("Interceptions", min_value=0, value=0)

if st.button("Update QB Stats"):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Update stats and return new points
        cur.execute("""
            UPDATE qb_stats 
            SET passingyards = %s, passingtds = %s, interceptions = %s
            WHERE playername = %s
            RETURNING playername, totalpoints;
        """, (passing_yards, passing_tds, interceptions, player_name))
        
        result = cur.fetchone()
        if result:
            st.success(f"Updated {result[0]}'s points to: {result[1]}")
            conn.commit()
        else:
            st.warning("Player not found")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Test Rank Validation Trigger
st.subheader("Test Rank Validation Trigger")
test_rank = st.number_input("Enter Rank (try negative to test trigger)", value=1)
if st.button("Test Rank Validation"):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE qb_stats 
            SET rank = %s
            WHERE playername = 'Patrick Mahomes'
        """, (test_rank,))
        conn.commit()
        st.success("Rank updated successfully!")
    except Exception as e:
        st.error(f"Trigger prevented invalid rank: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Remove the port configuration as it's handled by setup.sh 