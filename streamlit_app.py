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

# Position selection
position = st.sidebar.selectbox(
    "Select Position",
    ["QB", "RB", "WR", "TE", "K", "LB", "DL", "DB"]
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
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")

# Close the database connection when done
conn.close() 