import unittest
import requests

class TestWebsiteReachability(unittest.TestCase):
    def test_website_reachable(self):
        url = 'http://172.17.0.1:8000/'

        try:
            response = requests.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to reach {url}. Status code: {response.status_code}")
        except requests.ConnectionError:
            self.fail(f"Failed to connect to {url}. Make sure your Flask app is running.")

if __name__ == '__main__':
    unittest.main()