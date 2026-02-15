# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kairos is an Adaptive AI Coaching application that helps users achieve their goals through intelligent habit tracking and personalized coaching. It uses AI (via OpenRouter) to analyze progress, suggest habit changes, and provide conversational guidance.

## Tech Stack

**Backend:**
- FastAPI (async) with Uvicorn
- MongoDB (Motor async driver)
- OpenRouter API for AI capabilities
- Google OAuth for authentication
- JWT tokens (7-day expiration)
- Python 3.11.0

**Frontend:**
- React 19 + TypeScript
- Vite for bundling and dev server
- shadcn/ui components with Tailwind CSS 4
- TanStack Query for data fetching
- React Router for navigation
- Recharts for data visualization

## Development Commands

### Backend (from `/backend` directory)

```bash
# Start backend server (requires MongoDB running)
uvicorn app.main:app --reload --port 8000

# Install dependencies
pip install -r requirements.txt
```

### Frontend (from `/frontend` directory)

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Database

```bash
# Start MongoDB via Docker Compose (from project root)
docker-compose up -d

# Stop MongoDB
docker-compose down
```

## Environment Configuration

The backend requires a `.env` file in `/backend` with:
- `MONGODB_URL` - MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME` - Database name (default: kairos)
- `OPENROUTER_API_KEY` - OpenRouter API key for AI features
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_EXPIRE_MINUTES` - JWT expiration time (default: 10080 = 7 days)

The frontend requires a `.env` file in `/frontend` with:
- `VITE_GOOGLE_CLIENT_ID` - Google OAuth client ID (same as backend)

## Architecture

### Backend Structure

The backend follows a layered architecture:

1. **Routers** (`app/routers/`) - API endpoints and request/response handling
2. **Services** (`app/services/`) - Business logic and orchestration
3. **Models** (`app/models/`) - Pydantic models for data validation
4. **Database** (`app/database.py`) - MongoDB connection and indexes
5. **Auth** (`app/auth/`) - JWT token handling and Google OAuth
6. **Prompts** (`app/prompts/`) - AI system prompts for different coaching scenarios

API routes are mounted in `app/main.py` and include:
- `/auth` - Google OAuth login/signup
- `/goals` - CRUD for goals
- `/habits` - CRUD for habits
- `/trackers` - CRUD for custom metrics
- `/daily-logs` - Daily habit completion and tracker values
- `/coaching` - AI coaching sessions and chat
- `/models` - OpenRouter model selection

### Frontend Structure

The frontend is organized as:

1. **Pages** (`src/pages/`) - Route-level components
2. **Components** (`src/components/`) - Reusable UI components organized by feature
3. **API** (`src/api/`) - Axios client and API service functions
4. **Contexts** (`src/contexts/`) - React contexts for global state (auth)
5. **Hooks** (`src/hooks/`) - Custom React hooks
6. **UI Components** (`src/components/ui/`) - shadcn/ui base components

### Core Domain Concepts

- **Goal**: The user's primary objective (only one active goal at a time)
  - Has an `ai_context` with coaching state (summary, plan_philosophy, current_phase, next_review_date)

- **Habit**: A daily action tied to a goal
  - Status: active/paused/archived
  - Has frequency, time_of_day, intensity

- **Tracker**: A custom numeric metric to measure
  - E.g., "Weight", "Hours Studied", "Pages Read"

- **DailyLog**: Records for a specific date
  - Tracks which habits were completed
  - Records tracker values

- **CoachingSession**: AI-powered conversation
  - Trigger types: goal_setup, scheduled_review, user_initiated
  - Contains chat messages and proposed_changes
  - Proposed changes can be: add_habit, swap_habit, upgrade_intensity, downgrade_intensity, pause_habit, add_tracker

### AI Service

The AI service (`app/services/ai_service.py`) integrates with OpenRouter:
- Users can select which model to use via the `/models` endpoints
- Selected model is persisted in MongoDB
- Three AI prompt types are used:
  1. **goal_analysis** - Initial conversational goal setup
  2. **progress_evaluation** - Periodic review of habit/tracker performance
  3. **coaching_reply** - Conversational chat responses

All AI responses follow structured JSON schemas defined in `app/models/ai.py`.

### Database Indexes

MongoDB indexes are created on startup (see `app/database.py`):
- `daily_logs`: unique compound index on (user_id, goal_id, date)
- `habits`: index on (goal_id, status)
- `trackers`: index on (goal_id)
- `coaching_sessions`: index on (goal_id, status)
- `users`: unique index on (google_id)

### Authentication Flow

1. User clicks "Sign in with Google" on frontend
2. Google OAuth flow completes, returns credential
3. Frontend sends credential to `/auth/google` endpoint
4. Backend verifies with Google, creates/finds user
5. Backend returns JWT token
6. Frontend stores token in localStorage
7. All subsequent API calls include JWT in Authorization header
8. Axios interceptor redirects to /login on 401 responses

## AI Behavior & Coaching Patterns

### Current AI Architecture

The current implementation uses **structured JSON responses** with predefined schemas:

1. **CoachingReply** (`app/models/ai.py`)
   - `message`: The conversational response
   - `proposed_changes`: List of suggested habit/tracker modifications
   - Used for: goal_setup, coaching conversations

2. **ProgressEvaluation** (`app/models/ai.py`)
   - `phase_assessment`: Current progress evaluation
   - `recommendations`: Suggested next steps
   - Used for: periodic progress reviews

3. **ProposedChange** (`app/models/coaching.py`)
   - Types: add_habit, swap_habit, upgrade_intensity, downgrade_intensity, pause_habit, add_tracker
   - User must accept/reject each proposed change
   - Changes are tracked in coaching sessions

### AI Behavior Reference (from Kairos1)

The previous Kairos implementation used a **tag-based action system** that may be worth considering for future enhancements:

#### Tag-Based Action System

AI responses contained executable tags parsed by the backend:
- `[HABIT]{...}[/HABIT]` - Create habit
- `[TRACKER]{...}[/TRACKER]` - Create tracker
- `[LOG]{"key": "calories", "value": 1850}[/LOG]` - Log data immediately
- `[MEMORY]{"text": "User prefers morning workouts"}[/MEMORY]` - Save user facts
- `[GOAL]{...}[/GOAL]` - Create goal
- `[DELETE_HABIT]{"habit_id": "..."}[/DELETE_HABIT]` - Remove habit
- `[UPDATE_HABIT]{...}[/UPDATE_HABIT]` - Modify habit

**Advantages:**
- AI can execute multiple actions in one response
- Natural conversation flow with embedded actions
- User sees clean message text (tags are parsed out)
- Immediate data logging when user mentions numbers

#### Coaching Personalities

The reference implementation supported multiple coaching styles:
- **Strict**: Tough, demanding, no-nonsense ("You NEED to...", "No excuses")
- **Balanced**: Professional, constructive, evidence-based
- **Supportive**: Kind, encouraging, celebrates every win
- **Scientific**: Data-driven, analytical, focuses on metrics and trends

Each personality has distinct language patterns and motivational approaches.

#### Dynamic System Prompt Structure

The system prompt is built dynamically from:
1. **Time Context** - Greeting and focus change by time of day (morning/evening/etc.)
2. **Personality** - Loaded based on user's coaching_style preference
3. **Memories** - Accumulated facts about the user from past conversations
4. **Goals** - Active goals with progress percentages
5. **Trackers** - Today's logged values and 7-day averages
6. **Habits** - Formed vs building, completion counts, streaks
7. **Instructions** - Core behavioral rules and capabilities

#### Habit Formation System

Key concept: **Habits require 8 completions to "form"**
- New habits are "building" (0-7 completions)
- After 8 completions, they become "formed"
- Users can only add new habits once active habits are formed
- This prevents habit overload and ensures mastery

#### Smart Habit-Tracker Linking

Habits with numeric targets auto-link to trackers:
- "Walk 10k steps" + steps tracker → auto-completes when steps >= 10000
- "Drink 2L water" + water tracker → auto-completes when water >= 2
- Always create habits with specific numeric targets to enable linking

#### Memory System

AI saves user facts across conversations:
- Dietary preferences, allergies
- Schedule and lifestyle
- Exercise preferences
- Personal motivations and challenges
- Saved naturally during conversation (1-2 per chat max)

#### Behavioral Rules (from Kairos1 instructions.txt)

**Core Principles:**
- "YOU HAVE ALL THE USER'S DATA. NEVER say 'I'd need to know...' - USE IT."
- Always reference actual numbers from user's data
- Be proactive in suggesting habits and trackers
- NEVER create things without discussing first: Suggest → User agrees → Create
- When user tells you a number, LOG IT immediately
- Keep responses concise (2-4 sentences)
- Don't use markdown in chat - plain text for chat bubbles
- Know when to wrap up: Short responses like "cool", "okay", "thanks" = done
- Only ask ONE follow-up question at a time

**Habit Creation Rules:**
- Check "Can add new habit" status FIRST
- Only create after user agreement
- New habits become active TOMORROW
- Be specific: "Drink 2L water daily" not "Stay hydrated"
- Include numeric targets for auto-linking

**Data Logging Rules:**
- Parse numbers from natural language
- Log immediately and confirm
- Proactively ask about missing data

## Important Notes

- The frontend assumes the backend is running at `http://localhost:8000`
- The backend CORS is configured for `http://localhost:5173` (Vite default port)
- MongoDB must be running before starting the backend
- AI features require a valid OpenRouter API key
- Only one active goal is supported per user (business rule)
- When creating a goal, a coaching session is automatically started
- Current AI uses structured JSON responses; Kairos1 used tag-based parsing (see AI Behavior section)
