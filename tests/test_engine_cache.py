import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

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
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        root = stack.enter_context(tempfile.TemporaryDirectory())
        stack.enter_context(patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}))
        stack.enter_context(patch("platformdirs.user_cache_dir", return_value=root))
        self.client = stack.enter_context(patch("octotools.engine.openai.OpenAI")).return_value

    def test_planted_pickle_is_a_cache_miss(self):
        engine = ChatOpenAI(model_string="gpt-4o-mini", use_cache=True)
        self.addCleanup(engine.cache.close)
        completion = engine.client.chat.completions.create.return_value
        completion.choices[0].message.content = "Paris."

        # Another writer with the default Disk pickles an object into the folder.
        with diskcache_community.Cache(engine.cache_path) as writer:
            writer[engine.system_prompt + "Capital of France?"] = Planted()

        self.assertEqual(engine.generate("Capital of France?"), "Paris.")
        self.assertEqual(planted_calls, [])
        engine.client.chat.completions.create.assert_called_once()

    def test_cold_start_reads_existing_formatter(self):
        from octotools.models.formatters import QueryAnalysis

        with tempfile.TemporaryDirectory() as root:
            with diskcache_community.Cache(root) as writer:
                writer["query"] = QueryAnalysis(
                    concise_summary="saved",
                    required_skills="",
                    relevant_tools="",
                    additional_considerations="",
                )

            reader = dedent("""\
                import sys
                from octotools.engine.base import CachedEngine

                engine = CachedEngine(sys.argv[1])
                with engine.cache:
                    query = engine._check_cache("query")
                    assert "query" in engine.cache
                    assert query.concise_summary == "saved"
            """)
            subprocess.run(
                [sys.executable, "-c", reader, root],
                cwd=Path(__file__).resolve().parents[1],
                check=True,
            )

    def test_scorer_caches_repeated_verifications(self):
        gaia = import_module("tasks.gaia-text.calculate_score")
        parse = self.client.beta.chat.completions.parse
        answer = gaia.AnswerVerification(analysis="Exact match", true_false=True)
        parse.return_value.choices[0].message.parsed = answer

        for _ in range(2):
            scorer = gaia.ResultScorer()
            self.addCleanup(scorer.llm_engine.cache.close)
            self.assertEqual(
                scorer.answer_verification("42", "42"), ("Exact match", True)
            )
        parse.assert_called_once()

    def test_scorer_reads_only_its_trusted_legacy_type(self):
        gaia = import_module("tasks.gaia-text.calculate_score")
        engine = gaia.ResultScorer().llm_engine
        self.addCleanup(engine.cache.close)
        response_format = gaia.AnswerVerification
        answer = response_format(analysis="Saved", true_false=True)
        with diskcache_community.Cache(engine.cache_path) as writer:
            writer[engine.system_prompt + "legacy"] = answer
            writer[engine.system_prompt + "other"] = gaia.BinaryAnswerVerification(
                true_false=False
            )

        parse = engine.client.beta.chat.completions.parse
        self.assertEqual(engine.generate("legacy", response_format=response_format), answer)
        parse.assert_not_called()
        parse.return_value.choices[0].message.parsed = answer
        self.assertEqual(engine.generate("other", response_format=response_format), answer)
        parse.assert_called_once()

    def test_tutorial_caches_reject_planted_pickles(self):
        tutorials = Path(__file__).resolve().parents[1] / "tutorials"
        for name in ("02_llm_engine_.md", "09_caching___cachedengine___.md"):
            with self.subTest(tutorial=name), tempfile.TemporaryDirectory() as root:
                blocks = re.findall(r"```python\n(.*?)```", (tutorials / name).read_text(), re.S)
                snippet = next(block for block in blocks if "class CachedEngine:" in block)
                namespace = {}
                exec(dedent(snippet), namespace)
                engine = namespace["CachedEngine"](root)
                with engine.cache, diskcache_community.Cache(root) as writer:
                    engine._save_cache("question", "answer")
                    self.assertEqual(engine._check_cache("question"), "answer")
                    (key,) = writer
                    writer[key] = Planted()
                    self.assertIsNone(engine._check_cache("question"))
                    self.assertEqual(planted_calls, [])


if __name__ == "__main__":
    unittest.main()
