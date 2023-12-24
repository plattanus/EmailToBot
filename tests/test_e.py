import unittest
from unittest.mock import MagicMock, patch
from ..etb.emailtobot import Authenticator, get_mx, RelayHandler


class AuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self.authenticator = Authenticator()

    def test_call_with_invalid_mechanism_returns_fail_result(self):
        result = self.authenticator(None, None, None, "INVALID", None)
        self.assertFalse(result.success)
        self.assertFalse(result.handled)

    def test_call_with_invalid_auth_data_returns_fail_result(self):
        result = self.authenticator(None, None, None, "LOGIN", "invalid_auth_data")
        self.assertFalse(result.success)
        self.assertFalse(result.handled)

    def test_call_with_invalid_credentials_returns_fail_result(self):
        username = "testuser"
        password = "testpassword"
        auth_data = LoginPassword(username.encode("utf-8"), password.encode("utf-8"))
        result = self.authenticator(None, None, None, "LOGIN", auth_data)
        self.assertFalse(result.success)
        self.assertFalse(result.handled)



class RelayHandlerTest(unittest.TestCase):
    def setUp(self):
        self.relay_handler = RelayHandler()

    @patch("your_module.get_mx")
    @patch("your_module.snedtobot")
    def test_handle_DATA_with_valid_rcpt_tos_calls_snedtobot(self, snedtobot_mock, get_mx_mock):
        envelope = MagicMock()
        envelope.rcpt_tos = ["recipient1@example.com", "recipient2@example.com"]
        get_mx_mock.return_value = "example.com"
        self.relay_handler.handle_DATA(None, None, envelope)
        snedtobot_mock.assert_called_once_with(envelope.mail_from, envelope.rcpt_tos, envelope.original_content)

    # Add more test cases for different scenarios


class GetMxTest(unittest.TestCase):
    def test_get_mx_with_valid_domain_returns_mx_server(self):
        domain = "example.com"
        expected_mx_server = "mail.example.com"
        # Mock the DNS resolver to return the expected MX records
        with patch("dns.resolver.resolve") as resolve_mock:
            mx_record = MagicMock()
            mx_record.exchange = expected_mx_server
            resolve_mock.return_value = [mx_record]
            mx_server = get_mx(domain)
        self.assertEqual(mx_server, expected_mx_server)




if __name__ == "__main__":
    unittest.main()