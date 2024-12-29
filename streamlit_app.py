import streamlit as st
import pandas as pd
import psycopg2
import os

# Get the DATABASE_URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create a connection to the database
conn = psycopg2.connect(DATABASE_URL)

# Set page config
st.set_page_config(
    page_title="NFL Stats 2024",
    page_icon="🏈",
    layout="wide"
)

# Title
st.title("NFL Stats 2024 🏈")

# Sidebar for filtering
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
query = f"SELECT * FROM {table_name}"

try:
    # Read data into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Display the data
    st.dataframe(df)
    
    # Basic stats
    st.subheader("Summary Statistics")
    st.write(df.describe())
    
    # Additional position-specific stats
    if position in ["QB", "RB", "WR", "TE"]:
        st.subheader(f"Top 10 {position}s by Total Points")
        top_10 = df.nlargest(10, 'totalpoints')[['playername', 'team', 'totalpoints']]
        st.dataframe(top_10)
    elif position in ["LB", "DL", "DB"]:
        st.subheader(f"Top 10 {position}s by Tackles")
        top_10 = df.nlargest(10, 'tackles')[['playername', 'team', 'tackles', 'sacks', 'interceptions']]
        st.dataframe(top_10)
    elif position == "K":
        st.subheader("Kicker Rankings")
        kicker_stats = df[['playername', 'team', 'totalpoints']]
        st.dataframe(kicker_stats)
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")

# Close the database connection when done
conn.close()

# Get the port from Heroku environment
port = int(os.environ.get('PORT', 8501)) 