import unittest

from agents.finish_queue_agent import is_queue_transfer


class QueueTransferDetectionTests(unittest.TestCase):
    def test_detects_dialogflow_transfer_reply(self):
        reply = (
            "Sure, you've asked a help to reset your microsoft password. "
            "Let me transfer to an agent to assist your further."
        )
        self.assertTrue(is_queue_transfer(reply))

    def test_ignores_normal_reply(self):
        self.assertFalse(is_queue_transfer("Your password has been reset."))

    def test_ignores_empty_reply(self):
        self.assertFalse(is_queue_transfer(None))
