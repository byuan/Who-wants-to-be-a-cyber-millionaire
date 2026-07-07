// Dynamic question generation. Two interchangeable backends:
//   LLM_PROVIDER=anthropic (default) — Claude Fable 5 via the official SDK
//   LLM_PROVIDER=ollama             — a local Ollama server (OLLAMA_URL/OLLAMA_MODEL)
import Anthropic from '@anthropic-ai/sdk';
import { getTopics } from './store.js';
import { normalize, isDuplicate } from './similarity.js';

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

// Within-game difficulty ramp: like the TV show, early questions are worth
// little and should be easy, late questions are worth up to $1,000,000 and
// should be genuinely hard - all relative to the selected audience level.
// Slots 0-4 easy, 5-9 medium, 10-14 hard, matching the money ladder.
const RAMP = [
  'an easy warm-up question that most of this audience would get right',
  'a moderately challenging question for this audience',
  'a genuinely difficult question that would challenge the strongest of this audience',
];
const rampFor = (slot) => RAMP[Math.min(Math.floor(slot / 5), RAMP.length - 1)];
const BANDS = ['easy', 'medium', 'hard'];
const bandFor = (slot) => BANDS[Math.min(Math.floor(slot / 5), BANDS.length - 1)];

const RATING_PROMPT = (levelLabel, questions) =>
  `Rate the difficulty of each cybersecurity quiz question below for a ${levelLabel} audience, ` +
  'on a scale of 1 (very easy for this audience) to 5 (very hard for this audience). ' +
  'Respond with ONLY one line per question, in the format "<question number>: <rating>".\n\n' +
  questions.map((q, i) => `${i + 1}. ${q.question}`).join('\n');

const PROMPT = (level, topic, difficulty, avoid = []) =>
  `Write one unique ${level} level cybersecurity quiz question about ${topic} ` +
  'for an educational trivia game, and provide multiple-choice answers ' +
  '(one correct, three incorrect) similar to the game style of ' +
  'Who Wants to Be a Millionaire. ' +
  `The question should be ${difficulty}. ` +
  'All four answer options must be distinct. ' +
  (avoid.length
    ? 'Do NOT repeat or rephrase any of these already-used questions:\n' +
      avoid.map((q) => `- ${q}`).join('\n') +
      '\n'
    : '') +
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
  const content = answers.slice(0, 4);
  if (new Set(content.map(normalize)).size < 4) {
    throw new Error(`Model produced duplicate answer options:\n${text}`);
  }
  return {
    question,
    content,
    correct: correctLetter.charCodeAt(0) - 'A'.charCodeAt(0),
  };
}

async function generateOne(tier, topics, difficulty, avoid) {
  const [system, levelLabel] = LEVEL_META[tier];
  let lastError;
  for (let attempt = 0; attempt < ATTEMPTS_PER_QUESTION; attempt++) {
    const topic = topics[(Math.floor(Math.random() * topics.length) + attempt) % topics.length];
    try {
      return parseQuestion(await complete(system, PROMPT(levelLabel, topic, difficulty, avoid)));
    } catch (err) {
      lastError = err;
      console.warn(`Generation attempt ${attempt + 1} failed (${tier}/${topic}): ${err.message}`);
    }
  }
  throw lastError;
}

function shuffled(list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// Generates a full 15-question game concurrently (the Django version
// generated sequentially, which made dynamic games painfully slow).
// Questions ramp easy -> medium -> hard to match the money ladder, topics
// are spread round-robin so one topic doesn't dominate, and near-duplicate
// questions are regenerated with an avoid-list.
export async function generateGame(tier) {
  if (!LEVEL_META[tier]) throw new Error(`Unknown tier: ${tier}`);
  const topics = getTopics()[tier];

  // Round-robin over a shuffled topic list: with >= 5 topics no topic
  // repeats within a 5-question difficulty band.
  const order = shuffled(topics);
  const questions = await Promise.all(
    Array.from({ length: QUESTIONS_PER_GAME }, (_, slot) =>
      generateOne(tier, [order[slot % order.length]], rampFor(slot), []),
    ),
  );

  // Concurrent generation can still produce rephrasings of the same
  // question; regenerate offending slots with an explicit avoid-list.
  const MAX_DEDUP_ROUNDS = 2;
  for (let round = 0; round < MAX_DEDUP_ROUNDS; round++) {
    const seen = [];
    const duplicateSlots = [];
    questions.forEach((q, slot) => {
      if (isDuplicate(q.question, seen)) duplicateSlots.push(slot);
      else seen.push(q.question);
    });
    if (duplicateSlots.length === 0) break;

    console.warn(`Regenerating ${duplicateSlots.length} duplicate question(s), round ${round + 1}`);
    await Promise.all(
      duplicateSlots.map(async (slot) => {
        try {
          questions[slot] = await generateOne(
            tier,
            topics,
            rampFor(slot),
            questions.filter((_, i) => i !== slot).map((q) => q.question),
          );
        } catch {
          // Keep the duplicate rather than failing the whole game.
        }
      }),
    );
  }

  const calibrated = await calibrateOrder(questions, tier);
  return calibrated.map((q, slot) => ({ ...q, difficulty: bandFor(slot) }));
}

// Second-pass difficulty calibration: one extra model call rates every
// question 1-5 for the audience, and the game is re-ordered easiest-first
// so difficulty genuinely climbs with the money ladder (the generation
// prompts ask for a ramp, but the model's judgement of its own output is
// a better sort key). Falls back to the generated order if the rating
// response is unusable.
async function calibrateOrder(questions, tier) {
  const [, levelLabel] = LEVEL_META[tier];
  try {
    const text = await complete(
      'You assess quiz question difficulty for educators.',
      RATING_PROMPT(levelLabel, questions),
    );
    const ratings = new Map();
    for (const match of text.matchAll(/^\s*(\d+)\s*[:.]\s*([1-5])\s*$/gm)) {
      const index = Number(match[1]) - 1;
      if (index >= 0 && index < questions.length) ratings.set(index, Number(match[2]));
    }
    if (ratings.size < questions.length * 0.8) {
      throw new Error(`only ${ratings.size}/${questions.length} ratings parsed`);
    }
    // Stable sort: ties keep the generated (already ramped) order
    return questions
      .map((q, i) => ({ q, i, rating: ratings.get(i) ?? 3 }))
      .sort((a, b) => a.rating - b.rating || a.i - b.i)
      .map((entry) => entry.q);
  } catch (err) {
    console.warn(`Difficulty calibration skipped: ${err.message}`);
    return questions;
  }
}
