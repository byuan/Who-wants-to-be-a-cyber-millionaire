// File-backed persistence for game results and topic settings.
// Both files live in data/ and are gitignored (runtime state, not source).
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const RESULTS_PATH = join(here, '..', 'data', 'results.json');
const TOPICS_PATH = join(here, '..', 'data', 'topic_settings.json');

// Topic banks per generation tier (from the original dynamic_question_generation.py)
export const TOPIC_BANK = {
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

export const TIERS = Object.keys(TOPIC_BANK);

function readJson(path, fallback) {
  if (!existsSync(path)) return fallback;
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return fallback;
  }
}

export function getResults() {
  return readJson(RESULTS_PATH, []);
}

export function appendResult(result) {
  const results = getResults();
  results.push({ played_at: new Date().toISOString(), ...result });
  writeFileSync(RESULTS_PATH, JSON.stringify(results, null, 2));
  return results.length;
}

// Selected topics per tier; defaults to the full bank when never configured.
export function getTopics() {
  const saved = readJson(TOPICS_PATH, null);
  if (!saved) return { ...TOPIC_BANK };
  const topics = {};
  for (const tier of TIERS) {
    const valid = (saved[tier] || []).filter((t) => TOPIC_BANK[tier].includes(t));
    topics[tier] = valid.length > 0 ? valid : [...TOPIC_BANK[tier]];
  }
  return topics;
}

// Validates that every tier keeps at least one topic (an empty tier would
// leave dynamic games with nothing to generate from — the bug in the
// original save_topics view). Returns an error string or null.
export function saveTopics(selection) {
  const topics = {};
  for (const tier of TIERS) {
    const chosen = Array.isArray(selection[tier])
      ? selection[tier].filter((t) => TOPIC_BANK[tier].includes(t))
      : [];
    if (chosen.length === 0) {
      return `Select at least one topic for every level (missing: ${tier}).`;
    }
    topics[tier] = chosen;
  }
  writeFileSync(TOPICS_PATH, JSON.stringify(topics, null, 2));
  return null;
}
