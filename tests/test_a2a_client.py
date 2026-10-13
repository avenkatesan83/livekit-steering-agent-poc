import unittest

from core.a2a_client import caller_response_text, skill_result, status_message_text


class CallerResponseTextTests(unittest.TestCase):
    def test_extracts_dialogflow_response_message(self):
        task = {
            "artifacts": [
                {
                    "parts": [
                        {
                            "data": {
                                "responseMessages": [
                                    {"text": {"text": ["Hello", "caller."]}}
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        self.assertEqual(caller_response_text(task), "Hello caller.")

    def test_returns_none_when_no_response_message_exists(self):
        self.assertIsNone(caller_response_text({"artifacts": []}))


class StatusMessageTextTests(unittest.TestCase):
    def test_extracts_failure_detail(self):
        task = {
            "status": {
                "state": "TASK_STATE_FAILED",
                "message": {"parts": [{"text": "Server error '502 Bad Gateway'"}]},
            }
        }

        self.assertEqual(status_message_text(task), "Server error '502 Bad Gateway'")

    def test_returns_none_without_status_message(self):
        self.assertIsNone(status_message_text({"status": {"state": "TASK_STATE_FAILED"}}))


class SkillResultTests(unittest.TestCase):
    def test_extracts_dfcx_session_and_intent(self):
        task = {
            "artifacts": [
                {
                    "parts": [
                        {
                            "data": {
                                "dfcxSession": "projects/p/locations/us-east1/agents/a/environments/draft/sessions/console-123",
                                "match": {"intent": {"displayName": "MS Password Reset"}},
                            }
                        }
                    ]
                }
            ]
        }

        result = skill_result(task)
        self.assertTrue(result["dfcxSession"].endswith("sessions/console-123"))
        self.assertEqual(result["match"]["intent"]["displayName"], "MS Password Reset")

    def test_returns_empty_dict_without_artifacts(self):
        self.assertEqual(skill_result({}), {})