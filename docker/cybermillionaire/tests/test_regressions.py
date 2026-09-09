import unittest
from unittest.mock import patch

from django.conf import settings
if not settings.configured:
    settings.configure(SECRET_KEY="tests-only", DEFAULT_CHARSET="utf-8", ROOT_URLCONF="cybermillionaire.urls", INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.admin", "django.contrib.messages"])
import django
django.setup()
from django.test import RequestFactory
from django.urls import resolve
from django.middleware.csrf import CsrfViewMiddleware
from cybermillionaire.database_insert import parse_question_and_answers
from cybermillionaire import views, question_queue as queues

VALID = "Question: Choose one?\nA. First\nB. Second\nC. Third\nD. Fourth\nCorrect Answer: a"

class ParserTests(unittest.TestCase):
    def test_lowercase_correct_answer(self):
        self.assertEqual(parse_question_and_answers(VALID)[2], 0)

    def test_malformed_answers(self):
        for text in [VALID.replace("D. Fourth\n", ""), VALID.replace("D. Fourth", "D. First"), VALID.replace("B. Second", "A. Second"), VALID.replace("Correct Answer: a", "Correct Answer: Z"), None]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_question_and_answers(text)

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_feedback_routes(self):
        self.assertIs(resolve("/ai-feedback/").func, views.ai_feedback)
        self.assertIs(resolve("/ai-feedback/123/").func, views.ai_game_feedback)

    def test_results_reject_invalid_data_before_database(self):
        for body in ["not json", "[]", "{}", '{"finalMoney": -1, "history": []}']:
            request = self.factory.post("/save-results/", body, content_type="application/json")
            request.session = {"user_id": 1}
            with patch.object(views, "create_game_session") as save:
                self.assertEqual(views.save_results(request).status_code, 400)
                save.assert_not_called()

    def test_csrf_required_for_mutations(self):
        for view in [views.save_results, views.save_topics]:
            request = self.factory.post("/", {})
            response = CsrfViewMiddleware().process_view(request, view, (), {})
            self.assertEqual(response.status_code, 403)

class QueueTests(unittest.TestCase):
    def tearDown(self):
        queues.stop_question_generation(1)

    @patch.object(queues.threading, "Thread")
    def test_restart_cancels_old_queue(self, thread):
        queues.start_question_generation("easy", 1)
        old = queues.running_generators[1]
        queues.question_queues[1] = [{"question": "old"}]
        queues.start_question_generation("expert", 1)
        self.assertTrue(old["stop"].is_set())
        self.assertEqual(queues.get_questions(1), [])
        self.assertEqual(thread.call_args.kwargs["args"][:2], ("expert", 1))

    @patch.object(queues.threading, "Thread")
    def test_reads_are_copies_and_pop_consumes(self, thread):
        queues.start_question_generation("easy", 1)
        queues.question_queues[1] = [1, 2]
        queues.get_questions(1).clear()
        self.assertEqual(queues.pop_questions(1, 1), [1])
        self.assertEqual(queues.get_questions(1), [2])

    @patch.object(queues.threading, "Thread")
    def test_idle_generator_expires(self, thread):
        queues.start_question_generation("easy", 1)
        state = queues.running_generators[1]
        state["last_access"] -= queues.IDLE_TIMEOUT + 1
        with patch.object(queues, "generate_batch") as generate:
            queues.generate_questions_background("easy", 1, state)
            generate.assert_not_called()
        self.assertNotIn(1, queues.running_generators)

if __name__ == "__main__":
    unittest.main()
