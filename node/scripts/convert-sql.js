// One-off converter: parses the MySQL dump the Django version used
// (docker/mysql/static_import.sql) into data/questions.json so the Node
// version needs no database. Re-run with `npm run convert` if the SQL
// question bank changes.
import { readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const sqlPath = join(here, '..', '..', 'docker', 'mysql', 'static_import.sql');
const outPath = join(here, '..', 'data', 'questions.json');

// Row format: ("Question", "Ans1", "Ans2", "Ans3", "Ans4", correct, "difficulty", level),
function parseRow(line) {
  const values = [];
  let i = line.indexOf('(') + 1;
  while (i < line.length) {
    while (i < line.length && /[\s,]/.test(line[i])) i++;
    if (i >= line.length || line[i] === ')') break;
    if (line[i] === '"') {
      i++;
      let s = '';
      while (i < line.length && line[i] !== '"') {
        if (line[i] === '\\') i++; // unescape \' and \" from the dump
        s += line[i];
        i++;
      }
      i++; // closing quote
      values.push(s);
    } else {
      let j = i;
      while (j < line.length && !/[,)]/.test(line[j])) j++;
      values.push(Number(line.slice(i, j).trim()));
      i = j;
    }
  }
  return values;
}

const rows = readFileSync(sqlPath, 'utf8')
  .split('\n')
  .filter((line) => line.startsWith('('))
  .map(parseRow)
  .map(([question, a1, a2, a3, a4, correct, difficulty, level]) => ({
    // The dump has stray trailing spaces (e.g. "easy ") that MySQL's
    // padded VARCHAR comparison tolerated; trim so JS === works.
    question: question.trim(),
    answers: [a1, a2, a3, a4].map((a) => a.trim()),
    correct, // 0-based index into answers
    difficulty: difficulty.trim(),
    level,
  }));

// The dump contains repeated questions within a level, sometimes with
// conflicting difficulty tags ("What is phishing?" is tagged easy 3x and
// medium 3x in level 1) - which lets one game show the same question twice
// at different dollar amounts. Keep one copy per (level, question text),
// tagged with the majority difficulty (ties go to the easier tag).
const RANK = { easy: 0, medium: 1, hard: 2 };
const groups = new Map();
for (const row of rows) {
  const key = `${row.level}|${row.question.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim()}`;
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(row);
}

const questions = [...groups.values()].map((copies) => {
  const votes = {};
  for (const c of copies) votes[c.difficulty] = (votes[c.difficulty] || 0) + 1;
  const difficulty = Object.keys(votes).sort(
    (a, b) => votes[b] - votes[a] || RANK[a] - RANK[b],
  )[0];
  return { ...copies.find((c) => c.difficulty === difficulty), difficulty };
});

writeFileSync(outPath, JSON.stringify(questions, null, 2));
console.log(`Wrote ${questions.length} questions to ${outPath} (${rows.length - questions.length} duplicate rows merged)`);
