"""Dynamic question generation via the Anthropic Claude API (Claude Fable 5)."""

from __future__ import annotations

import random
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Single client instance reused across all calls. Reads ANTHROPIC_API_KEY
# from the environment by default.
# ---------------------------------------------------------------------------
_client = Anthropic()

_MODEL = "claude-fable-5"

# ---------------------------------------------------------------------------
# Topic banks per difficulty tier
# ---------------------------------------------------------------------------
_TOPICS: dict[str, list[str]] = {
    "easy": [
        "Passwords", "Internet Safety", "Cyberbullying", "Social Media",
        "Secure Websites", "Hacking", "Digital Footprints", "Data",
        "Phishing", "Safe Downloading",
    ],
    "medium": [
        "Passwords", "Phishing", "Encryption", "Firewall", "Malware",
        "Two-factor authentication", "Social Engineering",
        "Network Security", "Endpoint Security", "Advanced Persistent Threats",
    ],
    "hard": [
        "Intrusion Detection Systems", "Cyber Threat Intelligence",
        "Digital Forensics", "Cryptography", "Blockchain Security",
        "Secure Coding Practices", "Ethical Hacking", "Social Engineering",
        "Cyber Incident Response", "Network Encryption",
    ],
    "expert": [
        "TCP Protocol", "Wireless Security Protocol", "HTTP Headers",
        "Virtualization", "Kerberos Authentication", "TCP/UDP Protocol",
        "SSL/X509 Certificates", "Asymmetric/Symmetric Encryption for Cryptography",
        "Linux/Unix System Forensics", "Technical Aspects of Network Protocols",
    ],
}

# System prompt and human-readable level label per tier
_LEVEL_META: dict[str, tuple[str, str]] = {
    "easy":   ("You are an elementary school teacher creating a cybersecurity quiz.",
               "primary school"),
    "medium": ("You are a high school teacher creating a cybersecurity quiz.",
               "secondary school"),
    "hard":   ("You are a cybersecurity professor creating a quiz.",
               "college"),
    "expert": ("You are a cybersecurity expert creating a quiz.",
               "expert with technical experience"),
}

_PROMPT_TEMPLATE = (
    "Write one unique {level} level cybersecurity quiz question about {topic} "
    "for an educational trivia game, and provide multiple-choice answers "
    "(one correct, three incorrect) similar to the game style of "
    "Who Wants to Be a Millionaire. "
    "Respond with ONLY the following format and nothing else (no preamble, "
    "no markdown):\n"
    "Question: <question>\n\n"
    "A. <answer>\n"
    "B. <answer>\n"
    "C. <answer>\n"
    "D. <answer>\n\n"
    "Correct Answer: <letter>"
)


class GenerationRefusedError(RuntimeError):
    """Raised when the model declines to generate a question."""


def generate_question(tier: str) -> str:
    """
    Generate one cybersecurity multiple-choice question for *tier*.

    *tier* must be one of: ``"easy"``, ``"medium"``, ``"hard"``, ``"expert"``.

    Returns the raw model response string, ready for
    :func:`database_insert.parse_question_and_answers`.

    Raises :class:`GenerationRefusedError` if the model's safety classifiers
    decline the request (stop_reason == "refusal"), so callers can skip the
    question and retry rather than inserting an unparseable response.
    """
    if tier not in _LEVEL_META:
        raise ValueError(f"Unknown tier {tier!r}. Expected one of {list(_LEVEL_META)}")

    system_msg, level_label = _LEVEL_META[tier]
    topic = random.choice(_TOPICS[tier])

    message = _client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=system_msg,
        messages=[
            {
                "role": "user",
                "content": _PROMPT_TEMPLATE.format(level=level_label, topic=topic),
            }
        ],
    )

    if message.stop_reason == "refusal":
        raise GenerationRefusedError(
            f"Model declined to generate a question about {topic!r}"
        )

    # Concatenate text blocks (reasoning/other block types are skipped)
    return "".join(
        block.text for block in message.content if block.type == "text"
    )


if __name__ == "__main__":
    print(generate_question("expert"))
