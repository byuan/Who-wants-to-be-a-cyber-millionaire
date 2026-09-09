import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert


# Process-local queues: run one Gunicorn worker until these move to a shared store.
question_queues = {}
running_generators = {}
queue_lock = threading.RLock()
MAX_CONCURRENT = 5
QUEUE_TARGET = 10
IDLE_TIMEOUT = 300


def get_questions(user_id):
    with queue_lock:
        state = running_generators.get(user_id)
        if state:
            state["last_access"] = time.monotonic()
        return list(question_queues.get(user_id, []))


def pop_questions(user_id, amount):
    with queue_lock:
        state = running_generators.get(user_id)
        if state:
            state["last_access"] = time.monotonic()
        queue = question_queues.get(user_id, [])
        questions = queue[:amount]
        question_queues[user_id] = queue[amount:]
        return questions


def stop_question_generation(user_id):
    with queue_lock:
        state = running_generators.pop(user_id, None)
        if state:
            state["stop"].set()
        question_queues.pop(user_id, None)


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

def generate_questions_background(ai_level, user_id, state):
    stop = state["stop"]
    try:
        while not stop.is_set():
            with queue_lock:
                if running_generators.get(user_id) is not state:
                    return
                if time.monotonic() - state["last_access"] >= IDLE_TIMEOUT:
                    return
                amount = min(QUEUE_TARGET - len(question_queues[user_id]), MAX_CONCURRENT)
            if amount <= 0:
                stop.wait(1)
                continue
            questions = generate_batch(ai_level, user_id, amount)
            with queue_lock:
                if running_generators.get(user_id) is not state or stop.is_set():
                    return
                question_queues[user_id].extend(questions)
            if not questions:
                # Failed API calls must not cause an unbounded retry loop.
                stop.wait(5)
    finally:
        with queue_lock:
            if running_generators.get(user_id) is state:
                running_generators.pop(user_id, None)
                question_queues.pop(user_id, None)


def start_question_generation(ai_level, user_id):
    with queue_lock:
        stop_question_generation(user_id)
        state = {"stop": threading.Event(), "last_access": time.monotonic()}
        running_generators[user_id] = state
        question_queues[user_id] = []
        threading.Thread(
            target=generate_questions_background,
            args=(ai_level, user_id, state),
            daemon=True,
        ).start()
