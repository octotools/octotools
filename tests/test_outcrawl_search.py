import unittest
from unittest.mock import MagicMock, patch

from octotools.tools.outcrawl_search.tool import Outcrawl_Search_Tool


def fake_response(status_code=200, payload=None, reason="OK"):
    response = MagicMock()
    response.status_code = status_code
    response.reason = reason
    response.json.return_value = payload if payload is not None else {}
    return response


class OutcrawlSearchTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict("os.environ", {"OUTCRAWL_API_KEY": "test-key"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tool = Outcrawl_Search_Tool()

    def test_missing_key_returns_error(self):
        with patch.dict("os.environ", {}, clear=True):
            tool = Outcrawl_Search_Tool()
        with patch("requests.post") as post:
            result = tool.execute(query="python")
        post.assert_not_called()
        self.assertIn("OUTCRAWL_API_KEY", result[0]["error"])

    def test_maps_results_and_sends_bearer_key(self):
        payload = {"hits": [
            {"url": "https://www.python.org/", "title": "Python", "snippet": "Official site.", "rank": 1},
            {"url": "not-a-url", "title": "Broken", "snippet": "Not a URL.", "rank": 2},
            {"url": "https://docs.python.org/3/", "title": "Docs", "snippet": "Documentation.", "rank": 3},
            {"url": "https://example.org/", "title": "Extra", "snippet": "Over the limit.", "rank": 4},
        ], "usage": {"credits": "0.5"}}
        with patch("requests.post", return_value=fake_response(payload=payload)) as post:
            result = self.tool.execute(query="python", num_results=2)

        self.assertEqual(result, [
            {"title": "Python", "link": "https://www.python.org/", "snippet": "Official site."},
            {"title": "Docs", "link": "https://docs.python.org/3/", "snippet": "Documentation."},
        ])
        self.assertEqual(post.call_args.args[0], "https://api.outcrawl.ai/v1/search")
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["json"], {"query": "python", "limit": 2})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertNotIn("test-key", str(kwargs["json"]))

    def test_num_results_is_capped_at_twenty(self):
        with patch("requests.post", return_value=fake_response(payload={"hits": []})) as post:
            result = self.tool.execute(query="python", num_results=50)
        self.assertEqual(post.call_args.kwargs["json"]["limit"], 20)
        self.assertEqual(result, [{"error": "No results found."}])

    def test_api_error_detail_is_reported(self):
        response = fake_response(401, {"error": "Invalid API key"}, "Unauthorized")
        with patch("requests.post", return_value=response):
            result = self.tool.execute(query="python")
        self.assertEqual(result, [{"error": "Outcrawl API error (HTTP 401): Invalid API key"}])

    def test_api_error_without_json_body_uses_reason(self):
        response = fake_response(429, reason="Too Many Requests")
        response.json.side_effect = ValueError("no json")
        with patch("requests.post", return_value=response):
            result = self.tool.execute(query="python")
        self.assertEqual(result, [{"error": "Outcrawl API error (HTTP 429): Too Many Requests"}])


if __name__ == "__main__":
    unittest.main()
