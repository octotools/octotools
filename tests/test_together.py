import base64
import io
import json
import unittest
from contextlib import ExitStack
from unittest.mock import patch

import requests
from PIL import Image

from octotools.engine.factory import create_llm_engine


MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


class TogetherCompatibilityTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.dict("os.environ", {"TOGETHER_API_KEY": "test-key"}))
        self.requests = []

        def respond(session, method, url, **kwargs):
            self.requests.append((method, url, kwargs))
            response = requests.Response()
            response.status_code = 200
            response.headers["Content-Type"] = "application/json"
            response._content = json.dumps({
                "id": "chat-test",
                "object": "chat.completion",
                "created": 0,
                "model": MODEL,
                "choices": [{
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "Test answer"},
                }],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            }).encode()
            response.url = url
            return response

        stack.enter_context(patch(
            "requests.sessions.Session.request", autospec=True, side_effect=respond
        ))

    def request_body(self):
        self.assertEqual(len(self.requests), 1)
        method, url, options = self.requests[0]
        self.assertEqual(method.upper(), "POST")
        self.assertTrue(url.endswith("/chat/completions"), url)
        self.assertEqual(options["headers"]["Authorization"], "Bearer test-key")
        return json.loads(options["data"])

    def test_text_call_uses_the_sdk_and_returns_content(self):
        engine = create_llm_engine(f"together-{MODEL}", is_multimodal=False)
        self.assertEqual(engine.generate("Hello", max_tokens=17), "Test answer")
        body = self.request_body()
        self.assertEqual(body["model"], MODEL)
        self.assertEqual(body["max_tokens"], 17)
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["top_p"], 0.99)
        self.assertEqual(body["messages"], [
            {"role": "system", "content": engine.system_prompt},
            {"role": "user", "content": "Hello"},
        ])

    def test_image_call_preserves_the_image_bytes(self):
        image = io.BytesIO()
        Image.new("RGB", (3, 2), "white").save(image, format="JPEG")
        image_bytes = image.getvalue()
        engine = create_llm_engine(f"together-{MODEL}", is_multimodal=True)
        self.assertEqual(engine.generate(["Describe", image_bytes]), "Test answer")
        body = self.request_body()
        self.assertEqual(body["messages"][1]["content"], [
            {"type": "text", "text": "Describe"},
            {"type": "image_url", "image_url": {
                "url": "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode(),
            }},
        ])


if __name__ == "__main__":
    unittest.main()
