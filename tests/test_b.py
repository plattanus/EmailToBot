import unittest
from unittest.mock import MagicMock, patch

from ..etb.emailtobot import EmailToBot


class EmailToBotTest(unittest.TestCase):
    def setUp(self):
        self.context_mock = MagicMock()
        self.update_mock = MagicMock()

    @patch("your_module.all_chat_id")
    @patch("your_module.my_key")
    async def test_start_sends_message(self, my_key_mock, all_chat_id_mock):
        my_key_mock.return_value = "password123"
        all_chat_id_mock.return_value = set()
        self.update_mock.effective_chat.id = "12345"
        await EmailToBot.start(self.update_mock, self.context_mock)
        self.context_mock.bot.send_message.assert_called_once_with(
            chat_id="12345",
            text="Hello, I can help you to check email!"
        )



if __name__ == "__main__":
    unittest.main()