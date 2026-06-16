from openai import OpenAI
import random

# Bags of words for each level
BAG_O_WORDS_PRIMARY = [
    'Passwords', 'Internet Safety', 'Cyberbullying', 'Social Media',
    'Secure Websites', 'Hacking', 'Digital Footprints', 'Data',
    'Phishing', 'Safe Downloading'
]

BAG_O_WORDS_SECONDARY = [
    'Passwords', 'Phishing', 'Encryption', 'Firewall', 'Malware',
    'Two-factor authentication', 'Social Engineering', 'Network Security',
    'Endpoint Security', 'Advanced Persistent Threats'
]

BAG_O_WORDS_COLLEGE = [
    'Intrusion Detection Systems', 'Cyber Threat Intelligence',
    'Digital Forensics', 'Cryptography', 'Blockchain Security',
    'Secure Coding Practices', 'Ethical Hacking', 'Social Engineering',
    'Cyber Incident Response', 'Network Encryption'
]

BAG_O_WORDS_EXPERT = [
    'TCP Protocol', 'Wireless Security Protocol', 'HTTP Headers',
    'Virtualization', 'Kerberos Authentication', 'TCP/UDP Protocol',
    'SSL/X509 Certificates', 'Asymmetric/Symmetric Encryption for Cryptography',
    'Linux/Unix System Forensics', 'Technical Aspects of Network Protocols'
]

# Dictionary to hold all the level choices
levels = {
    "easy": (
        BAG_O_WORDS_PRIMARY,
        "You are an elementary school teacher trying to create a cybersecurity quiz.",
        "primary school"
    ),
    "medium": (
        BAG_O_WORDS_SECONDARY,
        "You are a high school teacher trying to create a cybersecurity quiz.",
        "secondary school"
    ),
    "hard": (
        BAG_O_WORDS_COLLEGE,
        "You are a cybersecurity professor trying to create a quiz.",
        "college"
    ),
    "expert": (
        BAG_O_WORDS_EXPERT,
        "You are a cybersecurity expert trying to create a quiz.",
        "expert with technical experience"
    )
}

# Pick a random word from a bag
def pick_a_word(BAG_O_WORDS):
    index = random.randint(0, len(BAG_O_WORDS) - 1)
    return BAG_O_WORDS[index]

# Function that reaches out to the API
def api(BAG_O_WORDS, content, question_level):
    word = pick_a_word(BAG_O_WORDS)

    client = OpenAI(api_key="")

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": content
            },
            {
                "role": "user",
                "content": (
                    f"Write one unique {question_level} level cybersecurity question about {word} "
                    "and provide multiple answers (one correct, three incorrect, but state the correct answer) "
                    "similar to the game style of Who Wants to Be a Millionaire.\n\n"
                    "Format:\n"
                    "Question: <question>\n\n"
                    "A. <answer>\n"
                    "B. <answer>\n"
                    "C. <answer>\n"
                    "D. <answer>\n\n"
                    "Correct Answer: <correct answer>"
                )
            }
        ]
    )

    return completion.choices[0].message.content

def generate_question(level):
    BAG_O_WORDS = levels[level][0]
    content = levels[level][1]
    question_level = levels[level][2]

    return api(BAG_O_WORDS, content, question_level)

if __name__ == "__main__":
    level = "expert"
    print(generate_question(level))