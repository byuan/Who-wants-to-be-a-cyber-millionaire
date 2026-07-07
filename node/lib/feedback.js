// AI performance feedback over saved game results (port of aI_report.py,
// but sends a compact summary instead of the full raw results dump).
import { complete } from './generate.js';
import { getResults } from './store.js';

function buildSummary(results) {
  let totalQuestions = 0;
  let totalCorrect = 0;
  const missed = new Map();

  const games = results.map((game) => {
    let correct = 0;
    for (const entry of game.history) {
      totalQuestions++;
      if (entry.isCorrect) {
        totalCorrect++;
        correct++;
      } else {
        missed.set(entry.question, (missed.get(entry.question) || 0) + 1);
      }
    }
    return {
      played_at: game.played_at,
      mode: game.mode,
      questions: game.history.length,
      correct,
    };
  });

  return {
    games_played: results.length,
    questions_answered: totalQuestions,
    questions_correct: totalCorrect,
    accuracy: totalQuestions ? Math.round((totalCorrect / totalQuestions) * 1000) / 10 : 0,
    most_missed_questions: [...missed.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5),
    games,
  };
}

export async function generateFeedback(player) {
  const results = getResults(player);
  if (results.length === 0) {
    throw new Error(
      player
        ? `No games saved for ${player} yet - play a game first, then come back for feedback.`
        : 'No games played yet - play a game first, then come back for feedback.',
    );
  }

  const summary = buildSummary(results);
  const who = player ? `A student named ${player}` : 'A student';
  const prompt = `${who} has completed multiple cybersecurity quiz sessions.

Here is a statistical summary of the student's performance:

${JSON.stringify(summary, null, 2)}

Provide feedback based on these rules:
- Focus only on patterns in correctness
- Identify strengths and weaknesses
- Detect improvement or decline over time
- Be concise and practical
- Do NOT repeat raw data
- Do NOT use emojis
- Give actionable feedback`;

  return complete('You are a cybersecurity learning coach.', prompt);
}
