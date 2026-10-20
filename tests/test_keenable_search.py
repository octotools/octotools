import os
import unittest
from unittest.mock import MagicMock, patch

from octotools.models.initializer import Initializer
from octotools.tools.keenable_search.tool import Keenable_Search_Tool


def fake_response(status_code=200, payload=None, reason="OK"):
    response = MagicMock()
    response.status_code = status_code
    response.reason = reason
    response.json.return_value = payload if payload is not None else {}
    return response


class KeenableSearchTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict("os.environ")
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("KEENABLE_API_KEY", None)
        self.tool = Keenable_Search_Tool()

    def test_keyless_search_uses_public_endpoint_with_app_title(self):
        with patch("requests.post", return_value=fake_response(payload={"results": []})) as post:
            self.tool.execute(query="python")
        self.assertEqual(post.call_args.args[0], "https://api.keenable.ai/v1/search/public")
        headers = post.call_args.kwargs["headers"]
        self.assertEqual(headers["X-Keenable-Title"], "OctoTools")
        self.assertNotIn("X-API-Key", headers)

    def test_api_key_uses_keyed_endpoint(self):
        with patch.dict("os.environ", {"KEENABLE_API_KEY": "test-key"}):
            tool = Keenable_Search_Tool()
        with patch("requests.post", return_value=fake_response(payload={"results": []})) as post:
            tool.execute(query="python")
        self.assertEqual(post.call_args.args[0], "https://api.keenable.ai/v1/search")
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["X-API-Key"], "test-key")
        self.assertNotIn("test-key", str(kwargs["json"]))

    def test_maps_results_and_sends_filters(self):
        payload = {"results": [
            {"title": "Python", "url": "https://www.python.org/", "description": "", "snippet": "Official site.",
             "published_at": "2025-01-02T00:00:00Z"},
            {"title": "Docs", "url": "https://docs.python.org/3/", "description": "Documentation."},
            {"title": "Extra", "url": "https://example.org/", "snippet": "Over the limit."},
        ]}
        with patch("requests.post", return_value=fake_response(payload=payload)) as post:
            result = self.tool.execute(query="python", num_results=2, site="python.org",
                                       published_after="2025-01-01", published_before="2025-12-31")

        self.assertEqual(result, [
            {"title": "Python", "link": "https://www.python.org/", "snippet": "Official site.",
             "published_date": "2025-01-02T00:00:00Z"},
            {"title": "Docs", "link": "https://docs.python.org/3/", "snippet": "Documentation."},
        ])
        self.assertEqual(post.call_args.kwargs["json"], {
            "query": "python", "max_results": 2, "site": "python.org",
            "published_after": "2025-01-01", "published_before": "2025-12-31",
        })

    def test_long_snippets_are_truncated(self):
        payload = {"results": [{"title": "Long", "url": "https://example.org/", "snippet": "x" * 5000}]}
        with patch("requests.post", return_value=fake_response(payload=payload)):
            result = self.tool.execute(query="python")
        self.assertEqual(len(result[0]["snippet"]), 2000)

    def test_num_results_is_capped_at_fifty(self):
        with patch("requests.post", return_value=fake_response(payload={"results": []})) as post:
            result = self.tool.execute(query="python", num_results=100)
        self.assertEqual(post.call_args.kwargs["json"]["max_results"], 50)
        self.assertEqual(result, [{"error": "No results found."}])

    def test_api_error_message_is_reported(self):
        payload = {"error": "Bad request", "message": "Invalid published_after value"}
        with patch("requests.post", return_value=fake_response(400, payload, "Bad Request")):
            result = self.tool.execute(query="python", published_after="last week")
        self.assertEqual(result, [{"error": "Keenable API error (HTTP 400): Invalid published_after value"}])

    def test_loaded_only_when_named_in_enabled_tools(self):
        # Isolate discovery from unrelated tools and their dependencies.
        tool_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "octotools", "tools", "keenable_search",
        )
        with patch(
            "octotools.models.initializer.os.walk",
            return_value=[(tool_dir, [], ["tool.py"])],
        ), patch("requests.post") as post:
            for enabled_tools, loaded in ((["all"], False), (["Keenable_Search_Tool"], True)):
                with self.subTest(enabled_tools=enabled_tools):
                    selected = Initializer(enabled_tools=enabled_tools, model_string="gpt-4o")
                    self.assertEqual("Keenable_Search_Tool" in selected.available_tools, loaded)
                    self.assertEqual("Keenable_Search_Tool" in selected.toolbox_metadata, loaded)
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
