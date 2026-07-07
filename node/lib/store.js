// File-backed persistence for game results and topic settings.
// Both files live in data/ and are gitignored (runtime state, not source).
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const RESULTS_PATH = join(here, '..', 'data', 'results.json');
const TOPICS_PATH = join(here, '..', 'data', 'topic_settings.json');
const BANK_PATH = join(here, '..', 'data', 'topic_bank.json');

// Default topic banks per generation tier (from the original
// dynamic_question_generation.py). The live bank is editable on the
// topic configuration page and stored in data/topic_bank.json.
export const DEFAULT_TOPIC_BANK = {
  easy: [
    'Passwords', 'Internet Safety', 'Cyberbullying', 'Social Media',
    'Secure Websites', 'Hacking', 'Digital Footprints', 'Data',
    'Phishing', 'Safe Downloading',
  ],
  medium: [
    'Passwords', 'Phishing', 'Encryption', 'Firewall', 'Malware',
    'Two-factor authentication', 'Social Engineering', 'Network Security',
    'Endpoint Security', 'Advanced Persistent Threats',
  ],
  hard: [
    'Intrusion Detection Systems', 'Cyber Threat Intelligence',
    'Digital Forensics', 'Cryptography', 'Blockchain Security',
    'Secure Coding Practices', 'Ethical Hacking', 'Social Engineering',
    'Cyber Incident Response', 'Network Encryption',
  ],
  expert: [
    'TCP Protocol', 'Wireless Security Protocol', 'HTTP Headers',
    'Virtualization', 'Kerberos Authentication', 'TCP/UDP Protocol',
    'SSL/X509 Certificates', 'Asymmetric/Symmetric Encryption for Cryptography',
    'Linux/Unix System Forensics', 'Technical Aspects of Network Protocols',
  ],
};

export const TIERS = Object.keys(DEFAULT_TOPIC_BANK);

const MAX_TOPIC_LENGTH = 60;
const MAX_TOPICS_PER_TIER = 30;

function readJson(path, fallback) {
  if (!existsSync(path)) return fallback;
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return fallback;
  }
}

// All results, or one player's results (matched case-insensitively so
// "alice" and "Alice" accumulate one history).
export function getResults(player) {
  const results = readJson(RESULTS_PATH, []);
  if (!player) return results;
  const needle = player.trim().toLowerCase();
  return results.filter((r) => (r.player || '').trim().toLowerCase() === needle);
}

// Distinct player names, most recent game first.
export function getPlayers() {
  const seen = new Map();
  for (const r of getResults()) {
    const name = (r.player || '').trim();
    if (name) seen.set(name.toLowerCase(), name);
  }
  return [...seen.values()].reverse();
}

export function appendResult(result) {
  const results = getResults();
  results.push({ played_at: new Date().toISOString(), ...result });
  writeFileSync(RESULTS_PATH, JSON.stringify(results, null, 2));
  return results.length;
}

// Normalizes one tier's topic list: trimmed, length-capped, de-duplicated
// case-insensitively. Returns an error string via the second element when
// the input is unusable.
function cleanTopicList(raw, tier) {
  if (!Array.isArray(raw)) return [null, `${tier} must be a list of topics`];
  const seen = new Set();
  const topics = [];
  for (const entry of raw) {
    if (typeof entry !== 'string') continue;
    const topic = entry.trim().slice(0, MAX_TOPIC_LENGTH);
    const key = topic.toLowerCase();
    if (!topic || seen.has(key)) continue;
    seen.add(key);
    topics.push(topic);
  }
  if (topics.length === 0) return [null, `Every level needs at least one topic (missing: ${tier}).`];
  if (topics.length > MAX_TOPICS_PER_TIER) {
    return [null, `Too many topics for ${tier} (max ${MAX_TOPICS_PER_TIER}).`];
  }
  return [topics, null];
}

// The live topic bank: the saved custom bank when valid, else the defaults.
export function getBank() {
  const saved = readJson(BANK_PATH, null);
  if (!saved) return structuredClone(DEFAULT_TOPIC_BANK);
  const bank = {};
  for (const tier of TIERS) {
    const [topics] = cleanTopicList(saved[tier], tier);
    if (!topics) return structuredClone(DEFAULT_TOPIC_BANK);
    bank[tier] = topics;
  }
  return bank;
}

// Selected topics per tier; falls back to the full bank for any tier whose
// saved selection is empty or no longer matches the bank.
export function getTopics() {
  const bank = getBank();
  const saved = readJson(TOPICS_PATH, null);
  if (!saved) return bank;
  const topics = {};
  for (const tier of TIERS) {
    const valid = (saved[tier] || []).filter((t) => bank[tier].includes(t));
    topics[tier] = valid.length > 0 ? valid : [...bank[tier]];
  }
  return topics;
}

// Saves the topic bank and the enabled selection together. Every tier must
// keep at least one enabled topic (an empty tier would leave dynamic games
// with nothing to generate from — the bug in the original save_topics view).
// Returns an error string or null.
export function saveTopicConfig({ bank: rawBank, selected: rawSelected } = {}) {
  const bank = {};
  for (const tier of TIERS) {
    const [topics, error] = cleanTopicList(rawBank?.[tier], tier);
    if (error) return error;
    bank[tier] = topics;
  }

  const selected = {};
  for (const tier of TIERS) {
    const chosen = Array.isArray(rawSelected?.[tier])
      ? rawSelected[tier]
          .filter((t) => typeof t === 'string')
          .map((t) => t.trim())
          .filter((t) => bank[tier].includes(t))
      : [];
    if (chosen.length === 0) {
      return `Enable at least one topic for every level (missing: ${tier}).`;
    }
    selected[tier] = [...new Set(chosen)];
  }

  writeFileSync(BANK_PATH, JSON.stringify(bank, null, 2));
  writeFileSync(TOPICS_PATH, JSON.stringify(selected, null, 2));
  return null;
}

// Restores the default bank with everything enabled.
export function resetTopics() {
  writeFileSync(BANK_PATH, JSON.stringify(DEFAULT_TOPIC_BANK, null, 2));
  writeFileSync(TOPICS_PATH, JSON.stringify(DEFAULT_TOPIC_BANK, null, 2));
}

// Per-player aggregates for the players overview page, most recent first.
export function getPlayerStats() {
  const byPlayer = new Map();
  for (const result of getResults()) {
    const name = (result.player || '').trim();
    if (!name) continue;
    const key = name.toLowerCase();
    if (!byPlayer.has(key)) byPlayer.set(key, { player: name, games: [] });

    const history = Array.isArray(result.history) ? result.history : [];
    const correct = history.filter((h) => h.isCorrect).length;
    byPlayer.get(key).games.push({
      played_at: result.played_at,
      selection: result.selection,
      mode: result.mode,
      won: Boolean(result.won),
      questions: history.length,
      correct,
      accuracy: history.length ? Math.round((correct / history.length) * 100) : 0,
    });
  }

  return [...byPlayer.values()]
    .map((entry) => {
      const questions = entry.games.reduce((n, g) => n + g.questions, 0);
      const correct = entry.games.reduce((n, g) => n + g.correct, 0);
      return {
        ...entry,
        gamesPlayed: entry.games.length,
        wins: entry.games.filter((g) => g.won).length,
        questions,
        correct,
        accuracy: questions ? Math.round((correct / questions) * 100) : 0,
        lastPlayed: entry.games[entry.games.length - 1]?.played_at ?? null,
      };
    })
    .sort((a, b) => new Date(b.lastPlayed) - new Date(a.lastPlayed));
}
