# Who Wants to Be a Cyber Millionaire — Node.js edition

A full port of the Django/MySQL app to a single Node.js service. The game
frontend (jQuery + Knockout) is carried over from the original, including the
newer features from Jacob's branch: configurable question topics, practice
mode, the post-game report, and AI performance feedback.

## What replaced what

| Django version                          | Node version                          |
|-----------------------------------------|---------------------------------------|
| Django 2.2 views + templates            | Express + static HTML in `public/`    |
| MySQL `millionaire` table (2nd container) | `data/questions.json` (committed)   |
| MySQL `dynamic` table + truncate        | Questions generated in memory         |
| `millionaire.json` written to disk per game | `GET /api/game` JSON API          |
| Sequential question generation (15 API calls in a row) | Concurrent generation (`Promise.all`) |
| `results.json` / `topic_settings.json` at repo root | Same files under `data/` (gitignored) |

## Run it

```bash
cd node
npm install
export ANTHROPIC_API_KEY=sk-ant-...   # for dynamic games and AI feedback
npm start                              # http://localhost:8000
```

Static games work with no API key at all.

### Configuration (environment variables)

| Variable          | Default                  | Purpose                                   |
|-------------------|--------------------------|-------------------------------------------|
| `PORT`            | `8000`                   | HTTP port                                 |
| `LLM_PROVIDER`    | `anthropic`              | `anthropic` or `ollama`                   |
| `ANTHROPIC_API_KEY` | —                      | Required for the anthropic provider       |
| `ANTHROPIC_MODEL` | `claude-fable-5`         | Claude model for question generation      |
| `OLLAMA_URL`      | `http://localhost:11434` | Ollama server (ollama provider)           |
| `OLLAMA_MODEL`    | `llama3.2:3b`            | Ollama model (ollama provider)            |

The Anthropic provider ships with server-side refusal fallbacks enabled
(`claude-fable-5` falls back to `claude-opus-4-8` inside the same request) so
a safety-classifier false positive on a cybersecurity quiz topic doesn't
break question generation.

### Docker

```bash
cd node
docker build -t cyber-millionaire .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... cyber-millionaire
```

## API

| Route                | Method | Purpose                                        |
|----------------------|--------|------------------------------------------------|
| `/api/game?selection=1..4` | GET | 15 static questions for a level (5 easy/5 medium/5 hard) |
| `/api/game?selection=dynamic-1..4` | GET | 15 AI-generated questions          |
| `/api/results[?player=X]` | GET | Lifetime game results, optionally one player's (case-insensitive) |
| `/api/results`       | POST   | Save a finished game (wins *and* losses); requires a `player` name |
| `/api/players`       | GET    | Distinct player names seen so far              |
| `/api/topics`        | GET/POST | Topic bank + selected topics per level; POST validates that every level keeps at least one topic |
| `/api/feedback[?player=X]` | GET | AI coaching feedback over saved results, per player when given |

## Players

The home page asks for a name before a game can start (remembered in the
browser for next time). Every saved result is tagged with the player, the
post-game report shows only that player's history, and the AI feedback
coach evaluates each player's performance over time individually. Names
match case-insensitively, so "alice" and "Alice" share one history.

## Question bank

`data/questions.json` is generated from the original MySQL dump
(`docker/mysql/static_import.sql`) by `npm run convert`. Re-run that after
editing the SQL file, or edit the JSON directly and treat it as the source
of truth going forward.
