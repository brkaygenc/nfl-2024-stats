# NFL Stats 2024

A comprehensive NFL statistics database and visualization project that provides real-time player statistics across different positions with both REST API and interactive web interface access. Built with Flask, Streamlit, and PostgreSQL.

## 🌟 Live Demo

- Web Interface: [https://nfl-website-db-8d1f1be10618.herokuapp.com/](https://nfl-website-db-8d1f1be10618.herokuapp.com/)
- API Endpoint: [https://nfl-website-db-8d1f1be10618.herokuapp.com/api](https://nfl-website-db-8d1f1be10618.herokuapp.com/api)

## 🎯 Key Features

- **Comprehensive NFL Database**: Complete player statistics for the 2024 season
- **Interactive Web Interface**:
  - Position-based player statistics with advanced filtering
  - Team roster views with detailed player information
  - Custom SQL query interface for advanced data analysis
  - Interactive data visualizations and analytics
- **RESTful API**: Programmatic access to all NFL statistics
- **Multi-Position Support**: Complete stats for QB, RB, WR, TE, K, DB, DL, LB
- **Advanced Database Features**: Optimized PostgreSQL schema with stored procedures
- **Real-time Updates**: Latest NFL statistics and player information

## 🖥️ Web Interface

Our Streamlit-powered web interface offers three main features:

1. **Stats Dashboard**
   - Interactive filters for position groups (Offense, Defense, Special Teams)
   - Detailed player statistics with sorting and filtering
   - Performance rankings and comparisons
   - Team-based analytics

2. **SQL Query Laboratory**
   - Write and execute custom SQL queries
   - Interactive query results with export options
   - Pre-built example queries for common analyses
   - Complete database schema documentation

3. **Team Analytics**
   - Comprehensive team statistics
   - Player performance within team context
   - Team comparison tools

## 🚀 Quick Start Guide

1. **Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/brkaygenc/nfl-2024-stats.git
cd nfl-2024-stats

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create .env file in config directory
echo "DATABASE_URL=postgresql://username:password@localhost/nfl_stats" > config/.env

# Initialize database and create procedures
python src/database.py
python src/create_procedures.py
```

3. **Run Applications**
```bash
# Terminal 1: Start API server
python src/app.py

# Terminal 2: Launch Streamlit interface
streamlit run src/streamlit_app.py
```

## 🔌 API Reference

### Core Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/api/teams` | GET | List all NFL teams | `/api/teams` |
| `/api/players/<position>` | GET | Get players by position | `/api/players/QB` |
| `/api/players/team/<team>` | GET | Get team roster | `/api/players/team/SF` |
| `/api/stats/<position>` | GET | Position statistics | `/api/stats/WR` |

### Query Parameters

- `limit`: Number of results (default: 25)
- `sort`: Sort field (e.g., 'yards', 'touchdowns')
- `order`: Sort order ('asc' or 'desc')

## 🛠️ Tech Stack

- **Backend**: Flask, PostgreSQL, SQLAlchemy
- **Frontend**: Streamlit, Pandas
- **Deployment**: Heroku
- **Data Processing**: Python, Pandas
- **Security**: SSL-secured connections, Environment-based configuration

## 📊 Database Architecture

Our PostgreSQL database is optimized for NFL statistics with:

- **Efficient Schema Design**: Normalized tables for players, teams, and statistics
- **Stored Procedures**:
  - `get_team_player_stats(team_code)`: Team roster with stats
  - `calculate_team_points(team_code)`: Team scoring analytics
  - `get_top_position_players(position, limit)`: Position rankings
- **Performance Optimizations**: Indexed queries, materialized views

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- Project Link: [https://github.com/brkaygenc/nfl-2024-stats](https://github.com/brkaygenc/nfl-2024-stats)
- Report Issues: [https://github.com/brkaygenc/nfl-2024-stats/issues](https://github.com/brkaygenc/nfl-2024-stats/issues)