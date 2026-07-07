// Static question bank, converted from docker/mysql/static_import.sql
// by scripts/convert-sql.js. Replaces the MySQL `millionaire` table.
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { isDuplicate } from './similarity.js';

const here = dirname(fileURLToPath(import.meta.url));
const BANK = JSON.parse(
  readFileSync(join(here, '..', 'data', 'questions.json'), 'utf8'),
);

const DIFFICULTIES = ['easy', 'medium', 'hard'];
const PER_DIFFICULTY = 5;

function shuffle(pool) {
  const copy = [...pool];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// 15 questions for a static game: 5 easy ($100-$1,000), then 5 medium
// ($2,000-$32,000), then 5 hard ($64,000-$1,000,000), matching the money
// ladder in game.html. Skips questions that are near-duplicates of ones
// already picked, so reworded variants of the same question (which the
// bank contains) can't appear twice in one game.
export function staticGame(level) {
  const picked = [];
  for (const difficulty of DIFFICULTIES) {
    const pool = shuffle(
      BANK.filter((q) => q.level === level && q.difficulty === difficulty),
    );
    let taken = 0;
    // First pass avoids near-duplicates; if the pool runs dry (small
    // buckets), a second pass tops up with whatever is left.
    for (const candidate of pool) {
      if (taken === PER_DIFFICULTY) break;
      if (isDuplicate(candidate.question, picked.map((p) => p.question))) continue;
      picked.push(candidate);
      taken++;
    }
    for (const candidate of pool) {
      if (taken === PER_DIFFICULTY) break;
      if (picked.includes(candidate)) continue;
      picked.push(candidate);
      taken++;
    }
  }
  return picked.map((q) => ({
    question: q.question,
    content: q.answers,
    correct: q.correct,
    difficulty: q.difficulty,
  }));
}
