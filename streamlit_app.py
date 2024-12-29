import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

# Page config
st.set_page_config(
    page_title="NFL Stats 2024",
    page_icon="🏈",
    layout="wide"
)

# Title
st.title("NFL Stats 2024 🏈")

# Sidebar filters
st.sidebar.header("Filters")
position = st.sidebar.selectbox(
    "Select Position",
    ["QB", "RB", "WR", "TE", "K", "LB", "DL", "DB"]
)

# Get data based on position
@st.cache_data
def load_data(position):
    conn = get_db_connection()
    query = f"SELECT * FROM {position.lower()}_season"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    # Load and display data
    df = load_data(position)
    
    # Display stats
    st.header(f"{position} Statistics")
    st.dataframe(df)
    
    # Basic stats
    st.subheader("Summary Statistics")
    st.write(df.describe())

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure the database is properly configured and contains data.") 