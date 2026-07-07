// Near-duplicate detection for question texts. The bank (and the LLM)
// produce reworded variants of the same question ("What is a good practice
// when creating a password?" vs "What is the best practice for creating a
// secure password?"), so exact matching isn't enough.

const STOPWORDS = new Set([
  'the', 'a', 'an', 'of', 'in', 'on', 'for', 'to', 'is', 'are', 'and', 'or',
  'what', 'which', 'when', 'why', 'how', 'does', 'do', 'you', 'your', 'their',
  'that', 'this', 'it', 'its', 'be', 'can', 'should', 'following', 'best',
  'good', 'most', 'primary', 'main', 'purpose',
]);

export function normalize(text) {
  return String(text).toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
}

function words(text) {
  return new Set(normalize(text).split(' ').filter((w) => w.length > 2 && !STOPWORDS.has(w)));
}

// Jaccard similarity over content words: 1 = same word set, 0 = disjoint.
export function similarity(a, b) {
  const A = words(a);
  const B = words(b);
  if (A.size === 0 || B.size === 0) return normalize(a) === normalize(b) ? 1 : 0;
  let shared = 0;
  for (const w of A) if (B.has(w)) shared++;
  return shared / (A.size + B.size - shared);
}

// Two questions this similar are treated as the same question for the
// purpose of one game.
export const DUPLICATE_THRESHOLD = 0.6;

export function isDuplicate(question, picked) {
  return picked.some((p) => similarity(question, p) >= DUPLICATE_THRESHOLD);
}
