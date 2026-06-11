# Who Wants to be a Cyber Millionaire

A cybersecurity-themed trivia game inspired by the game show *Who Wants to be a Millionaire?*. Test your knowledge across a variety of cybersecurity topics, progressing through increasingly challenging questions to win virtual currency and achieve the title of Cyber Millionaire.

In this game, players must answer a series of multiple-choice questions, each worth a higher amount of points than the last. The questions cover a wide range of cybersecurity-related topics, from basic concepts to advanced technical knowledge. Just like the classic game show, players can use lifelines to assist with difficult questions.

## Table of Contents

1. Features 
2. Game Modes
3. Anthropic API Key Setup
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

To enable dynamic play, the game requires an Anthropic API key to access Claude (model: claude-fable-5). Follow these steps to securely store your API key:

1. Obtain your API key from the Anthropic Console (https://platform.claude.com -> Settings -> API keys).
2. Locate the `api_config.env` file in the root of the repository.
3. Replace the text `placeholder` in the file with your actual Anthropic API key:
   ```
   ANTHROPIC_API_KEY="placeholder"
   ```
4. Save the file. Ensure this file is not committed to the repository to keep your key secure.

---

## Starting the Game

The game is hosted in Docker containers. Follow these steps to start:

1. Ensure Docker and Docker-Compose are installed on your machine.
2. Clone the repository from the `Django-branch`:
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
