// Quality checks for question selection and generation:
//  - static games: difficulty matches the money ladder, no near-duplicates
//  - dynamic games: prompts ramp easy->medium->hard, duplicates regenerated,
//    duplicate answer options rejected
// Run: LLM_PROVIDER=ollama OLLAMA_URL=http://localhost:<mock> node scripts/test-quality.mjs
import { readFileSync } from 'fs';
import { staticGame } from '../lib/questions.js';
import { generateGame } from '../lib/generate.js';
import { similarity } from '../lib/similarity.js';

const BANK = JSON.parse(readFileSync(new URL('../data/questions.json', import.meta.url)));
// Key by level+text: the same question text can exist at several levels
// with different (legitimate) difficulty tags.
const difficultyOf = new Map(BANK.map((q) => [`${q.level}|${q.question}`, q.difficulty]));

let failures = 0;
const check = (ok, label) => {
  console.log((ok ? 'PASS' : 'FAIL') + ' - ' + label);
  if (!ok) failures++;
};

// --- similarity sanity ---
check(
  similarity(
    'What is a good practice when creating a password?',
    'What is the best practice for creating a secure password?',
  ) >= 0.6,
  'similarity: reworded password questions detected as duplicates',
);
check(
  similarity('What is phishing?', 'What does a firewall do?') < 0.6,
  'similarity: unrelated questions not flagged',
);

// --- static games: 200 samples per level ---
for (const level of [1, 2, 3, 4]) {
  let ladderOk = true;
  let dupPairs = 0;
  for (let run = 0; run < 200; run++) {
    const game = staticGame(level);
    if (game.length !== 15) ladderOk = false;
    game.forEach((q, i) => {
      const expected = i < 5 ? 'easy' : i < 10 ? 'medium' : 'hard';
      if (difficultyOf.get(`${level}|${q.question}`) !== expected) ladderOk = false;
    });
    for (let i = 0; i < game.length; i++) {
      for (let j = i + 1; j < game.length; j++) {
        if (similarity(game[i].question, game[j].question) >= 0.6) dupPairs++;
      }
    }
  }
  check(ladderOk, `static level ${level}: slots 1-5 easy, 6-10 medium, 11-15 hard (200 games)`);
  // Small pools (level 1 hard has 9 questions) may occasionally be forced
  // to accept a similar pair; it must be rare, not the norm.
  check(dupPairs <= 200 * 0.05, `static level ${level}: near-duplicate pairs rare (${dupPairs} in 200 games)`);
}

// --- dynamic games (needs the duplicating mock LLM) ---
const game = await generateGame('medium');
check(game.length === 15, 'dynamic: 15 questions generated');

let noDups = true;
for (let i = 0; i < game.length; i++) {
  for (let j = i + 1; j < game.length; j++) {
    if (similarity(game[i].question, game[j].question) >= 0.6) noDups = false;
  }
}
check(noDups, 'dynamic: duplicates regenerated away (mock duplicated the whole first batch)');

const rampOk = game.every((q, i) => {
  const expected = i < 5 ? '[easy]' : i < 10 ? '[medium]' : '[hard]';
  return q.question.includes(expected);
});
check(rampOk, 'dynamic: prompt difficulty ramps with the money ladder (mock echoes it)');

const answersOk = game.every((q) => new Set(q.content).size === 4);
check(answersOk, 'dynamic: all games have 4 distinct answer options');

process.exit(failures ? 1 : 0);
