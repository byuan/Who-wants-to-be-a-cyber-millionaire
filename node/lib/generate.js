// Dynamic question generation. Two interchangeable backends:
//   LLM_PROVIDER=anthropic (default) — Claude Fable 5 via the official SDK
//   LLM_PROVIDER=ollama             — a local Ollama server (OLLAMA_URL/OLLAMA_MODEL)
import Anthropic from '@anthropic-ai/sdk';
import { getTopics } from './store.js';

const PROVIDER = process.env.LLM_PROVIDER || 'anthropic';
const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL || 'claude-fable-5';
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2:3b';

const QUESTIONS_PER_GAME = 15;
const ATTEMPTS_PER_QUESTION = 3;

// System prompt and human-readable level label per tier
const LEVEL_META = {
  easy: ['You are an elementary school teacher creating a cybersecurity quiz.', 'primary school'],
  medium: ['You are a high school teacher creating a cybersecurity quiz.', 'secondary school'],
  hard: ['You are a cybersecurity professor creating a quiz.', 'college'],
  expert: ['You are a cybersecurity expert creating a quiz.', 'expert with technical experience'],
};

const PROMPT = (level, topic) =>
  `Write one unique ${level} level cybersecurity quiz question about ${topic} ` +
  'for an educational trivia game, and provide multiple-choice answers ' +
  '(one correct, three incorrect) similar to the game style of ' +
  'Who Wants to Be a Millionaire. ' +
  'Respond with ONLY the following format and nothing else (no preamble, no markdown):\n' +
  'Question: <question>\n\n' +
  'A. <answer>\n' +
  'B. <answer>\n' +
  'C. <answer>\n' +
  'D. <answer>\n\n' +
  'Correct Answer: <letter>';

export class GenerationRefusedError extends Error {}

let anthropicClient = null;
function anthropic() {
  anthropicClient ??= new Anthropic();
  return anthropicClient;
}

async function completeAnthropic(system, prompt) {
  // Fable 5: thinking is always on (omit the param); thinking tokens count
  // against max_tokens, so the budget must be much larger than the visible
  // answer. effort=low keeps thinking minimal for this simple task.
  // The server-side fallback re-serves the request on Opus 4.8 if the cyber
  // safety classifiers decline a quiz topic (a false-positive risk for a
  // cybersecurity trivia game), so one flagged topic doesn't stall the game.
  const message = await anthropic().beta.messages.create({
    model: ANTHROPIC_MODEL,
    max_tokens: 8000,
    output_config: { effort: 'low' },
    betas: ['server-side-fallback-2026-06-01'],
    fallbacks: [{ model: 'claude-opus-4-8' }],
    system,
    messages: [{ role: 'user', content: prompt }],
  });

  if (message.stop_reason === 'refusal') {
    throw new GenerationRefusedError('Model declined to generate this question');
  }

  const text = message.content
    .filter((block) => block.type === 'text')
    .map((block) => block.text)
    .join('');
  if (!text.trim()) {
    throw new Error(`Empty response from model (stop_reason=${message.stop_reason})`);
  }
  return text;
}

async function completeOllama(system, prompt) {
  const res = await fetch(`${OLLAMA_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: OLLAMA_MODEL,
      prompt: `${system}\n\n${prompt}`,
      stream: false,
    }),
  });
  if (!res.ok) throw new Error(`Ollama request failed: ${res.status}`);
  return (await res.json()).response;
}

export function complete(system, prompt) {
  return PROVIDER === 'ollama'
    ? completeOllama(system, prompt)
    : completeAnthropic(system, prompt);
}

// Parses "Question: ... / A. ... D. ... / Correct Answer: X" into the shape
// the game frontend expects. Throws on malformed output so callers retry.
export function parseQuestion(text) {
  const cleaned = text.replace(/\*\*/g, '').replace(/__/g, '');
  const question = cleaned.match(/Question:\s*(.+)/)?.[1]?.trim();
  const answers = [...cleaned.matchAll(/^\s*[A-D]\.\s*(.+)$/gm)].map((m) => m[1].trim());
  const correctLetter = cleaned.match(/Correct Answer:\s*([A-D])/i)?.[1]?.toUpperCase();

  if (!question || answers.length < 4 || !correctLetter) {
    throw new Error(`Unable to parse model response:\n${text}`);
  }
  return {
    question,
    content: answers.slice(0, 4),
    correct: correctLetter.charCodeAt(0) - 'A'.charCodeAt(0),
  };
}

async function generateOne(tier, topics) {
  const [system, levelLabel] = LEVEL_META[tier];
  let lastError;
  for (let attempt = 0; attempt < ATTEMPTS_PER_QUESTION; attempt++) {
    const topic = topics[Math.floor(Math.random() * topics.length)];
    try {
      return parseQuestion(await complete(system, PROMPT(levelLabel, topic)));
    } catch (err) {
      lastError = err;
      console.warn(`Generation attempt ${attempt + 1} failed (${tier}/${topic}): ${err.message}`);
    }
  }
  throw lastError;
}

// Generates a full 15-question game concurrently (the Django version
// generated sequentially, which made dynamic games painfully slow).
export async function generateGame(tier) {
  if (!LEVEL_META[tier]) throw new Error(`Unknown tier: ${tier}`);
  const topics = getTopics()[tier];
  return Promise.all(
    Array.from({ length: QUESTIONS_PER_GAME }, () => generateOne(tier, topics)),
  );
}
