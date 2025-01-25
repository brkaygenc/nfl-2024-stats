# NFL Stats API Requirements

This document outlines the required API endpoints and data structures for the NFL Stats application.

## API Endpoints

### 1. Search Players
```http
GET /api/search
```

**Parameters:**
- `name` (required): Player's name to search for
- `position` (optional): Player's position (QB, RB, WR, etc.)

**Example Response:**
```json
[
    {
        "name": "Patrick Mahomes",
        "position": "QB",
        "team": "KC",
        "passing_yards": 4000,
        "passing_touchdowns": 30,
        "interceptions": 10,
        "rushing_yards": 200,
        "total_points": 285
    }
]
```

### 2. Get Players by Position
```http
GET /api/players/{position}
```

**Parameters:**
- `position`: Player position (QB, RB, WR, TE, K, DEF, LB, DB, DL)

**Example Response:**
```json
[
    {
        "name": "Player Name",
        "position": "QB",
        "team": "KC",
        "passing_yards": 4000,
        "passing_touchdowns": 30,
        "interceptions": 10,
        "rushing_yards": 200,
        "total_points": 285
    }
]
```

### 3. Get Teams
```http
GET /api/teams
```

**Example Response:**
```json
[
    {
        "code": "KC",
        "name": "Kansas City Chiefs",
        "division": "AFC West"
    }
]
```

### 4. Get Team Players
```http
GET /api/teams/{team_code}/players
```

**Parameters:**
- `team_code`: Team code (e.g., KC, SF, etc.)

**Example Response:**
```json
[
    {
        "name": "Player Name",
        "position": "QB",
        "team": "KC",
        "passing_yards": 4000,
        "passing_touchdowns": 30,
        "interceptions": 10,
        "rushing_yards": 200,
        "total_points": 285
    }
]
```

## Position-Specific Statistics

### QB (Quarterback) Statistics
- `passing_yards`: Total passing yards
- `passing_touchdowns`: Number of passing touchdowns
- `rushing_yards`: Total rushing yards
- `interceptions`: Number of interceptions thrown
- `total_points`: Total fantasy points

### RB (Running Back) Statistics
- `rushing_yards`: Total rushing yards
- `rushing_touchdowns`: Number of rushing touchdowns
- `receiving_yards`: Total receiving yards
- `receptions`: Number of receptions
- `total_points`: Total fantasy points

### WR/TE (Wide Receiver/Tight End) Statistics
- `receiving_yards`: Total receiving yards
- `receiving_touchdowns`: Number of receiving touchdowns
- `receptions`: Number of receptions
- `targets`: Number of times targeted
- `total_points`: Total fantasy points

### K (Kicker) Statistics
- `fieldgoals`: Number of field goals made
- `fieldgoal_attempts`: Number of field goal attempts
- `extrapoints`: Number of extra points made
- `extrapoint_attempts`: Number of extra point attempts
- `total_points`: Total fantasy points

### Defensive Players (LB, DB, DL) Statistics
- `tackles`: Total tackles
- `sacks`: Number of sacks
- `tackles_for_loss`: Number of tackles for loss
- `forced_fumbles`: Number of forced fumbles
- `total_points`: Total fantasy points

## Notes
- All endpoints should return JSON data
- Error responses should include appropriate HTTP status codes and error messages
- Rate limiting information should be included in response headers
- Authentication requirements to be determined
