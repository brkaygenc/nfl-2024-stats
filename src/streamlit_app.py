import streamlit as st
import pandas as pd
import os
import re
import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Set page config - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="NFL Stats 2024",
    page_icon="🏈",
    layout="wide"
)

# API configuration
API_URL = os.getenv('API_URL', 'https://nfl-stats-api-2024-b3f5cb494117.herokuapp.com/api')

def get_data_from_api(endpoint):
    """Helper function to get data from API"""
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {str(e)}")
        return None

# Sidebar for navigation
st.sidebar.title("Navigation")
view_mode = st.sidebar.radio("Choose a view:", ["Stats View", "SQL Query"])

if view_mode == "Stats View":
    st.sidebar.header("Filters")

    # Get all positions from API
    positions = get_data_from_api("players/positions")
    if positions:
        selected_position = st.sidebar.selectbox("Select Position", positions)
        
        # Get players for selected position
        players = get_data_from_api(f"players/{selected_position}")
        if players:
            df = pd.DataFrame(players)
            
            # Display the data
            st.title(f"NFL Player Stats - {selected_position}")
            st.dataframe(df)
            
            # Plotting
            if 'totalpoints' in df.columns:
                st.subheader("Top Players by Total Points")
                top_players = df.nlargest(10, 'totalpoints')
                st.bar_chart(data=top_players.set_index('name')['totalpoints'])

else:
    # SQL Query view
    st.sidebar.header("Available Tables and Procedures")
    st.sidebar.markdown("""
    **Tables:**
    - players
    - teams
    - player_stats
    
    **Example Queries:**
    1. SELECT * FROM players LIMIT 5;
    2. SELECT * FROM teams WHERE team_name LIKE 'New%';
    3. SELECT p.name, t.team_name 
       FROM players p 
       JOIN teams t ON p.team_id = t.id 
       LIMIT 5;
    """)
    
    # Query input
    query = st.text_area("Enter your SQL query:", height=150)
    
    if st.button("Run Query"):
        if query.strip():
            try:
                # Replace with API call when endpoint is ready
                st.error("SQL Query feature is under development")
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
        else:
            st.warning("Please enter a query")