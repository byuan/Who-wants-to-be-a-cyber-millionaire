import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert


question_queues = {}
running_generators = set()

MAX_CONCURRENT = 5
QUEUE_TARGET = 10


def add_questions(user_id, questions):
    if user_id not in question_queues:
        question_queues[user_id] = []

    question_queues[user_id].extend(questions)


def get_questions(user_id):
    if user_id not in question_queues:
        return []

    return question_queues[user_id]


def pop_questions(user_id, amount):
    if user_id not in question_queues:
        return []

    questions = question_queues[user_id][:amount]
    question_queues[user_id] = question_queues[user_id][amount:]

    return questions


def generate_question(ai_level, user_id):

    question_text = generation.generate_question(
        ai_level,
        user_id
    )

    question, answers, correct_answer = \
        insert.parse_question_and_answers(question_text)

    return {
        "question": question,
        "content": answers,
        "correct": correct_answer
    }


def generate_batch(ai_level, user_id, amount):

    questions = []

    with ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT
    ) as executor:

        futures = [
            executor.submit(
                generate_question,
                ai_level,
                user_id
            )
            for _ in range(amount)
        ]

        for future in as_completed(futures):

            try:
                question = future.result()
                questions.append(question)

            except Exception as e:
                print("Generation error:", e)

    return questions

def generate_initial_questions(ai_level, user_id, amount=5):
    print(
        "Generating initial questions:",
        amount,
        "for",
        user_id
    )

    questions = generate_batch(
        ai_level,
        user_id,
        amount
    )

    print(
        "Initial questions generated:",
        len(questions)
    )

    return questions

def generate_questions_background(ai_level, user_id):

    print(
        "STARTING GENERATOR FOR",
        user_id,
        ai_level
    )

    if user_id not in question_queues:
        question_queues[user_id] = []

    while True:

        try:

            current_size = len(question_queues[user_id])

            if current_size < QUEUE_TARGET:

                amount = min(
                    QUEUE_TARGET - current_size,
                    MAX_CONCURRENT
                )

                print(
                    "Generating",
                    amount,
                    "questions"
                )

                questions = generate_batch(
                    ai_level,
                    user_id,
                    amount
                )

                add_questions(
                    user_id,
                    questions
                )

                print(
                    "QUEUE SIZE:",
                    len(question_queues[user_id])
                )

            else:

                # Don't hammer the CPU while waiting
                threading.Event().wait(1)

        except Exception as e:

            print(
                "Background generation error:",
                e
            )

            threading.Event().wait(1)


def start_question_generation(ai_level, user_id):

    if user_id in running_generators:

        print(
            "Generator already running"
        )

        return

    running_generators.add(user_id)

    thread = threading.Thread(
        target=generate_questions_background,
        args=(ai_level, user_id),
        daemon=True
    )

    thread.start()

    print(
        "Started question generator for",
        user_id
    )