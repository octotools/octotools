import tempfile
import unittest
from unittest.mock import MagicMock, patch

import diskcache_community

from octotools.engine.openai import ChatOpenAI

planted_calls = []


def planted():
    planted_calls.append(True)
    return "Answer planted in the cache folder."


class Planted:
    def __reduce__(self):
        return (planted, ())


class EngineCacheTests(unittest.TestCase):
    def test_planted_pickle_is_a_cache_miss(self):
        cache_root = tempfile.TemporaryDirectory()
        self.addCleanup(cache_root.cleanup)
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("platformdirs.user_cache_dir", return_value=cache_root.name):
                engine = ChatOpenAI(model_string="gpt-4o-mini", use_cache=True)
        self.addCleanup(engine.cache.close)
        engine.client = MagicMock()
        completion = engine.client.chat.completions.create.return_value
        completion.choices[0].message.content = "Paris."

        # Another writer with the default Disk pickles an object into the folder.
        with diskcache_community.Cache(engine.cache_path) as writer:
            writer[engine.system_prompt + "Capital of France?"] = Planted()

        self.assertEqual(engine.generate("Capital of France?"), "Paris.")
        self.assertEqual(planted_calls, [])
        engine.client.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
