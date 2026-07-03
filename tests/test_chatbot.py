import unittest

from app.chatbot import get_bot


class SafeXFAQBotTest(unittest.TestCase):
    def test_answers_service_question(self):
        response = get_bot().answer("What services does SafeX offer?")

        self.assertGreater(response["confidence"], 0)
        self.assertIn("SafeX", response["answer"])
        self.assertTrue(response["sources"])

    def test_unknown_question_has_fallback(self):
        response = get_bot().answer("Who won the cricket match yesterday?")

        self.assertIn("contact the SafeX team", response["answer"])
        self.assertEqual(response["sources"][0]["url"], "https://safexsolutions.com/contact/")

    def test_greeting_gets_small_talk_response(self):
        response = get_bot().answer("hello")

        self.assertIn("SafeX AI Assistant", response["answer"])
        self.assertEqual(response["confidence"], 1.0)
        self.assertEqual(response["sources"], [])

    def test_wellbeing_gets_small_talk_response(self):
        response = get_bot().answer("how are you?")

        self.assertIn("doing great", response["answer"])
        self.assertEqual(response["sources"], [])


if __name__ == "__main__":
    unittest.main()
