import unittest
from unittest.mock import patch
from modem_os.exceptions import ModemOSException
from modem_os.utils import ModemOSUtils

def perform_deep_analysis(result):
    """Performs a fallback analysis on the given result."""
    return {"analysis": "fallback", "result": result}

class TestPerformDeepAnalysis(unittest.TestCase):
    def setUp(self):
        """Set up common test variables."""
        self.sample_result = "Sample result"
        self.expected_output = {"analysis": "fallback", "result": self.sample_result}

    def test_with_valid_result(self):
        self.assertEqual(perform_deep_analysis(self.sample_result), self.expected_output)

    def test_with_empty_result(self):
        result = ""
        expected_output = {"analysis": "fallback", "result": result}
        self.assertEqual(perform_deep_analysis(result), expected_output)

    def test_with_none_result(self):
        result = None
        expected_output = {"analysis": "fallback", "result": result}
        self.assertEqual(perform_deep_analysis(result), expected_output)

    @patch("modem_os.ModemOS.perform_deep_analysis", side_effect=ModemOSException("Error"))
    def test_with_modem_os_exception(self, mock_modem_os):
        with self.assertRaises(ModemOSException):
            perform_deep_analysis(self.sample_result)

    @patch("modem_os.utils.ModemOSUtils.perform_deep_analysis", return_value={"analysis": "fallback", "result": "Sample result"})
    def test_with_modem_os_utils(self, mock_modem_os_utils):
        output = perform_deep_analysis(self.sample_result)
        self.assertEqual(output, self.expected_output)

    @patch("modem_os.utils.ModemOSUtils.perform_deep_analysis", side_effect=ModemOSException("Error"))
    def test_with_modem_os_utils_exception(self, mock_modem_os_utils):
        with self.assertRaises(ModemOSException):
            perform_deep_analysis(self.sample_result)

if __name__ == "__main__":
    unittest.main()