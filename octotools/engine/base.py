# Reference: https://github.com/zou-group/textgrad/blob/main/textgrad/engine/base.py

import hashlib
import diskcache_community as dc
from abc import ABC, abstractmethod

class EngineLM(ABC):
    system_prompt: str = "You are a helpful, creative, and smart assistant."
    model_string: str
    @abstractmethod
    def generate(self, prompt, system_prompt=None, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass


class CachedEngine:
    def __init__(self, cache_path):
        super().__init__()
        self.cache_path = cache_path
        self.cache = dc.Cache(
            cache_path,
            disk=dc.SafeDisk.with_types(
                modules=("octotools.models.formatters",)
            ).with_options(on_error="miss"),
        )

    def _hash_prompt(self, prompt: str):
        return hashlib.sha256(f"{prompt}".encode()).hexdigest()

    def _check_cache(self, prompt: str):
        return self.cache.get(prompt)

    def _save_cache(self, prompt: str, response: str):
        try:
            self.cache[prompt] = response
        except TypeError:
            pass

    def __getstate__(self):
        # Remove the cache from the state before pickling
        state = self.__dict__.copy()
        del state['cache']
        return state

    def __setstate__(self, state):
        # Restore the cache after unpickling
        self.__dict__.update(state)
        self.cache = dc.Cache(
            self.cache_path,
            disk=dc.SafeDisk.with_types(
                modules=("octotools.models.formatters",)
            ).with_options(on_error="miss"),
        )