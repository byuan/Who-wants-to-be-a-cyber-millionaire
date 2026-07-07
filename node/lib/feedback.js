// AI performance feedback over saved game results (port of aI_report.py,
// but sends a compact summary instead of the full raw results dump).
import { complete } from './generate.js';
import { getResults, accuracyByDifficulty } from './store.js';

// "4/5" per difficulty band, for compact per-game reporting
function compactByDifficulty(history) {
  const by = accuracyByDifficulty(history);
  const compact = {};
  for (const [band, stats] of Object.entries(by)) {
    compact[band] = `${stats.correct}/${stats.questions}`;
  }
  return compact;
}

export function buildSummary(results) {
  let totalQuestions = 0;
  let totalCorrect = 0;
  const missed = new Map();
  const allHistory = [];

  const games = results.map((game) => {
    let correct = 0;
    for (const entry of game.history) {
      totalQuestions++;
      allHistory.push(entry);
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
      correct_by_difficulty: compactByDifficulty(game.history),
    };
  });

  return {
    games_played: results.length,
    questions_answered: totalQuestions,
    questions_correct: totalCorrect,
    accuracy: totalQuestions ? Math.round((totalCorrect / totalQuestions) * 1000) / 10 : 0,
    accuracy_by_difficulty: accuracyByDifficulty(allHistory),
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

Questions are tagged easy, medium, or hard; harder questions are worth more
in the game, so accuracy on hard questions matters more than raw accuracy.

Provide feedback based on these rules:
- Focus only on patterns in correctness
- Identify strengths and weaknesses
- Compare performance across question difficulties (easy vs medium vs hard)
  and say at which difficulty the student starts to struggle
- Detect improvement or decline over time
- Be concise and practical
- Do NOT repeat raw data
- Do NOT use emojis
- Give actionable feedback`;

  return complete('You are a cybersecurity learning coach.', prompt);
}
