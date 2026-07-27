import threading

import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert
from .question_queue import add_questions


def generate_questions(difficulty, user_id):
    questions = []
    for i in range(10):
        try:

            question_text = generation.generate_question(
                difficulty,
                user_id
            )


            question, answers, correct_answer = insert.parse_question_and_answers(
                question_text
            )


            questions.append({
                "question": question,
                "answers": answers,
                "correct_answer": correct_answer
            })


            print(
                f"Background generated {i+1}/10"
            )


        except Exception as e:

            print(
                "Background generation error:",
                e
            )


    add_questions(
        user_id,
        questions
    )



def start_background_generation(difficulty, user_id):

    thread = threading.Thread(
        target=generate_questions,
        args=(difficulty,user_id),
        daemon=True
    )

    thread.start()