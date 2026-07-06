// Static question bank, converted from docker/mysql/static_import.sql
// by scripts/convert-sql.js. Replaces the MySQL `millionaire` table.
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const BANK = JSON.parse(
  readFileSync(join(here, '..', 'data', 'questions.json'), 'utf8'),
);

const DIFFICULTIES = ['easy', 'medium', 'hard'];
const PER_DIFFICULTY = 5;

function sample(pool, n) {
  const copy = [...pool];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, n);
}

// 15 questions for a static game: 5 easy, then 5 medium, then 5 hard,
// mirroring the ORDER BY rand() LIMIT 5 queries of the Django version.
export function staticGame(level) {
  return DIFFICULTIES.flatMap((difficulty) =>
    sample(
      BANK.filter((q) => q.level === level && q.difficulty === difficulty),
      PER_DIFFICULTY,
    ),
  ).map((q) => ({ question: q.question, content: q.answers, correct: q.correct }));
}
