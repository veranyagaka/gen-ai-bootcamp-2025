# Backend Server Technical Specs

## Business Goal:

A language learning school wants to build a prototype of a learning portal which will act as three things:
- Inventory of possible vocabulary that can be learned
- Act as a Learning record store (LRS), providing correct and wrong scores on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements

- The backend will be built using Flask
- The database will be SQLite3
- The API will be built using Flask-RESTful
- Flask-Script or Flask-Migrate will be used for task running
- The API will always return JSON
- There will be no authentication or authorization
- Everything will be treated as a single user

## Directory Structure

```text
backend_flask/
├── app/
│   ├── models/     # Data structures and database operations
│   ├── routes/     # API routes organized by feature (dashboard, words, groups, etc.)
│   └── services/   # Business logic
├── db/
│   ├── migrations/
│   └── seeds/      # For initial data population
├── manage.py
├── requirements.txt
└── words.db
```

## Database Schema

Our database will be a single SQLite database called `words.db` that will be in the root of the project folder of `backend_flask`

We have the following tables:
- words - stored vocabulary words
  - id integer
  - french string
  - english string
  - parts json
- words_groups - join table for words and groups many-to-many
  - id integer
  - word_id integer
  - group_id integer
- groups - thematic groups of words
  - id integer
  - name string
- study_sessions - records of study sessions grouping word_review_items
  - id integer
  - group_id integer
  - created_at datetime
  - study_activity_id integer
- study_activities - a specific study activity, linking a study session to a group
  - id integer
  - study_session_id integer
  - group_id integer
  - created_at datetime
- word_review_items - a record of word practice, determining if the word was correct or not
  - word_id integer
  - study_session_id integer
  - correct boolean
  - created_at datetime

## API Endpoints

### GET /api/dashboard/last_study_session
Returns information about the most recent study session.

#### JSON Response
```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2025-02-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_id": 456,
  "group_name": "Basic Greetings"
}
```

### GET /api/dashboard/study_progress
Returns study progress statistics.

#### JSON Response
```json
{
  "total_words_studied": 3,
  "total_available_words": 124
}
```

### GET /api/dashboard/quick-stats
Returns quick overview statistics.

#### JSON Response
```json
{
  "success_rate": 80.0,
  "total_study_sessions": 4,
  "total_active_groups": 3,
  "study_streak_days": 4
}
```

### GET /api/words

- pagination with 100 items per page

#### JSON Response
```json
{
  "items": [
    {
      "french": "bonjour",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 500,
    "items_per_page": 100
  }
}
```

### GET /api/words/:id
#### JSON Response
```json
{
  "french": "bonjour",
  "english": "hello",
  "stats": {
    "correct_count": 5,
    "wrong_count": 2
  },
  "groups": [
    {
      "id": 1,
      "name": "Basic Greetings"
    }
  ]
}
```

### Seed Data
This task will import JSON files and transform them into target data for our database.

All seed files live in the `seeds` folder.

In our task we should have DSL to specify each seed file and its expected group word name.

```json
[
  {
    "french": "payer",
    "english": "to pay"
  },
  ...
]
```
