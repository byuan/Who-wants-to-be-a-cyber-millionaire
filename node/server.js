// Who Wants to Be a Cyber Millionaire - Node.js edition.
// Express replaces Django; the question bank is a JSON file instead of MySQL;
// game data is served as JSON APIs instead of a millionaire.json file written
// to disk per game (which was a race between concurrent players).
import express from 'express';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { staticGame } from './lib/questions.js';
import { generateGame } from './lib/generate.js';
import { generateFeedback } from './lib/feedback.js';
import { TOPIC_BANK, getResults, appendResult, getTopics, saveTopics } from './lib/store.js';

const here = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 8000;

app.use(express.json({ limit: '1mb' }));
app.use(express.static(join(here, 'public')));

// Pretty routes for the pages (also reachable as /*.html via the static dir)
for (const page of ['game', 'topics', 'feedback']) {
  app.get(`/${page}`, (req, res) => res.sendFile(join(here, 'public', `${page}.html`)));
}

const STATIC_LEVELS = { 1: 1, 2: 2, 3: 3, 4: 4 };
const DYNAMIC_TIERS = {
  'dynamic-1': 'easy',
  'dynamic-2': 'medium',
  'dynamic-3': 'hard',
  'dynamic-4': 'expert',
};

// GET /api/game?selection=1..4 | dynamic-1..dynamic-4
app.get('/api/game', async (req, res) => {
  const { selection } = req.query;
  try {
    if (selection in STATIC_LEVELS) {
      return res.json({ questions: staticGame(STATIC_LEVELS[selection]) });
    }
    if (selection in DYNAMIC_TIERS) {
      return res.json({ questions: await generateGame(DYNAMIC_TIERS[selection]) });
    }
    res.status(400).json({ error: `Invalid selection: ${selection}` });
  } catch (err) {
    console.error('Failed to build game:', err);
    res.status(500).json({ error: 'Question generation failed. Check the server logs and LLM configuration.' });
  }
});

app.get('/api/results', (req, res) => {
  res.json(getResults());
});

app.post('/api/results', (req, res) => {
  const { history, finalMoney, won, mode, selection } = req.body ?? {};
  if (!Array.isArray(history) || history.length === 0) {
    return res.status(400).json({ error: 'history must be a non-empty array' });
  }
  appendResult({ selection, mode, won: Boolean(won), finalMoney, history });
  res.json({ status: 'success' });
});

app.get('/api/topics', (req, res) => {
  res.json({ bank: TOPIC_BANK, selected: getTopics() });
});

app.post('/api/topics', (req, res) => {
  const error = saveTopics(req.body ?? {});
  if (error) return res.status(400).json({ error });
  res.json({ status: 'success' });
});

app.get('/api/feedback', async (req, res) => {
  try {
    res.json({ feedback: await generateFeedback() });
  } catch (err) {
    console.error('Feedback generation failed:', err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Cyber Millionaire listening on http://localhost:${PORT}`);
});
