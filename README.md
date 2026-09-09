# Who Wants to be a Cyber Millionaire

A cybersecurity-themed trivia game inspired by the game show *Who Wants to be a Millionaire?*. Test your knowledge across a variety of cybersecurity topics, progressing through increasingly challenging questions to win virtual currency and achieve the title of Cyber Millionaire.

In this game, players must answer a series of multiple-choice questions, each worth a higher amount of points than the last. The questions cover a wide range of cybersecurity-related topics, from basic concepts to advanced technical knowledge. Just like the classic game show, players can use lifelines to assist with difficult questions.

## Table of Contents

1. Features 
2. Game Modes
3. OPENAI API Key Setup
4. Starting the Game

---

## Features

- Trivia game inspired by *Who Wants to be a Millionaire?* with a cybersecurity twist.
- Four different levels to choose from: Primary School, Secondary School, College, and Expert.
- Two exciting game modes: Static and Dynamic, which can be selected through a toggle button on the landing page.
- Lifelines to help players navigate tough questions.

---

## Game Modes

### Static Mode
- In this mode, players answer a random set of questions that are all AI generated, but built into the game through a fixed database.

### Dynamic Mode
- In this mode, questions are randomly generated dynamically through the API, ensuring a unique experience every time you play as the questions cannot be predicted.

---

## API Key Setup

To enable dyanmic play, the game requires an API key to access the CHATGPT OPENAI services. Follow these steps to securely store your API key:

1. Obtain your API key from the provided service.
2. Locate the `api_config.env` file in the root of the repository.
3. Replace the text `placeholder` in the file with your actual OPENAI API key:
   ```
   OPENAI_API_KEY="placeholder"
   ```
4. Save the file. Ensure this file is not committed to the repository to keep your key secure.

---

## Starting the Game

The game is hosted in Docker containers. Follow these steps to start:

1. Ensure Docker and Docker-Compose are installed on your machine.
2. Clone the repository from the `Jacob-Branch`:
3. Ensure your API key is set within the `api_config.env` file if you plan on playing the dynamic gameplay.
4. Navigate to the `docker` directory:
   ```bash
   cd docker
   ```
5. Build and start the containers:
   ```bash
   sudo docker-compose up --build -d
   ```
6. Open your browser and navigate to [https://localhost](https://localhost) to play the game.
7. Enjoy the game!

---


## AI configuration

Set `AI_MODEL` in `api_config.env` to a model supported by your provider.
GPT uses `GPT_API_KEY` (or `OPENAI_API_KEY`), Claude uses `CLAUDE_API_KEY`,
and Llama uses `AI_IP` pointing to a compatible generation endpoint.
Static quizzes do not require AI credentials; AI feedback does.
Never commit real credentials.

## Current deployment limits

Question queues currently live in one server process. The entrypoint runs one
Gunicorn worker with four threads. Do not increase the worker count or deploy
multiple replicas until queue storage is shared. Starting a new dynamic game
replaces that user's previous queue; simultaneous games for the same account
are not supported. Idle generators expire after five minutes.

This remains a development deployment: production requires external secrets,
debug disabled, restricted hosts, supported framework/database versions, and
restricted database access. Quiz scores are still client-reported and must not
be used as verified assessment results. Server-authoritative games and scoring
are required before adding competitive rankings or graded assessments.

## Regression tests

With the Python requirements installed, run from `docker/cybermillionaire`:

```bash
python -m unittest discover -s tests -v
node tests/test_frontend.js
```


## ARM64 database support

The database image is MariaDB 11.4, which supports ARM64 and AMD64 natively.
The existing MySQL-compatible schema, seed scripts, and Python connector are
retained. Compose waits for database readiness before starting Gunicorn, and
stores MariaDB data in the `mariadb_data` named volume. Port 3306 is exposed
only on localhost; containers connect using the existing `db` service name.

From the `docker` directory, start with:

```bash
docker compose up --build -d
```

For an existing MySQL installation, export any users and game history before
replacing its container, then import a compatible SQL dump into MariaDB.
Do not mount a MySQL data directory directly into MariaDB. The new named volume
starts with the bundled questions and an empty user database; it does not
migrate existing records automatically. Avoid `docker compose down -v` unless
you intend to delete the database volume.
