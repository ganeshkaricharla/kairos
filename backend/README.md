# Kairos Backend

FastAPI backend with MongoDB for the Kairos adaptive AI coaching application.

## Quick Start

### 1. Prerequisites

- Python 3.11.0
- MongoDB (via Docker Compose recommended)

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and fill in your actual values:
# - OPENROUTER_API_KEY (get from https://openrouter.ai/keys)
# - GOOGLE_CLIENT_ID (get from Google Cloud Console)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start MongoDB

```bash
# From project root
cd ..
docker-compose up -d
```

### 5. Run Database Migration

```bash
# Add formation tracking and coaching features to existing data
python migrations/add_formation_tracking.py
```

### 6. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `kairos` |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI features | Required |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Required |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | JWT expiration time in minutes | `10080` (7 days) |

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app setup
│   ├── config.py               # Configuration settings
│   ├── database.py             # MongoDB connection
│   ├── auth/                   # Authentication (JWT, Google OAuth)
│   ├── models/                 # Pydantic models
│   ├── routers/                # API endpoints
│   ├── services/               # Business logic
│   │   ├── ai_service.py       # OpenRouter integration
│   │   ├── coaching_service.py # Coaching sessions
│   │   ├── tag_parser.py       # Tag-based action system
│   │   └── user_service.py     # User preferences & memories
│   ├── prompts/                # AI prompts
│   │   ├── personalities.py    # Coaching styles
│   │   └── prompt_builder.py   # Dynamic prompt assembly
│   └── utils/                  # Utility functions
└── migrations/                 # Database migrations
```

## Key Features

### AI Coaching System
- **Tag-based actions**: AI can create habits, log data, save memories via tags
- **4 coaching personalities**: Strict, Balanced, Supportive, Scientific
- **Dynamic prompts**: Context-aware with user memories and data
- **Habit formation tracking**: 8-completion rule to prevent overload

### API Endpoints

**Authentication**
- `POST /auth/google` - Google OAuth login

**Users**
- `GET /users/me` - Get user profile
- `PATCH /users/me/coaching-style` - Update coaching personality
- `POST /users/me/memories` - Add memory
- `GET /users/personalities` - List available personalities

**Goals**
- `POST /goals` - Create goal
- `GET /goals` - Get active goal
- `GET /goals/{id}` - Get specific goal
- `PATCH /goals/{id}` - Update goal

**Habits**
- `GET /goals/{goal_id}/habits` - List habits
- `PATCH /habits/{id}` - Update habit

**Trackers**
- Similar CRUD operations for custom metrics

**Daily Logs**
- `POST /daily/{date}/goals/{goal_id}/habits/{habit_id}/toggle` - Toggle habit
- `POST /daily/{date}/goals/{goal_id}/trackers/{tracker_id}/log` - Log tracker value

**Coaching**
- `POST /goals/{goal_id}/coaching/start` - Start coaching session
- `POST /coaching/{session_id}/message` - Send message (triggers AI with tag parsing)

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black app/

# Lint
pylint app/
```

## Troubleshooting

**MongoDB Connection Error**
```bash
# Make sure MongoDB is running
docker-compose ps

# If not running, start it
docker-compose up -d
```

**Import Errors**
```bash
# Make sure you're in the backend directory and have installed dependencies
pip install -r requirements.txt
```

**Migration Issues**
```bash
# Check MongoDB connection
python -c "from app.config import settings; print(settings.mongodb_url)"

# Re-run migration
python migrations/add_formation_tracking.py
```
