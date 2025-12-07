import unittest

from cybermillionaire import database_insert


class ParseQuestionTests(unittest.TestCase):
    def test_parses_question_and_answers(self):
        sample_text = (
            "Question: What is HTTPS?\n\n"
            "A. A secure version of HTTP\n"
            "B. A programming language\n"
            "C. A database system\n"
            "D. A type of malware\n"
            "Correct Answer: A"
        )

        question, answers, correct_answer = database_insert.parse_question_and_answers(sample_text)

        self.assertEqual(question, "What is HTTPS?")
        self.assertEqual(
            answers,
            [
                "A secure version of HTTP",
                "A programming language",
                "A database system",
                "A type of malware",
            ],
        )
        self.assertEqual(correct_answer, 1)

    def test_raises_error_with_incomplete_answers(self):
        incomplete_text = (
            "Question: Missing answers example\n\n"
            "A. First option\n"
            "B. Second option\n"
            "Correct Answer: A"
        )

        with self.assertRaises(ValueError):
            database_insert.parse_question_and_answers(incomplete_text)


if __name__ == "__main__":
    unittest.main()
