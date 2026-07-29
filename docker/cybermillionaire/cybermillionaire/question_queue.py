import threading
import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert

question_queues = {}
running_generators = set()


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
    question_text = generation.generate_question(ai_level,user_id)
    question, answers, correct_answer = insert.parse_question_and_answers(question_text)

    return {"question": question,"content": answers,"correct": correct_answer}


def generate_questions_background(ai_level, user_id):

    print("STARTING GENERATOR FOR", user_id, ai_level)
    if user_id not in question_queues:
        question_queues[user_id] = []

    while True:
        try:
            if len(question_queues[user_id]) < 10:
                question = generate_question(ai_level,user_id)
                question_queues[user_id].append(question)
                print("QUEUE SIZE:",len(question_queues[user_id]))
        except Exception as e:
            print("Generation error:", e)

def start_question_generation(ai_level, user_id):
    if user_id in running_generators:
        print("Generator already running")
        return
    running_generators.add(user_id)
    thread = threading.Thread(
        target=generate_questions_background,
        args=(ai_level, user_id),
        daemon=True
    )

    thread.start()
    print("Started question generator for", user_id)