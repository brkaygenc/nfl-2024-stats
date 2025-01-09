# NFL Stats 2024 Application Structure

## 1. Application Components

### 1.1 API Server (`src/app.py`)
This is our Flask API server that handles data requests and updates.

```python
# Main components:
1. Database Connection
2. API Endpoints
3. Data Processing
```

Key Features:
- Provides REST API endpoints for stats retrieval
- Handles database operations
- Processes data requests from XML project

Example Endpoint:
```python
@app.route('/api/qb/<player_name>')
def get_qb_stats(player_name):
    # Returns QB stats in JSON format
    return {
        "stats": {
            "passingYards": value,
            "passingTDs": value,
            ...
        }
    }
```

### 1.2 Web Interface (`src/streamlit_app.py`)
This is our Streamlit web application for viewing and updating stats.

```python
# Main components:
1. User Interface
2. Stats Display
3. Points Calculation
4. Data Updates
```

Key Features:
- Interactive web interface
- Real-time points calculation
- Stats update functionality
- Position-based filtering

Example Structure:
```python
# 1. Database Connection
conn = get_db_connection()

# 2. UI Components
st.title("NFL Stats 2024 🏈")
position = st.sidebar.selectbox("Select Position", ["QB", "RB", "WR", "TE"])

# 3. Stats Display
query = """SELECT * FROM qb_stats ORDER BY totalpoints DESC"""
display_stats(query)

# 4. Update Function
def update_qb_stats(player_name, stats):
    # Calculate points
    points = calculate_points(stats)
    # Update database
    update_database(player_name, stats, points)
```

## 2. Points Calculation System

### 2.1 QB Points Formula
```python
QB Points = (PassingYards × 0.04) + 
            (PassingTDs × 4) + 
            (Interceptions × -2) + 
            (RushingYards × 0.1) + 
            (RushingTDs × 6)
```

### 2.2 Implementation
```python
def calculate_qb_points(stats):
    passing_points = round(stats['passingyards'] * 0.04, 2)
    td_points = round(stats['passingtds'] * 4, 2)
    int_points = round(stats['interceptions'] * -2, 2)
    rush_points = round(stats['rushingyards'] * 0.1, 2)
    rush_td_points = round(stats['rushingtds'] * 6, 2)
    return round(sum([passing_points, td_points, int_points, 
                     rush_points, rush_td_points]), 2)
```

## 3. Database Structure

### 3.1 Tables
- `qb_stats`: Quarterback statistics
- `rb_stats`: Running back statistics
- `wr_stats`: Wide receiver statistics
- `te_stats`: Tight end statistics
- `teams`: Team information

### 3.2 Example QB Stats Schema
```sql
CREATE TABLE qb_stats (
    playerid VARCHAR(10) PRIMARY KEY,
    playername VARCHAR(100) NOT NULL,
    team VARCHAR(3),
    passingyards INTEGER,
    passingtds INTEGER,
    interceptions INTEGER,
    rushingyards INTEGER,
    rushingtds INTEGER,
    totalpoints NUMERIC
);
```

## 4. Application Flow

1. **Data Input**
   - User selects position
   - Enters player name
   - Updates stats

2. **Processing**
   - Validate input
   - Calculate points
   - Update database

3. **Display**
   - Show updated stats
   - Display points breakdown
   - Sort by total points

## 5. Key Features

### 5.1 Real-time Updates
- Instant points calculation
- Immediate UI feedback
- Database synchronization

### 5.2 Data Validation
- Input validation
- Error handling
- Success messages

### 5.3 User Interface
- Dark mode theme
- Position-based filtering
- Sortable stats display

## 6. Deployment

### 6.1 Heroku Configuration
```bash
# Procfile
web: sh config/setup.sh && streamlit run src/streamlit_app.py
```

### 6.2 Environment Setup
```bash
# setup.sh
- Configure Streamlit
- Set environment variables
- Install dependencies
``` 