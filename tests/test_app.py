import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class FrontendAppTests(unittest.TestCase):
    def create_app(self) -> AppTest:
        return AppTest.from_file(str(APP_PATH), default_timeout=10)

    def test_chat_is_disabled_when_no_data_is_selected(self) -> None:
        app = self.create_app().run()
        app.checkbox[0].uncheck().run()

        self.assertTrue(app.chat_input[0].disabled)
        self.assertEqual(len(app.info), 1)
        self.assertFalse(app.exception)

    @patch.dict(os.environ, {"BACKEND_API_URL": "http://api.example.test/"})
    @patch("requests.post")
    def test_question_is_sent_and_answer_is_displayed(self, post: unittest.mock.Mock) -> None:
        post.return_value = SimpleNamespace(
            ok=True,
            json=lambda: {"answer": "Standard delivery takes three days."},
        )
        app = self.create_app().run()

        app.chat_input[0].set_value("How long is standard delivery?").run()

        post.assert_called_once_with(
            "http://api.example.test/api/ask",
            data={
                "question": "How long is standard delivery?",
                "include_samples": "true",
            },
            files=None,
            timeout=(5, 120),
        )
        self.assertIn(
            "Standard delivery takes three days.",
            [element.value for element in app.markdown],
        )
        self.assertFalse(app.exception)

    @patch("requests.post")
    def test_backend_error_is_shown(self, post: unittest.mock.Mock) -> None:
        post.return_value = SimpleNamespace(
            ok=False,
            status_code=400,
            text="Bad request",
            json=lambda: {"detail": "The CSV file is invalid."},
        )
        app = self.create_app().run()

        app.chat_input[0].set_value("Look up an answer").run()

        self.assertIn(
            "Backend error (400): The CSV file is invalid.",
            [element.value for element in app.error],
        )
        self.assertFalse(app.exception)

    @patch("requests.post", side_effect=requests.ConnectionError("Connection refused"))
    def test_backend_connection_error_is_shown(
        self, post: unittest.mock.Mock
    ) -> None:
        app = self.create_app().run()

        app.chat_input[0].set_value("Look up an answer").run()

        self.assertIn(
            "Could not reach the Hello Agent backend: Connection refused",
            [element.value for element in app.error],
        )
        self.assertFalse(app.exception)

    @patch("requests.post")
    def test_malformed_success_response_is_shown(
        self, post: unittest.mock.Mock
    ) -> None:
        post.return_value = SimpleNamespace(
            ok=True,
            json=lambda: {"unexpected": "shape"},
        )
        app = self.create_app().run()

        app.chat_input[0].set_value("Look up an answer").run()

        self.assertIn(
            "The backend returned an invalid response: 'answer'",
            [element.value for element in app.error],
        )
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
